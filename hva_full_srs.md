# Haitham Voice Agent (HVA) – Full Integrated SRS

A complete, unified Software Requirements Specification combining:
- Voice Agent Core
- Hybrid LLM Routing (Gemini + GPT)
- File/Folder Tools
- Document Tools
- Browser Tools
- Terminal Tools (Safe Mode)
- Gmail Module
- Advanced Memory System (Local + Vector + Sheets Sync)
- Execution Plan Framework
- Error Handling
- Architecture
- Constraints

---

## 1. Introduction
**Purpose:** Define all requirements for building the Haitham Voice Agent (HVA), a macOS-based voice-operated automation agent with persistent memory and Gmail integration.

**Platform:** macOS (Apple Silicon)

**Technologies:** Python, Gemini API, OpenAI API, AppleScript, Google Sheets API, SQLite/JSON/Vector DB.

**Core Objectives:**
- Voice to action automation
- Hybrid LLM routing
- Structured execution plans
- Local-first external memory
- Gmail reading, drafting, and classification
- Safe macOS automation

---

## 2. System Overview

### 2.1 High-Level Flow
```
User Voice
 → STT
 → LLM Router (Gemini vs GPT)
 → Execution Plan
 → User Confirmation
 → Dispatcher
 → Tools Layer
 → Local Memory / Gmail / File Operations
 → macOS TTS
 → User
```

### 2.2 Core Principles
- Plan-first execution
- Safety-first operations
- Hybrid LLM routing
- Persistent memory
- Clear capability boundaries
- Modular design

---

## 3. Functional Requirements

### 3.1 Voice System
#### FR-V1 STT
- Arabic (ar-SA) and English (en-US)
- Noise tolerant

#### FR-V2 TTS
- macOS `say`
- Voices: "Majed" (AR), "Samantha/Alex" (EN)
- Respond in detected language

---

### 3.2 LLM Routing
#### FR-L1 Gemini for:
- PDFs, translations, comparisons
- Task extraction
- Large-context reasoning
- Image analysis

#### FR-L2 GPT for:
- JSON outputs
- Execution plans
- Tool invocation
- Memory operations
- Email and system tasks

#### FR-L3 Routing Rules
- Analytical → Gemini
- Tool/action → GPT
- Ambiguous → ask user

---

### 3.3 Execution Plan
#### FR-P1 Structure
```
{
  "intent": "...",
  "steps": [...],
  "tools": [...],
  "risks": [...],
  "requires_confirmation": true
}
```

#### FR-P2 Mandatory Confirmation
- No execution without explicit yes

#### FR-P3 Cancel on unclear intent

---

### 3.4 Tools – File & Folder
- list_files
- search_files
- open_folder
- create_folder
- delete_folder (confirmation required)
- move_file
- copy_file
- rename_file
- sort_files

---

### 3.5 Tools – Document Processing (Gemini)
- summarize_file
- translate_file
- compare_files
- extract_tasks
- read_pdf

---

### 3.6 Tools – Browser
- open_url
- search_google

---

### 3.7 Tools – Terminal (Safe Mode)
Allowed commands:
```
ls
pwd
echo
whoami
df
```
No sudo or destructive commands.

---

## 3.8 Gmail Module (Full)
### 3.8.1 Gmail Reading
- fetch_latest_email
- fetch_email_by_query
- fetch_email_thread

### 3.8.2 Gmail Drafting
- create_draft
- reply_to_email
- forward_email

### 3.8.3 Gmail Classification
- summarize_email (Gemini)
- extract_tasks_from_email
- categorize_email

### 3.8.4 Constraints
- Never auto-send emails
- Draft-only mode
- OAuth required

### 3.8.5 Error Handling
```
{
  "error": true,
  "reason": "...",
  "suggestion": "..."
}
```

---

## 3.9 Memory System (Advanced)

### 3.9.1 Purpose
Store persistent knowledge: ideas, decisions, tasks, project insights, and AI conversation excerpts.

### 3.9.2 Data Model
```
id (UUID)
timestamp
source (Voice/Chat/Manual)
project
topic
type (idea, decision, question, task, note)
summary
details
decisions
next_actions
tags
raw_ref
```

### 3.9.3 Local Canonical Store
- SQLite DB (preferred)
- JSON fallback
- Path: ~/.hva_memory.*

### 3.9.4 Vector DB (Semantic Memory)
- FAISS or Chroma
- Local embeddings
- semantic_query_local

### 3.9.5 Memory Tools
- save_note_local
- get_notes_local
- list_recent_memories_local
- semantic_query_local

### 3.9.6 Google Sheets Sync (Optional)
- save_note_sheet
- query_memory_sheet
- list_recent_memories_sheet
- Sheets is secondary, not canonical

---

## 4. Non-Functional Requirements
### 4.1 Security
- No dangerous terminal commands
- No email auto-send
- No password/keychain access
- Confirm all destructive actions

### 4.2 Performance
- STT < 1.5s
- GPT plan generation < 3s
- Gemini PDF tasks < 10s

### 4.3 Reliability
- No crashes
- Always structured errors

### 4.4 Maintainability
- Modular tool structure
- Config-driven models

---

## 5. Implementation Constraints
- Python 3.11+
- macOS Apple Silicon
- Required ENV variables: OPENAI_API_KEY, GEMINI_API_KEY, SHEETS_CREDS

### Directory Structure
```
hva/
  main.py
  stt.py
  tts.py
  llm_router.py
  dispatcher.py
  config.py
  tools/
    files.py
    docs.py
    terminal.py
    mail.py
    browser.py
    memory_local.py
    memory_sheets.py
  memory/
    embeddings/
  tests/
  requirements.txt
```

---

## 6. Tool Contract
- JSON input/output
- Schema validation
- No system exit
- Safe fallbacks

---

## 7. Error Handling
```
{
  "error": true,
  "reason": "...",
  "suggestion": "..."
}
```

---

## 8. Execution Plan Requirement
- Always required
- Spoken to user
- Must receive explicit confirmation

---

## 9. Out-of-Scope
- GUI automation (mouse/keyboard)
- OS settings
- Keychain/passwords
- Unsafe terminal
- Automatic downloads

---

## 10. Acceptance Criteria
- ≥25 successful voice commands
- Hybrid routing validated
- Memory persistent and queryable
- Gmail drafts working
- Document tools accurate
- Safety rules respected

---

## 11. Builder Instructions
1. Read entire SRS
2. Produce implementation plan
3. Await approval
4. Generate code
5. Stop and warn on conflicts
6. Follow modular design

