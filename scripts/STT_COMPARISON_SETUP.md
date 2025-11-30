# STT Comparison Tool - Setup Instructions

## Quick Start

### 1. Install Dependencies ✅
```bash
pip install google-cloud-speech
```

### 2. Set Up Google Cloud STT (Optional)

#### Option A: Use Application Default Credentials (Recommended)
```bash
gcloud auth application-default login
```

#### Option B: Use Service Account Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Cloud Speech-to-Text API"
4. Create a service account key (JSON)
5. Set environment variable:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
```

### 3. Record Test Audio

Record yourself saying: **"افتح ملف باسم العمل في مجلد هيثم"**

#### Using macOS:
```bash
# Record 5 seconds of audio
sox -d -r 16000 -c 1 ~/test_audio.wav trim 0 5
```

#### Or use QuickTime:
1. Open QuickTime Player
2. File → New Audio Recording
3. Record your command
4. Export as: `~/test_audio.wav`
5. Convert to 16kHz mono:
```bash
ffmpeg -i ~/test_audio.wav -ar 16000 -ac 1 ~/test_audio_converted.wav
mv ~/test_audio_converted.wav ~/test_audio.wav
```

### 4. Run Comparison

```bash
cd /Users/haitham/development/Haitham\ Voice\ Agent\ \(HVA\)
source .venv/bin/activate
python scripts/compare_stt.py
```

## Expected Output

```
============================================================
STT COMPARISON TOOL - Arabic Command Recognition
============================================================

📁 Test audio: /Users/haitham/test_audio.wav
📏 File size: 45.2 KB

============================================================
TESTING...
============================================================

============================================================
RESULTS
============================================================

🔹 Wav2Vec2 (Local)
   Cost: Free
   Speed: Medium (3-5s)
   Confidence: 0.96
   Text: إفتح ملف بأسم العمل داف ا مجلد هيثا

🔹 Whisper API
   Cost: $0.006/min
   Speed: Fast (2-3s)
   Confidence: N/A
   Text: افتح ملف باسم العمل في مجلد هيثم

🔹 Google Cloud STT
   Cost: $0.006/15s
   Speed: Fast (1-2s)
   Confidence: 0.98
   Text: افتح ملف باسم العمل في مجلد هيثم

============================================================
COMPARISON COMPLETE
============================================================
```

## Notes

- **Whisper API** requires `OPENAI_API_KEY` in `.env`
- **Google Cloud STT** requires credentials setup (see above)
- **Wav2Vec2** works offline, no setup needed

## Cost Comparison

| Service | Cost | Speed | Accuracy (Arabic) |
|---------|------|-------|-------------------|
| Wav2Vec2 | Free | 3-5s | 70-80% |
| Whisper API | $0.006/min | 2-3s | 75-85% |
| Google STT | $0.006/15s | 1-2s | 90-95% |
