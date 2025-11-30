"""
Whisper Arabic Backend (Local)
Provides local Arabic transcription using faster-whisper large-v3
Optimized for long sessions (meetings, notes, etc.)
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def transcribe_arabic_whisper(audio_bytes: bytes, duration_seconds: float) -> Tuple[str, float]:
    """
    Transcribe Arabic audio using local Whisper large-v3
    
    Args:
        audio_bytes: Raw audio data (WAV format)
        duration_seconds: Duration of audio in seconds
        
    Returns:
        Tuple of (transcribed_text, confidence_score)
    """
    try:
        from faster_whisper import WhisperModel
        from haitham_voice_agent.tools.voice.stt import WHISPER_MODELS, init_whisper_models
        import io
        import tempfile
        
        # Ensure Whisper models are loaded
        if not WHISPER_MODELS.get("session"):
            logger.info("Initializing Whisper models...")
            init_whisper_models()
        
        model = WHISPER_MODELS.get("session")
        if not model:
            logger.error("Whisper session model not available")
            return "", 0.0
        
        # Save audio to temp file (faster-whisper needs file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        logger.info(f"Transcribing {duration_seconds:.1f}s of Arabic audio with Whisper large-v3...")
        
        # Transcribe with Arabic language hint
        segments, info = model.transcribe(
            tmp_path,
            language="ar",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        
        # Collect all segments
        text_parts = []
        total_confidence = 0.0
        segment_count = 0
        
        for segment in segments:
            text_parts.append(segment.text)
            # faster-whisper doesn't provide per-segment confidence
            # We'll use a heuristic based on no_speech_prob
            segment_count += 1
        
        text = " ".join(text_parts).strip()
        
        # Estimate confidence (Whisper doesn't provide direct confidence)
        # Use language detection confidence as proxy
        confidence = info.language_probability if hasattr(info, 'language_probability') else 0.85
        
        # Clean up temp file
        import os
        try:
            os.unlink(tmp_path)
        except:
            pass
        
        logger.info(f"Whisper result: '{text[:100]}...' (estimated conf: {confidence:.2f})")
        
        return text, confidence
        
    except ImportError:
        logger.error("faster-whisper not installed. Run: pip install faster-whisper")
        return "", 0.0
    except Exception as e:
        logger.error(f"Whisper Arabic transcription failed: {e}")
        return "", 0.0

if __name__ == "__main__":
    # Test
    print("Whisper Arabic Backend - Test Mode")
    print("Note: Requires faster-whisper and Whisper models")
