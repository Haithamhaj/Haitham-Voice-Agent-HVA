"""
Gemini Router

Chooses between Flash and Pro variants based on task requirements.
Priority: Quality first, then cost optimization.
"""

from typing import Dict
from haitham_voice_agent.model_router import TaskMeta

# Type alias for router result
GeminiResult = Dict[str, str]


def choose_gemini_variant(meta: TaskMeta) -> GeminiResult:
    """
    Decide between 'logical.gemini.flash' and 'logical.gemini.pro'
    based on task requirements.
    
    This function MUST be pure and deterministic (no LLM calls).
    
    Priority:
    1. QUALITY FIRST: Prefer Pro for reasoning, complex documents, or high-risk tasks
    2. COST SECOND: Use Flash ONLY for simple, low-risk, or latency-sensitive tasks
    
    Args:
        meta: TaskMeta instance describing the task
        
    Returns:
        GeminiResult with keys: logical_model, reason
    """
    
    # Rule 1: Massive Context → Force Pro
    if meta.context_tokens > 75_000:
        return {
            "logical_model": "logical.gemini.pro",
            "reason": "Massive context (>75k tokens) requires Pro stability."
        }
    
    # Rule 2: High Risk / Heavy Reasoning → Pro
    if meta.risk == "high" or meta.task_type == "multi_step_reasoning":
        return {
            "logical_model": "logical.gemini.pro",
            "reason": "High risk or complex reasoning requires Pro quality."
        }
    
    # Rule 3: Complex Document Tasks → Pro
    if (meta.task_type in ["doc_analysis", "comparison", "translation"] 
        and meta.is_document):
        return {
            "logical_model": "logical.gemini.pro",
            "reason": "Document-level comparison/translation needs Pro nuance."
        }
    
    # Rule 4: Simple Vision / Low-Risk Tasks → Flash
    if (meta.task_type in ["classification", "tagging"] 
        and meta.risk == "low"):
        return {
            "logical_model": "logical.gemini.flash",
            "reason": "Simple low-risk task; Flash is sufficient and cheaper."
        }
    
    # Rule 5: Interactive Latency → Prefer Flash if not high-risk
    if meta.latency == "interactive" and meta.risk != "high":
        return {
            "logical_model": "logical.gemini.flash",
            "reason": "User waiting in real time; Flash preferred for speed."
        }
    
    # Rule 6: Default Fallback → Pro
    return {
        "logical_model": "logical.gemini.pro",
        "reason": "Defaulting to Pro to ensure highest quality."
    }
