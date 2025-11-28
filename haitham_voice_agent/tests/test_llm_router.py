"""
Test LLM Router Module
"""

import pytest
import asyncio
from haitham_voice_agent.llm_router import LLMRouter, LLMType


@pytest.fixture
def router():
    """Create router instance for testing"""
    # Note: Requires API keys in environment
    try:
        return LLMRouter()
    except Exception:
        pytest.skip("API keys not configured")


def test_router_initialization(router):
    """Test router initializes correctly"""
    assert router.gpt_model is not None


def test_routing_to_gemini(router):
    """Test routing logic for Gemini tasks"""
    test_cases = [
        "Summarize this PDF file",
        "Translate this text to Arabic",
        "Analyze this image",
        "Compare these two documents"
    ]
    
    for intent in test_cases:
        llm_type = router.route(intent)
        assert llm_type == LLMType.GEMINI, f"Failed for: {intent}"


def test_routing_to_gpt(router):
    """Test routing logic for GPT tasks"""
    test_cases = [
        "Create a draft email to John",
        "Save this idea to memory",
        "Generate an execution plan",
        "Classify this note"
    ]
    
    for intent in test_cases:
        llm_type = router.route(intent)
        assert llm_type == LLMType.GPT, f"Failed for: {intent}"


@pytest.mark.asyncio
async def test_execution_plan_generation(router):
    """Test execution plan generation"""
    intent = "List files in Downloads folder"
    
    plan = await router.generate_execution_plan(intent)
    
    assert "intent" in plan
    assert "steps" in plan
    assert "tools" in plan
    assert "requires_confirmation" in plan
    assert isinstance(plan["steps"], list)


@pytest.mark.asyncio
async def test_execution_plan_structure(router):
    """Test execution plan has correct structure"""
    intent = "Read my latest email and save important points"
    
    plan = await router.generate_execution_plan(intent)
    
    # Check required keys
    assert all(key in plan for key in ["intent", "steps", "tools", "requires_confirmation"])
    
    # Check steps structure
    if len(plan["steps"]) > 0:
        step = plan["steps"][0]
        assert "tool" in step
        assert "action" in step
