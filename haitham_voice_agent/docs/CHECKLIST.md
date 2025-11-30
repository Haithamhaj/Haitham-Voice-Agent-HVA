# Pre-Change Checklist

## Pre-Change Checklist

Before requesting changes, I have:
- [ ] **Described the specific problem or feature** clearly.
- [ ] **Listed the files** I think need changing.
- [ ] **Run the health check** and confirmed it passes:
      `python -m haitham_voice_agent.main --test "status"`
- [ ] **Backed up current state** (git commit or file backup).

## Post-Change Verification

After changes are made, verify:
- [ ] **Health check passes**: `python -m haitham_voice_agent.main --test "status"`
- [ ] **Specific feature works**: (e.g., "Open Google" actually opens Google).
- [ ] **Related features still work**: (e.g., Did fixing Gmail break Memory?).
- [ ] **No new errors** in `hva.log`.

---
## UPDATE LOG
| Date | Change | Verified By | Test Result |
|------|--------|-------------|-------------|
| 2025-12-01 | Initial creation | Antigravity | Pass |
