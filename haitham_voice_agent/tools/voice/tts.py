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
        
        # Select voice and rate based on language
        tts_config = Config.TTS_CONFIG.get(language, Config.TTS_CONFIG["en"])
        voice = tts_config["voice"]
        # Use configured rate, or override if rate arg was explicitly passed (though we default to config)
        # Actually, let's respect the rate argument if it differs from default 200, 
        # otherwise use config. But the method signature has default 200.
        # Let's prioritize config rate for better quality control.
        config_rate = tts_config["rate"]
        
        try:
            logger.info(f"Speaking ({language}, voice={voice}, rate={config_rate}): {text[:50]}...")
            
            # Use macOS say command
            subprocess.run(
                ["say", "-v", voice, "-r", str(config_rate), text],
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
