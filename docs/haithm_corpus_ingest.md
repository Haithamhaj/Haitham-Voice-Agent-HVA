# Haithm Corpus Ingestion Pipeline

## Purpose
The goal of this pipeline is to ingest various documents and chat logs authored by or relevant to "Haithm" (the user/persona) into a single, normalized machine-learning-ready corpus (`jsonl`). This raw text corpus will serve as the foundation for building a "Style" fine-tuning dataset for the Qwen model.

## Directory Structure

You should manually place your raw files into the `haithm_corpus` directory:

```
haithm_corpus/
├── docs/       # Articles, CV, Frameworks (PDF, DOCX, MD, TXT)
├── chats/      # GPT/LLM chat exports (JSON, HTML)
└── other/      # Miscellaneous text data
```

## How to Run

1. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Ingestion Script**:
   ```bash
   python scripts/ingest_haithm_corpus.py
   ```

   **Options**:
   - `--force`: Overwrite the output file if it exists.
   - `--max-chars <int>`: Maximum characters per chunk (default: 2000).
   - `--root <path>`: Custom input root directory (default: `haithm_corpus`).
   - `--output <path>`: Custom output path (default: `data/haithm_corpus_raw.jsonl`).

## Output Format

The script generates `data/haithm_corpus_raw.jsonl`. Each line is a JSON object corresponding to a chunk of text.

### Schema
```json
{
  "id": "7f8a9d..._0",              // Unique ID (Hash of path + chunk index)
  "source_path": "haithm_corpus/docs/my_cv.pdf",
  "source_type": "pdf",             // txt, md, pdf, docx, chat_json, chat_html
  "role": "user",                   // user (Haithm), assistant, or system
  "chunk_index": 0,                 // integer index
  "text": "Extracted text content..."
}
```

### Roles
- **user**: Represents Haithm's voice (human input in chats, or the author of static docs).
- **assistant**: Represents AI model outputs (in chat logs).
- **system**: System prompts (if found in chat logs).

## Next Steps
After populating this raw corpus, a separate process (Dataset Builder) will filter and format these records into `(Instruction, Input, Output)` pairs for fine-tuning.
