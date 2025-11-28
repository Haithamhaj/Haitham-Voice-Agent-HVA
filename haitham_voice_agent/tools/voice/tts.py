"""
Text-to-Speech (TTS) Module

Converts text to speech using macOS `say` command.
Supports Arabic and English voices.
"""

import subprocess
import logging
from typing import Literal
from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)

Language = Literal["ar", "en"]


class TTS:
    """Text-to-Speech handler"""
    
    def speak(self, text: str, language: Language = "en", rate: int = 200):
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to speak
            language: "ar" for Arabic, "en" for English
            rate: Speaking rate (words per minute, default 200)
        """
        if not text:
            logger.warning("Empty text provided to TTS")
            return
        
        # Select voice based on language
        voice = Config.TTS_VOICE_AR if language == "ar" else Config.TTS_VOICE_EN
        
        try:
            logger.info(f"Speaking ({language}): {text[:50]}...")
            
            # Use macOS say command
            subprocess.run(
                ["say", "-v", voice, "-r", str(rate), text],
                check=True,
                capture_output=True
            )
            
            logger.info("Speech completed")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"TTS command failed: {e}")
        except FileNotFoundError:
            logger.error("'say' command not found. Are you on macOS?")
        except Exception as e:
            logger.error(f"TTS error: {e}")
    
    def speak_to_file(self, text: str, output_file: str, language: Language = "en"):
        """
        Convert text to speech and save to audio file.
        
        Args:
            text: Text to speak
            output_file: Path to output audio file (AIFF format)
            language: "ar" or "en"
        """
        voice = Config.TTS_VOICE_AR if language == "ar" else Config.TTS_VOICE_EN
        
        try:
            subprocess.run(
                ["say", "-v", voice, "-o", output_file, text],
                check=True,
                capture_output=True
            )
            logger.info(f"Speech saved to {output_file}")
        except Exception as e:
            logger.error(f"TTS file save error: {e}")
