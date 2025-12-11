import os
import json
import yaml
import argparse
import torch
import logging
from datasets import load_dataset, concatenate_datasets
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train(config_path, run_id):
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    hyperparams = config['hyperparameters']
    output_dir = f"{config['output_dir_base']}_{run_id}"
    
    logger.info(f"Starting run: {run_id}")
    logger.info(f"Base Model: {config['base_model_name']}")
    logger.info(f"Output Dir: {output_dir}")

    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(config['base_model_name'], trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right" # Fix for fp16

    # Load Datasets
    logger.info("Loading datasets...")
    data_files = {"train": config['dataset_path_natural']}
    dataset = load_dataset("json", data_files=data_files, split="train")
    
    if config.get('use_prompts_dataset') and os.path.exists(config['dataset_path_prompts']):
        try:
            prompts_ds = load_dataset("json", data_files={"train": config['dataset_path_prompts']}, split="train")
            # Up-sample prompts? Or just mix them in.
            # Since prompts are few (26), let's repeat them 10x to ensure they aren't drowned out?
            # For now, just simple concatenation.
            for _ in range(5): # Repeat 5 times
                 dataset = concatenate_datasets([dataset, prompts_ds])
            logger.info(f"Mixed in prompts dataset (x5). Total records: {len(dataset)}")
        except Exception as e:
            logger.warning(f"Could not load prompts dataset: {e}")

    # QLoRA Config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    # Load Model
    model = AutoModelForCausalLM.from_pretrained(
        config['base_model_name'],
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model.config.use_cache = False
    model.config.pretraining_tp = 1
    model = prepare_model_for_kbit_training(model)

    # LoRA Config
    peft_config = LoraConfig(
        lora_alpha=hyperparams['lora_alpha'],
        lora_dropout=hyperparams['lora_dropout'],
        r=hyperparams['lora_r'],
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=hyperparams['target_modules']
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=hyperparams['num_train_epochs'],
        per_device_train_batch_size=hyperparams['per_device_train_batch_size'],
        gradient_accumulation_steps=hyperparams['gradient_accumulation_steps'],
        learning_rate=hyperparams['learning_rate'],
        weight_decay=0.001,
        fp16=True,
        bf16=False,
        max_grad_norm=hyperparams['max_grad_norm'],
        max_steps=-1,
        warmup_ratio=hyperparams['warmup_ratio'],
        group_by_length=True,
        lr_scheduler_type="constant",
        logging_steps=10,
        save_strategy="epoch",
        optim="paged_adamw_32bit"
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="output", # Simple fine-tuning on text, or use formatting func
        max_seq_length=hyperparams['max_seq_length'],
        tokenizer=tokenizer,
        args=training_args,
        packing=False,
    )

    # Train
    logger.info("Starting training...")
    trainer.train()
    
    # Save
    logger.info(f"Saving model to {output_dir}")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    # Update Runs Registry
    update_registry(run_id, output_dir, config['base_model_name'])

def update_registry(run_id, output_dir, base_model):
    REGISTRY_PATH = "finetune/haithm_style/runs.json"
    try:
        from datetime import datetime
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, 'r') as f:
                runs = json.load(f)
        else:
            runs = []
            
        runs.append({
            "run_id": run_id,
            "date": datetime.now().isoformat(),
            "output_dir": output_dir,
            "base_model": base_model,
            "status": "COMPLETED"
        })
        
        with open(REGISTRY_PATH, 'w') as f:
            json.dump(runs, f, indent=2)
            
    except Exception as e:
        logger.error(f"Failed to update registry: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to config yaml")
    parser.add_argument("--run-id", required=True, help="Unique Run ID")
    args = parser.parse_args()
    
    train(args.config, args.run_id)
