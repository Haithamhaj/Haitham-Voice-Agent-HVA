# Change Rules & Safety Protocol

## Before ANY Change

1.  **Run Health Check**: Ensure the system is currently working.
    ```bash
    python -m haitham_voice_agent.main --test "health check"
    ```
2.  **Backup Critical Files**: If modifying `config.py` or `main.py`, create a copy.
    ```bash
    cp haitham_voice_agent/config.py haitham_voice_agent/config.py.bak
    ```
3.  **Identify Dependencies**: Check `PROJECT_MAP.md` to see what else might break.

## Rules by File

### `config.py` (CRITICAL)
-   **Rule**: NEVER remove an existing configuration variable unless you are 100% sure it's unused.
-   **Check**: After modifying, run `pytest haitham_voice_agent/tests/test_config.py`.
-   **Risk**: Breaking API keys or paths will stop the entire agent.

### `main.py` (CRITICAL)
-   **Rule**: Do not modify the main `while` loop or `process_command_mode` logic without manual verification.
-   **Check**: Run the full integration test (Voice or Text mode) after changes.
-   **Related**: Changes here often affect `gui_process.py`.

### `llm_router.py`
-   **Rule**: If changing keywords, verify that "plan" commands still go to GPT and "analyze" commands go to Gemini.
-   **Check**: Run `pytest haitham_voice_agent/tests/test_llm_router.py`.

### `intent_router.py`
-   **Rule**: Ensure new regex patterns don't shadow existing ones.
-   **Check**: Test with specific phrases that trigger the new intent AND old intents.

## Common Pitfalls

1.  **Path Issues**:
    -   *Problem*: Hardcoding paths like `/Users/haitham/...`.
    -   *Fix*: ALWAYS use `Path.home() / ...` or `Config.HVA_HOME`.
    
2.  **Async/Await**:
    -   *Problem*: Calling an async function without `await` in `main.py`.
    -   *Fix*: Ensure all tool calls in `execute_plan` are properly awaited.

3.  **Infinite Loops**:
    -   *Problem*: The `while self.is_running:` loop in `main.py` must have a blocking call (like `input` or `listen`) to prevent CPU spikes.

## Rollback Procedure

If a change breaks the system:

1.  **Stop the Agent**: Ctrl+C.
2.  **Restore Backup**:
    ```bash
    cp haitham_voice_agent/config.py.bak haitham_voice_agent/config.py
    ```
    OR revert via Git:
    ```bash
    git checkout haitham_voice_agent/config.py
    ```
3.  **Verify**: Run the health check again.

---
## UPDATE LOG
| Date | Change | Verified By | Test Result |
|------|--------|-------------|-------------|
| 2025-12-01 | Initial creation | Antigravity | Pass |
