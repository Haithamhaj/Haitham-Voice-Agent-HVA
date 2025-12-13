# Haithm Style Datasets - V2 (Refactored)
**Date:** 2025-12-12
**Status:** Ready for Training

## Overview
The V2 dataset refactoring splits the training data into three distinct biological layers to better control the model's behavior:
1.  **Natural Style:** How Haithm talks/writes (from real data).
2.  **Persona:** Who Haithm is (Identity, Values, Bio).
3.  **Cognitive:** How Haithm thinks (Reasoning, Frameworks).

## Dataset Statistics

| Dataset | Filename | Records | Size | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Natural Style** | `dataset_haithm_style_natural_v2.jsonl` | **28,513** | ~13 MB | Merged GPT & WhatsApp high-quality messages (200-4000 chars). |
| **Persona** | `dataset_haithm_style_persona_v2.jsonl` | **10** | ~5 KB | Q&A pairs defining identity, role, and values. |
| **Cognitive** | `dataset_haithm_style_cognitive_v2.jsonl` | **10** | ~6 KB | Q&A pairs defining reasoning frameworks (e.g., CRAFTS/INSPIRE). |

### Source Breakdown (Natural Style)
The Natural Style dataset is a fusion of multiple sources:
- **GPT Archive:** High-quality thoughtful responses.
- **WhatsApp:** Verified "Haithm-only" messages, filtered for junk/length.

*(Exact breakdown available in `dataset_haithm_style_natural_stats_v2.json`)*

## Construction Methodology

### 1. Natural Style V2
- **Sources:** `haithm_corpus_raw_gpt_2025-12-11.jsonl` + `haithm_corpus_whatsapp_haithm_only.jsonl`
- **Filtering:**
    - Length: 200 - 4000 characters.
    - Identity: Sender must be Haithm.
    - Quality: Removed system messages, short replies ("ok", "thanks"), and code-heavy blocks.
- **Format:** Alpaca-style (`instruction`, `input`, `output`) + `source_type` metadata.

### 2. Persona V2
- **Sources:** Derived from the **Haithm Mini-Me YAML Spec**.
- **Content:** Explicit Q&A regarding:
    - Identity & Roles (LeapAI, Osool & Bakheet).
    - Handling clients/colleagues.
    - Values (Responsibility, Truth-first).

### 3. Cognitive V2
- **Sources:** Derived from the **Haithm Mini-Me YAML Spec**.
- **Content:** Explicit Q&A regarding:
    - Thinking processes (Pipelines, System Design).
    - Frameworks (INSPIRE, CRAFTS).
    - Balancing creativity vs. execution.

## Caveats & Next Steps
- **Audio:** Audio transcripts are **not yet included** in this V2 build.
- **Prompts:** Pure "Acting as an Engineer" prompts are separated out or implicit in the cognitive layer.
- **Validation:** Recommend manual inspection of 5-10 random Natural records before full training to ensure WhatsApp formatting looks clean.
