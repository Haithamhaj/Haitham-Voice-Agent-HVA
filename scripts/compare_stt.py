#!/usr/bin/env python3
"""
STT Comparison Tool
Compare Whisper API, Google Cloud STT, and Wav2Vec2 for Arabic accuracy
"""

import asyncio
import os
from pathlib import Path
import wave
import json

# Test audio file path (you'll need to record a test command)
TEST_AUDIO_PATH = Path("~/test_audio.wav").expanduser()

async def test_whisper_api(audio_path: Path) -> dict:
    """Test OpenAI Whisper API"""
    try:
        import openai
        from haitham_voice_agent.config import Config
        
        client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        
        with open(audio_path, "rb") as audio_file:
            response = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ar"
            )
        
        return {
            "service": "Whisper API",
            "text": response.text,
            "confidence": "N/A",
            "cost": "$0.006/min",
            "speed": "Fast (2-3s)"
        }
    except Exception as e:
        return {"service": "Whisper API", "error": str(e)}

async def test_google_stt(audio_path: Path) -> dict:
    """Test Google Cloud Speech-to-Text"""
    try:
        from google.cloud import speech
        import google.auth
        
        # Try to get credentials (will use GOOGLE_APPLICATION_CREDENTIALS env var if set)
        try:
            credentials, project = google.auth.default()
            client = speech.SpeechClient(credentials=credentials)
        except google.auth.exceptions.DefaultCredentialsError:
            # If no credentials, try without (will fail but give clear error)
            client = speech.SpeechClient()
        
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="ar-SA",
            enable_automatic_punctuation=True,
        )
        
        response = client.recognize(config=config, audio=audio)
        
        if response.results:
            result = response.results[0]
            alternative = result.alternatives[0]
            return {
                "service": "Google Cloud STT",
                "text": alternative.transcript,
                "confidence": f"{alternative.confidence:.2f}",
                "cost": "$0.006/15s",
                "speed": "Fast (1-2s)"
            }
        else:
            return {"service": "Google Cloud STT", "error": "No results"}
            
    except Exception as e:
        return {"service": "Google Cloud STT", "error": str(e)}

async def test_wav2vec2(audio_path: Path) -> dict:
    """Test current Wav2Vec2 Arabic model"""
    try:
        from haitham_voice_agent.tools.stt_wav2vec2_ar import transcribe_arabic_wav2vec2
        
        # Read audio file
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        
        # Get duration
        with wave.open(str(audio_path), 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            duration = frames / float(rate)
        
        text, conf = transcribe_arabic_wav2vec2(audio_bytes, duration)
        
        return {
            "service": "Wav2Vec2 (Local)",
            "text": text,
            "confidence": f"{conf:.2f}",
            "cost": "Free",
            "speed": "Medium (3-5s)"
        }
    except Exception as e:
        return {"service": "Wav2Vec2 (Local)", "error": str(e)}

async def main():
    print("=" * 60)
    print("STT COMPARISON TOOL - Arabic Command Recognition")
    print("=" * 60)
    
    if not TEST_AUDIO_PATH.exists():
        print(f"\n❌ Test audio file not found: {TEST_AUDIO_PATH}")
        print("\nTo create a test file:")
        print("1. Record yourself saying: 'افتح ملف باسم العمل في مجلد هيثم'")
        print("2. Save as WAV file (16kHz, mono)")
        print(f"3. Place at: {TEST_AUDIO_PATH}")
        return
    
    print(f"\n📁 Test audio: {TEST_AUDIO_PATH}")
    print(f"📏 File size: {TEST_AUDIO_PATH.stat().st_size / 1024:.1f} KB")
    
    print("\n" + "=" * 60)
    print("TESTING...")
    print("=" * 60)
    
    # Run all tests
    results = await asyncio.gather(
        test_wav2vec2(TEST_AUDIO_PATH),
        test_whisper_api(TEST_AUDIO_PATH),
        test_google_stt(TEST_AUDIO_PATH),
        return_exceptions=True
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    for result in results:
        if isinstance(result, Exception):
            print(f"\n❌ Error: {result}")
            continue
            
        print(f"\n🔹 {result['service']}")
        print(f"   Cost: {result.get('cost', 'N/A')}")
        print(f"   Speed: {result.get('speed', 'N/A')}")
        
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Text: {result.get('text', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("COMPARISON COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
