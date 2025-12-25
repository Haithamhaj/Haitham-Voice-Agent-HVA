# Redaction Rules Proposal

## 1. AI Boilerplate
Regex: `((As|I am|I'm) an AI (language model|assistant)[^.]*\.)`
Action: Remove sentence.

## 2. Tool Artifacts
Regex: `(GPT-4o returned|DALL-E returned|Tool output):?.*`
Action: Remove line/segment.
