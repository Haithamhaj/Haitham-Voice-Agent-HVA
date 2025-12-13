# HVA Finetune V2 - Haithm Mini-Me (Text Only)
# Target: Qwen/Qwen2.5-3B-Instruct
# Mode: QLoRA (4-bit)
# Platform: Google Colab (Robust / Dynamic Args)

# ==========================================
# PART 1: SETUP & CONFIGURATION
# ==========================================
print("=== PART 1: SETUP ===")
try:
    import torch
    import os
    import inspect
    from datasets import load_dataset, concatenate_datasets
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer
    print("✅ Dependencies already installed.")
except ImportError:
    print("📦 Installing dependencies...")
    os.system("pip install -q -U torch transformers peft bitsandbytes datasets scipy trl")
    
    import torch
    import os
    import inspect
    from datasets import load_dataset, concatenate_datasets
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        TrainingArguments,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer

# Configuration
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
OUTPUT_DIR = "hva_haithm_style_lora_v2"
MAX_SEQ_LENGTH = 1024

# Dataset Weights
WEIGHTS = {
    "natural": 1,
    "prompts": 3,
    "persona": 6,
    "cognitive": 6
}

# Helper: Load Datasets safely
data_files = {
    "natural": "/content/data/dataset_haithm_style_natural_v2.jsonl",
    "prompts": "/content/data/dataset_haithm_style_prompts.jsonl",
    "persona": "/content/data/dataset_haithm_style_persona_v2.jsonl",
    "cognitive": "/content/data/dataset_haithm_style_cognitive_v2.jsonl"
}

datasets = {}
print("Checking for datasets...")
for name, path in data_files.items():
    if os.path.exists(path):
        datasets[name] = load_dataset('json', data_files=path, split='train')
        print(f"✅ Loaded {name}: {len(datasets[name])} records")
    else:
        print(f"⚠️ Warning: Missing {name} at {path}")

if not datasets:
    # Graceful exit for local editing, but error in Colab
    print("❌ No datasets found! (If running locally, ignore this. If in Colab, unzip first.)")
else:
    print("Setup Complete. Ready for Part 2.")


# ==========================================
# PART 2: DATA FORMATTING & MODEL PREP
# ==========================================
if datasets:
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
    print(f"✅ Variable 'train_dataset' is now defined.")

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


# ==========================================
# PART 3: TRAINING (DYNAMIC/BULLETPROOF)
# ==========================================
if 'train_dataset' in locals() and 'model' in locals():
    print("\n=== PART 3: TRAINING ===")
    print("Configuring Trainer (Dynamic Mode)...")

    # 1. Standard Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        num_train_epochs=3,
        warmup_ratio=0.03,
        logging_steps=10,
        save_strategy="no", 
        fp16=False,
        bf16=True, 
        optim="paged_adamw_32bit",
        report_to="none",
    )

    # 2. Dynamic Allocator
    # This checks what SFTTrainer actually accepts to avoid errors
    sft_signature = inspect.signature(SFTTrainer.__init__)
    accepted_params = sft_signature.parameters.keys()
    print(f"ℹ️ SFTTrainer params: {list(accepted_params)}")

    trainer_kwargs = {
        "model": model,
        "train_dataset": train_dataset,
        "peft_config": peft_config,
        "args": training_args,
    }

    # --- DYNAMIC PARAMETER MAPPING ---

    # 1. Pass Tokenizer (Renamed to 'processing_class' in new versions)
    if "processing_class" in accepted_params:
        trainer_kwargs["processing_class"] = tokenizer
        print("✅ Mapped tokenizer -> processing_class")
    elif "tokenizer" in accepted_params:
        trainer_kwargs["tokenizer"] = tokenizer
        print("✅ Mapped tokenizer -> tokenizer")

    # 2. Pass Max Seq Length
    if "max_seq_length" in accepted_params:
        trainer_kwargs["max_seq_length"] = MAX_SEQ_LENGTH
        print("✅ Enabled max_seq_length")

    # 3. Pass Dataset Text Field
    if "dataset_text_field" in accepted_params:
        trainer_kwargs["dataset_text_field"] = "text"
        print("✅ Enabled dataset_text_field")

    # 4. Pass Packing
    if "packing" in accepted_params:
        trainer_kwargs["packing"] = False
        print("✅ Enabled packing")

    # ----------------------------------

    print("🚀 Initializing Trainer...")
    trainer = SFTTrainer(**trainer_kwargs)

    print("🚀 Starting Training Now... (This may take 1-2 hours)")
    trainer.train()

    # Save & Download
    print(f"✅ Training Complete. Saving adapter to {OUTPUT_DIR}...")
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("📦 Zipping output for download...")
    output_zip = f"{OUTPUT_DIR}.zip"
    os.system(f"zip -r {output_zip} {OUTPUT_DIR}")

    print(f"🎉 DONE! Download {output_zip} now.")
    try:
        from google.colab import files
        files.download(output_zip)
    except:
        print(f"Download manually from file explorer on the left.")
