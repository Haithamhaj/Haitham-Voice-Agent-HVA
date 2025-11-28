"""
Gemini Model Discovery

Dynamically discovers the latest available Gemini models (Flash vs Pro) from the API.
Called once at startup to map logical model names to real API model strings.
"""

import google.generativeai as genai
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Safe fallbacks in case discovery fails
FALLBACKS = {
    "flash": "gemini-2.0-flash-exp",
    "pro": "gemini-1.5-pro",
}


def get_best_model(pattern: str, fallback: str) -> str:
    """
    Find the latest model version matching the regex pattern.
    If anything goes wrong, return the fallback.
    
    Args:
        pattern: Regex pattern to match model names
        fallback: Safe fallback model name
        
    Returns:
        str: Best matching model name or fallback
    """
    try:
        # List all available models
        models = [
            m.name
            for m in genai.list_models()
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        
        # Filter by pattern
        matches = [m for m in models if re.search(pattern, m, re.IGNORECASE)]
        
        if not matches:
            logger.warning(
                "No Gemini models matched pattern %s, using fallback %s",
                pattern,
                fallback
            )
            return fallback
        
        # Simple heuristic: sort descending and pick the first
        # This assumes newer versions sort higher lexicographically
        matches.sort(reverse=True)
        best_match = matches[0]
        
        logger.info("Pattern %s matched: %s", pattern, best_match)
        return best_match
        
    except Exception as exc:
        logger.warning(
            "Error while discovering Gemini models: %s. Falling back to %s",
            exc,
            fallback
        )
        return fallback


def resolve_gemini_mapping() -> Dict[str, str]:
    """
    Maps Logical Roles → Real API Models.
    Should be called once at startup.
    
    Returns:
        dict: Mapping of logical names to real API model strings
    """
    logger.info("[HVA] Discovering Gemini Models...")
    
    # Discover Flash variant (2.x or higher)
    flash_real = get_best_model(
        r"gemini-[2-9]\.\d+-flash",
        FALLBACKS["flash"]
    )
    
    # Discover Pro variant (1.5 or higher, or 3.x+)
    pro_real = get_best_model(
        r"gemini-(1\.5|[3-9]\.\d+)-pro",
        FALLBACKS["pro"]
    )
    
    logger.info("Logical Flash mapped to: %s", flash_real)
    logger.info("Logical Pro   mapped to: %s", pro_real)
    
    return {
        "logical.gemini.flash": flash_real,
        "logical.gemini.pro": pro_real,
    }
