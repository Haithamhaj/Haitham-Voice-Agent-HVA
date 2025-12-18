
import json
import time
import argparse
import sys
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
# from peft import PeftModel # Not needed for base model

# --- CONFIGURATION ---
BASE_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
# ADAPTER_PATH = "models/hva_haithm_style_lora_v2" # DISABLED
REPORT_FILE = "docs/Qwen_Base_Evaluation_Report.md"

# --- TEST DATA ---
PERSONA_QUESTIONS = [
    "كيف تصف نفسك بكلمة واحدة؟",
    "ليش لازم أتعلم الذكاء الاصطناعي؟",
    "أعطني نصيحة لشخص ضايع في حياته المهنية.",
    "وش رأيك في الاجتماعات الطويلة؟",
    "اختصر لي مبدأ 'العمل بذكاء' بأسلوبك."
]

JSON_COMMANDS = [
    "افتح مجلد التنزيلات",
    "بحث عن ملف العقد",
    "نظم سطح المكتب",
    "شغل وضع التركيز",
    "اعرض حالة النظام",
    "تحقق من استهلاك الذاكرة",
    "ابحث عن صورة القطة",
    "افتح متصفح سفاري",
    "لخص لي آخر ايميل",
    "سكر الجهاز"
]

def load_model(device):
    print(f"🔹 Loading Base Model on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_NAME,
        torch_dtype=torch.float16 if device != "cpu" else torch.float32,
        device_map=device,
        trust_remote_code=True
    )
    # print(f"🔸 Loading Adapter from: {ADAPTER_PATH}")
    # model = PeftModel.from_pretrained(model, ADAPTER_PATH)
    return model, tokenizer

def evaluate_persona(model, tokenizer, device):
    results = []
    print("\n🧐 STARTING PERSONA TEST (Style & Character)...")
    
    total_time = 0
    for q in PERSONA_QUESTIONS:
        print(f"   Asking: '{q}' ... ", end="", flush=True)
        inputs = tokenizer(q, return_tensors="pt").to(device)
        
        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        duration = time.time() - start
        total_time += duration
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Clean prompt from response usually
        # For Qwen instruct it might just append.
        
        results.append({
            "question": q,
            "response": response,
            "time": duration
        })
        print(f"Done ({duration:.2f}s)")
        
    avg_speed = total_time / len(PERSONA_QUESTIONS)
    return results, avg_speed

def evaluate_json(model, tokenizer, device):
    results = []
    print("\n🤖 STARTING JSON STRESS TEST (Functionality)...")
    
    # We construct a system prompt that forces JSON output
    SYSTEM_PROMPT = """Sytem: You are an AI assistant orchestrator. 
User will give a command. You must output ONLY a valid JSON object describing the action.
Format: {"action": "action_name", "target": "target_name"}
Do not output any other text."""

    valid_count = 0
    total_time = 0
    
    for cmd in JSON_COMMANDS:
        print(f"   Command: '{cmd}' ... ", end="", flush=True)
        
        # Format as input with system instruction (Simulated)
        full_prompt = f"{SYSTEM_PROMPT}\nUser: {cmd}\nOutput:"
        
        inputs = tokenizer(full_prompt, return_tensors="pt").to(device)
        
        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.1, # Low temp for JSON stability
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id
            )
        duration = time.time() - start
        total_time += duration
        
        raw_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract the part after "Output:"
        if "Output:" in raw_output:
            json_part = raw_output.split("Output:")[-1].strip()
        else:
            json_part = raw_output # Fallback
            
        # Validate JSON
        is_valid = False
        try:
            # Try to find { ... }
            start_idx = json_part.find('{')
            end_idx = json_part.rfind('}')
            if start_idx != -1 and end_idx != -1:
                potential_json = json_part[start_idx : end_idx+1]
                json.loads(potential_json)
                is_valid = True
        except:
            is_valid = False
            
        if is_valid:
            valid_count += 1
            print("✅ Valid JSON")
        else:
            print("❌ Invalid JSON")
            
        results.append({
            "command": cmd,
            "raw_output": json_part,
            "valid": is_valid,
            "time": duration
        })
        
    success_rate = (valid_count / len(JSON_COMMANDS)) * 100
    avg_speed = total_time / len(JSON_COMMANDS)
    return results, success_rate, avg_speed

def generate_report(persona_results, json_results, persona_speed, json_speed, json_success):
    report = f"""# 📊 Qwen 2.5 (3B) Base Model - Evaluation Report
**Date:** {time.strftime('%Y-%m-%d %H:%M')}
**Model:** Qwen/Qwen2.5-3B-Instruct (Base)
**Status:** {'✅ PASSED' if json_success >= 80 else '⚠️ WARNING'}

## 1. Persona Evaluation (Style Check)
**Average Response Time:** {persona_speed:.2f}s

| Question | Response Preview | Time |
|----------|------------------|------|
"""
    for res in persona_results:
        preview = res['response'].replace("\n", " ")[:100] + "..."
        report += f"| {res['question']} | {preview} | {res['time']:.2f}s |\n"
        
    report += f"""
## 2. Technical Evaluation (JSON Stress Test)
**Success Rate:** {json_success:.1f}%
**Average Processing Time:** {json_speed:.2f}s

| Command | Output Consistency | Valid JSON |
|---------|-------------------|------------|
"""
    for res in json_results:
        mark = "✅" if res['valid'] else "❌"
        output_clean = res['raw_output'].replace("\n", "").replace("|", "-")[:50]
        report += f"| {res['command']} | `{output_clean}` | {mark} |\n"
        
    report += """
## 3. Final Conclusion
- **Style Alignment:** Assessed on base model default persona.
- **Technical Capability:** Assessed on base model instruction following.
"""
    
    with open(REPORT_FILE, "w") as f:
        f.write(report)
    print(f"\n📄 Report saved to: {REPORT_FILE}")

def main():
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    
    try:
        model, tokenizer = load_model(device)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return

    # Run Tests
    p_results, p_speed = evaluate_persona(model, tokenizer, device)
    j_results, j_success, j_speed = evaluate_json(model, tokenizer, device)
    
    # Generate Report
    generate_report(p_results, j_results, p_speed, j_speed, j_success)

if __name__ == "__main__":
    main()
