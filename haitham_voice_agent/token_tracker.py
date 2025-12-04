import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TokenTracker:
    """
    Tracks token usage and calculates costs for LLM calls.
    Singleton instance.
    """
    
    # Cost per 1k tokens (USD)
    # As of late 2024/2025 estimates
    PRICING = {
        # OpenAI
        "gpt-4o": {"input": 0.0025, "output": 0.01}, # Updated to $2.50/$10.00 per 1M
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-5": {"input": 0.01, "output": 0.03}, # Estimated Premium Pricing
        "gpt-5-mini": {"input": 0.0002, "output": 0.0008}, # Estimated Mini Pricing
        
        # Google Gemini
        "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105}, # < 128k context
        "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003}, # < 128k context
        "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004}, # Estimated
        
        # Local Models (Free)
        "qwen": {"input": 0.0, "output": 0.0},
        "llama3": {"input": 0.0, "output": 0.0},
        "mistral": {"input": 0.0, "output": 0.0},
        "whisper": {"input": 0.0, "output": 0.0}, # STT usually per minute, but let's track 0 for now
    }
    
    def __init__(self):
        self.pricing_file = Path(__file__).parent / "data" / "pricing.json"
        self.PRICING = self._load_pricing()
        
    def _load_pricing(self) -> Dict[str, Any]:
        """Load pricing from JSON file"""
        try:
            import json
            if self.pricing_file.exists():
                with open(self.pricing_file, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load pricing.json: {e}")
            
        # Fallback to hardcoded defaults if file fails
        return {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-5": {"input": 0.01, "output": 0.03},
            "gpt-5-mini": {"input": 0.0002, "output": 0.0008},
            "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
            "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
            "qwen": {"input": 0.0, "output": 0.0},
            "llama3": {"input": 0.0, "output": 0.0},
            "mistral": {"input": 0.0, "output": 0.0},
            "whisper": {"input": 0.0, "output": 0.0}
        }

    def reload_pricing(self):
        """Reload pricing from file"""
        self.PRICING = self._load_pricing()
        logger.info("Pricing reloaded from file")
        
    async def track_usage(self, model: str, input_tokens: int, output_tokens: int, context: Dict[str, Any] = None):
        """
        Calculate cost and log usage to DB.
        """
        from haitham_voice_agent.tools.memory.memory_system import memory_system
        
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        # Log to DB
        # We access sqlite_store via memory_system
        if memory_system and memory_system.sqlite_store:
            await memory_system.sqlite_store.log_token_usage(
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                context=context
            )
            
        # Log to console for debug
        if cost > 0:
            logger.debug(f"Token Usage [{model}]: {input_tokens}+{output_tokens} tokens = ${cost:.6f}")

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost based on model pricing.
        """
        # Normalize model name for matching
        model_key = self._find_pricing_key(model)
        
        if not model_key:
            # Default to 0 if unknown (or log warning)
            # logger.warning(f"Unknown model for pricing: {model}")
            return 0.0
            
        rates = self.PRICING[model_key]
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        
        return input_cost + output_cost

    def _find_pricing_key(self, model_name: str) -> Optional[str]:
        """Match model string to pricing key (e.g. 'gemini-1.5-flash-001' -> 'gemini-1.5-flash')"""
        model_lower = model_name.lower()
        
        # Direct match
        if model_lower in self.PRICING:
            return model_lower
            
        # Partial match (longest match wins)
        matches = [k for k in self.PRICING.keys() if k in model_lower]
        if matches:
            return max(matches, key=len)
            
        # Fallback for local models
        if "qwen" in model_lower or "llama" in model_lower:
            return "qwen" # Free tier generic
            
        return None

# Singleton
_tracker = None

def get_tracker():
    global _tracker
    if _tracker is None:
        _tracker = TokenTracker()
    return _tracker
