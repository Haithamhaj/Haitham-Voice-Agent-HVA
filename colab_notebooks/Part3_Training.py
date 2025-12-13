# Part 3: Training (Dynamic/Bulletproof)
# ======================================
import os
import inspect
from transformers import TrainingArguments
from trl import SFTTrainer

# NOTE: This part assumes Part 2 has been run and 'model'/'train_dataset' variables exist.

OUTPUT_DIR = "hva_haithm_style_lora_v2"
MAX_SEQ_LENGTH = 1024

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
    if "processing_class" in accepted_params:
        trainer_kwargs["processing_class"] = tokenizer
        print("✅ Mapped tokenizer -> processing_class")
    elif "tokenizer" in accepted_params:
        trainer_kwargs["tokenizer"] = tokenizer
        print("✅ Mapped tokenizer -> tokenizer")

    if "max_seq_length" in accepted_params:
        trainer_kwargs["max_seq_length"] = MAX_SEQ_LENGTH
        print("✅ Enabled max_seq_length")

    if "dataset_text_field" in accepted_params:
        trainer_kwargs["dataset_text_field"] = "text"
        print("✅ Enabled dataset_text_field")

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
else:
    print("❌ Model or Dataset not loaded. Please run Part 2 first.")
