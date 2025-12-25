import re
import pandas as pd

# Strict Regex Patterns (Leakage)
LEAKAGE_PATTERNS = [
    r"GPT-4o returned", 
    r"DALL[·-]E", 
    r"turn\d+file", 
    r"file_search", 
    r"web\.run", 
    r"python_user_visible", 
    r"image_gen", 
    r"\[STATE:", 
    r"As an AI", 
    r"I am an AI",
    r"OpenAI"
]

def strict_validation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates generated chat records.
    """
    results = []
    
    for idx, row in df.iterrows():
        is_valid = True
        reason = ""
        
        # Parse content
        # Assuming Data Designer outputs a structured object or we construct it
        # For this function, let's assume 'chat_record' column contains the JSON/Dict
        record = row.get("chat_record")
        
        if not record or not isinstance(record, dict):
             results.append({"is_valid": False, "validation_reason": "Invalid Format"})
             continue
             
        messages = record.get("messages", [])
        bucket = row.get("bucket", "unknown")
        
        full_text = ""
        assist_text = ""
        
        for m in messages:
            content = m.get("content", "")
            full_text += content + "\n"
            if m.get("role") == "assistant": assist_text += content
            
        # 1. Leakage
        for pat in LEAKAGE_PATTERNS:
            if re.search(pat, full_text, re.IGNORECASE):
                is_valid = False
                reason = f"Leakage: {pat}"
                break
        
        if not is_valid:
            results.append({"is_valid": False, "validation_reason": reason})
            continue
            
        # 2. Bucket Specifics
        if bucket == "numeric_discipline":
            if not (re.search(r"\d+/\d+", assist_text) or re.search(r"\d+%", assist_text)):
                is_valid = False
                reason = "Numeric Discipline: Missing score"
                
        elif bucket == "refuse_to_guess_source_needed":
             if not (re.search(r"لا (أستطيع|أملك|أعرف)", assist_text) or "غير متأكد" in assist_text):
                 is_valid = False
                 reason = "Refusal: Missing refusal cue"
                 
        elif bucket == "error_correction_dialogues":
            # Must have multiple turns (System, User, Assistant, User, Assistant) -> 5
            if len(messages) < 5:
                is_valid = False
                reason = "Error Correction: Too few turns"

        results.append({"is_valid": is_valid, "validation_reason": reason})

    return pd.DataFrame(results, index=df.index)
