#!/usr/bin/env python3
"""
Haithm Style Dataset Builder
============================

Purpose:
    Parses the raw corpus (JSONL) and creates filtered datasets for style fine-tuning.
    
    Modes:
    1. V1 (Default): Builds legacy natural/prompt datasets.
    2. V2 (--v2): Builds refined Datasets:
       - Natural (GPT + WhatsApp + Stats)
       - Persona (from spec Q&A)
       - Cognitive (from spec Q&A)

Usage:
    python scripts/build_haithm_style_dataset.py [--force]
    python scripts/build_haithm_style_dataset.py --v2 --force
"""

import json
import argparse
import re
import collections
import statistics
import shutil
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

# --- Optional Integrations ---
INCLUDE_WHATSAPP = True
WHATSAPP_CORPUS_PATH = "data/haithm_corpus_whatsapp_haithm_only.jsonl"
GPT_CORPUS_PATH = "data/haithm_corpus_raw_gpt_2025-12-11.jsonl" # Default

# V2 Paths
V2_NATURAL_OUT = "data/dataset_haithm_style_natural_v2.jsonl"
V2_NATURAL_STATS = "data/dataset_haithm_style_natural_stats_v2.json"

V2_PERSONA_OUT = "data/dataset_haithm_style_persona_v2.jsonl"
V2_PERSONA_STATS = "data/dataset_haithm_style_persona_stats_v2.json"
# Source for Persona (generated from YAML spec)
PERSONA_SOURCE = "data/dataset_haithm_persona_qa.jsonl"

V2_COGNITIVE_OUT = "data/dataset_haithm_style_cognitive_v2.jsonl"
V2_COGNITIVE_STATS = "data/dataset_haithm_style_cognitive_stats_v2.json"
# Source for Cognitive (generated from YAML spec)
COGNITIVE_SOURCE = "data/dataset_haithm_cognitive_qa.jsonl"


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

def build_v1_datasets(input_path, natural_out, prompt_out, force,
                   min_nat, max_nat, min_prm):
    """Original logic for V1 datasets."""
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
    
    # Process GPT Data
    with open(in_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                rec = json.loads(line)
                if rec.get('role') != 'user': continue
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

    # Process WhatsApp (Optional for V1, but kept as per original edit)
    if INCLUDE_WHATSAPP:
        wa_path = Path(WHATSAPP_CORPUS_PATH)
        if wa_path.exists():
            print(f"Reading from WhatsApp Corpus: {wa_path}")
            wa_count = 0
            with open(wa_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        rec = json.loads(line)
                        text = rec.get('text', "")
                        label = classify_record(text, min_nat, max_nat, min_prm)
                        
                        if label == "NATURAL":
                            stats["natural"] += 1
                            stats["nat_lens"].append(len(text))
                            natural_records.append({
                                "instruction": NATURAL_INSTRUCTION,
                                "input": "",
                                "output": text
                            })
                            wa_count += 1
                        elif label == "PROMPT":
                             stats["prompt"] += 1
                             stats["prm_lens"].append(len(text))
                             prompt_records.append({
                                "instruction": PROMPT_INSTRUCTION,
                                "input": "",
                                "output": text
                            })
                             wa_count += 1
                    except json.JSONDecodeError:
                        continue
            print(f"  Added {wa_count} records from WhatsApp.")

    # Write Outputs
    nat_file.parent.mkdir(parents=True, exist_ok=True)
    with open(nat_file, 'w', encoding='utf-8') as f:
        for r in natural_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    with open(prm_file, 'w', encoding='utf-8') as f:
        for r in prompt_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"V1 Build Complete. Natural: {len(natural_records)}, Prompts: {len(prompt_records)}")

def build_v2_datasets(force, min_nat, max_nat, min_prm):
    """V2 Logic: Natural V2 (GPT+WA), Persona V2, Cognitive V2."""
    
    print("\n=== Building V2 Datasets ===")
    
    # 1. Natural V2
    # ----------------
    nat_v2_file = Path(V2_NATURAL_OUT)
    if nat_v2_file.exists() and not force:
        print(f"Skipping Natural V2: {nat_v2_file} exists (use --force)")
    else:
        print(f"Building Natural V2 -> {nat_v2_file}")
        
        sources = [
            ("gpt", Path(GPT_CORPUS_PATH)),
            ("whatsapp", Path(WHATSAPP_CORPUS_PATH))
        ]
        
        nat_stats = {
            "total_records": 0,
            "by_source": collections.defaultdict(int),
            "skipped_by_source": collections.defaultdict(int),
            "total_chars_by_source": collections.defaultdict(int),
        }
        
        nat_records = []
        
        for source_name, source_path in sources:
            if not source_path.exists():
                print(f"Warning: Source {source_name} not found at {source_path}")
                continue
                
            print(f"  Processing {source_name}...")
            with open(source_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        rec = json.loads(line)
                        
                        # Handle different source formats
                        # GPT has 'text'. WhatsApp has 'text'.
                        text = rec.get('text', "")
                        
                        # Apply V1 filters
                        label = classify_record(text, min_nat, max_nat, min_prm)
                        
                        if label == "NATURAL":
                            # V2 Format: Alpaca + Source metadata
                            new_rec = {
                                "instruction": NATURAL_INSTRUCTION,
                                "input": "",
                                "output": text,
                                "source_type": source_name
                            }
                            nat_records.append(new_rec)
                            
                            nat_stats["total_records"] += 1
                            nat_stats["by_source"][source_name] += 1
                            nat_stats["total_chars_by_source"][source_name] += len(text)
                        else:
                            nat_stats["skipped_by_source"][source_name] += 1
                            
                    except json.JSONDecodeError:
                        continue

        # Write Natural V2
        nat_v2_file.parent.mkdir(parents=True, exist_ok=True)
        with open(nat_v2_file, 'w', encoding='utf-8') as f:
            for r in nat_records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        
        # Write Stats
        with open(V2_NATURAL_STATS, 'w', encoding='utf-8') as f:
            json.dump(nat_stats, f, indent=2, ensure_ascii=False)
            
        print(f"  > Saved {len(nat_records)} records to Natural V2.")


    # 2. Persona V2
    # ----------------
    # Logic: Read from verified Q&A source, clean if needed, save as V2.
    process_aux_dataset("Persona", PERSONA_SOURCE, V2_PERSONA_OUT, V2_PERSONA_STATS, force)

    # 3. Cognitive V2
    # ----------------
    process_aux_dataset("Cognitive", COGNITIVE_SOURCE, V2_COGNITIVE_OUT, V2_COGNITIVE_STATS, force)

def process_aux_dataset(name, input_path, output_path, stats_path, force):
    p_in = Path(input_path)
    p_out = Path(output_path)
    
    if p_out.exists() and not force:
        print(f"Skipping {name} V2: {p_out} exists.")
        return

    if not p_in.exists():
        print(f"Warning: {name} source not found at {p_in}. Skipping.")
        return

    print(f"Building {name} V2 -> {p_out}")
    records = []
    unique_outputs = set()
    
    with open(p_in, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                rec = json.loads(line)
                # Ensure instruction/output format
                if "instruction" in rec and "output" in rec:
                    # Deduplication check
                    out_txt = rec["output"].strip()
                    if out_txt not in unique_outputs:
                        records.append(rec)
                        unique_outputs.add(out_txt)
            except json.JSONDecodeError:
                continue
    
    # Write Output
    p_out.parent.mkdir(parents=True, exist_ok=True)
    with open(p_out, 'w', encoding='utf-8') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    # Write Stats
    stats = {
        "total_records": len(records),
        "source_file": str(p_in)
    }
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
        
    print(f"  > Saved {len(records)} records to {name} V2.")


def main():
    parser = argparse.ArgumentParser(description="Build Haithm Style Datasets")
    parser.add_argument("--input", default="data/haithm_corpus_raw_gpt_2025-12-11.jsonl", help="Used for V1 only")
    parser.add_argument("--natural-output", default="data/dataset_haithm_style_natural.jsonl", help="Used for V1 only")
    parser.add_argument("--prompts-output", default="data/dataset_haithm_style_prompts.jsonl", help="Used for V1 only")
    
    parser.add_argument("--min-chars-natural", type=int, default=200)
    parser.add_argument("--max-chars-natural", type=int, default=4000)
    parser.add_argument("--min-chars-prompts", type=int, default=150)
    parser.add_argument("--force", action="store_true")
    
    parser.add_argument("--v2", action="store_true", help="Build V2 datasets (Natural + Persona + Cognitive)")
    
    args = parser.parse_args()
    
    if args.v2:
        build_v2_datasets(
            args.force,
            args.min_chars_natural,
            args.max_chars_natural,
            args.min_chars_prompts
        )
    else:
        build_v1_datasets(
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
