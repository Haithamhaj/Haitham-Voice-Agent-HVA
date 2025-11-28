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
            
        # Log available microphones for debugging
        try:
            mics = sr.Microphone.list_microphone_names()
            logger.info(f"Available Microphones: {mics}")
            # Note: sr.Microphone() uses the system default device.
            # To change it, one would need to pass device_index to sr.Microphone(device_index=...)
        except Exception as e:
            logger.warning(f"Could not list microphones: {e}")
            
    def capture_audio(self) -> Optional[tuple[bytes, float]]:
        """
        Captures audio from the microphone until silence is detected.
        Returns (audio_bytes, duration_seconds) or None if capture failed.
        """
        try:
            with sr.Microphone() as source:
                # Configure VAD settings from config
                _recognizer.pause_threshold = Config.VOICE_VAD_CONFIG.get("pause_threshold", 1.0)
                _recognizer.energy_threshold = Config.VOICE_VAD_CONFIG.get("energy_threshold", 300)
                _recognizer.dynamic_energy_threshold = Config.VOICE_VAD_CONFIG.get("dynamic_energy_threshold", True)

                logger.info("Listening (VAD)...")
                # Adjust for ambient noise briefly
                _recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = _recognizer.listen(source)
                logger.info("Audio captured.")

            # Calculate duration
            wav_bytes = audio.get_wav_data()
            duration = len(wav_bytes) / (audio.sample_width * audio.sample_rate)
            
            return wav_bytes, duration
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return None
        except Exception as e:
            logger.error(f"Audio capture error: {e}", exc_info=True)
            return None

    def listen_realtime(self, language: Optional[str] = None) -> Optional[dict]:
        """
        Command Mode STT:
        - Uses speech_recognition + Microphone for VAD
        - Transcribes using local Whisper 'realtime' model
        
        Args:
            language: "ar", "en", or None (auto-detect)
            
        Returns:
            dict: {
                "text": str, 
                "duration": float, 
                "confidence": float
            } or None if filtered out
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
                _recognizer.pause_threshold = Config.VOICE_VAD_CONFIG.get("pause_threshold", 1.0)
                _recognizer.energy_threshold = Config.VOICE_VAD_CONFIG.get("energy_threshold", 300)
                _recognizer.dynamic_energy_threshold = Config.VOICE_VAD_CONFIG.get("dynamic_energy_threshold", True)

                logger.info("Listening (Local Whisper)...")
                # Adjust for ambient noise briefly
                _recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = _recognizer.listen(source)
                logger.info("Audio captured, transcribing...")

            # Calculate duration roughly
            # AudioData.get_wav_data() returns bytes. 
            # WAV is usually 16-bit (2 bytes) * sample_rate * channels
            # sr defaults: 16-bit, mono, 44100Hz usually, but let's check audio.sample_rate
            # Duration = len(bytes) / (sample_width * sample_rate)
            wav_bytes = audio.get_wav_data()
            duration = len(wav_bytes) / (audio.sample_width * audio.sample_rate)
            logger.info(f"Audio duration: {duration:.2f}s")
            
            # Convert to file-like object
            wav_buf = io.BytesIO(wav_bytes)
            data, samplerate = sf.read(wav_buf)
            
            # Transcribe
            # Force Arabic for robustness as requested
            target_lang = "ar"
            
            segments, info = model.transcribe(
                data, 
                language=target_lang, 
                task="transcribe",
                beam_size=5  # Increased beam size for better quality (large-v3)
            )

            # Collect segments and check confidence
            collected_segments = list(segments)
            text = " ".join(seg.text for seg in collected_segments).strip()
            
            # Calculate average confidence (probability = exp(logprob))
            avg_prob = 0.0
            if collected_segments:
                avg_prob = np.mean([np.exp(seg.avg_logprob) for seg in collected_segments])
            
            logger.info(f"Realtime transcription (lang={target_lang}, conf={avg_prob:.2f}): {text}")

            # Strict Filtering
            strict_config = getattr(Config, "STT_STRICT_CONFIG", {
                "min_confidence": 0.7,
                "min_length": 6,
                "max_realtime_seconds": 10.0
            })
            
            # 1. Check if it's long speech (pass through, but flag it)
            if duration > strict_config["max_realtime_seconds"]:
                logger.info(f"Long speech detected ({duration:.2f}s). Passing as session note.")
                return {
                    "text": text,
                    "duration": duration,
                    "confidence": avg_prob,
                    "is_long_speech": True
                }

            # 2. Garbage Filter for short commands
            if len(text) < strict_config["min_length"]:
                logger.info(f"Ignoring short transcript (< {strict_config['min_length']} chars)")
                return None
                
            if avg_prob < strict_config["min_confidence"]:
                logger.warning(f"Low confidence ({avg_prob:.2f} < {strict_config['min_confidence']}). Ignoring.")
                return None

            if text:
                return {
                    "text": text,
                    "duration": duration,
                    "confidence": avg_prob,
                    "is_long_speech": False
                }
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
