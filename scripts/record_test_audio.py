#!/usr/bin/env python3
"""
Quick Audio Recorder for STT Testing
Records 5 seconds of audio for testing
"""

import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from pathlib import Path

SAMPLE_RATE = 16000
DURATION = 5  # seconds
OUTPUT_FILE = Path.home() / "test_audio.wav"

print("=" * 60)
print("AUDIO RECORDER FOR STT TESTING")
print("=" * 60)
print(f"\n📝 Say: 'افتح ملف باسم العمل في مجلد هيثم'")
print(f"⏱️  Recording will start in 2 seconds...")
print(f"🎤 Duration: {DURATION} seconds")
print(f"💾 Output: {OUTPUT_FILE}")
print("\n" + "=" * 60)

import time
time.sleep(2)

print("\n🔴 RECORDING...")
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
sd.wait()
print("✅ Recording complete!")

# Save as WAV
wav.write(str(OUTPUT_FILE), SAMPLE_RATE, audio)
print(f"💾 Saved to: {OUTPUT_FILE}")
print(f"📏 File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")

print("\n" + "=" * 60)
print("READY TO TEST!")
print("=" * 60)
print("\nRun comparison:")
print("  python scripts/compare_stt.py")
