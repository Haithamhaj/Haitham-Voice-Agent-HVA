import logging
import io
import soundfile as sf
import numpy as np
from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.voice.stt import WHISPER_MODELS, init_whisper_models

logger = logging.getLogger(__name__)

def detect_language_whisper(audio_bytes: bytes, total_duration: float) -> tuple[str, float]:
    """
    Uses the existing faster-whisper model ONLY to detect language.
    Returns (language_code, confidence).
    
    Language codes: "en", "ar", "unknown"
    """
    # Ensure models are loaded
    if not WHISPER_MODELS["realtime"]:
        init_whisper_models()
        
    model = WHISPER_MODELS["realtime"]
    if not model:
        logger.error("Whisper model not available for language detection")
        return "unknown", 0.0

    try:
        # Prepare audio
        # We only need the first few seconds as per config
        max_seconds = Config.STT_ROUTER_CONFIG["lang_detect"]["max_seconds"]
        
        # Convert bytes to numpy array
        wav_buf = io.BytesIO(audio_bytes)
        audio_data, sample_rate = sf.read(wav_buf)
        
        # If stereo, convert to mono
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
            
        # Trim to max_seconds
        max_samples = int(max_seconds * sample_rate)
        if len(audio_data) > max_samples:
            audio_data = audio_data[:max_samples]
            
        # Detect language
        # faster-whisper's detect_language returns (probabilities, language_info)? 
        # Actually model.detect_language returns (probs, info) is not quite right.
        # model.detect_language(audio) returns (probabilities_list, language_token_ids)?
        # Let's check faster-whisper API or use transcribe with task="transcribe" and check info.language
        
        # Using transcribe is safer as it handles preprocessing
        segments, info = model.transcribe(
            audio_data, 
            beam_size=1,
            vad_filter=True
        )
        
        # We don't need to iterate segments, info contains the detected language
        detected_lang = info.language
        confidence = info.language_probability
        
        logger.info(f"Language detected: {detected_lang} (conf={confidence:.2f})")
        
        # Map to our codes
        if detected_lang == "en":
            return "en", confidence
        elif detected_lang == "ar":
            return "ar", confidence
        else:
            # Treat other languages as unknown or maybe map to closest?
            # For now, return unknown if not en/ar, or maybe just return the code?
            # The prompt says: Map Whisper’s language code to "en", "ar", or "unknown".
            return "unknown", confidence

    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        return "unknown", 0.0
