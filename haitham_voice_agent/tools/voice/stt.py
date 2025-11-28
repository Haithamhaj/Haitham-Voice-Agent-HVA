"""
Local Speech-to-Text (STT) Engine

Uses faster-whisper for local transcription.
Supports two modes:
1. Realtime: For interactive commands (using VAD)
2. Session: For long recordings (meetings)
"""

import io
import os
import logging
import speech_recognition as sr
import soundfile as sf
import numpy as np
from typing import Optional, Literal

# Try importing faster_whisper, handle if missing
try:
    from faster_whisper import WhisperModel
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False

from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)

# Global cache for Whisper model instances
# Loaded once at startup to avoid reloading latency
WHISPER_MODELS = {
    "realtime": None,
    "session": None,
}

_recognizer = sr.Recognizer()


def init_whisper_models():
    """
    Initialize and cache Whisper models for realtime and session profiles.
    Must be called ONCE at startup.
    """
    global WHISPER_MODELS
    
    if not HAS_WHISPER:
        logger.error("faster-whisper not installed. Local STT will not work.")
        return

    try:
        for profile in ("realtime", "session"):
            model_name = Config.WHISPER_MODEL_NAMES.get(profile)
            if not model_name:
                logger.warning(f"No Whisper model configured for profile '{profile}'")
                continue

            if WHISPER_MODELS[profile] is None:
                logger.info(f"Loading Whisper model for profile '{profile}': {model_name}")
                
                try:
                    # Attempt to load the configured model
                    WHISPER_MODELS[profile] = WhisperModel(
                        model_name, 
                        device="cpu", 
                        compute_type="int8"
                    )
                    logger.info(f"Whisper model '{profile}' ({model_name}) loaded successfully")
                    
                except Exception as e:
                    # Fallback logic specifically for heavy models
                    if "large" in model_name:
                        logger.warning(f"Failed to load heavy model '{model_name}' for '{profile}'. Error: {e}")
                        logger.info("Attempting fallback to 'medium' model...")
                        try:
                            WHISPER_MODELS[profile] = WhisperModel(
                                "medium", 
                                device="cpu", 
                                compute_type="int8"
                            )
                            logger.info(f"Fallback model 'medium' loaded for '{profile}'")
                        except Exception as fallback_error:
                            logger.error(f"Fallback failed for '{profile}': {fallback_error}")
                    else:
                        logger.error(f"Failed to load model '{model_name}' for '{profile}': {e}")
                
    except Exception as e:
        logger.error(f"Failed to initialize Whisper models: {e}", exc_info=True)


class LocalSTT:
    """Local STT Handler using faster-whisper"""
    
    def __init__(self):
        if not any(WHISPER_MODELS.values()):
            init_whisper_models()
            
    def listen_realtime(self, language: Optional[str] = None) -> Optional[str]:
        """
        Command Mode STT:
        - Uses speech_recognition + Microphone for VAD
        - Transcribes using local Whisper 'realtime' model
        
        Args:
            language: "ar", "en", or None (auto-detect)
            
        Returns:
            str: Transcribed text
        """
        if not HAS_WHISPER:
            logger.error("faster-whisper missing")
            return None
            
        model = WHISPER_MODELS["realtime"]
        if model is None:
            logger.error("Realtime Whisper model not initialized")
            return None

        try:
            with sr.Microphone() as source:
                # Configure VAD settings from config
                _recognizer.pause_threshold = Config.VOICE_VAD_CONFIG.get("pause_threshold", 0.8)
                _recognizer.energy_threshold = Config.VOICE_VAD_CONFIG.get("energy_threshold", 300)
                _recognizer.dynamic_energy_threshold = Config.VOICE_VAD_CONFIG.get("dynamic_energy_threshold", True)

                logger.info("Listening (Local Whisper)...")
                # Adjust for ambient noise briefly
                _recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = _recognizer.listen(source)
                logger.info("Audio captured, transcribing...")

            # Convert AudioData to numpy array for faster-whisper
            wav_bytes = audio.get_wav_data()
            wav_buf = io.BytesIO(wav_bytes)
            data, samplerate = sf.read(wav_buf)
            
            # Transcribe
            # beam_size=1 for speed in realtime mode
            segments, info = model.transcribe(
                data, 
                language=language, 
                beam_size=1
            )

            text = " ".join(seg.text for seg in segments).strip()
            
            if text:
                logger.info(f"Realtime transcription ({info.language}): {text}")
                return text
            return None
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return None
        except Exception as e:
            logger.error(f"Realtime STT error: {e}", exc_info=True)
            return None

    def transcribe_session(self, file_path: str, language: Optional[str] = None) -> str:
        """
        Session Mode STT:
        - Transcribes a full audio file using 'session' model
        
        Args:
            file_path: Path to WAV file
            language: "ar", "en", or None
            
        Returns:
            str: Full transcription
        """
        if not HAS_WHISPER:
            return "Error: faster-whisper not installed"
            
        model = WHISPER_MODELS["session"]
        if model is None:
            # Fallback to realtime model if session model failed to load
            model = WHISPER_MODELS["realtime"]
            if model is None:
                return "Error: No Whisper models initialized"
            logger.warning("Session model missing, falling back to realtime model")

        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return ""

        logger.info(f"Transcribing session file: {file_path}")
        
        try:
            # Transcribe file directly
            # beam_size=5 for better accuracy in session mode
            segments, info = model.transcribe(
                file_path, 
                language=language,
                beam_size=5
            )

            text = " ".join(seg.text for seg in segments).strip()
            logger.info(f"Session transcription complete. Length: {len(text)} chars")
            return text
            
        except Exception as e:
            logger.error(f"Session transcription error: {e}", exc_info=True)
            return f"Error transcribing session: {str(e)}"
