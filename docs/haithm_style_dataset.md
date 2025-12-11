# Haithm Style Datasets

## Overview
These datasets are designed to fine-tune a model to emulate "Haithm's" writing voice. The data is derived from the ingested corpus (`data/haithm_corpus_raw_gpt_2025-12-11.jsonl`).

## Datasets

### 1. Natural Style (`data/dataset_haithm_style_natural.jsonl`)
- **Purpose**: Teach the model to write like Haithm in normal conversation (analysis, questions, reflections).
- **Size**: 6,170 records.
- **Criteria**:
  - Role: `user`
  - Length: 200 - 4000 characters.
  - Excludes explicit system prompts or heavy code blocks.
- **Schema**:
  ```json
  {
    "instruction": "You are Haithm. Write in Haithm's natural style...",
    "input": "",
    "output": "<original text>"
  }
  ```

### 2. Prompt Style (`data/dataset_haithm_style_prompts.jsonl`)
- **Purpose**: Teach the model how Haithm writes strict system instructions (Prompt Engineering).
- **Size**: 26 records.
- **Criteria**:
  - Role: `user`
  - Explicit keywords: "Your task is", "Act as", "System:", "RULES:".
- **Schema**:
  ```json
  {
    "instruction": "You are Haithm writing system-level instructions...",
    "input": "",
    "output": "<original text>"
  }
  ```

## Usage
These files are ready for QLoRA fine-tuning. 
- Use **Natural** dataset to make the assistant sound like the user.
- Use **Prompt** dataset to make the assistant better at generating system prompts in the user's preferred format.
