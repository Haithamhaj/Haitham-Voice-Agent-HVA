import os
import json
import random
import time
import pandas as pd
from dotenv import load_dotenv
from typing import List, Literal, Optional, Dict
from pydantic import BaseModel, Field
import openai

# Imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from validators_strict import strict_validation

load_dotenv()

# Setup OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is missing!")

client = openai.OpenAI(api_key=api_key)

# --- SCHEMA ---
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatRecord(BaseModel):
    messages: List[Message]
    bucket: str

# --- CONFIG ---
OUTPUT_DIR = "Data training V4.2_patch_datadesigner/release_chat_patch"
QUARANTINE_DIR = "Data training V4.2_patch_datadesigner/quarantine"
TARGET_COUNT = 600
BATCH_SIZE = 5

BUCKETS = {
    "ambiguity_handling": 180,
    "error_correction_dialogues": 140,
    "numeric_discipline": 140,
    "refuse_to_guess_source_needed": 70,
    "grounded_summaries": 70
}

SYSTEM_PROMPT = """أنت هيثم Mini-Me. الحقيقة أولاً. بدون حشو ولا مجاملة. إذا غير متأكد قل غير مؤكد مع نسبة ثقة وسبب مختصر. اشتغل بمنطق: مدخلات→خيارات/Levers→مخرجات→مخاطر→خطوة تالية. العربية افتراضيًا."""

GENERATION_PROMPT = """
Context: You are helping build a dataset for 'Haitham Mini-Me'.
Use the following specifications:
- Bucket: {{ bucket }}
- Goal: Create a realistic conversation formatted as a list of messages.
- Requirements:
    - **LANGUAGE: Assistant output MUST be in ARABIC (use English only for technical terms).**
    - Must follow the System Prompt behavior provided in the schema (Direct, Truth-first, No Fluff).
    - If bucket='ambiguity_handling': User asks vague question, Assistant clarifies steps/risks.
    - If bucket='error_correction_dialogues': User corrects assistant or vice versa. Multi-turn.
    - If bucket='numeric_discipline': Assistant MUST give a score (X/10) or %.
    - If bucket='refuse_to_guess_source_needed': Assistant refuses to guess without source.
    - If bucket='grounded_summaries': User provides text, Assistant summarizes grounded in text only.
    
Output Format: structured JSON matching ChatRecord.
"""

def generate_batch():
    # 1. Determine Needs
    current_valid_count = 0
    if os.path.exists(os.path.join(OUTPUT_DIR, "v4_2_patch.jsonl")):
        with open(os.path.join(OUTPUT_DIR, "v4_2_patch.jsonl"), "r") as f:
            current_valid_count = sum(1 for _ in f)
            
    remaining = TARGET_COUNT - current_valid_count
    if remaining <= 0:
        print("Target reached.")
        return False # Add stop condition

    print(f"Goal: {TARGET_COUNT}. Current: {current_valid_count}. Generating batch of {BATCH_SIZE}...")
    
    # Select buckets for this batch
    batch_buckets = random.choices(list(BUCKETS.keys()), k=BATCH_SIZE)
    results = []
    
    for i, bucket in enumerate(batch_buckets):
        print(f"  [{i+1}/{BATCH_SIZE}] Generating {bucket}...")
        try:
            prompt = GENERATION_PROMPT.replace("{{ bucket }}", bucket)
            
            completion = client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a synthetic data generator."},
                    {"role": "user", "content": prompt}
                ],
                response_format=ChatRecord
            )
            
            record = completion.choices[0].message.parsed
            
            # Post-processing: Enforce System Prompt
            msgs = record.messages
            # Ensure index 0 is system prompt
            if not msgs or msgs[0].role != 'system' or msgs[0].content != SYSTEM_PROMPT:
                 # Insert or Replace
                 if msgs and msgs[0].role == 'system':
                     msgs[0].content = SYSTEM_PROMPT
                 else:
                     msgs.insert(0, Message(role="system", content=SYSTEM_PROMPT))
            
            results.append({"chat_record": record.model_dump(), "bucket": bucket})
            
        except Exception as e:
            print(f"Gen Error ({bucket}): {e}")
            
    # 2. Validation
    if results:
        df_results = pd.DataFrame(results)
        validated_df = strict_validation(df_results) # Uses validators_strict.py
        
        df_results["is_valid"] = validated_df["is_valid"]
        df_results["validation_reason"] = validated_df["validation_reason"]
        
        # 3. Save
        valid_rows = df_results[df_results["is_valid"] == True]
        rejected_rows = df_results[df_results["is_valid"] == False]
        
        with open(os.path.join(OUTPUT_DIR, "v4_2_patch.jsonl"), "a", encoding="utf-8") as f:
            for _, r in valid_rows.iterrows():
                rec = r["chat_record"]
                # Clean up for jsonl
                out = {"messages": rec["messages"], "bucket": r["bucket"], "tags": ["generated", "v4.2"]}
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
                
        with open(os.path.join(QUARANTINE_DIR, "rejected.jsonl"), "a", encoding="utf-8") as f:
            for _, r in rejected_rows.iterrows():
                 rec = r["chat_record"] if "chat_record" in r else {}
                 out = {"record": rec, "reason": r["validation_reason"]}
                 f.write(json.dumps(out, ensure_ascii=False) + "\n")
                 
        print(f"Batch Saved. Valid: {len(valid_rows)}, Rejected: {len(rejected_rows)}")
    
    return True

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    
    max_loops = 20 # Safety cap
    for i in range(max_loops):
        should_continue = generate_batch()
        if not should_continue: break
        time.sleep(1)
