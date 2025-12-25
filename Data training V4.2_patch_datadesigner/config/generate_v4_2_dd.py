import os
import sys
import json
import logging
import pandas as pd
import numpy as np
import random
from typing import List, Literal, Optional, Dict, Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import re
import math
import traceback

# Official Imports
from data_designer.essentials import (
    DataDesigner, 
    DataDesignerConfigBuilder,
    SeedDatasetColumnConfig,
    SamplerColumnConfig,
    SamplerType,
    UniformDistributionParams,
    CategorySamplerParams,
    LLMStructuredColumnConfig,
    LLMTextColumnConfig,
    ValidationColumnConfig,
    ModelConfig,
    ChatCompletionInferenceParams
)

load_dotenv()

# --- CONFIG ---
OUTPUT_DIR = "Data training V4.2_patch_datadesigner/release_chat_patch"
QUARANTINE_DIR = "Data training V4.2_patch_datadesigner/quarantine"
CONFIG_DIR = "Data training V4.2_patch_datadesigner/config"
LOGS_DIR = "logs"
PROGRESS_LOG = os.path.join(LOGS_DIR, "progress_v14.log")

TARGETS = {
    "ambiguity_handling": 180,
    "error_correction_dialogues": 140,
    "numeric_discipline": 140,
    "refuse_to_guess_source_needed": 70,
    "grounded_summaries": 70
}

SYSTEM_PROMPT = """أنت هيثم Mini-Me. الحقيقة أولاً. بدون حشو ولا مجاملة. إذا غير متأكد قل غير مؤكد مع نسبة ثقة وسبب مختصر. اشتغل بمنطق: مدخلات→خيارات/Levers→مخرجات→مخاطر→خطوة تالية. العربية افتراضيًا. استخدم الإنجليزية فقط للمصطلحات التقنية بين قوسين."""

# --- SCHEMA (Reference only, used for manual validation) ---
class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
class ChatRecord(BaseModel):
    messages: List[Message]

# --- VALIDATOR (Manual) ---
def strict_validator_manual(row_data, rec_dict=None) -> bool:
    """Manual validation function called on dict/Series"""
    try:
        if not rec_dict:
             return False
        
        record = rec_dict
        bucket = row_data.get("bucket")
        
        # Helper to get py value
        def get_val(key, default=None):
            v = row_data.get(key, default)
            if hasattr(v, "item"): v = v.item()
            return v

        if not isinstance(record, dict) or "messages" not in record:
             return False
        
        msgs = record["messages"]
        
        # Handle Numpy Array if present
        if hasattr(msgs, "tolist"):
            msgs = msgs.tolist()
        if hasattr(msgs, "__array__"):
             msgs = np.array(msgs).tolist()
             
        full_text = ""
        assist_text = ""
        user_text = ""
        
        try:
            full_text = " ".join([m.get("content","") for m in msgs])
            assist_text = " ".join([m.get("content","") for m in msgs if m.get("role") == "assistant"])
            user_text = " ".join([m.get("content","") for m in msgs if m.get("role") == "user"])
        except:
            # If msgs are strings (schema fail), this will crash. Catch it.
            return False
        
        # 1. Leakage
        LEAKAGE = [r"GPT-4o returned", r"DALL[·-]E", r"turn\d+file", r"file_search", 
                   r"web\.run", r"\[STATE:", "As an AI", "OpenAI", "Mixed/English"]
        for pat in LEAKAGE:
            if re.search(pat, full_text, re.IGNORECASE):
                return False
        
        # 2. Refusal check
        if "Can you tell me" in full_text and "I can't" in assist_text:
            if not re.search(r"[\u0600-\u06FF]", assist_text):
                 return False

        # 3. Bucket Specifics
        if bucket == "ambiguity_handling":
            q_count = assist_text.count("?") + assist_text.count("؟")
            options_count = len(re.findall(r"[-*] ", assist_text))
            if q_count == 0 and options_count < 2:
                return False
                
        elif bucket == "error_correction_dialogues":
            if len(msgs) < 5: return False
            last_msg = msgs[-1].get("content", "")
            ack_keys = ["أعتذر", "آسف", "صحيح", "شكراً", "تصحيح", "عفواً"]
            if not any(x in last_msg for x in ack_keys):
                return False

        elif bucket == "numeric_discipline":
            # STRICT check: Recompute + "الثقة: 100%"
            if "الثقة: 100%" not in assist_text:
                return False
            
            try:
                # A and B are pure Python STRINGS (from Seed loop)
                A_str = str(get_val("A", "0"))
                B_str = str(get_val("B", "0"))
                op = str(get_val("op", "+"))
                
                A = float(A_str)
                B = float(B_str)
                
                res = None
                if op == "+": res = A + B
                elif op == "-": res = A - B
                elif op == "*": res = A * B
                elif op == "/": res = A / B if B!=0 else 0
                
                if res is not None:
                    # Check exact string match for int or float format
                    res_int_s = str(int(res))
                    res_float_s = f"{res:.2f}".rstrip("0").rstrip(".")
                    
                    found = False
                    if res_int_s in assist_text: found = True
                    if res_float_s in assist_text: found = True
                    
                    if not found: return False
            except:
                pass

        elif bucket == "refuse_to_guess_source_needed":
            keywords = ["مصدر", "سياق", "متوفر", "لا يمكنني", "زودني"]
            if not any(k in assist_text for k in keywords):
                return False

        elif bucket == "grounded_summaries":
            if "النص:" not in user_text: return False
            input_text_len = len(user_text.replace("النص:", ""))
            summary_len = len(assist_text)
            if summary_len > input_text_len * 1.2:
                return False

        return True
    except Exception:
        return False

def generate_dd_patch():
    # Setup
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Precompute string values for Samplers to avoid numpy int
    str_values_1_100 = [str(i) for i in range(1, 101)]
    
    MAX_TOTAL_ATTEMPTS = 5000
    total_attempts_counter = 0
    loop_cnt = 0
    
    while True:
        loop_cnt += 1
        
        # FRESH DATA DESIGNER INSTANCE PER LOOP
        dd = DataDesigner()
        
        # 1. Check Needs
        current_counts = {k: 0 for k in TARGETS}
        patch_path = os.path.join(OUTPUT_DIR, "v4_2_patch.jsonl")
        if os.path.exists(patch_path):
            with open(patch_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        b = json.loads(line).get("bucket")
                        if b in current_counts: current_counts[b] += 1
                    except: pass
        
        # Log Progress
        needs_work = False
        rows = []
        
        print(f"--- Loop {loop_cnt} ---")
        print(f"Counts: {current_counts}")
        
        # Build Rows
        for bucket, target in TARGETS.items():
            needed = target - current_counts[bucket]
            if needed > 0:
                needs_work = True
                # LARGER BATCHES FOR SPEED
                count = min(10, needed + 2)
                for _ in range(count):
                    # PURE PYTHON RANDOM GENERATION - NO SAMPLER COLUMN NEEDED
                    rA = str(random.randint(1, 100))
                    rB = str(random.randint(1, 100))
                    rOp = random.choice(["+", "-", "*", "/"])
                    rows.append({"bucket": bucket, "A": rA, "B": rB, "op": rOp})
                    total_attempts_counter += 1
        
        # Exit conditions
        if not needs_work:
            print("DONE: All targets met.")
            break
            
        if total_attempts_counter >= MAX_TOTAL_ATTEMPTS:
            print("MAX TOTAL ATTEMPTS REACHED. Stopping.")
            break
            
        if len(rows) > 10: rows = rows[:10] # Limit batch size total to 10
        
        print(f"Generating {len(rows)} items...")

        # 2. Config
        df_seed = pd.DataFrame(rows)
        # Ensure pure string types (should be already, but explicit casting avoids numpy inference)
        df_seed["A"] = df_seed["A"].astype(str)
        df_seed["B"] = df_seed["B"].astype(str)
        df_seed["op"] = df_seed["op"].astype(str)
        
        seed_path = os.path.join(CONFIG_DIR, f"seed_cache_{loop_cnt}.parquet")
        seed_ref = dd.make_seed_reference_from_dataframe(df_seed, seed_path)
        
        builder = DataDesignerConfigBuilder()
        builder.with_seed_dataset(seed_ref)
        
        builder.add_model_config(ModelConfig(
            alias="gpt-4o",
            model="gpt-4o",
            provider="openai",
            inference_parameters=ChatCompletionInferenceParams(max_parallel_requests=10, timeout=120)
        ))
        
        # COLUMNS FROM SEED DATASET (A, B, op, bucket)
        builder.add_column(SeedDatasetColumnConfig(name="bucket"))
        builder.add_column(SeedDatasetColumnConfig(name="A"))
        builder.add_column(SeedDatasetColumnConfig(name="B"))
        builder.add_column(SeedDatasetColumnConfig(name="op"))
        
        # LLM - raw text result with explicit schema prompt
        prompt_text = """
        User: Execute the following task based on the 'Mini-Me' persona.
        Bucket: {{ bucket }}
        
        {% if bucket == 'numeric_discipline' %}
        Task: Create a user query asking to calculate {{ A }} {{ op }} {{ B }}? (in Arabic).
        Assistant: Must provide the result with a numeric score context 'الثقة: 100%'.
        {% elif bucket == 'ambiguity_handling' %}
        Task: User asks a vague question. Assistant asks 1-2 clarifying questions OR offers options.
        {% elif bucket == 'error_correction_dialogues' %}
        Task: Create a multi-turn dialogue (>=5 turns) where user corrects the assistant.
        {% elif bucket == 'refuse_to_guess_source_needed' %}
        Task: User asks for speculation. Assistant refuses politely in Arabic citing need for source.
        {% elif bucket == 'grounded_summaries' %}
        Task: User text starts with 'النص:'. Assistant summarizes it using ONLY that text.
        {% endif %}
        
        Output format: Valid JSON string with 'messages' list. 
        EACH Message object must look like: {"role": "user/assistant/system", "content": "..."}.
        DO NOT WRAP IN MARKDOWN CODE BLOCKS.
        Language: Arabic dominant (No English unless technical).
        """
        
        # Use LLMTextColumnConfig for raw string output
        builder.add_column(LLMTextColumnConfig(
            name="chat_record",
            prompt=prompt_text,
            system_prompt=SYSTEM_PROMPT,
            model_alias="gpt-4o"
        ))
        
        # MANUAL VALIDATION - NO ValidationColumnConfig
        
        # 3. Create
        try:
            res = dd.create(config_builder=builder, num_records=len(df_seed))
            df_out = res.load_dataset()
            
            # Process & Save
            valid_rows_batch = []
            rejected_rows_batch = []
            
            for idx, row in df_out.iterrows():
                
                bucket = row.get("bucket")
                rec_raw = row.get("chat_record") # Raw string
                
                # CLEANUP RAW 
                rec_dict = None
                if isinstance(rec_raw, dict):
                    rec_dict = rec_raw
                elif isinstance(rec_raw, str):
                    # Remove markdown blocks if present
                    rec_cleaned = rec_raw.replace("```json", "").replace("```", "").strip()
                    try:
                        rec_dict = json.loads(rec_cleaned)
                    except:
                        rec_dict = None

                # MANUAL VALIDATION
                is_valid = False
                if rec_dict:
                    is_valid = strict_validator_manual(row, rec_dict)
                
                if is_valid and rec_dict:
                     # Convert numpy list to py list if needed for saving
                     msgs = rec_dict["messages"]
                     if hasattr(msgs, "tolist"): msgs = msgs.tolist()
                     
                     valid_rows_batch.append({"bucket": bucket, "messages": msgs})
                else:
                     rejected_rows_batch.append({"bucket": bucket, "record": str(rec_raw), "reason": "Manually Validated: Failed or Parse Error"})
                     
            # Flush to disk
            with open(patch_path, "a", encoding="utf-8") as f:
                for v in valid_rows_batch:
                    # Convert samplers to py int/float if needed (from string now)
                    A = row.get("A", "0")
                    B = row.get("B", "0")
                    op = row.get("op", "")
                    
                    out = {
                        "messages": v["messages"], 
                        "bucket": v["bucket"], 
                        "tags": ["v4.2", "dd_real"],
                        "meta": {"A": str(A), "B": str(B), "op": str(op)}
                    }
                    f.write(json.dumps(out, ensure_ascii=False) + "\n")
                    
            with open(os.path.join(QUARANTINE_DIR, "rejected.jsonl"), "a", encoding="utf-8") as f:
                 for r in rejected_rows_batch:
                     f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
            # Log Stat
            acc_rate = len(valid_rows_batch)/len(rows) if rows else 0
            msg = f"Loop {loop_cnt}: {len(valid_rows_batch)} Valid, {len(rejected_rows_batch)} Rejected, Rate: {acc_rate:.2f}"
            print(msg)
            with open(PROGRESS_LOG, "a") as f:
                f.write(f"{msg} | Counts: {current_counts}\n")
                
        except Exception as e:
            traceback.print_exc() # Print full stack to stdout
            err_msg = f"Loop {loop_cnt} Error: {e}"
            print(err_msg)
            with open(PROGRESS_LOG, "a") as f:
                f.write(f"{err_msg}\n")

if __name__ == "__main__":
    generate_dd_patch()
