Final File: dataset_haithm_style_cognitive_v2.jsonl = 10
Final File: dataset_haithm_v3_cognitive_map.jsonl = 16
Final File: dataset_haithm_style_natural_v2.jsonl = 26476
Final File: dataset_haithm_style_persona_v2.jsonl = 10
Final File: dataset_haithm_style_prompts.jsonl = 26
SUM_TOTAL_FINAL (Unique IDs): 26536
SUM_TOTAL_FINAL (Rows): 26538
Split File: v4_mask_pii_train.jsonl = 26009
Split File: v4_mask_pii_val.jsonl = 529
SUM_TOTAL_SPLIT (Unique IDs): 26536
SUM_TOTAL_SPLIT (Rows): 26538

## Counts Matched. Zero reconciliation delta.

## Part B: Empty Input Check
| File | Empty String | Null | Missing Key | Total |
|---|---|---|---|---|
| dataset_haithm_style_cognitive_v2.jsonl | 10 | 0 | 0 | 10 |
| dataset_haithm_v3_cognitive_map.jsonl | 16 | 0 | 0 | 16 |
| dataset_haithm_style_natural_v2.jsonl | 26476 | 0 | 0 | 26476 |
| dataset_haithm_style_persona_v2.jsonl | 10 | 0 | 0 | 10 |
| dataset_haithm_style_prompts.jsonl | 26 | 0 | 0 | 26 |

## Part C: Salvageability Analysis
- Total Leakage Rows: 1541
- Salvageable (len>=200 after redaction): 1382 (89.7%)

### Breakdown by Category (Salvageable)
- Other: 1361
- Policy: 19
- AI_Disclaimer: 2

## Part D: Splits OK. No fix needed.