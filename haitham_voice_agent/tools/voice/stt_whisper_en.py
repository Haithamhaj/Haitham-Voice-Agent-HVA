import logging
import io
import soundfile as sf
import numpy as np
from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.voice.stt import WHISPER_MODELS, init_whisper_models

logger = logging.getLogger(__name__)

def transcribe_english_whisper(audio_bytes: bytes, duration_seconds: float) -> str:
    """
    Uses faster-whisper to transcribe English audio.
    """
    # Ensure models are loaded
    if not WHISPER_MODELS["realtime"]:
        init_whisper_models()
        
    # Use 'realtime' model for commands, or maybe check duration?
    # The prompt says "Use an English-optimized faster-whisper model (choose from config; base or medium is fine)".
    # But our config has "realtime": "large-v3".
    # I'll use the 'realtime' model as it's likely already loaded.
    model = WHISPER_MODELS["realtime"]
    
    if not model:
        logger.error("Whisper model not available")
        return ""

    try:
        # Convert bytes to numpy array
        wav_buf = io.BytesIO(audio_bytes)
        audio_data, sample_rate = sf.read(wav_buf)
        
        # If stereo, convert to mono
        if len(audio_data.shape) > 1:
            audio_data = audio_data.mean(axis=1)
            
        # Transcribe
        segments, info = model.transcribe(
            audio_data, 
            language="en", 
            task="transcribe",
            initial_prompt="AI, data, logistics, Haitham, HVA" # Bias for context
        )
        
        text = " ".join(seg.text for seg in segments).strip()
        return text

    except Exception as e:
        logger.error(f"English transcription failed: {e}")
        return ""
