# Test Commands Guide

## Quick Health Check

Run this command to verify the system is up and running without using voice:

```bash
python -m haitham_voice_agent.main --test "hello"
```

**Expected Output:**
- Logs showing initialization of HVA.
- "HVA initialized successfully"
- "Test Mode: hello"
- A response from the agent (e.g., "Hello! How can I help you?" or similar).

## Test Individual Modules

We use `pytest` for module-level testing.

### 1. Configuration & Setup
Verify that environment variables and paths are correct.
```bash
pytest haitham_voice_agent/tests/test_config.py
```

### 2. LLM Router
Test if the router correctly sends tasks to GPT or Gemini.
```bash
pytest haitham_voice_agent/tests/test_llm_router.py
```

### 3. Tools (Files, Browser, System)
Test the basic tools functionality.
```bash
pytest haitham_voice_agent/tests/test_tools.py
```

### 4. Memory System
Test the memory database and vector store.
```bash
pytest haitham_voice_agent/tests/test_memory_foundation.py
```

### 5. Gmail Integration
Test email fetching and drafting (requires valid credentials).
```bash
pytest haitham_voice_agent/tests/test_gmail_llm.py
```

## Full Integration Test

To test the full loop (Voice -> STT -> LLM -> TTS), run the main app:

```bash
python -m haitham_voice_agent.main
```

Then speak a command like "Hello" or "What time is it?".

**Expected Behavior:**
1.  App starts and prints "Press ENTER to speak".
2.  After pressing Enter, it listens.
3.  It prints the transcribed text.
4.  It speaks the response.

## Manual Verification Steps

### Voice Recognition (STT)
1.  Run `python -m haitham_voice_agent.main`
2.  Say "Open Google"
3.  **Verify**: Browser opens to Google.

### Memory
1.  Run `python -m haitham_voice_agent.main --test "save note buy milk"`
2.  Run `python -m haitham_voice_agent.main --test "search notes milk"`
3.  **Verify**: The agent finds the note about milk.

### File Operations
1.  Run `python -m haitham_voice_agent.main --test "list files in downloads"`
2.  **Verify**: It lists files from your Downloads folder.

---
## UPDATE LOG
| Date | Change | Verified By | Test Result |
|------|--------|-------------|-------------|
| 2025-12-01 | Initial creation | Antigravity | Pass |
