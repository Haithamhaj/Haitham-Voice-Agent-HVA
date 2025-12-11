# Haithm Corpus Audio Verification Report

## Current Corpus Status
- **Corpus File**: `data/haithm_corpus_raw_gpt_2025-12-11.jsonl`
- **Total Records**: 44,593
- **Audio Records**: 0
- **Conclusion**: Audio has **NOT** been ingested into the corpus.

## Ingestion Capability Diagnostics
- **Script**: `scripts/ingest_haithm_corpus.py`
  - Supports: `.m4a`, `.mp3`, `.wav`
  - Backend: `openai-whisper` (Python) + `ffmpeg` (System)
- **Environment Status**:
  - `is_whisper_available`: **False** (Python module `whisper` not found)
  - `is_ffmpeg_available`: **False** (Command `ffmpeg` not found)

## Audio Files on Disk
- **Total Audio Files Found**: 22
- **Breakdown**:
  - `.wav`: 22
  - `.m4a`: 0
  - `.mp3`: 0
- **Locations**:
  - Found in: `Haitham Data/`
  - Not found in: `haithm_corpus/`

## Recommended Safe Audio Ingest Plan

### 1. Install Prerequisites (macOS)
The ingestion script requires `ffmpeg` for audio decoding and the `openai-whisper` package for transcription.

```bash
# 1. Install ffmpeg (system dependency)
brew install ffmpeg

# 2. Install OpenAI Whisper (python dependency)
pip install openai-whisper
```

### 2. Ingest Command
After installing the tools, use the following command to ingest. We recommend writing to a *new* file first to verify results without overwriting your stable corpus.

```bash
python scripts/ingest_haithm_corpus.py \
  --root "Haitham Data" \
  --output "data/haithm_corpus_raw_with_audio.jsonl"
```

> **Note**: If `Haitham Data` contains only the raw audio and not the text corpus, you may want to merge or point to the correct root containing BOTH. If your goal is just to add audio, the above command works but will generate a dataset containing *only* what is in "Haitham Data".
