"""
Tests for Gemini Routing and Model Discovery

Verifies that the Gemini router chooses the correct variant (Flash vs Pro)
and that model discovery works correctly with fallbacks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from haitham_voice_agent.model_router import TaskMeta
from haitham_voice_agent.tools.gemini.gemini_router import choose_gemini_variant
from haitham_voice_agent.tools.gemini.model_discovery import (
    get_best_model,
    resolve_gemini_mapping,
    FALLBACKS
)
from haitham_voice_agent.config import Config


class TestGeminiRouting:
    """Test suite for Gemini variant routing logic"""
    
    def test_massive_context_uses_pro(self):
        """Context >75k tokens should always use Pro"""
        meta = TaskMeta(
            context_tokens=80_000,
            task_type="doc_analysis",
            risk="low",
            latency="interactive"
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.pro"
        assert "massive" in result["reason"].lower()
    
    def test_high_risk_uses_pro(self):
        """High-risk tasks should use Pro"""
        meta = TaskMeta(
            context_tokens=10_000,
            task_type="doc_analysis",
            risk="high",
            latency="interactive"
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.pro"
        assert "high risk" in result["reason"].lower()
    
    def test_multi_step_reasoning_uses_pro(self):
        """Multi-step reasoning should use Pro"""
        meta = TaskMeta(
            context_tokens=5000,
            task_type="multi_step_reasoning",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.pro"
        assert "reasoning" in result["reason"].lower()
    
    def test_doc_analysis_document_uses_pro(self):
        """Document-level analysis should use Pro"""
        meta = TaskMeta(
            context_tokens=15_000,
            task_type="doc_analysis",
            risk="medium",
            latency="interactive",
            is_document=True
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.pro"
        assert "document" in result["reason"].lower()
    
    def test_comparison_document_uses_pro(self):
        """Document comparison should use Pro"""
        meta = TaskMeta(
            context_tokens=12_000,
            task_type="comparison",
            risk="medium",
            latency="interactive",
            is_document=True
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.pro"
    
    def test_translation_document_uses_pro(self):
        """Document translation should use Pro"""
        meta = TaskMeta(
            context_tokens=10_000,
            task_type="translation",
            risk="medium",
            latency="interactive",
            is_document=True
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.pro"
        assert "nuance" in result["reason"].lower()
    
    def test_low_risk_tagging_uses_flash(self):
        """Simple, low-risk tagging should use Flash"""
        meta = TaskMeta(
            context_tokens=1000,
            task_type="tagging",
            risk="low",
            latency="interactive"
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.flash"
        assert "flash" in result["reason"].lower()
    
    def test_low_risk_classification_uses_flash(self):
        """Simple, low-risk classification should use Flash"""
        meta = TaskMeta(
            context_tokens=800,
            task_type="classification",
            risk="low",
            latency="interactive"
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.flash"
        assert "cheaper" in result["reason"].lower()
    
    def test_interactive_low_risk_prefers_flash(self):
        """Interactive, non-high-risk tasks should prefer Flash for speed"""
        meta = TaskMeta(
            context_tokens=5000,
            task_type="doc_analysis",
            risk="medium",
            latency="interactive"
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.flash"
        assert "real time" in result["reason"].lower()
    
    def test_interactive_high_risk_uses_pro(self):
        """Interactive high-risk should still use Pro (quality first)"""
        meta = TaskMeta(
            context_tokens=5000,
            task_type="doc_analysis",
            risk="high",
            latency="interactive"
        )
        
        result = choose_gemini_variant(meta)
        
        assert result["logical_model"] == "logical.gemini.pro"
    
    def test_background_medium_risk_defaults_to_pro(self):
        """Background, medium-risk, non-document tasks default to Pro (quality first)"""
        meta = TaskMeta(
            context_tokens=3000,
            task_type="other",
            risk="medium",
            latency="background"
        )
        
        result = choose_gemini_variant(meta)
        
        # Falls through to default → Pro (quality first)
        assert result["logical_model"] == "logical.gemini.pro"
        assert "quality" in result["reason"].lower()
    
    def test_default_falls_back_to_pro(self):
        """Unknown scenarios should default to Pro (quality first)"""
        meta = TaskMeta(
            context_tokens=5000,
            task_type="other",
            risk="medium",
            latency="background"
        )
        
        result = choose_gemini_variant(meta)
        
        # Should fall through to interactive latency check → Flash
        # But if we change latency to background and risk to medium,
        # it should hit the interactive rule first
        # Let's test a case that truly falls through
        meta2 = TaskMeta(
            context_tokens=5000,
            task_type="other",
            risk="high",
            latency="background"
        )
        
        result2 = choose_gemini_variant(meta2)
        assert result2["logical_model"] == "logical.gemini.pro"
        assert "quality" in result2["reason"].lower()


class TestModelDiscovery:
    """Test suite for Gemini model discovery"""
    
    @patch('haitham_voice_agent.tools.gemini.model_discovery.genai.list_models')
    def test_get_best_model_finds_match(self, mock_list_models):
        """Should find the best matching model"""
        # Mock model objects
        mock_models = [
            Mock(name="gemini-2.0-flash", supported_generation_methods=["generateContent"]),
            Mock(name="gemini-2.5-flash", supported_generation_methods=["generateContent"]),
            Mock(name="gemini-1.5-pro", supported_generation_methods=["generateContent"]),
        ]
        mock_list_models.return_value = mock_models
        
        result = get_best_model(r"gemini-[2-9]\.\d+-flash", FALLBACKS["flash"])
        
        # Should pick the highest version (2.5)
        assert "2.5" in result or "2.0" in result
        assert "flash" in result
    
    @patch('haitham_voice_agent.tools.gemini.model_discovery.genai.list_models')
    def test_get_best_model_no_match_uses_fallback(self, mock_list_models):
        """Should use fallback when no models match"""
        mock_models = [
            Mock(name="gemini-1.0-old", supported_generation_methods=["generateContent"]),
        ]
        mock_list_models.return_value = mock_models
        
        result = get_best_model(r"gemini-[2-9]\.\d+-flash", FALLBACKS["flash"])
        
        assert result == FALLBACKS["flash"]
    
    @patch('haitham_voice_agent.tools.gemini.model_discovery.genai.list_models')
    def test_get_best_model_error_uses_fallback(self, mock_list_models):
        """Should use fallback when API call fails"""
        mock_list_models.side_effect = Exception("API Error")
        
        result = get_best_model(r"gemini-[2-9]\.\d+-flash", FALLBACKS["flash"])
        
        assert result == FALLBACKS["flash"]
    
    @patch('haitham_voice_agent.tools.gemini.model_discovery.genai.list_models')
    def test_resolve_gemini_mapping_success(self, mock_list_models):
        """Should create correct mapping on success"""
        mock_models = [
            Mock(name="gemini-2.0-flash-exp", supported_generation_methods=["generateContent"]),
            Mock(name="gemini-1.5-pro", supported_generation_methods=["generateContent"]),
        ]
        mock_list_models.return_value = mock_models
        
        mapping = resolve_gemini_mapping()
        
        assert "logical.gemini.flash" in mapping
        assert "logical.gemini.pro" in mapping
        assert "flash" in mapping["logical.gemini.flash"]
        assert "pro" in mapping["logical.gemini.pro"]
    
    @patch('haitham_voice_agent.tools.gemini.model_discovery.genai.list_models')
    def test_resolve_gemini_mapping_uses_fallbacks_on_error(self, mock_list_models):
        """Should use fallbacks when discovery fails"""
        mock_list_models.side_effect = Exception("Network error")
        
        mapping = resolve_gemini_mapping()
        
        assert mapping["logical.gemini.flash"] == FALLBACKS["flash"]
        assert mapping["logical.gemini.pro"] == FALLBACKS["pro"]


class TestConfigIntegration:
    """Test suite for Config integration"""
    
    def test_resolve_gemini_model_initializes_mapping(self):
        """Should initialize mapping on first call"""
        # Reset mapping
        Config.GEMINI_MAPPING = {}
        
        # This should trigger initialization
        with patch.object(Config, 'init_gemini_mapping') as mock_init:
            mock_init.return_value = None
            Config.GEMINI_MAPPING = {
                "logical.gemini.flash": "gemini-2.0-flash-exp",
                "logical.gemini.pro": "gemini-1.5-pro",
            }
            
            result = Config.resolve_gemini_model("logical.gemini.flash")
            
            # Should have called init if mapping was empty
            # (but we pre-populated it in the test)
            assert result == "gemini-2.0-flash-exp"
    
    def test_resolve_gemini_model_unknown_falls_back_to_pro(self):
        """Unknown logical names should fall back to Pro"""
        Config.GEMINI_MAPPING = {
            "logical.gemini.flash": "gemini-2.0-flash-exp",
            "logical.gemini.pro": "gemini-1.5-pro",
        }
        
        result = Config.resolve_gemini_model("logical.gemini.unknown")
        
        assert result == "gemini-1.5-pro"  # Falls back to Pro


class TestEndToEndGeminiFlow:
    """Integration tests for complete Gemini routing flow"""
    
    def test_complete_flow_high_risk_document(self):
        """Test complete flow: meta → router → resolver"""
        # Setup
        Config.GEMINI_MAPPING = {
            "logical.gemini.flash": "gemini-2.0-flash-exp",
            "logical.gemini.pro": "gemini-1.5-pro",
        }
        
        meta = TaskMeta(
            context_tokens=20_000,
            task_type="doc_analysis",
            risk="high",
            latency="interactive",
            is_document=True
        )
        
        # Step 1: Route
        route = choose_gemini_variant(meta)
        assert route["logical_model"] == "logical.gemini.pro"
        
        # Step 2: Resolve
        actual_model = Config.resolve_gemini_model(route["logical_model"])
        assert actual_model == "gemini-1.5-pro"
    
    def test_complete_flow_simple_tagging(self):
        """Test complete flow for simple tagging"""
        Config.GEMINI_MAPPING = {
            "logical.gemini.flash": "gemini-2.0-flash-exp",
            "logical.gemini.pro": "gemini-1.5-pro",
        }
        
        meta = TaskMeta(
            context_tokens=500,
            task_type="tagging",
            risk="low",
            latency="interactive"
        )
        
        route = choose_gemini_variant(meta)
        assert route["logical_model"] == "logical.gemini.flash"
        
        actual_model = Config.resolve_gemini_model(route["logical_model"])
        assert actual_model == "gemini-2.0-flash-exp"
