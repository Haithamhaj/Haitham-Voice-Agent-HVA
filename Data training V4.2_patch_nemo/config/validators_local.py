import re
import pandas as pd
from typing import List, Dict

# Regex Patterns for Leakage (From V4.1 rules)
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

def validate_chat_records(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates a DataFrame of ChatRecords.
    Input df columns expected: ['messages', 'bucket', 'tags', 'expected_check']
    Output df columns: ['is_valid', 'validation_reason']
    """
    
    results = []
    
    for idx, row in df.iterrows():
        is_valid = True
        reason = ""
        
        messages = row.get("messages", [])
        if not messages:
            is_valid = False
            reason = "Empty messages"
            
        full_text = ""
        user_text = ""
        assist_text = ""
        
        for m in messages:
            content = m.get("content", "")
            full_text += content + "\n"
            if m.get("role") == "user": user_text += content + "\n"
            if m.get("role") == "assistant": assist_text += content + "\n"

        # 1. Leakage Check
        for pat in LEAKAGE_PATTERNS:
            if re.search(pat, full_text, re.IGNORECASE):
                is_valid = False
                reason = f"Leakage found: {pat}"
                break
        
        if not is_valid:
            results.append({"is_valid": False, "validation_reason": reason})
            continue

        # 2. Bucket Specific Checks
        bucket = row.get("bucket", "unknown")
        
        if bucket == "numeric_discipline":
            # Must contain X/10 or %
            if not (re.search(r"\d+/\d+", assist_text) or re.search(r"\d+%", assist_text)):
                is_valid = False
                reason = "Numeric Discipline: Missing score/percentage"
        
        elif bucket == "refuse_to_guess_source_needed":
            # Must contain refusal cues
            if not (re.search(r"لا (أستطيع|أملك|أعرف)", assist_text) or "غير متأكد" in assist_text or "لا يمكنني" in assist_text):
                 is_valid = False
                 reason = "Refuse to Guess: Missing refusal phrases"
                 
        results.append({"is_valid": is_valid, "validation_reason": reason})

    return pd.DataFrame(results, index=df.index)
