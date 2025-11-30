"""
Google Cloud Speech-to-Text Backend
Provides high-accuracy Arabic transcription using Google Cloud STT API
"""

import logging
from typing import Tuple
import io

logger = logging.getLogger(__name__)

def transcribe_arabic_google(audio_bytes: bytes, duration_seconds: float) -> Tuple[str, float]:
    """
    Transcribe Arabic audio using Google Cloud Speech-to-Text
    
    Args:
        audio_bytes: Raw audio data (WAV format, 16kHz, mono)
        duration_seconds: Duration of audio in seconds
        
    Returns:
        Tuple of (transcribed_text, confidence_score)
    """
    try:
        from google.cloud import speech
        import google.auth
        
        # Initialize client with credentials
        try:
            credentials, project = google.auth.default()
            client = speech.SpeechClient(credentials=credentials)
        except google.auth.exceptions.DefaultCredentialsError:
            logger.error("Google Cloud credentials not found. Run: gcloud auth application-default login")
            return "", 0.0
        
        # Detect sample rate from audio
        # The audio_bytes should be WAV format with header
        import wave
        import io
        
        try:
            with wave.open(io.BytesIO(audio_bytes), 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
        except Exception as e:
            logger.warning(f"Could not detect sample rate from audio: {e}. Using default 16000Hz")
            sample_rate = 16000
            channels = 1
        
        logger.info(f"Detected audio: {sample_rate}Hz, {channels} channel(s)")
        
        # Configure recognition
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,  # Use detected sample rate
            language_code="ar-SA",  # Saudi Arabic
            alternative_language_codes=["en-US"],  # Support mixed English/Arabic
            enable_automatic_punctuation=True,
            model="default",  # Use default model for best accuracy
            use_enhanced=True,  # Use enhanced model if available
            audio_channel_count=channels,
        )
        
        logger.info(f"Transcribing {duration_seconds:.1f}s of Arabic audio with Google Cloud STT...")
        
        # Perform recognition
        response = client.recognize(config=config, audio=audio)
        
        if not response.results:
            logger.warning("Google STT returned no results")
            return "", 0.0
        
        # Get best result
        result = response.results[0]
        alternative = result.alternatives[0]
        
        text = alternative.transcript
        confidence = alternative.confidence
        
        logger.info(f"Google STT result: '{text}' (confidence: {confidence:.2f})")
        
        return text, confidence
        
    except ImportError:
        logger.error("google-cloud-speech not installed. Run: pip install google-cloud-speech")
        return "", 0.0
    except Exception as e:
        logger.error(f"Google STT failed: {e}")
        return "", 0.0

if __name__ == "__main__":
    # Test
    print("Google Cloud STT Backend - Test Mode")
    print("Note: Requires valid Google Cloud credentials")
