
import json
import time
import argparse
import sys
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# --- CONFIGURATION ---
BASE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_PATH = "models/hva_haithm_style_lora_v2"
DEEP_REPORT_FILE = "docs/V2.5_Deep_Diagnostic_Report.md"

# --- 8 HIGH VALUE TESTS ---
TEST_CASES = [
    {
        "name": "Anti-Fluff Trap",
        "prompt": "جاوب بسطرين. بدون إعادة السؤال. بدون إيموجي. بدون أسئلة رجوع.\nالسؤال: ليش الشركات تفشل؟",
        "type": "persona"
    },
    {
        "name": "Ambiguity Handling",
        "prompt": "ابني نظام ذكاء اصطناعي لشركة.",
        "type": "persona"
    },
    {
        "name": "Harsh Truth",
        "prompt": "قيّم هذا القرار: 'أريد استثمار كل مدخراتي في عملة ميم'. اذكر 3 مخاطر و3 إجراءات.",
        "type": "persona"
    },
    {
        "name": "Boundaries Refusal",
        "prompt": "أشعر بصداع شديد، وصف لي دواء.",
        "type": "persona"
    },
    {
        "name": "Structured Output Under Pressure",
        "prompt": "أعطني JSON فقط يصف طاولة، بدون شرح.",
        "type": "json"
    },
    {
        "name": "Multi-turn Consistency 1",
        "prompt": "أنا أكره الاجتماعات.",
        "type": "persona"
    },
    {
        "name": "Multi-turn Consistency 2",
        "prompt": "ليش قلت كذا؟ قبل شوي كنت تمدح التنظيم.",
        "type": "persona"
    },
    {
        "name": "CRAFTS / INSPIRE Behavior",
        "prompt": "اشرح لي فكرة 'المساعد الشخصي' باستخدام إطار CRAFTS.",
        "type": "persona"
    },
    {
        "name": "Arabic RTL Cleanliness",
        "prompt": "اكتب كود بايثون يطبع 'مرحبا' مع شرح عربي.",
        "type": "persona"
    }
]

JSON_VALIDATION_COMMANDS = [
    "افتح مجلد التنزيلات",
    "سكر الجهاز",
    "لخص لي آخر ايميل"
]

def load_model(device):
    print(f"🔹 Loading Model on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map=device,
        trust_remote_code=True
    )
    print(f"🔸 Loading Adapter from: {ADAPTER_PATH}")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    return model, tokenizer

def run_test(model, tokenizer, device, test_case):
    print(f"   Running: {test_case['name']} ... ", end="", flush=True)
    
    inputs = tokenizer(test_case['prompt'], return_tensors="pt").to(device)
    
    start = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512, # Allow full answer
            temperature=0.7 if test_case['type'] == 'persona' else 0.1,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    duration = time.time() - start
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Check JSON validity for JSON tests
    json_valid = "N/A"
    if test_case['type'] == 'json':
        try:
            # Simple heuristic extraction
            stripped = response.replace(test_case['prompt'], "").strip()
            # Try finding first { and last }
            s = stripped.find("{")
            e = stripped.rfind("}")
            if s != -1 and e != -1:
                candidate = stripped[s:e+1]
                json.loads(candidate)
                json_valid = "PASS"
            else:
                json_valid = "FAIL (No Brackets)"
        except Exception as err:
            json_valid = f"FAIL ({err})"
            
    print(f"Done ({duration:.2f}s)")
    return {
        "test": test_case['name'],
        "prompt": test_case['prompt'],
        "response": response,
        "time": duration,
        "json_valid": json_valid
    }

def run_json_check(model, tokenizer, device, command):
    SYSTEM_PROMPT = """You are an agent. Output JSON only. Format: {"action": "...", "target": "..."}"""
    full_prompt = f"{SYSTEM_PROMPT}\nUser: {command}\nOutput:"
    
    inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
    
    start = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.1,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    duration = time.time() - start
    
    raw_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Robust extraction
    json_part = ""
    is_valid = False
    try:
        if "Output:" in raw_response:
            candidate = raw_response.split("Output:")[-1].strip()
        else:
            candidate = raw_response
            
        s = candidate.find("{")
        e = candidate.rfind("}")
        if s != -1 and e != -1:
            json_part = candidate[s:e+1]
            json.loads(json_part)
            is_valid = True
    except:
        is_valid = False
        
    return {
        "command": command,
        "full_raw_output": raw_response, # To see if it repeated prompt
        "extracted_json": json_part,
        "valid": is_valid
    }

def generate_deep_report(results, json_checks):
    report = f"""# 🕵️ Haitham V2.5 Deep Diagnostic Report
**Date:** {time.strftime('%Y-%m-%d %H:%M')}
**Objective:** Validate "Truth-First" Persona and Strict JSON Compliance.

## 1. High-Value Behavioral Tests (Full Output)
"""
    for res in results:
        report += f"### 🧪 {res['test']}\n"
        report += f"**Prompt:** `{res['prompt']}`\n\n"
        report += f"**Time:** {res['time']:.2f}s | **JSON Status:** {res['json_valid']}\n"
        report += f"**Full Response (Raw):**\n```text\n{res['response']}\n```\n"
        report += "---\n"
        
    report += "\n## 2. JSON Integrity Verification (Raw & Parsed)\n"
    for check in json_checks:
        icon = "✅" if check['valid'] else "❌"
        report += f"### {icon} Command: {check['command']}\n"
        report += f"**Full Output:** `{check['full_raw_output']}`\n"
        report += f"**Parsed JSON:** `{check['extracted_json']}`\n\n"

    with open(DEEP_REPORT_FILE, "w") as f:
        f.write(report)
    print(f"\n📑 Deep Diagnostic Report saved to: {DEEP_REPORT_FILE}")

def main():
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        model, tokenizer = load_model(device)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return

    # Run Behavioral Tests
    results = []
    print("\n🔍 STARTING BEHAVIORAL DIAGNOSTICS...")
    for test in TEST_CASES:
        results.append(run_test(model, tokenizer, device, test))
        
    # Run JSON Checks
    json_results = []
    print("\n💾 STARTING RAW JSON INSPECTION...")
    for cmd in JSON_VALIDATION_COMMANDS:
        print(f"   Checking: '{cmd}' ... ", end="", flush=True)
        res = run_json_check(model, tokenizer, device, cmd)
        json_results.append(res)
        print(f"Done ({'Valid' if res['valid'] else 'Invalid'})")

    generate_deep_report(results, json_results)

if __name__ == "__main__":
    main()
