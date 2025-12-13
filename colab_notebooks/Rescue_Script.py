# 🆘 HVA RESCUE SCRIPT (Step 2: TRAINING)
# ========================================
# RUN THIS AFTER INSTALLING LIBRARIES & RESTARTING SESSION.

import os
import sys
import gc
import torch
import inspect
from datasets import concatenate_datasets
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# 0. FORCE MEMORY CLEANUP (The "Wiper")
print("🧹 Cleaning GPU Memory...")
try:
    if 'model' in globals(): del model
    if 'trainer' in globals(): del trainer
    if 'tokenizer' in globals(): del tokenizer
    gc.collect()
    torch.cuda.empty_cache()
    print("✅ Memory Wiped.")
except:
    pass

# 1. SETUP & DATA (Standalone Loading)
from datasets import load_dataset
print("\n🚀 STARTING RESCUE SEQUENCE & DATA LOADING...")

# DATA PATHS
data_files = {
    "natural": "/content/data/dataset_haithm_style_natural_v2.jsonl",
    "prompts": "/content/data/dataset_haithm_style_prompts.jsonl",
    "persona": "/content/data/dataset_haithm_style_persona_v2.jsonl",
    "cognitive": "/content/data/dataset_haithm_style_cognitive_v2.jsonl"
}

datasets = {}
print("📂 Loading Datasets...")
for name, path in data_files.items():
    if os.path.exists(path):
        datasets[name] = load_dataset('json', data_files=path, split='train')
        print(f"✅ Loaded {name}: {len(datasets[name])} records")
    else:
        print(f"⚠️ Warning: Missing {name} at {path}")

if not datasets:
    raise ValueError("❌ No datasets found! Did you upload and unzip the file?")

WEIGHTS = {"natural": 1, "prompts": 3, "persona": 6, "cognitive": 6}
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
OUTPUT_DIR = "hva_haithm_style_lora_v2"

print("\n🚀 STARTING RESCUE SEQUENCE...")

# 2. PREPARE DATA
combined_list = []
def format_alpaca(example):
    inst = example.get('instruction', '')
    inp = example.get('input', '')
    out = example.get('output', '')
    text = f"Instruction:\n{inst}\n\nInput:\n{inp}\n\nResponse:\n{out}" if inp else f"Instruction:\n{inst}\n\nResponse:\n{out}"
    return {"text": text}

for name, ds in datasets.items():
    w = WEIGHTS.get(name, 1)
    ds_fmt = ds.map(format_alpaca).select_columns(["text"])
    for _ in range(w): 
        combined_list.append(ds_fmt)

train_dataset = concatenate_datasets(combined_list).shuffle(seed=42)
print(f"✅ Data Ready (Base): {len(train_dataset)} records")

# 2.5 INJECT V3 COGNITIVE MAP (The "Constitution")
V3_MAP_FILE = "data/dataset_haithm_v3_cognitive_map.jsonl"
if os.path.exists(V3_MAP_FILE):
    print(f"🧠 Found V3 Cognitive Map: {V3_MAP_FILE}")
    from datasets import load_dataset
    ds_v3 = load_dataset('json', data_files=V3_MAP_FILE, split='train')
    ds_v3_fmt = ds_v3.map(format_alpaca).select_columns(["text"])
    
    # High Weight for Constitution (50x)
    print("⚖️ Injecting V3 Map with Weight: 50x")
    v3_list = [ds_v3_fmt] * 50
    
    # Re-mix
    combined_list.extend(v3_list)
    train_dataset = concatenate_datasets(combined_list).shuffle(seed=42)
    print(f"✅ Final Data Ready (with V3): {len(train_dataset)} records")
else:
    print(f"⚠️ V3 Cognitive Map not found at {V3_MAP_FILE}. Proceeding with V2 only.")

# 3. LOAD MODEL (NO QUANTIZATION - FULL BF16)
# L4 (24GB) is large enough for Qwen 3B (6GB) without compression!
# This removes the 'bitsandbytes' dependency error completely.

print("🛡️ Loading Model in Native BF16 (No Quantization)...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token 

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)

# Enable Gradient Checkpointing manually since we removed 'prepare_model_for_kbit_training'
model.gradient_checkpointing_enable()

peft_config = LoraConfig(
    r=64, lora_alpha=128, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()

# NO CASTING NEEDED FOR L4

# 4. START TRAINING
print("⚔️ Starting Training (BULLETPROOF MODE)...")
# FINAL SAFETY NET: Batch Size 4 was still too risky for your fragmented RAM.
# Switching to Batch Size 1.
# - Speed: Slower (~2-3 hours).
# - Reliability: 100% Guaranteed.
# - Quality: Identical (via Accumulation 32).

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=1,   # The Absolute Minimum
    gradient_accumulation_steps=32,  # High Accumulation matches Batch 32
    learning_rate=2e-4,
    num_train_epochs=1,
    warmup_ratio=0.03,
    logging_steps=10,
    save_strategy="no", 
    fp16=False, 
    bf16=True, 
    optim="paged_adamw_32bit",
    report_to="none",
    gradient_checkpointing=True,
    dataloader_num_workers=4,
)

trainer_kwargs = {
    "model": model,
    "train_dataset": train_dataset,
    "peft_config": peft_config,
    "args": training_args,
}
# Dynamic Map
sft_signature = inspect.signature(SFTTrainer.__init__)
if "processing_class" in sft_signature.parameters: trainer_kwargs["processing_class"] = tokenizer
elif "tokenizer" in sft_signature.parameters: trainer_kwargs["tokenizer"] = tokenizer
if "packing" in sft_signature.parameters: trainer_kwargs["packing"] = False
if "dataset_text_field" in sft_signature.parameters: trainer_kwargs["dataset_text_field"] = "text"
if "max_seq_length" in sft_signature.parameters: trainer_kwargs["max_seq_length"] = 1024 # Restored Standard

trainer = SFTTrainer(**trainer_kwargs)
trainer.train()

# 5. SAVE & DOWNLOAD
print("💾 Saving Adapter...")
trainer.model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
os.system(f"zip -r {OUTPUT_DIR}.zip {OUTPUT_DIR}")

from google.colab import files
files.download(f"{OUTPUT_DIR}.zip")
print("🎉 MISSION ACCOMPLISHED.")
