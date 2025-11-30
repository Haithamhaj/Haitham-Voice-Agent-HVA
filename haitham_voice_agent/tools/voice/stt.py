"""
Unified Speech-to-Text (STT) Engine
The Single Source of Truth for HVA's "Ears".

Routing Logic (The Golden Rule):
1. Short Commands (Realtime):
   - English -> Whisper (Local)
   - Arabic -> Google Cloud STT (Best Accuracy)
2. Long Sessions:
   - English -> Whisper (Local)
   - Arabic -> Whisper Large-v3 (Local, Best for Context)
"""

import logging
import speech_recognition as sr
import re
from typing import Optional, Tuple

from haitham_voice_agent.config import Config

# Import the specialized engines (now located in tools/voice/)
from haitham_voice_agent.tools.voice.stt_langid import detect_language_whisper
from haitham_voice_agent.tools.voice.stt_whisper_en import transcribe_english_whisper
from haitham_voice_agent.tools.voice.stt_google import transcribe_arabic_google
from haitham_voice_agent.tools.voice.stt_whisper_ar import transcribe_arabic_whisper

logger = logging.getLogger(__name__)

# Initialize Recognizer for VAD
_recognizer = sr.Recognizer()

ARABIC_CHARS_RE = re.compile(r"[\u0600-\u06FF]")

def count_arabic_chars(text: str) -> int:
    """Count number of Arabic characters in text."""
    return len(ARABIC_CHARS_RE.findall(text or ""))

def _validate_arabic_transcript(text: str, conf: float, config: dict) -> bool:
    """
    Validate Arabic transcript against config thresholds.
    Returns True if valid, False otherwise.
    """
    text = (text or "").strip()
    conf = float(conf or 0.0)
    arabic_len = len(text)
    arabic_chars = count_arabic_chars(text)
    
    min_chars = config.get("min_valid_chars", 6)
    min_conf = config.get("min_confidence", 0.7)
    require_ar = config.get("require_arabic_chars", True)
    log_rej = config.get("log_rejections", False)
    
    valid = True
    rejection_reason = ""
    
    if not text or arabic_len < min_chars:
        valid = False
        rejection_reason = f"length {arabic_len} < {min_chars}"
        
    elif require_ar and arabic_chars < max(2, arabic_len // 3):
        # require at least some Arabic letters (heuristic: at least 2 or 1/3rd of text)
        valid = False
        rejection_reason = f"insufficient arabic chars ({arabic_chars}/{arabic_len})"
        
    elif conf < min_conf:
        valid = False
        rejection_reason = f"confidence {conf:.2f} < {min_conf}"
        
    if not valid:
        if log_rej:
            logger.warning(
                "Arabic STT rejected: text=%r conf=%.2f reason=%s",
                text, conf, rejection_reason
            )
        return False
        
    logger.info(
        "Arabic STT accepted: text=%r conf=%.2f len=%d arabic_chars=%d",
        text, conf, arabic_len, arabic_chars
    )
    return True

class STTHandler:
    """
    Unified STT Handler.
    Replaces old LocalSTT and stt_router.
    """
    
    def __init__(self):
        # Log available microphones for debugging
        try:
            mics = sr.Microphone.list_microphone_names()
            logger.info(f"Available Microphones: {mics}")
        except Exception as e:
            logger.warning(f"Could not list microphones: {e}")

    def capture_audio(self) -> Optional[tuple[bytes, float]]:
        """
        Captures audio from the microphone until silence is detected (VAD).
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

    def listen_realtime(self) -> Optional[str]:
        """
        Main entry point for Command Mode.
        Captures audio -> Detects Language -> Routes to correct engine.
        Returns: Transcript string or None.
        """
        capture = self.capture_audio()
        if not capture:
            return None
            
        audio_bytes, duration = capture
        
        # Check for long speech (treat as session note?)
        # For now, we just route it. If it's very long, the router might handle it or we can flag it.
        # But the user asked for strict routing based on "Short Commands" vs "Long Sessions".
        # Usually "listen_realtime" implies short command intent.
        
        return self.transcribe_command(audio_bytes, duration)

    def transcribe_command(self, audio_bytes: bytes, duration_seconds: float) -> Optional[str]:
        """
        Routes short commands based on language.
        """
        config = Config.STT_ROUTER_CONFIG
        
        # 1. Detect Language
        lang, lang_conf = detect_language_whisper(audio_bytes, duration_seconds)
        logger.info(f"STT Router: Detected lang={lang} conf={lang_conf:.2f}")
        
        # 2. Route
        # If English and confident
        if lang == "en" and lang_conf >= config["lang_detect"]["min_confidence"]:
            logger.info("Routing to Whisper English Backend")
            text = transcribe_english_whisper(audio_bytes, duration_seconds)
            
            if not text or len(text.strip()) < 2:
                logger.warning("English transcript too short or empty")
                return None
                
            return text
            
        else:
            # Default to Arabic (Google Cloud STT) - The Golden Rule
            logger.info("Routing to Google Cloud STT Arabic Backend")
            text, conf = transcribe_arabic_google(audio_bytes, duration_seconds)
            
            # 3. Validate Arabic
            if _validate_arabic_transcript(text, conf, config["arabic"]):
                return text
                
            return None

    def transcribe_session(self, audio_bytes: bytes, duration_seconds: float) -> Optional[str]:
        """
        Routes long sessions based on language.
        """
        config = Config.STT_ROUTER_CONFIG
        
        # 1. Detect Language
        lang, lang_conf = detect_language_whisper(audio_bytes, duration_seconds)
        logger.info(f"STT Router (Session): Detected lang={lang} conf={lang_conf:.2f}")
        
        # 2. Route
        if lang == "en":
            # Use Whisper English for full session
            logger.info("Session: Using Whisper English")
            text = transcribe_english_whisper(audio_bytes, duration_seconds)
            
            if not text or len(text.strip()) < 5:
                logger.warning("Session transcript empty or too short")
                return None
                
            return text
        else:
            # Use Whisper large-v3 Arabic for full session (local, free, private) - The Golden Rule
            logger.info("Session: Using Whisper large-v3 Arabic (local)")
            text, conf = transcribe_arabic_whisper(audio_bytes, duration_seconds)
            
            # For sessions, we use the same validation logic
            if _validate_arabic_transcript(text, conf, config["arabic"]):
                return text
                
            return None

# For backward compatibility if needed, or just use the class
def init_whisper_models():
    """
    Initialize Whisper models.
    Now delegated to the specific modules if they need it, 
    but we can keep a global init here if main calls it.
    """
    # The new modules (stt_whisper_en, stt_whisper_ar) handle their own model loading lazily or globally.
    # But to prevent latency on first request, we can trigger them here.
    pass 
