"""
Intent Router Module

Implements deterministic, rule-based routing for core Arabic commands.
This layer sits BEFORE the LLM planner to ensure reliability for common actions.
"""

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IntentRouter:
    """
    Deterministic Intent Router for HVA.
    Matches spoken text against known patterns to trigger specific actions directly.
    """
    
    def __init__(self):
        # Define core patterns
        # Format: "action_name": [list of regex patterns or keywords]
        self.patterns = {
            "save_memory_note": [
                r"احفظ ملاحظة",
                r"سجّل ملاحظة",
                r"اكتب ملاحظة",
                r"save note",
                r"take a note"
            ],
            "start_session_recording": [
                r"ابدأ جلسة",
                r"ابدأ تسجيل",
                r"تسجيل اجتماع",
                r"start session",
                r"start recording"
            ],
            "stop_session_recording": [
                r"انهِ الجلسة",
                r"أوقف الجلسة",
                r"أوقف التسجيل",
                r"stop session",
                r"stop recording"
            ],
            "fetch_latest_email": [
                r"هات آخر إيميل",
                r"اعرض آخر إيميل",
                r"اقرأ آخر إيميل",
                r"read latest email",
                r"fetch latest email",
                r"check email"
            ],
            "summarize_latest_email": [
                r"لخّص آخر إيميل",
                r"ملخص آخر إيميل",
                r"summarize latest email"
            ]
        }

    def route_command(self, text: str) -> Dict[str, Any]:
        """
        Route a command text to an action.
        
        Args:
            text: Spoken text
            
        Returns:
            dict: {
                "action": str,
                "params": dict,
                "confidence": float
            }
        """
        text_lower = text.lower().strip()
        
        # 1. Check explicit patterns
        for action, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    logger.info(f"Intent matched: {action} (pattern: {pattern})")
                    
                    # Extract params if needed
                    params = {}
                    if action == "save_memory_note":
                        # Use the whole text as the note content
                        params["content"] = text
                    
                    return {
                        "action": action,
                        "params": params,
                        "confidence": 1.0
                    }
        
        # 2. (Removed) Check for long unrecognized speech
        # We now handle long speech in main.py based on duration.
        # Short unrecognized speech should be treated as unknown to avoid garbage.
            
        # 3. Unknown
        return {
            "action": "unknown",
            "params": {},
            "confidence": 0.0
        }

# Singleton instance
_router = IntentRouter()

def route_command(text: str) -> Dict[str, Any]:
    """Public interface for routing"""
    return _router.route_command(text)
