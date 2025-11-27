# Haitham Voice Agent (HVA)

A voice-operated automation agent for macOS with hybrid LLM routing, Gmail integration, and advanced memory system.

## Features

- 🎤 **Voice Control**: Arabic and English voice commands
- 🤖 **Hybrid LLM**: Gemini for analysis, GPT for actions
- 📧 **Gmail Integration**: Read, draft, and manage emails with API/IMAP fallback
- 🧠 **Advanced Memory**: Knowledge graph with semantic search
- 📁 **File Operations**: Safe file and folder management
- 📄 **Document Processing**: Summarize, translate, and extract from PDFs
- 🔒 **Security First**: No auto-send, confirmation required, encrypted credentials

## Installation

### Prerequisites

- macOS (Apple Silicon recommended)
- Python 3.11+
- OpenAI API key
- Google Gemini API key

### Setup

1. **Clone the repository**:
   ```bash
   cd "/Users/haitham/development/Haitham Voice Agent (HVA)"
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Test configuration**:
   ```bash
   python -m haitham_voice_agent.config
   ```

## Usage

### Interactive Mode

Run HVA in continuous listening mode:

```bash
python -m haitham_voice_agent.main
```

### Test Mode

Test with a text command (no voice):

```bash
python -m haitham_voice_agent.main --test "List files in Downloads"
```

### Voice Commands

**Arabic Examples:**
- "اقرأ آخر إيميل" (Read latest email)
- "احفظ هذه الفكرة للمشروع Mind-Q" (Save this idea for Mind-Q project)
- "لخص هذا الملف" (Summarize this file)

**English Examples:**
- "Read my latest emails"
- "Create a draft email to John"
- "Search for files about project X"

## Architecture

```
Voice Input → STT → LLM Router → Execution Plan → 
User Confirmation → Dispatcher → Tools → TTS Response
```

### LLM Routing

- **Gemini**: PDFs, translation, summarization, image analysis
- **GPT**: JSON outputs, execution plans, tool invocation, memory operations

## Project Structure

```
haitham_voice_agent/
├── main.py              # Main orchestrator
├── config.py            # Configuration management
├── stt.py               # Speech-to-Text
├── tts.py               # Text-to-Speech
├── llm_router.py        # Hybrid LLM routing
├── dispatcher.py        # Tool dispatcher
└── tools/
    ├── files.py         # File operations
    ├── docs.py          # Document processing
    ├── browser.py       # Browser tools
    ├── terminal.py      # Safe terminal
    ├── gmail/           # Gmail module
    └── memory/          # Memory module
```

## Development Status

- ✅ **Phase 1**: Core infrastructure (STT, TTS, LLM router, dispatcher)
- 🚧 **Phase 2**: Basic tools (files, docs, browser, terminal)
- 🚧 **Phase 3**: Gmail module (API + IMAP fallback)
- 🚧 **Phase 4**: Memory module (knowledge graph + semantic search)
- 🚧 **Phase 5**: Integration and testing

## Security

- ✅ No auto-send of emails without confirmation
- ✅ Credentials encrypted in macOS Keychain
- ✅ Safe terminal commands only (no sudo)
- ✅ Confirmation required for destructive operations

## Testing

Run tests:

```bash
pytest tests/ -v
```

## Documentation

- [Architecture Analysis](/.gemini/antigravity/brain/94c9a49c-1d61-4c52-a2ce-bbc3f61c672e/architecture_analysis.md)
- [Implementation Plan](/.gemini/antigravity/brain/94c9a49c-1d61-4c52-a2ce-bbc3f61c672e/implementation_plan.md)
- [Master SRS](hva_full_srs.md)
- [Gmail Module SRS](HVA_Gmail_Module_SRS_v1.0.md)
- [Memory Module SRS](HVA_Advanced_Memory_System_Module_SRS.md)

## License

Private project - All rights reserved

## Author

Haitham - 2025
