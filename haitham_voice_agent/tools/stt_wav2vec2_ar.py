import logging
import io
import soundfile as sf
import numpy as np
import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from scipy import signal
from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)

# Singleton storage
_W2V2_MODEL = None
_W2V2_PROCESSOR = None

def load_wav2vec2_model():
    """Load the Wav2Vec2 model and processor if not already loaded."""
    global _W2V2_MODEL, _W2V2_PROCESSOR
    
    if _W2V2_MODEL is not None:
        return

    model_name = Config.W2V2_AR_MODEL_NAME
    logger.info(f"Loading Wav2Vec2 model: {model_name}")
    
    try:
        _W2V2_PROCESSOR = Wav2Vec2Processor.from_pretrained(model_name)
        _W2V2_MODEL = Wav2Vec2ForCTC.from_pretrained(model_name)
        logger.info("Wav2Vec2 model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Wav2Vec2 model: {e}")
        raise

def transcribe_arabic_wav2vec2(audio_bytes: bytes, original_sample_rate: int = 16000) -> tuple[str, float]:
    """
    Transcribes Arabic speech using Wav2Vec2.
    Returns (text, confidence_score).
    """
    global _W2V2_MODEL, _W2V2_PROCESSOR
    
    if _W2V2_MODEL is None:
        try:
            load_wav2vec2_model()
        except Exception:
            return "", 0.0

    try:
        # Load audio
        wav_buf = io.BytesIO(audio_bytes)
        audio_input, sample_rate = sf.read(wav_buf)
        
        # Convert to mono if stereo
        if len(audio_input.shape) > 1:
            audio_input = audio_input.mean(axis=1)
            
        # Resample to 16000 Hz if needed
        target_sr = 16000
        if sample_rate != target_sr:
            # Calculate number of samples
            num_samples = int(len(audio_input) * target_sr / sample_rate)
            audio_input = signal.resample(audio_input, num_samples)
            
        # Process
        inputs = _W2V2_PROCESSOR(audio_input, sampling_rate=target_sr, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            logits = _W2V2_MODEL(inputs.input_values).logits

        # Decode
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = _W2V2_PROCESSOR.batch_decode(predicted_ids)[0]
        
        # Calculate confidence
        # Softmax to get probabilities
        probs = torch.nn.functional.softmax(logits, dim=-1)
        
        # Get probabilities of predicted tokens
        # logits shape: [batch, time, vocab]
        # predicted_ids shape: [batch, time]
        
        # We want to gather the prob of the chosen token at each timestep
        # But we should ignore padding/blank tokens for a better score?
        # For simplicity, let's take the mean probability of the max token at each step
        
        token_probs = torch.max(probs, dim=-1).values # [batch, time]
        confidence_score = torch.mean(token_probs).item()
        
        return transcription.strip(), confidence_score

    except Exception as e:
        logger.error(f"Wav2Vec2 transcription failed: {e}")
        return "", 0.0
