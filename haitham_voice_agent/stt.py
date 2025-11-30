"""
Speech-to-Text (STT) Module

Handles voice input and transcription.
Wraps recording and routing logic.
"""

import logging
import tempfile
import os
import wave
import pyaudio
import time
from typing import Optional

from haitham_voice_agent.tools.stt_router import transcribe_command

logger = logging.getLogger(__name__)

def listen_once(duration: int = 8) -> Optional[str]:
    """
    Listen for a single command and transcribe it.
    
    Args:
        duration: Recording duration in seconds (default: 8)
        
    Returns:
        str: Transcribed text or None if failed/empty
    """
    logger.info(f"Listening for {duration} seconds...")
    
    # Audio settings
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    p = pyaudio.PyAudio()
    
    try:
        # Open stream
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        
        frames = []
        
        # Record
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
            
        # Stop stream
        stream.stop_stream()
        stream.close()
        
        # Save to WAV in memory
        import io
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            
        wav_bytes = wav_buffer.getvalue()
        
        # Transcribe
        logger.info(f"Transcribing {len(wav_bytes)} bytes of WAV audio...")
        text = transcribe_command(wav_bytes, duration)
        
        return text
        
    except Exception as e:
        logger.error(f"Error in listen_once: {e}")
        return None
        
    finally:
        p.terminate()

class STTModule:
    """Legacy STT Module class for backward compatibility"""
    def listen_once(self, duration: int = 5) -> Optional[str]:
        return listen_once(duration)

_stt_instance = STTModule()

def get_stt() -> STTModule:
    return _stt_instance
