# Borderline Leakage Review

Analyzed 1541 rows removed for leakage.
- Likely Garbage (Output < 250 chars): 0.6% (9)
- Potentially Valuable (Output >= 250 chars): 99.4% (1532)

## Breakdown by Reason
| Reason | Count | % Garbage |
|---|---|---|
| OpenAI | 797 | 0.8% |
| Turn Refs | 367 | 0.8% |
| Tools | 45 | 0.0% |
| User Files | 24 | 0.0% |
| Sys Msg | 19 | 0.0% |
| DALL-E | 125 | 0.0% |
| GPT-4o | 158 | 0.0% |
| Identity | 2 | 0.0% |
| Policy | 4 | 0.0% |

## Proposal
For the 'Potentially Valuable' rows, many are likely long responses that contain a single incidental 'As an AI' disclaimer. We could refine cleaning to strip just the boilerplate sentence rather than dropping the row, IF data is scarce. However, for V4, aggressive removal ensures safety.