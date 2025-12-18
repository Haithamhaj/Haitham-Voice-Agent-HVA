
import json
import time
import torch
import os
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel 

# --- CONFIGURATION ---
BASE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
ADAPTER_PATH = "models/hva_haithm_style_lora_v2"
REPORT_FILE = "docs/V3_Heavy_Duty_Report.md"

# --- DATASETS ---

# 1. Identity & Persona (Trap Questions)
# Testing for: Repetition, "As an AI", "ChatGPT", Formal MSA vs Dialect
PERSONA_TESTS = [
    {"q": "مين أنت؟", "type": "Identity"},
    {"q": "أنت من شركة OpenAI؟", "type": "Company_Trap"},
    {"q": "كيف حالك اليوم يا وحش؟", "type": "Dialect_Chat"},
    {"q": "اكتب لي قصيدة عن الصبر.", "type": "Refusal_Check (Should happen or be brief)"},
    {"q": "ليش صوتك متغير؟", "type": "Context_Awareness"},
    {"q": "مين معلمك؟", "type": "Creator_Credit"},
    {"q": "وش رأيك في اللي يصير بالعالم؟", "type": "Opinion_Trap"},
    {"q": "عرف نفسك بلهجة سعودية قحة.", "type": "Dialect_Force"},
]

# 2. Complex JSON (Param Extraction & Edge Cases)
JSON_TESTS = [
    # Basic
    {"cmd": "افتح التيرمينال", "expect": "open_app"},
    {"cmd": "طفي النور", "expect": "smart_home"},
    
    # Complex / Nested
    {"cmd": "ابحث عن كل ملفات الـ PDF في المجلد 'مشاريع' اللي عدلتها امس", "expect": "search_files", "complexity": "High"},
    {"cmd": "ارسل ايميل لأحمد قله الاجتماع تأجل", "expect": "send_email", "complexity": "High"},
    {"cmd": "ذكرني بعد ٥ دقايق اطفي الفرن", "expect": "set_reminder", "complexity": "High"},
    
    # Dialect/Ambiguity Traps
    {"cmd": "سكر الجهاز", "expect": "system_control", "note": "sugar vs close"},
    {"cmd": "سكر الموضوع", "expect": "ignore/cancel", "note": "metaphorical close"},
    {"cmd": "شوف لي حل في النت", "expect": "web_search", "note": "vague intent"},
    
    # Negative / Impossible
    {"cmd": "سوي لي كبسة", "expect": "unknown/refusal", "note": "physical action"},
    {"cmd": "احك لي نكتة", "expect": "chat_mode", "note": "not a command"}
]

SYSTEM_PROMPT_JSON = """System: You are 'Haitham Agent'. 
Input: User voice command.
Output: VALID JSON ONLY. No markdown, no explanations.
Schema: {"tool": "tool_name", "params": {"key": "value"}}"""

def load_model(device):
    print(f"🔹 Loading Base Model: {BASE_MODEL_NAME} on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map=device,
        trust_remote_code=True
    )
    print(f"🔸 Loading Adapter: {ADAPTER_PATH}")
    model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    return model, tokenizer

def check_repetition(prompt, response):
    # Check if a significant part of the prompt is repeated at the start of response
    # Normalize: remove punctuation, lowercase
    p_norm = re.sub(r'[^\w\s]', '', prompt).strip()
    r_norm = re.sub(r'[^\w\s]', '', response).strip()
    
    # If the first 50% of prompt chars appear in first 50% of response
    if p_norm in r_norm[:len(p_norm)+20]:
        return True
    return False

def run_persona_test(model, tokenizer, device):
    print("\n🧠 RUNNING HEAVY DUTY PERSONA CHECK...")
    results = []
    
    for item in PERSONA_TESTS:
        q = item['q']
        print(f"   [Type: {item['type']}] Asking: '{q}' ... ", end="", flush=True)
        
        inputs = tokenizer(q, return_tensors="pt").to(device)
        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        duration = time.time() - start
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # ANALYSIS
        repetition = check_repetition(q, response)
        chatgpt_mention = "chatgpt" in response.lower() or "openai" in response.lower()
        assistant_mention = "مساعد" in response or "assistant" in response.lower()
        
        status = "✅ PASS"
        issues = []
        if repetition: 
            status = "⚠️ REPEAT"
            issues.append("Repetition")
        if chatgpt_mention:
            status = "❌ FAIL"
            issues.append("Identity_Hallucination")
        if assistant_mention:
            status = "⚠️ WEAK"
            issues.append("Generic_Persona")
            
        results.append({
            "q": q,
            "response": response,
            "status": status,
            "issues": issues,
            "time": duration
        })
        print(f"{status} ({duration:.2f}s)")
        
    return results

def run_json_test(model, tokenizer, device):
    print("\n⚡ RUNNING HEAVY DUTY JSON CHECK...")
    results = []
    
    for item in JSON_TESTS:
        cmd = item['cmd']
        print(f"   Cmd: '{cmd}' ... ", end="", flush=True)
        
        # Strict Prompting
        full_prompt = f"{SYSTEM_PROMPT_JSON}\nUser: {cmd}\nOutput:"
        inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
        
        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=0.1,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        duration = time.time() - start
        raw = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON
        json_str = ""
        if "Output:" in raw:
            json_str = raw.split("Output:")[-1].strip()
        else:
            # Fallback extraction
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                json_str = raw.strip()

        # Validation
        valid_json = False
        parsed = {}
        try:
            parsed = json.loads(json_str)
            valid_json = True
            # Check structure roughly
            if "tool" in parsed or "action" in parsed:
                pass # Good
        except:
            valid_json = False
            
        status = "✅ VALID" if valid_json else "❌ INVALID"
        
        # Check logic (did it get the right tool?)
        logic_check = "❓"
        if valid_json:
            val_str = str(parsed).lower()
            expected = item.get("expect", "").lower()
            if expected in val_str:
                logic_check = "✅ LOGIC OK"
            else:
                logic_check = f"⚠️ LOGIC DIFF ({expected})"
                
        results.append({
            "cmd": cmd,
            "raw": json_str,
            "valid": valid_json,
            "logic": logic_check,
            "time": duration
        })
        print(f"{status} | {logic_check}")
        
    return results

def generate_full_report(p_res, j_res):
    # Stats
    p_fail = len([r for r in p_res if "FAIL" in r['status']])
    p_warn = len([r for r in p_res if "WARN" in r['status'] or "REPEAT" in r['status']])
    j_valid = len([r for r in j_res if r['valid']])
    j_total = len(j_res)
    
    report = f"""# 🛡️ V3 Heavy Duty Evaluation Report
**Model:** Qwen 2.5 3B + Adapter V2
**Date:** {time.strftime('%Y-%m-%d %H:%M')}

## 1. Executive Summary
- **JSON Reliability:** {j_valid}/{j_total} ({(j_valid/j_total)*100:.1f}%)
- **Persona Integrity:** {len(p_res) - p_fail - p_warn}/{len(p_res)} Clean Responses
- **Critical Failures:** {p_fail} (Identity Hallucinations)

## 2. Persona Deep Dive
| Question | Status | Issues | Response Preview |
|----------|--------|--------|------------------|
"""
    for r in p_res:
        preview = r['response'].replace("\n", " ")[:100]
        report += f"| {r['q']} | {r['status']} | {', '.join(r['issues'])} | {preview} |\n"
        
    report += """
## 3. JSON Stress Test
| Command | Valid? | Logic Check | Output |
|---------|--------|-------------|--------|
"""
    for r in j_res:
        valid_mark = "✅" if r['valid'] else "❌"
        out_prev = r['raw'].replace("\n", "")[:50]
        report += f"| {r['cmd']} | {valid_mark} | {r['logic']} | `{out_prev}` |\n"
        
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"\n📄 Full Report: {REPORT_FILE}")

def main():
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    try:
        model, tokenizer = load_model(device)
        p_res = run_persona_test(model, tokenizer, device)
        j_res = run_json_test(model, tokenizer, device)
        generate_full_report(p_res, j_res)
    except Exception as e:
        print(f"FATAL ERROR: {e}")

if __name__ == "__main__":
    main()
