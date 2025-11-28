import logging
import re
from typing import Optional, Literal

from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.stt_langid import detect_language_whisper
from haitham_voice_agent.tools.stt_whisper_en import transcribe_english_whisper
from haitham_voice_agent.tools.stt_wav2vec2_ar import transcribe_arabic_wav2vec2

logger = logging.getLogger(__name__)

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
        
        # 3. Validate Arabic
        if _validate_arabic_transcript(text, conf, config["arabic"]):
            return text
            
        return None

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
        
        if not text or len(text.strip()) < 5:
            logger.warning("Session transcript empty or too short")
            return None
            
        return text
    else:
        # Use Wav2Vec2 Arabic for full session
        logger.info("Session: Using Wav2Vec2 Arabic")
        text, conf = transcribe_arabic_wav2vec2(audio_bytes)
        
        # For sessions, we use the same validation logic but maybe we want to be slightly more lenient?
        # The prompt says "Apply the same pattern for transcribe_session".
        # Let's use the same validator.
        if _validate_arabic_transcript(text, conf, config["arabic"]):
            return text
            
        return None
