# V4.2 Patch Report (Strict 600)
- Generated: 2025-12-25T15:38:56.941065Z
- Status: COMPLETE_STRICT_600

## Targets vs Actual
| Bucket | Target | Actual | OK |
|---|---:|---:|:--:|
| `ambiguity_handling` | 180 | 180 | ✅ |
| `error_correction_dialogues` | 140 | 140 | ✅ |
| `numeric_discipline` | 140 | 140 | ✅ |
| `refuse_to_guess_source_needed` | 70 | 70 | ✅ |
| `grounded_summaries` | 70 | 70 | ✅ |

## Integrity
- Total lines: 600
- Leakage hits: 0
- sha256(v4_2_patch.jsonl): `3ce7d6a7fb94032a5db4ef118e8e50dbb9bdb96db70ba29d4ae70b3021e8ef3f`
- bytes: 442696

## Note
This bundle is a strict downsample from the previous 608-row release to hit the agreed bucket targets exactly. No row content was modified.
