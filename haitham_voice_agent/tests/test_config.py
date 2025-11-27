"""
Test Configuration Module
"""

import pytest
from pathlib import Path
from haitham_voice_agent.config import Config


def test_config_paths_exist():
    """Test that all configured paths exist"""
    Config.ensure_directories()
    
    assert Config.HVA_HOME.exists()
    assert Config.CREDENTIALS_DIR.exists()
    assert Config.CACHE_DIR.exists()
    assert Config.LOGS_DIR.exists()
    assert Config.MEMORY_DIR.exists()


def test_config_has_required_keys():
    """Test that required configuration keys are present"""
    # Note: In actual testing, you'd set these in environment
    assert hasattr(Config, 'OPENAI_API_KEY')
    assert hasattr(Config, 'GEMINI_API_KEY')
    assert hasattr(Config, 'GPT_MODEL')
    assert hasattr(Config, 'GEMINI_MODEL')


def test_config_supported_languages():
    """Test supported languages configuration"""
    assert "ar" in Config.SUPPORTED_LANGUAGES
    assert "en" in Config.SUPPORTED_LANGUAGES


def test_config_gmail_scopes():
    """Test Gmail API scopes"""
    assert len(Config.GMAIL_SCOPES) > 0
    assert 'gmail.modify' in str(Config.GMAIL_SCOPES)


def test_config_memory_paths():
    """Test memory module paths"""
    assert Config.MEMORY_DB_PATH.parent == Config.MEMORY_DIR
    assert Config.VECTOR_DB_PATH.parent == Config.MEMORY_DIR
    assert Config.KNOWLEDGE_GRAPH_PATH.parent == Config.MEMORY_DIR


def test_config_summary():
    """Test configuration summary generation"""
    summary = Config.get_config_summary()
    assert "HVA Configuration Summary" in summary
    assert Config.HVA_VERSION in summary
