#!/usr/bin/env python3
import json
import statistics
import collections
import argparse
from pathlib import Path

def analyze_corpus(jsonl_path):
    print(f"Analyzing: {jsonl_path}")
    
    total_records = 0
    by_type = collections.Counter()
    by_role = collections.Counter()
    user_lengths = []
    source_counts = collections.Counter()
    
    samples = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                record = json.loads(line)
                total_records += 1
                
                src_type = record.get('source_type', 'unknown')
                role = record.get('role', 'null')
                text = record.get('text', '')
                src_path = record.get('source_path', 'unknown')
                
                by_type[src_type] += 1
                by_role[role] += 1
                
                if role == 'user':
                    user_lengths.append(len(text))
                    source_counts[src_path] += 1
                    
                    if len(samples) < 5 and len(text) > 50:
                        samples.append(text[:200].replace('\n', ' '))
                        
            except Exception as e:
                print(f"Error parsing line: {e}")

    # Stats
    print("\n=== SUMMARY Stats ===")
    print(f"Total Records: {total_records}")
    
    print("\n--- By Type ---")
    for k, v in by_type.most_common():
        print(f"{k}: {v}")
        
    print("\n--- By Role ---")
    for k, v in by_role.most_common():
        print(f"{k}: {v}")
        
    print("\n--- User Input Stats ---")
    count_user = len(user_lengths)
    print(f"User Records: {count_user}")
    if count_user > 0:
        print(f"Min Length: {min(user_lengths)}")
        print(f"Max Length: {max(user_lengths)}")
        print(f"Avg Length: {statistics.mean(user_lengths):.2f}")
    
    print("\n--- Top Sources (User content) ---")
    for k, v in source_counts.most_common(5):
        print(f"{k}: {v} records")
        
    print("\n--- Samples (User) ---")
    for i, s in enumerate(samples):
        print(f"{i+1}. {s}...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    analyze_corpus(args.path)
