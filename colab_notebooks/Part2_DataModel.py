# Part 2: Model & Data Preparation
# ================================
import torch
from datasets import concatenate_datasets
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# NOTE: This part assumes Part 1 has been run and 'datasets' variable exists.

# Dataset Weights
WEIGHTS = {
    "natural": 1,
    "prompts": 3,
    "persona": 6,
    "cognitive": 6
}

# Configuration
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

if 'datasets' in locals() and datasets:
    print("\n=== PART 2: DATA & MODEL ===")
    
    # 1. Format Datasets (Alpaca Style)
    def format_alpaca(example):
        inst = example.get('instruction', '')
        inp = example.get('input', '')
        out = example.get('output', '')
        # Combined Instruction + Input + Response
        text = f"Instruction:\n{inst}\n\nInput:\n{inp}\n\nResponse:\n{out}" if inp else f"Instruction:\n{inst}\n\nResponse:\n{out}"
        return {"text": text}

    combined_list = []
    print("Formatting and Mixing Datasets...")

    for name, ds in datasets.items():
        w = WEIGHTS.get(name, 1)
        # Apply formatting and keep only 'text' column
        ds_fmt = ds.map(format_alpaca).select_columns(["text"])
        # Oversampling based on weights
        for _ in range(w): 
            combined_list.append(ds_fmt)

    # Concatenate all lists into one Training Dataset
    train_dataset = concatenate_datasets(combined_list).shuffle(seed=42)
    print(f"✅ Final Training Dataset Size: {len(train_dataset)} records")

    # 2. Model & Tokenizer
    print("Loading Model & Tokenizer...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token 

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    # 3. LoRA Configuration
    peft_config = LoraConfig(
        r=64,
        lora_alpha=128,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
    print("Model Prep Complete. Ready for Part 3.")
else:
    print("❌ Datasets not loaded or empty. Please run Part 1 first.")
