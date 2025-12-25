# V4 Dataset Audit Report

## 1. Processing Statistics
| File | Rows In | Rows Out | Leakage Dropped | Dedup Dropped | Length (Med/Max) |
|---|---|---|---|---|---|
| dataset_haithm_style_natural_v2.jsonl | 28513 | 26476 | 1541 | 496 | 1413/3982 |
| dataset_haithm_style_prompts.jsonl | 26 | 26 | 0 | 0 | 1616/2050 |
| dataset_haithm_style_persona_v2.jsonl | 10 | 10 | 0 | 0 | 184/267 |
| dataset_haithm_style_cognitive_v2.jsonl | 10 | 10 | 0 | 0 | 260/405 |
| dataset_haithm_v3_cognitive_map.jsonl | 16 | 16 | 0 | 0 | 58/583 |

## 2. Leakage Pattern Hits
- **OpenAI mention**: 797
- **turnXtool**: 367
- **GPT-4o returned**: 158
- **DALL-E**: 125
- **file_search**: 42
- **files uploaded by user**: 24
- **system message**: 19
- **content policy**: 4
- **web.run**: 3
- **You are ChatGPT**: 2

## 3. PII Masking
- Total PII hits replaced: 674

## 4. Verification
- **Artifact Scan**: PASSED (Zero hits for banned terms)

## 5. Manifests
- `manifest_v4_keep_pii.json`
- `manifest_v4_mask_pii.json`
