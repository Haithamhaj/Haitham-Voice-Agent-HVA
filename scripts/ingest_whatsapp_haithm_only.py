#!/usr/bin/env python3
"""
WhatsApp Corpus Ingestion Script
================================

Ingests WhatsApp chat exports from ZIP files, parses them, 
and filters for messages sent by Haithm.

Formats:
- Android: "12/09/2024, 21:35 - Sender: Message"
- iOS: "[12/09/2024, 21:35] Sender: Message"

Output:
- JSONL file with fields: id, source_path, role, sender, chat_name, timestamp, text
"""

import os
import re
import json
import zipfile
import argparse
import uuid
from pathlib import Path
from datetime import datetime

# --- Configuration ---
HAITHM_NAMES = [
    "Haithm",
    "Haitham",
    "Haitham Hamadneh"
]

# Common system messages to skip
SYSTEM_MESSAGES_SUBSTRINGS = [
    "Messages to this group are now secured",
    "joined using an invite link",
    "left the group",
    "added",
    "removed",
    "changed the subject",
    "changed the group icon",
    "You deleted this message",
    "This message was deleted",
    "waiting for this message",
    "security code changed",
    "created group",
    "call ended",
    "missed call",
    "missed voice call",
    "missed video call"
]

# Regex Patterns
# Android: 12/09/2024, 21:35 - Haithm: message
ANDROID_PATTERN = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2})\s-\s([^:]+): (.*)$')

# iOS: [12/09/2024, 21:35] Haithm: message
# Note: Sometimes iOS uses periods or different brackets, but standard export is []
IOS_PATTERN = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}:?\d{0,2})\]\s([^:]+): (.*)$')


def parse_line(line):
    """
    Attempts to parse a line using known patterns.
    Returns (timestamp, sender, message) or None.
    """
    line = line.strip()
    if not line:
        return None
        
    # Check Android
    match = ANDROID_PATTERN.match(line)
    if match:
        return match.groups()
        
    # Check iOS
    match = IOS_PATTERN.match(line)
    if match:
        return match.groups()
        
    return None

def is_haithm(sender):
    """Checks if sender is Haithm."""
    return sender in HAITHM_NAMES

def is_system_message(text):
    """Checks for common system message patterns."""
    for s in SYSTEM_MESSAGES_SUBSTRINGS:
        if s in text:
            return True
    return False

def process_zip_file(zip_path):
    """
    Reads a ZIP file in memory, finds the first .txt file, parses it.
    Returns list of message dicts.
    """
    messages = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            txt_files = [f for f in z.namelist() if f.endswith('.txt')]
            if not txt_files:
                return []
                
            # Usually there's only one _chat.txt or Chat.txt
            target_file = txt_files[0]
            chat_name = Path(zip_path).stem.replace("WhatsApp Chat - ", "")
            
            with z.open(target_file) as f:
                # Read line by line, decoding UTF-8
                for line_bytes in f:
                    try:
                        line_str = line_bytes.decode('utf-8').strip()
                        # Remove LTR/RTL marks just in case
                        line_str = line_str.replace('\u200e', '').replace('\u200f', '')
                        
                        parsed = parse_line(line_str)
                        if parsed:
                            timestamp, sender, text = parsed
                            
                            # Filter Identity
                            if is_haithm(sender):
                                # Filter System Messages
                                if not is_system_message(text):
                                    messages.append({
                                        "id": str(uuid.uuid4()),
                                        "source_path": Path(zip_path).name,
                                        "source_type": "whatsapp_chat",
                                        "role": "user",
                                        "sender": "haithm",
                                        "chat_name": chat_name,
                                        "timestamp": timestamp,
                                        "text": text
                                    })
                    except UnicodeDecodeError:
                        continue # Skip bad encoding lines
                        
    except zipfile.BadZipFile:
        print(f"Warning: Bad ZIP file {zip_path}")
        return []
    except Exception as e:
        print(f"Error processing {zip_path}: {e}")
        return []

    return messages

def main():
    parser = argparse.ArgumentParser(description="Ingest WhatsApp Haithm-Only Corpus")
    parser.add_argument("--root", default="/Users/haitham/development/Haitham Voice Agent (HVA)/WhatsApp", help="Root folder containing ZIPs")
    parser.add_argument("--output", default="data/haithm_corpus_whatsapp_haithm_only.jsonl", help="Output JSONL path")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output")
    
    args = parser.parse_args()
    
    root_path = Path(args.root)
    out_path = Path(args.output)
    
    if out_path.exists() and not args.force:
        print(f"Output file {out_path} exists. Use --force to overwrite.")
        return

    if not root_path.exists():
        print(f"Root path {root_path} does not exist.")
        return
        
    print(f"Scanning {root_path} for ZIP files...")
    zip_files = list(root_path.glob("*.zip"))
    
    total_zips = 0
    total_parsed = 0 # Approximate
    total_haithm = 0
    total_skipped = 0 # Approximate (based on line count logic might be hard without counting every line, let's track non-haithm parsed)
    
    all_messages = []
    
    for zip_file in zip_files:
        chat_msgs = process_zip_file(zip_file)
        if chat_msgs:
            total_zips += 1
            total_haithm += len(chat_msgs)
            all_messages.extend(chat_msgs)
        
        # Simple progress
        print(f"Processed {zip_file.name}: Found {len(chat_msgs)} Haithm messages")

    # Write output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        for msg in all_messages:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
            
    print("\n=== Ingestion Summary ===")
    print(f"ZIP Files Processed: {total_zips}")
    print(f"Total Haithm Messages: {total_haithm}")
    print(f"Output: {out_path}")
    print("=========================")

if __name__ == "__main__":
    main()
