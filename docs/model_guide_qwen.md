# Qwen 2.5 (Local Model) Guide

## Overview
This project uses **Qwen 2.5** (via Ollama) for local, private, and cost-effective intelligence. Unlike massive cloud models (GPT-4, Gemini Pro), smaller local models require specific prompting strategies to perform reliably.

## Best Practices

### 1. System Prompts
Qwen responds best when you explicitly define its identity and constraints at the very beginning.
*   **Identity:** Start with `You are Qwen, a helpful assistant...` or specific roles like `You are a strict data extractor`.
*   **Persona Enforcement:** To prevent "parroting" (repeating user text), explicitly add:
    ```
    DO NOT continue the user's sentence.
    Treat the input as a COMMAND or QUESTION.
    ```

### 2. Structured Output (JSON)
Qwen 2.5 is strong at JSON but needs clear rules:
*   **Explicit Instruction:** "Respond in JSON ONLY."
*   **Schema Definition:** Provide a mini-example of the desired JSON structure.
    ```text
    Response Format:
    {"key": "value", "confidence": 0.9}
    ```
*   **Constraint:** "Do not add markdown formatting (```json) or introductory text."

### 3. Improving Accuracy (CoT)
For complex logic, ask it to "think" before answering, or break tasks down:
*   **Chain of Thought:** "Think step-by-step before provided the final JSON." (Note: This increases latency).
*   **Few-Shot Prompting:** Provide 1-2 examples of Input -> Output in the prompt.

## Common Pitfalls & Solutions

| Issue | Solution |
| :--- | :--- |
| **Hallucination** (Inventing facts) | Set `temperature` to `0.1` or `0.2` for factual tasks. |
| **Parroting** (Repeating input) | Add negative constraints: "DO NOT rephrase". Use "Question: {text}" format. |
| **Command Confusion** | If it confuses "I have a meeting" with "Meeting Mode", be explicit in keyword mapping triggers. |

## Example System Prompt (Robust)
```python
SYSTEM_PROMPT = """
You are Haitham's Assistant (Qwen 2.5 Local).
Your task is to classify user intents accurately.

RULES:
1. Output JSON ONLY.
2. If uncertain, return {"type": "needs_clarification"}.
3. DO NOT output conversational filler ("Here is the JSON...").

INTENTS:
- create_task: "Remind me to...", "I have a meeting..."
- system_control: "Turn off volume", "Activate meeting mode"
"""
```

## Resources
*   [Qwen 2.5 Technical Report & Docs](https://huggingface.co/Qwen)
*   [Ollama Model Card](https://ollama.com/library/qwen2.5)
