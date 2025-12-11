#!/usr/bin/env python3
"""
Haithm Style Dataset Builder
============================

Purpose:
    Parses the raw corpus (JSONL) and creates two filtered datasets for style fine-tuning:
    1. Natural Style: Haitham's conversational/analytical writing.
    2. Prompt Style: Haitham's prompt engineering/instruction writing.

Usage:
    python scripts/build_haithm_style_dataset.py [--force]
"""

import json
import argparse
import re
import collections
import statistics
from pathlib import Path

# --- Configuration & Heuristics ---
NATURAL_INSTRUCTION = "You are Haithm. Write in Haithm's natural style: concise, realistic, truth-first, no flattery, focus on practical value, mixing Arabic/English when natural."
PROMPT_INSTRUCTION = "You are Haithm writing system-level instructions and prompt-engineering guidelines. Use precise, strict rules, numbered lists, and clear constraints."

# Patterns that strongly suggest Prompt Engineering
PROMPT_PATTERNS = [
    r"(?i)^your task is",
    r"(?i)^you are (a|the|an)",
    r"(?i)^act as",
    r"(?i)^role:",
    r"(?i)^system:",
    r"(?i)^rules:",
    r"(?i)^instructions:",
    r"(?i)^context:",
    r"(?i)do not reveal",
    r"(?i)you must always"
]

# Patterns that suggest junk/trivial content
JUNK_PATTERNS = [
    r"(?i)^ok\.?$",
    r"(?i)^thanks\.?$",
    r"(?i)^hello\.?$",
    r"(?i)^hi\.?$",
    r"(?i)^yes\.?$",
    r"(?i)^no\.?$",
]

def classify_record(text, min_natural=200, max_natural=4000, min_prompt=150):
    """
    Classifies text into 'NATURAL', 'PROMPT', or 'SKIP'.
    """
    length = len(text)
    
    # 1. Skip trivial/short
    if length < 50: 
        return "SKIP"
        
    # 2. Check for Prompt Patterns
    is_prompt_style = False
    for pat in PROMPT_PATTERNS:
        if re.search(pat, text):
            is_prompt_style = True
            break
            
    # Heuristic: numbered lists near start (e.g. "1. ", "2. ") often imply instructions
    if re.search(r"(?m)^\s*\d+\.\s+", text[:500]): 
         # Only treat as prompt if it matches other strong signals or is very structured?
         # For now, let's say if we see explicit "1." "2." at start of lines early on, likely a prompt or list.
         pass # Actually, Haithm uses lists in natural analysis too. Let's rely on explicit prompt keywords more.

    if is_prompt_style and length >= min_prompt:
        return "PROMPT"
        
    # 3. Code/JSON Heavy Check (skip if > 40% symbols)
    # Count specific code symbols
    code_chars = sum(text.count(c) for c in "{}[]<>@#$%^&*()=+/\\|")
    if code_chars / length > 0.40:
        return "SKIP"

    # 4. Natural Check
    if min_natural <= length <= max_natural and not is_prompt_style:
        return "NATURAL"
        
    return "SKIP"

def build_datasets(input_path, natural_out, prompt_out, force,
                   min_nat, max_nat, min_prm):
    
    in_file = Path(input_path)
    nat_file = Path(natural_out)
    prm_file = Path(prompt_out)
    
    if not in_file.exists():
        print(f"Error: Input file not found: {in_file}")
        return

    if (nat_file.exists() or prm_file.exists()) and not force:
        print("Error: Output files exist. Use --force to overwrite.")
        return

    print(f"Reading from: {in_file}")
    
    stats = {
        "total_user": 0,
        "natural": 0,
        "prompt": 0,
        "skipped": 0,
        "nat_lens": [],
        "prm_lens": []
    }
    
    natural_records = []
    prompt_records = []
    
    with open(in_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                rec = json.loads(line)
                if rec.get('role') != 'user':
                    continue
                
                text = rec.get('text', "")
                label = classify_record(text, min_nat, max_nat, min_prm)
                
                stats["total_user"] += 1
                
                if label == "NATURAL":
                    stats["natural"] += 1
                    stats["nat_lens"].append(len(text))
                    natural_records.append({
                        "instruction": NATURAL_INSTRUCTION,
                        "input": "",
                        "output": text
                    })
                elif label == "PROMPT":
                    stats["prompt"] += 1
                    stats["prm_lens"].append(len(text))
                    prompt_records.append({
                        "instruction": PROMPT_INSTRUCTION,
                        "input": "",
                        "output": text
                    })
                else:
                    stats["skipped"] += 1
                    
            except json.JSONDecodeError:
                continue

    # Write Outputs
    nat_file.parent.mkdir(parents=True, exist_ok=True)
    prm_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(nat_file, 'w', encoding='utf-8') as f:
        for r in natural_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    with open(prm_file, 'w', encoding='utf-8') as f:
        for r in prompt_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    # Print Summary
    print("\n=== Dataset Build Complete ===")
    print(f"Input: {in_file}")
    print(f"Total User Records Processed: {stats['total_user']}")
    print("-" * 30)
    print(f"NATURAL Style:   {stats['natural']} records")
    if stats['nat_lens']:
        print(f"  Avg Length:    {statistics.mean(stats['nat_lens']):.2f} chars")
    print(f"  Output:        {nat_file}")
    print("-" * 30)
    print(f"PROMPT Style:    {stats['prompt']} records")
    if stats['prm_lens']:
        print(f"  Avg Length:    {statistics.mean(stats['prm_lens']):.2f} chars")
    print(f"  Output:        {prm_file}")
    print("-" * 30)
    print(f"SKIPPED:         {stats['skipped']} records")
    print("==============================\n")


def main():
    parser = argparse.ArgumentParser(description="Build Haithm Style Datasets")
    parser.add_argument("--input", default="data/haithm_corpus_raw_gpt_2025-12-11.jsonl")
    parser.add_argument("--natural-output", default="data/dataset_haithm_style_natural.jsonl")
    parser.add_argument("--prompts-output", default="data/dataset_haithm_style_prompts.jsonl")
    parser.add_argument("--min-chars-natural", type=int, default=200)
    parser.add_argument("--max-chars-natural", type=int, default=4000)
    parser.add_argument("--min-chars-prompts", type=int, default=150)
    parser.add_argument("--force", action="store_true")
    
    args = parser.parse_args()
    
    build_datasets(
        args.input,
        args.natural_output,
        args.prompts_output,
        args.force,
        args.min_chars_natural,
        args.max_chars_natural,
        args.min_chars_prompts
    )

if __name__ == "__main__":
    main()
