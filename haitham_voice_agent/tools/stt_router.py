import logging
import re
from typing import Optional, Literal

from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.stt_langid import detect_language_whisper
from haitham_voice_agent.tools.stt_whisper_en import transcribe_english_whisper
from haitham_voice_agent.tools.stt_wav2vec2_ar import transcribe_arabic_wav2vec2

logger = logging.getLogger(__name__)

def _is_valid_arabic(text: str, min_chars: int, require_arabic: bool) -> bool:
    """Validate Arabic text quality."""
    if not text:
        return False
        
    if len(text.strip()) < min_chars:
        return False
        
    if require_arabic:
        # Check for Arabic characters
        # Unicode range for Arabic: \u0600-\u06FF
        arabic_chars = re.findall(r'[\u0600-\u06FF]', text)
        if not arabic_chars:
            return False
            
    return True

def transcribe_command(audio_bytes: bytes, duration_seconds: float) -> Optional[str]:
    """
    Returns a transcript string for short commands,
    or None if the system could not confidently understand the speech.
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
        # Default to Arabic (Wav2Vec2)
        logger.info("Routing to Wav2Vec2 Arabic Backend")
        text, conf = transcribe_arabic_wav2vec2(audio_bytes)
        
        logger.info(f"Wav2Vec2 Result: '{text}' (conf={conf:.2f})")
        
        # 3. Validate Arabic
        ar_config = config["arabic"]
        if not _is_valid_arabic(text, ar_config["min_valid_chars"], ar_config["require_arabic_chars"]):
            logger.warning("Arabic transcript failed validation (length or chars)")
            return None
            
        if conf < ar_config["min_confidence"]:
            logger.warning(f"Arabic transcript low confidence ({conf:.2f} < {ar_config['min_confidence']})")
            return None
            
        return text

def transcribe_session(audio_bytes: bytes, duration_seconds: float) -> Optional[str]:
    """
    Returns a transcript string for long recordings (sessions),
    or None if transcription fails.
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
    else:
        # Use Wav2Vec2 Arabic for full session
        logger.info("Session: Using Wav2Vec2 Arabic")
        text, conf = transcribe_arabic_wav2vec2(audio_bytes)
        # For sessions, we might be more lenient with confidence, but check empty
        if conf < 0.2: # Very low threshold for sessions just to catch garbage
             logger.warning(f"Session Wav2Vec2 confidence very low: {conf:.2f}")
    
    if not text or len(text.strip()) < 5:
        logger.warning("Session transcript empty or too short")
        return None
        
    return text
