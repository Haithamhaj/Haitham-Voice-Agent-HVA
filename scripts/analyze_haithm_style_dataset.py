#!/usr/bin/env python3
"""
Haithm Style Dataset Analyzer
=============================
analyzes the prepared JSONL datasets for style fine-tuning.
"""

import json
import statistics
import argparse
from pathlib import Path

def analyze_dataset(path):
    print(f"\nAnalyzing: {path}")
    path = Path(path)
    if not path.exists():
        print(f"  ❌ File not found: {path}")
        return

    records = []
    output_lens = []
    
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            try:
                rec = json.loads(line)
                records.append(rec)
                output = rec.get("output", "")
                if output:
                    output_lens.append(len(output))
            except json.JSONDecodeError:
                pass
    
    count = len(records)
    print(f"  ✅ Records: {count}")
    if count > 0:
        print(f"  Min Length: {min(output_lens)}")
        print(f"  Max Length: {max(output_lens)}")
        print(f"  Avg Length: {statistics.mean(output_lens):.2f}")
    else:
        print("  ⚠️ Dataset is empty.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--natural", default="data/dataset_haithm_style_natural.jsonl")
    parser.add_argument("--prompts", default="data/dataset_haithm_style_prompts.jsonl")
    args = parser.parse_args()
    
    analyze_dataset(args.natural)
    analyze_dataset(args.prompts)

if __name__ == "__main__":
    main()
