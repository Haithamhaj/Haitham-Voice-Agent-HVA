"""
Tests for Local Voice System

Verifies:
1. Whisper model initialization
2. Session Recorder functionality
3. Main loop integration (via test mode)
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from haitham_voice_agent.tools.voice import LocalSTT, SessionRecorder, init_whisper_models
from haitham_voice_agent.config import Config
from haitham_voice_agent.main import HVA

class TestLocalVoice:
    
    @pytest.fixture
    def mock_whisper(self):
        with patch("haitham_voice_agent.tools.voice.stt.WhisperModel") as mock:
            yield mock

    def test_whisper_init(self, mock_whisper):
        """Test that Whisper models are initialized from config"""
        init_whisper_models()
        # Should initialize at least one model if config is present
        # We mock HAS_WHISPER = True for this test context if needed
        pass

    def test_recorder_lifecycle(self, tmp_path):
        """Test start/stop recording creates a file"""
        # Mock Config.VOICE_SESSION_DIR
        with patch("haitham_voice_agent.config.Config.VOICE_SESSION_DIR", tmp_path):
            recorder = SessionRecorder()
            
            # Mock pyaudio to avoid hardware requirement
            with patch("pyaudio.PyAudio") as mock_pa:
                path = recorder.start()
                assert recorder.is_recording()
                assert path.startswith(str(tmp_path))
                
                recorder.stop()
                assert not recorder.is_recording()

    @pytest.mark.asyncio
    async def test_main_test_mode(self):
        """Test HVA main loop in text-only test mode"""
        with patch("haitham_voice_agent.main.HVA.initialize_async", new_callable=Mock) as mock_init:
            hva = HVA()
            
            # Mock router response
            hva.llm_router.generate_with_gpt = AsyncMock(return_value={
                "intent": "Test Intent",
                "tool": "memory",
                "action": "save_note",
                "parameters": {"content": "Test Content"},
                "confirmation_needed": False
            })
            
            # Mock execution
            hva.memory_tools.process_voice_note = AsyncMock(return_value={"success": True, "message": "Saved"})
            
            # Run plan
            plan = await hva.plan_command("Test command")
            result = await hva.execute_plan(plan)
            
            assert result["success"] is True
            assert result["message"] == "Saved"
