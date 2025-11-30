"""
Text-to-Speech (TTS) Module

Handles voice output using macOS 'say' command.
Supports Arabic (Majed) and English (Samantha/Alex) voices.
"""

import asyncio
import subprocess
import logging
import os
from typing import Optional

from .config import Config

logger = logging.getLogger(__name__)


class TTSModule:
    """Text-to-Speech using macOS 'say' command"""
    
    def __init__(self):
        self.voices = {
            "ar": Config.TTS_VOICE_AR,
            "en": Config.TTS_VOICE_EN
        }
        self.current_language = "ar"  # Default to Arabic
        self.on_speak_callback = None # Callback for GUI updates

    def set_callback(self, callback):
        """Set callback to receive spoken text (for GUI)"""
        self.on_speak_callback = callback

    
    async def speak(self, text: str, language: Optional[str] = None, wait: bool = True):
        """
        Speak text using macOS TTS or just log if disabled
        
        Args:
            text: Text to speak
            language: Language code ('ar' or 'en'), auto-detect if None
            wait: Wait for speech to complete before returning
        """
        if not text:
            logger.warning("Empty text provided to TTS")
            return
            
        # Trigger callback (e.g. for GUI)
        if self.on_speak_callback:
            try:
                self.on_speak_callback(text)
            except Exception as e:
                logger.error(f"TTS callback error: {e}")
            
        # Check if TTS is enabled in config
        if not Config.TTS_ENABLED:
            logger.info(f"TTS Disabled. Text would be: {text[:50]}...")
            # Optionally play a notification sound to indicate response
            if Config.SOUND_EFFECTS_ENABLED:
                await self.play_sound("notification")
            return
        
        # Auto-detect language if not specified
        if language is None:
            language = self._detect_language(text)
        
        if language not in self.voices:
            logger.warning(f"Unsupported language: {language}, using English")
            language = "en"
        
        voice = self.voices[language]
        logger.info(f"Speaking in {language} ({voice}): {text[:50]}...")
        
        try:
            # Use macOS 'say' command
            cmd = ["say", "-v", voice, text]
            
            if wait:
                # Wait for speech to complete
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            else:
                # Fire and forget
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            logger.debug("Speech completed")
            
        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise

    async def play_sound(self, sound_name: str, wait: bool = False):
        """
        Play a system sound effect
        
        Args:
            sound_name: Name of sound from Config.SOUNDS
            wait: Wait for sound to finish
        """
        if not Config.SOUND_EFFECTS_ENABLED:
            return
            
        sound_path = Config.SOUNDS.get(sound_name)
        if not sound_path or not os.path.exists(sound_path):
            logger.warning(f"Sound not found: {sound_name} ({sound_path})")
            return
            
        try:
            cmd = ["afplay", sound_path]
            
            if wait:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            else:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
        except Exception as e:
            logger.error(f"Failed to play sound {sound_name}: {e}")

    async def speak_ar(self, text: str, wait: bool = True):
        """Speak in Arabic"""
        await self.speak(text, language="ar", wait=wait)
    
    async def speak_en(self, text: str, wait: bool = True):
        """Speak in English"""
        await self.speak(text, language="en", wait=wait)
    
    def _detect_language(self, text: str) -> str:
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
        Set the current language for TTS
        
        Args:
            language: Language code ('ar' or 'en')
        """
        if language not in self.voices:
            raise ValueError(f"Unsupported language: {language}")
        
        self.current_language = language
        logger.info(f"TTS language set to: {language}")
    
    def set_voice(self, language: str, voice: str):
        """
        Set custom voice for a language
        
        Args:
            language: Language code ('ar' or 'en')
            voice: Voice name (e.g., 'Samantha', 'Alex', 'Majed')
        """
        if language not in self.voices:
            raise ValueError(f"Unsupported language: {language}")
        
        self.voices[language] = voice
        logger.info(f"Voice for {language} set to: {voice}")
    
    @staticmethod
    def list_available_voices():
        """
        List all available macOS voices
        
        Returns:
            list: Available voice names
        """
        try:
            result = subprocess.run(
                ["say", "-v", "?"],
                capture_output=True,
                text=True
            )
            
            voices = []
            for line in result.stdout.split("\n"):
                if line.strip():
                    # Extract voice name (first word)
                    voice_name = line.split()[0]
                    voices.append(voice_name)
            
            return voices
            
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []


# Singleton instance
_tts_instance: Optional[TTSModule] = None


def get_tts() -> TTSModule:
    """Get singleton TTS instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSModule()
    return _tts_instance


if __name__ == "__main__":
    # Test TTS module
    async def test():
        tts = get_tts()
        
        print("Testing TTS module...")
        print(f"Current voices: {tts.voices}")
        
        print("\nAvailable macOS voices:")
        voices = TTSModule.list_available_voices()
        for voice in voices[:10]:  # Show first 10
            print(f"  - {voice}")
        
        print("\nTesting language detection:")
        print(f"'Hello world' -> {tts._detect_language('Hello world')}")
        print(f"'مرحبا بالعالم' -> {tts._detect_language('مرحبا بالعالم')}")
        
        print("\nTesting speech (you should hear audio):")
        await tts.speak_en("Hello, this is a test in English")
        await tts.speak_ar("مرحبا، هذا اختبار باللغة العربية")
        
        print("\nTTS test completed")
    
    asyncio.run(test())
