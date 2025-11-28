"""
Session Recorder

Handles long-form audio recording for meetings and sessions.
Records raw audio to WAV files without immediate transcription.
"""

import os
import time
import threading
import logging
import wave
import pyaudio
from pathlib import Path
from typing import Optional

from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)


class SessionRecorder:
    """
    Records audio sessions to WAV files.
    Thread-safe start/stop control.
    """
    
    def __init__(self):
        self._recording = False
        self._thread: Optional[threading.Thread] = None
        self._output_path: Optional[str] = None
        
        # Audio settings
        self._chunk = 1024
        self._format = pyaudio.paInt16
        self._channels = 1
        self._rate = 16000
        
        self._pyaudio = pyaudio.PyAudio()
        
        # Ensure session directory exists
        Config.VOICE_SESSION_DIR.mkdir(parents=True, exist_ok=True)

    def _record_loop(self, output_path: str):
        """Internal recording loop running in a separate thread"""
        logger.info(f"Recording started: {output_path}")
        
        try:
            stream = self._pyaudio.open(
                format=self._format,
                channels=self._channels,
                rate=self._rate,
                input=True,
                frames_per_buffer=self._chunk
            )
            
            frames = []
            
            while self._recording:
                data = stream.read(self._chunk)
                frames.append(data)
            
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            
            # Save to WAV file
            wf = wave.open(output_path, 'wb')
            wf.setnchannels(self._channels)
            wf.setsampwidth(self._pyaudio.get_sample_size(self._format))
            wf.setframerate(self._rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            logger.info(f"Recording saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Recording error: {e}", exc_info=True)
        finally:
            self._recording = False

    def start(self) -> str:
        """
        Start a new session recording.
        
        Returns:
            str: Path where the audio will be saved
        """
        if self._recording:
            logger.warning("Recording already in progress")
            return self._output_path
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"session_{timestamp}.wav"
        self._output_path = str(Config.VOICE_SESSION_DIR / filename)
        
        self._recording = True
        self._thread = threading.Thread(
            target=self._record_loop,
            args=(self._output_path,)
        )
        self._thread.start()
        
        return self._output_path

    def stop(self) -> Optional[str]:
        """
        Stop the recording and save the file.
        
        Returns:
            str: Path to the saved WAV file
        """
        if not self._recording:
            logger.warning("No recording in progress to stop")
            return None
            
        logger.info("Stopping recording...")
        self._recording = False
        
        if self._thread:
            self._thread.join()
            self._thread = None
            
        return self._output_path
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._recording
