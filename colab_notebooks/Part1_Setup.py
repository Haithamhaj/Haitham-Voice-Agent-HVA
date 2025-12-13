# Part 1: Setup & Configuration
# =============================
import os

print("=== PART 1: SETUP ===")
try:
    import torch
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
    os.system("pip uninstall -y pillow")
    os.system("pip install pillow==9.5.0")
    os.system("pip install -q -U torch transformers peft bitsandbytes datasets scipy trl")
    
    import torch
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
    print("❌ No datasets found! Did you upload and unzip the file?")
else:
    print("Setup Complete. Ready for Part 2.")
