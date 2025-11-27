"""
Speech-to-Text (STT) Module

Handles voice input using macOS Speech Recognition APIs.
Supports Arabic (ar-SA) and English (en-US) with automatic language detection.
"""

import asyncio
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
import logging

from .config import Config

logger = logging.getLogger(__name__)


class STTModule:
    """Speech-to-Text using macOS APIs"""
    
    def __init__(self):
        self.supported_languages = {
            "ar": Config.STT_LANGUAGE_AR,
            "en": Config.STT_LANGUAGE_EN
        }
        self.current_language = "ar"  # Default to Arabic
    
    async def listen(self, duration: int = 5, language: Optional[str] = None) -> bytes:
        """
        Listen for voice input and capture audio
        
        Args:
            duration: Recording duration in seconds
            language: Language code ('ar' or 'en'), auto-detect if None
            
        Returns:
            bytes: Raw audio data
        """
        logger.info(f"Listening for {duration} seconds...")
        
        # Create temporary file for audio
        temp_audio = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp_audio.name
        temp_audio.close()
        
        try:
            # Record audio using macOS 'rec' command (via sox) or afplay
            # Note: macOS doesn't have built-in command-line recording
            # We'll use a simple approach with subprocess
            
            # For now, we'll use a placeholder that simulates recording
            # In production, you'd use PyAudio or similar
            logger.warning("Audio recording not fully implemented - using placeholder")
            
            # Simulate audio data
            audio_data = b"placeholder_audio_data"
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to record audio: {e}")
            raise
        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Raw audio bytes
            language: Language code ('ar' or 'en'), auto-detect if None
            
        Returns:
            str: Transcribed text
        """
        if language is None:
            language = self.current_language
        
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        
        locale = self.supported_languages[language]
        logger.info(f"Transcribing audio in {locale}...")
        
        try:
            # In production, use macOS Speech Recognition or OpenAI Whisper
            # For now, placeholder implementation
            
            # Option 1: Use OpenAI Whisper API
            # from openai import OpenAI
            # client = OpenAI(api_key=Config.OPENAI_API_KEY)
            # response = client.audio.transcriptions.create(
            #     model="whisper-1",
            #     file=audio_data,
            #     language=language
            # )
            # return response.text
            
            # Placeholder for development
            logger.warning("STT not fully implemented - returning placeholder")
            return "placeholder transcription"
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def listen_and_transcribe(self, duration: int = 5, language: Optional[str] = None) -> str:
        """
        Convenience method: listen and transcribe in one call
        
        Args:
            duration: Recording duration in seconds
            language: Language code ('ar' or 'en')
            
        Returns:
            str: Transcribed text
        """
        audio = await self.listen(duration, language)
        return await self.transcribe(audio, language)
    
    async def listen_for_confirmation(self, timeout: int = 10) -> bool:
        """
        Listen for yes/no confirmation
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            bool: True if confirmed (yes/نعم), False if rejected (no/لا)
        """
        logger.info("Listening for confirmation...")
        
        try:
            text = await self.listen_and_transcribe(duration=timeout)
            text_lower = text.lower().strip()
            
            # Check for affirmative responses
            affirmative = ["yes", "yeah", "yep", "ok", "okay", "نعم", "اه", "ايوه", "تمام"]
            negative = ["no", "nope", "cancel", "لا", "لأ", "إلغاء"]
            
            if any(word in text_lower for word in affirmative):
                logger.info("User confirmed")
                return True
            elif any(word in text_lower for word in negative):
                logger.info("User rejected")
                return False
            else:
                logger.warning(f"Unclear response: {text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to get confirmation: {e}")
            return False
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text (simple heuristic)
        
        Args:
            text: Input text
            
        Returns:
            str: Language code ('ar' or 'en')
        """
        # Simple detection: if text contains Arabic characters, it's Arabic
        arabic_chars = set("ابتثجحخدذرزسشصضطظعغفقكلمنهويىأإآؤئءة")
        
        if any(char in arabic_chars for char in text):
            return "ar"
        else:
            return "en"
    
    def set_language(self, language: str):
        """
        Set the current language for STT
        
        Args:
            language: Language code ('ar' or 'en')
        """
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        
        self.current_language = language
        logger.info(f"STT language set to: {language}")


# Singleton instance
_stt_instance: Optional[STTModule] = None


def get_stt() -> STTModule:
    """Get singleton STT instance"""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = STTModule()
    return _stt_instance


if __name__ == "__main__":
    # Test STT module
    async def test():
        stt = get_stt()
        
        print("Testing STT module...")
        print(f"Supported languages: {stt.supported_languages}")
        
        # Test language detection
        print("\nTesting language detection:")
        print(f"'Hello world' -> {stt.detect_language('Hello world')}")
        print(f"'مرحبا بالعالم' -> {stt.detect_language('مرحبا بالعالم')}")
        
        # Note: Actual audio recording/transcription requires additional setup
        print("\nNote: Full audio recording/transcription requires:")
        print("  - PyAudio or similar for audio capture")
        print("  - OpenAI Whisper API or macOS Speech Recognition")
    
    asyncio.run(test())
