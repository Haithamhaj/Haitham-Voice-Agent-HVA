"""
Tests for Model Router

Verifies that the deterministic model router chooses the correct
logical models based on task metadata.
"""

import pytest
from haitham_voice_agent.model_router import TaskMeta, choose_model
from haitham_voice_agent.config import Config


class TestModelRouter:
    """Test suite for model routing logic"""
    
    def test_low_risk_classification_uses_logical_nano(self):
        """Simple, low-risk classification should use logical.nano"""
        meta = TaskMeta(
            context_tokens=500,
            task_type="classification",
            risk="low",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.nano"
        assert result["mode"] == "default"
        assert "nano" in result["reason"].lower()
    
    def test_low_risk_classification_background_uses_batch_flex(self):
        """Low-risk classification in background should use batch+flex mode"""
        meta = TaskMeta(
            context_tokens=500,
            task_type="classification",
            risk="low",
            latency="background"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.nano"
        assert result["mode"] == "batch+flex"
    
    def test_medium_risk_classification_uses_logical_nano_plus(self):
        """Medium-risk classification should use logical.nano-plus"""
        meta = TaskMeta(
            context_tokens=500,
            task_type="classification",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.nano-plus"
        assert result["mode"] == "default"
        assert "nano-plus" in result["reason"].lower()
    
    def test_planning_uses_logical_mini(self):
        """Planning tasks should use logical.mini (main workhorse)"""
        meta = TaskMeta(
            context_tokens=2000,
            task_type="planning",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.mini"
        assert result["mode"] == "default"
        assert "workhorse" in result["reason"].lower()
    
    def test_tool_calling_uses_logical_mini(self):
        """Tool calling should use logical.mini"""
        meta = TaskMeta(
            context_tokens=1500,
            task_type="tool_calling",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.mini"
        assert result["mode"] == "default"
    
    def test_memory_op_uses_logical_mini(self):
        """Memory operations should use logical.mini"""
        meta = TaskMeta(
            context_tokens=1000,
            task_type="memory_op",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.mini"
    
    def test_email_reply_uses_logical_mini(self):
        """Email reply generation should use logical.mini"""
        meta = TaskMeta(
            context_tokens=800,
            task_type="email_reply",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.mini"
    
    def test_high_risk_uses_logical_premium(self):
        """High-risk tasks should use logical.premium"""
        meta = TaskMeta(
            context_tokens=3000,
            task_type="planning",
            risk="high",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.premium"
        assert result["mode"] == "default"
        assert "premium" in result["reason"].lower()
    
    def test_multi_step_reasoning_uses_logical_premium(self):
        """Multi-step reasoning should use logical.premium"""
        meta = TaskMeta(
            context_tokens=2000,
            task_type="multi_step_reasoning",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.premium"
        assert "premium" in result["reason"].lower()
    
    def test_doc_analysis_long_context_uses_logical_doc_gemini(self):
        """Document analysis with >8k tokens should use Gemini"""
        meta = TaskMeta(
            context_tokens=10_000,
            task_type="doc_analysis",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "gemini"
        assert result["model"] == "logical.doc-gemini"
        assert result["mode"] == "default"
        assert "gemini" in result["reason"].lower()
    
    def test_is_document_flag_uses_logical_doc_gemini(self):
        """Tasks marked as documents should use Gemini regardless of size"""
        meta = TaskMeta(
            context_tokens=5000,
            task_type="other",
            risk="low",
            latency="interactive",
            is_document=True
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "gemini"
        assert result["model"] == "logical.doc-gemini"
    
    def test_very_large_context_uses_logical_doc_gemini(self):
        """Context >20k tokens should always use Gemini"""
        meta = TaskMeta(
            context_tokens=25_000,
            task_type="classification",
            risk="low",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "gemini"
        assert result["model"] == "logical.doc-gemini"
    
    def test_translation_large_context_uses_logical_doc_gemini(self):
        """Translation with >8k tokens should use Gemini"""
        meta = TaskMeta(
            context_tokens=9000,
            task_type="translation",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "gemini"
        assert result["model"] == "logical.doc-gemini"
    
    def test_comparison_large_context_uses_logical_doc_gemini(self):
        """Comparison with >8k tokens should use Gemini"""
        meta = TaskMeta(
            context_tokens=10_000,
            task_type="comparison",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "gemini"
        assert result["model"] == "logical.doc-gemini"
    
    def test_background_latency_uses_flex_mode(self):
        """Background tasks should use flex mode"""
        meta = TaskMeta(
            context_tokens=2000,
            task_type="planning",
            risk="medium",
            latency="background"
        )
        
        result = choose_model(meta)
        
        assert result["mode"] == "flex"
    
    def test_fallback_uses_logical_mini(self):
        """Unknown task types should fall back to logical.mini"""
        meta = TaskMeta(
            context_tokens=1000,
            task_type="other",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_model(meta)
        
        assert result["provider"] == "openai"
        assert result["model"] == "logical.mini"
        assert result["mode"] == "default"
        assert "default" in result["reason"].lower()


class TestModelResolution:
    """Test suite for logical model name resolution"""
    
    def test_resolve_logical_nano(self):
        """logical.nano should resolve to gpt-4o-mini"""
        actual = Config.resolve_model("logical.nano")
        assert actual == "gpt-4o-mini"
    
    def test_resolve_logical_nano_plus(self):
        """logical.nano-plus should resolve to gpt-4o-mini"""
        actual = Config.resolve_model("logical.nano-plus")
        assert actual == "gpt-4o-mini"
    
    def test_resolve_logical_mini(self):
        """logical.mini should resolve to gpt-4o"""
        actual = Config.resolve_model("logical.mini")
        assert actual == "gpt-4o"
    
    def test_resolve_logical_premium(self):
        """logical.premium should resolve to gpt-4o"""
        actual = Config.resolve_model("logical.premium")
        assert actual == "gpt-4o"
    
    def test_resolve_logical_doc_gemini(self):
        """logical.doc-gemini should resolve to gemini-2.0-flash-exp"""
        actual = Config.resolve_model("logical.doc-gemini")
        # Note: This depends on init_gemini_mapping being called or mocked.
        # Since we can't easily mock the class method here without patching Config,
        # we'll assume it falls back to the default which is now gemini-2.0-flash-exp
        assert actual == "gemini-2.0-flash-exp"
    
    def test_resolve_unknown_falls_back_to_mini(self):
        """Unknown logical names should fall back to logical.mini's target"""
        actual = Config.resolve_model("logical.unknown")
        assert actual == "gpt-4o"  # Same as logical.mini
    
    def test_resolve_empty_string_falls_back_to_mini(self):
        """Empty string should fall back to logical.mini's target"""
        actual = Config.resolve_model("")
        assert actual == "gpt-4o"


class TestEndToEndRouting:
    """Integration tests for complete routing flow"""
    
    def test_complete_flow_classification(self):
        """Test complete flow: meta → router → resolver"""
        meta = TaskMeta(
            context_tokens=500,
            task_type="classification",
            risk="low",
            latency="interactive"
        )
        
        # Step 1: Route
        route = choose_model(meta)
        assert route["model"] == "logical.nano"
        
        # Step 2: Resolve
        actual_model = Config.resolve_model(route["model"])
        assert actual_model == "gpt-4o-mini"
    
    def test_complete_flow_planning(self):
        """Test complete flow for planning task"""
        meta = TaskMeta(
            context_tokens=2000,
            task_type="planning",
            risk="medium",
            latency="interactive"
        )
        
        route = choose_model(meta)
        assert route["model"] == "logical.mini"
        
        actual_model = Config.resolve_model(route["model"])
        assert actual_model == "gpt-4o"
    
    def test_complete_flow_document(self):
        """Test complete flow for document analysis"""
        meta = TaskMeta(
            context_tokens=15_000,
            task_type="doc_analysis",
            risk="medium",
            latency="interactive"
        )
        
        route = choose_model(meta)
        assert route["model"] == "logical.doc-gemini"
        assert route["provider"] == "gemini"
        
        actual_model = Config.resolve_model(route["model"])
        assert actual_model == "gemini-2.0-flash-exp"
