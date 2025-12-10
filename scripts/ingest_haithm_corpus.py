#!/usr/bin/env python3
"""
Haithm Corpus Ingestion Script
==============================

Purpose:
    Walks through `haithm_corpus/` and ingests supported files into 
    a normalized JSONL dataset (`data/haithm_corpus_raw.jsonl`).

Supported Formats:
    - Text: .txt, .md
    - Documents: .pdf, .docx
    - Chats: .json (OpenAI export), .html (heuristic)

Usage:
    python scripts/ingest_haithm_corpus.py [--force]
"""

import os
import json
import argparse
import hashlib
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

# Library Imports
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import docx
except ImportError:
    docx = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Ingestor")

class CorpusIngestor:
    def __init__(self, root_dir: str, output_file: str, max_chars: int, force: bool):
        self.root_dir = Path(root_dir)
        self.output_file = Path(output_file)
        self.max_chars = max_chars
        self.force = force
        self.stats = {
            "scanned": 0,
            "ingested": 0,
            "skipped": 0,
            "records": 0,
            "by_type": {},
            "by_role": {}
        }

    def run(self):
        # Checks
        if not self.root_dir.exists():
            logger.error(f"Root directory not found: {self.root_dir}")
            return

        if self.output_file.exists() and not self.force:
            logger.error(f"Output file exists: {self.output_file}")
            logger.info("Use --force to overwrite.")
            return

        logger.info(f"Starting ingestion from: {self.root_dir}")
        all_records = []

        # Walk directory
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                file_path = Path(root) / file
                # Skip hidden files
                if file.startswith("."): 
                    continue
                
                self.stats["scanned"] += 1
                records = self.process_file(file_path)
                
                if records:
                    all_records.extend(records)
                    self.stats["ingested"] += 1
                else:
                    self.stats["skipped"] += 1

        # Write output
        if all_records:
            self._write_jsonl(all_records)
            self._print_summary()
        else:
            logger.warning("No records were generated. Is the directory empty?")

    def process_file(self, path: Path) -> List[Dict]:
        """Dispatch to appropriate handler based on extension."""
        ext = path.suffix.lower()
        
        try:
            if ext in [".txt", ".md"]:
                return self._handle_text(path)
            elif ext == ".pdf":
                if not PyPDF2:
                    logger.warning(f"Skipping {path.name}: PyPDF2 not installed")
                    return []
                return self._handle_pdf(path)
            elif ext == ".docx":
                if not docx:
                    logger.warning(f"Skipping {path.name}: python-docx not installed")
                    return []
                return self._handle_docx(path)
            elif ext == ".json":
                return self._handle_json_chat(path)
            elif ext in [".html", ".htm"]:
                if not BeautifulSoup:
                    logger.warning(f"Skipping {path.name}: beautifulsoup4 not installed")
                    return []
                return self._handle_html_chat(path)
            else:
                logger.debug(f"Skipping unsupported type: {path.name}")
                return []
        except Exception as e:
            logger.error(f"Error processing {path.name}: {e}")
            return []

    # --- Handlers ---

    def _handle_text(self, path: Path) -> List[Dict]:
        """Simple text ingestion."""
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        
        return self._create_chunks(text, path, source_type=path.suffix[1:], role="user")

    def _handle_pdf(self, path: Path) -> List[Dict]:
        """PDF ingestion (User role by default for static docs)."""
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n\n"
        
        return self._create_chunks(text, path, source_type="pdf", role="user")

    def _handle_docx(self, path: Path) -> List[Dict]:
        """DOCX ingestion."""
        doc = docx.Document(path)
        text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return self._create_chunks(text, path, source_type="docx", role="user")

    def _handle_json_chat(self, path: Path) -> List[Dict]:
        """
        Handle JSON chats. Assumes structure like:
        1. List of messages: [{"role": "user", "content/text": "..."}]
        2. OpenAI Export: [{"mapping": { "id": {"message": { ... }} }}] (Complex)
        3. Simple conversation dict: {"messages": [...]}
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        messages = []
        
        # Heuristic 1: Root is list
        if isinstance(data, list):
            # Check if likely OpenAI conversation export (list of conversation objects)
            if len(data) > 0 and "mapping" in data[0]:
                logger.info(f"Detected OpenAI Export format in {path.name}")
                for convo in data:
                    messages.extend(self._extract_openai_messages(convo))
            else:
                # Assume list of messages
                messages = data
        # Heuristic 2: Root is dict with 'messages'
        elif isinstance(data, dict) and "messages" in data:
            messages = data["messages"]
        else:
            logger.warning(f"Unknown JSON structure in {path.name}")
            return []

        records = []
        for msg in messages:
            # Normalize fields
            role = msg.get("role") or msg.get("author") or msg.get("author_role")
            content = msg.get("content") or msg.get("text") or msg.get("parts") # OpenAI uses 'parts' list
            
            # OpenAI specific normalization
            if isinstance(content, list): 
                # usually list of strings for openai
                content = "\n".join([str(c) for c in content if c])
            elif not isinstance(content, str):
                continue # Skip non-text content
                
            if not content.strip(): continue
            
            # Map roles
            normalized_role = "user"
            if role in ["assistant", "model", "bot"]:
                normalized_role = "assistant"
            elif role == "system":
                normalized_role = "system"
            
            # Only intake non-empty valid roles
            chunks = self._create_chunks(content, path, source_type="chat_json", role=normalized_role)
            records.extend(chunks)

        return records

    def _extract_openai_messages(self, conversation: Dict) -> List[Dict]:
        """Helper to extract linear messages from OpenAI export structure."""
        msgs = []
        mapping = conversation.get("mapping", {})
        for key, val in mapping.items():
            message = val.get("message")
            if not message: continue
            
            author = message.get("author", {})
            role = author.get("role")
            content_parts = message.get("content", {}).get("parts", [])
            
            # Filter valid parts
            text_parts = [p for p in content_parts if isinstance(p, str) and p]
            if not text_parts: continue
            
            msgs.append({
                "role": role,
                "content": "\n".join(text_parts),
                "timestamp": message.get("create_time") # Optional, not used yet
            })
        
        # Sort by timestamp if available? OpenAI export usually strictly linked list but unordered in mapping dict keys.
        # Ideally, we should traverse 'root' -> 'children' links, but for bulk ingestion, linear is okay-ish 
        # or relying on create_time sorting.
        # Let's simple sort by create_time if exists
        msgs.sort(key=lambda x: x.get("timestamp") or 0)
        return msgs

    def _handle_html_chat(self, path: Path) -> List[Dict]:
        """Simple HTML heuristic extraction."""
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        # Common selectors for chat logs
        # 1. Custom div classes (e.g. .user-message, .assistant-message)
        # 2. Generic paragraphs
        
        records = []
        
        # Heuristic: Find elements with clear role indicators in class
        # This is very generic and assumes the user will put specific html files
        
        # Strategy: Get all text, treat as user document if no structure found?
        # Better: Look for common 'message' containers.
        
        # Try finding everything, and use class name to guess role
        all_divs = soup.find_all("div")
        found_structure = False
        
        for div in all_divs:
            classes = div.get("class", [])
            text = div.get_text(strip=True)
            if not text: continue
            
            role = "user" # Default
            
            class_str = " ".join(classes).lower()
            if "assistant" in class_str or "model" in class_str or "bot" in class_str:
                role = "assistant"
                found_structure = True
            elif "user" in class_str or "human" in class_str:
                role = "user"
                found_structure = True
            
            # If we found explicit structure markers, ingest segments
            if found_structure and len(text) > 20: # Skip tiny bits
                 records.extend(self._create_chunks(text, path, source_type="chat_html", role=role))

        # Fallback: Treats whole body as one user document (e.g. article saved as html)
        if not records:
             text = soup.get_text(separator="\n", strip=True)
             records.extend(self._create_chunks(text, path, source_type="chat_html", role="user"))
             
        return records

    # --- Core Logic ---

    def _create_chunks(self, text: str, path: Path, source_type: str, role: str) -> List[Dict]:
        """Split text into chunks and wrap in JSON objects."""
        if not text: return []
        
        chunks = []
        
        # Simple splitting by newlines and regrouping until max_chars
        # This preserves paragraph integrity better than strict char slicing
        lines = text.split('\n')
        current_chunk = []
        current_length = 0
        
        chunk_segments = []
        
        for line in lines:
            line_len = len(line)
            if current_length + line_len > self.max_chars and current_chunk:
                # Flush
                chunk_segments.append("\n".join(current_chunk))
                current_chunk = []
                current_length = 0
            
            current_chunk.append(line)
            current_length += line_len
            
        if current_chunk:
            chunk_segments.append("\n".join(current_chunk))
        
        # Create Records
        relative_path = os.path.relpath(path, self.root_dir)
        path_hash = hashlib.md5(str(relative_path).encode()).hexdigest()[:8]
        
        for i, segment in enumerate(chunk_segments):
            if not segment.strip(): continue
            
            record = {
                "id": f"{path_hash}_{i}",
                "source_path": str(relative_path),
                "source_type": source_type,
                "role": role,
                "chunk_index": i,
                "text": segment
            }
            chunks.append(record)
            
            # Stats
            self.stats["records"] += 1
            self.stats["by_type"][source_type] = self.stats["by_type"].get(source_type, 0) + 1
            self.stats["by_role"][str(role)] = self.stats["by_role"].get(str(role), 0) + 1
            
        return chunks

    def _write_jsonl(self, records: List[Dict]):
        """Write records to output file."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        logger.info(f"Successfully wrote {len(records)} records to {self.output_file}")

    def _print_summary(self):
        print("\n--- Ingestion Summary ---")
        print(f"Files Scanned:    {self.stats['scanned']}")
        print(f"Files Ingested:   {self.stats['ingested']}")
        print(f"Files Skipped:    {self.stats['skipped']}")
        print(f"Total Chunks:     {self.stats['records']}")
        print("\nBreakdown by Type:")
        for k, v in self.stats["by_type"].items():
            print(f"  {k}: {v}")
        print("\nBreakdown by Role:")
        for k, v in self.stats["by_role"].items():
            print(f"  {k}: {v}")
        print("-------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Ingest Haithm Corpus Files")
    parser.add_argument("--root", default="haithm_corpus", help="Root directory for input files")
    parser.add_argument("--output", default="data/haithm_corpus_raw.jsonl", help="Output JSONL file")
    parser.add_argument("--max-chars", type=int, default=2000, help="Max characters per text chunk")
    parser.add_argument("--force", action="store_true", help="Overwrite existing output file")
    
    args = parser.parse_args()
    
    ingestor = CorpusIngestor(
        root_dir=args.root,
        output_file=args.output,
        max_chars=args.max_chars,
        force=args.force
    )
    ingestor.run()

if __name__ == "__main__":
    main()
