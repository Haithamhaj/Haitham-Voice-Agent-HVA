"""
Haitham Voice Agent (HVA)

A voice-operated automation agent for macOS with:
- Hybrid LLM routing (Gemini + GPT)
- Gmail integration
- Advanced Memory System
- Safe file and system operations
"""

__version__ = "1.0.0"
__author__ = "Haitham"

from .config import Config, validate_config

__all__ = ["Config", "validate_config"]
