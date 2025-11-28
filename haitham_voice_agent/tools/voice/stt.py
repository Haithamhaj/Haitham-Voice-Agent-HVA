"""
Speech-to-Text (STT) Module

Converts spoken audio to text using Google Speech Recognition API.
Supports Arabic and English.
"""

import speech_recognition as sr
import logging
from typing import Optional, Literal
from haitham_voice_agent.config import Config

logger = logging.getLogger(__name__)

Language = Literal["ar", "en"]


class STT:
    """Speech-to-Text handler"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust for ambient noise
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
    def listen(
        self, 
        language: Language = "en",
        timeout: int = None,
        phrase_time_limit: int = None
    ) -> Optional[str]:
        """
        Listen to microphone and convert speech to text.
        
        Args:
            language: "ar" for Arabic, "en" for English
            timeout: Max seconds to wait for speech to start
            phrase_time_limit: Max seconds for the phrase
            
        Returns:
            str: Recognized text or None if failed
        """
        timeout = timeout or Config.STT_TIMEOUT
        
        # Map language codes
        lang_code = Config.STT_LANGUAGE_AR if language == "ar" else Config.STT_LANGUAGE_EN
        
        try:
            with sr.Microphone() as source:
                logger.info(f"Listening... (language: {language})")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                logger.info("Processing speech...")
                
                # Recognize using Google Speech Recognition
                text = self.recognizer.recognize_google(
                    audio,
                    language=lang_code
                )
                
                logger.info(f"Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition: {e}")
            return None
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None
    
    def listen_from_file(self, audio_file: str, language: Language = "en") -> Optional[str]:
        """
        Convert audio file to text.
        
        Args:
            audio_file: Path to audio file (WAV format)
            language: "ar" or "en"
            
        Returns:
            str: Recognized text or None
        """
        lang_code = Config.STT_LANGUAGE_AR if language == "ar" else Config.STT_LANGUAGE_EN
        
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=lang_code)
                logger.info(f"Recognized from file: {text}")
                return text
        except Exception as e:
            logger.error(f"File STT error: {e}")
            return None
