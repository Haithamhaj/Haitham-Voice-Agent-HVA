import os
import json
import hashlib
import pandas as pd
from collections import Counter
import re
from datetime import datetime

OUTPUT_DIR = "Data training V4.2_patch_datadesigner/release_chat_patch"
FILE_NAME = "v4_2_patch.jsonl"
MANIFEST_NAME = "manifest_patch.json"
REPORT_NAME = "report_patch.md"

TARGETS = {
    "ambiguity_handling": 180,
    "error_correction_dialogues": 140,
    "numeric_discipline": 140,
    "refuse_to_guess_source_needed": 70,
    "grounded_summaries": 70
}
ALLOWED_BUCKETS = set(TARGETS.keys())

# Augmented Leakage List (Strict)
LEAKAGE = [
    r"GPT-4o returned", 
    r"DALL[·-]E", 
    r"turn\d+file", 
    r"file_search", 
    r"web\.run", 
    r"\[STATE:", 
    "As an AI", 
    "OpenAI", 
    "Mixed/English",
    r":contentReference\[oaicite:\d+\]\{index=\d+\}" # Catches :contentReference[oaicite:2]{index=2}
]

def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def check_leakage(text):
    found = []
    for pat in LEAKAGE:
        if re.search(pat, text, re.IGNORECASE):
            found.append(pat)
    return found

def main():
    filepath = os.path.join(OUTPUT_DIR, FILE_NAME)
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    print(f"Processing {filepath}...")
    
    records = []
    leakage_count = 0
    buckets = []
    
    # Read and Validate
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
                records.append(rec)
                buckets.append(rec.get("bucket", "unknown"))
                
                # Leakage check
                msgs = rec.get("messages", [])
                full_text = " ".join([m.get("content", "") for m in msgs])
                leaks = check_leakage(full_text)
                if leaks:
                    print(f"LEAKAGE FOUND in bucket {rec.get('bucket')}: {leaks}")
                    leakage_count += 1
            except:
                pass
                
    total_count = len(records)
    print(f"Total Records: {total_count}")
    
    # Histogram
    hist = Counter(buckets)
    print("Bucket Histogram:", dict(hist))
    
    # Manifest
    file_hash = calculate_sha256(filepath)
    manifest = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_records": total_count,
        "files": [
            {
                "path": FILE_NAME,
                "sha256": file_hash,
                "count": total_count
            }
        ]
    }
    
    with open(os.path.join(OUTPUT_DIR, MANIFEST_NAME), 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Manifest saved to {MANIFEST_NAME}")
    
    # Report
    match_targets = all(hist.get(k, 0) >= v for k, v in TARGETS.items())
    
    report_md = f"""# V4.2 Patch Generation Report

**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
**Status:** {'✅ COMPLETE' if match_targets and total_count >= 600 else '⚠️ IN PROGRESS / PARTIAL'}

## Statistics
- **Total Records:** {total_count}
- **Target:** 600
- **Leakage Found:** {leakage_count} (Must be 0)

## Bucket Distribution
| Bucket | Count | Target | Status |
|---|---|---|---|
"""
    for k, v in TARGETS.items():
        c = hist.get(k, 0)
        status = "✅" if c >= v else "⏳"
        report_md += f"| `{k}` | {c} | {v} | {status} |\n"
        
    other_count = sum(c for k, c in hist.items() if k not in TARGETS)
    if other_count > 0:
        report_md += f"| `other` | {other_count} | 0 | ❓ |\n"
        
    with open(os.path.join(OUTPUT_DIR, REPORT_NAME), 'w', encoding='utf-8') as f:
        f.write(report_md)
        
    print(f"Report saved to {REPORT_NAME}")
    
    # Final Proof Output
    if leakage_count == 0 and total_count >= 600 and match_targets:
        print("SUCCESS: All criteria met.")
    else:
        print("WARNING: Criteria not strictly met.")
        if leakage_count > 0: print(f"Leakage Count: {leakage_count}")
        if total_count < 600: print(f"Total Count {total_count} < 600")

if __name__ == "__main__":
    main()
