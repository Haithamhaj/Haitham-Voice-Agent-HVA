# Running the Haitham Voice Agent

## Prerequisites

1. **API Keys** (in `.env`):
   ```bash
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=AIza...
   ```

2. **Dependencies**:
   ```bash
   # Install portaudio first (required for pyaudio)
   brew install portaudio
   
   # Then install Python packages
   pip install SpeechRecognition pyaudio aiosqlite chromadb google-generativeai openai
   ```

3. **macOS** (for TTS using `say` command)

---

## Running Modes

### 1. Interactive Voice Mode
```bash
python3 -m haitham_voice_agent.main
```

**Flow:**
1. HVA says: "مرحباً، أنا HVA جاهز للمساعدة"
2. You speak a command
3. HVA generates a plan and asks for confirmation
4. You say "نعم" to confirm
5. HVA executes and speaks the result

**Example Commands:**
- Arabic: "احفظ ملاحظة عن اجتماع اليوم"
- Arabic: "ابحث عن Mind-Q"
- Arabic: "اجلب آخر إيميل"

### 2. Test Mode (No Voice)
```bash
python3 -m haitham_voice_agent.main --test "احفظ ملاحظة عن اجتماع اليوم"
```

This processes a text command without voice I/O (useful for testing).

---

## System Architecture

```
User Voice Input
      ↓
   [STT] → Transcribe to text
      ↓
[LLM Router] → Generate execution plan (JSON)
      ↓
   [TTS] → Speak plan for confirmation
      ↓
   [STT] → Listen for "Yes"
      ↓
[Dispatcher] → Execute tool (Memory/Gmail)
      ↓
   [TTS] → Speak result
```

---

## Supported Commands

### Memory Commands
- **Save Note**: "احفظ ملاحظة عن [topic]"
- **Search**: "ابحث عن [query]"

### Gmail Commands
- **Fetch Email**: "اجلب آخر إيميل"
- **Send Email**: (Coming soon)

---

## Troubleshooting

### Microphone Not Working
```bash
# Test microphone
python3 -c "import speech_recognition as sr; r = sr.Recognizer(); print(sr.Microphone.list_microphone_names())"
```

### TTS Not Working
```bash
# Test macOS say command
say -v Majed "مرحبا"
```

### API Errors
- Check `.env` file has valid keys
- Ensure keys don't have extra spaces or quotes

---

## Next Steps

1. Add more Gmail commands (send, draft, search)
2. Add calendar integration
3. Add web search
4. Improve Arabic NLU
5. Add conversation context/memory
