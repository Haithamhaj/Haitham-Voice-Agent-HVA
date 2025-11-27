"""
Test Basic Tools
"""

import pytest
import asyncio
from pathlib import Path
from haitham_voice_agent.tools.files import FileTools
from haitham_voice_agent.tools.docs import DocTools
from haitham_voice_agent.tools.browser import BrowserTools
from haitham_voice_agent.tools.terminal import TerminalTools


@pytest.fixture
def file_tools():
    """Create FileTools instance"""
    return FileTools()


@pytest.fixture
def doc_tools():
    """Create DocTools instance"""
    return DocTools()


@pytest.fixture
def browser_tools():
    """Create BrowserTools instance"""
    return BrowserTools()


@pytest.fixture
def terminal_tools():
    """Create TerminalTools instance"""
    return TerminalTools()


# ==================== File Tools Tests ====================

@pytest.mark.asyncio
async def test_list_files(file_tools, tmp_path):
    """Test listing files in a directory"""
    # Create test files
    (tmp_path / "test1.txt").write_text("test")
    (tmp_path / "test2.txt").write_text("test")
    
    result = await file_tools.list_files(str(tmp_path))
    
    assert not result.get("error")
    assert result["count"] == 2
    assert len(result["files"]) == 2


@pytest.mark.asyncio
async def test_create_folder(file_tools, tmp_path):
    """Test creating a folder"""
    new_folder = tmp_path / "new_folder"
    
    result = await file_tools.create_folder(str(new_folder))
    
    assert not result.get("error")
    assert result["status"] == "created"
    assert new_folder.exists()


@pytest.mark.asyncio
async def test_delete_folder_requires_confirmation(file_tools, tmp_path):
    """Test that delete requires confirmation"""
    test_folder = tmp_path / "test_folder"
    test_folder.mkdir()
    
    # Try without confirmation
    result = await file_tools.delete_folder(str(test_folder), confirmed=False)
    
    assert result.get("error")
    assert "confirmation" in result["message"].lower()
    assert test_folder.exists()  # Should still exist


@pytest.mark.asyncio
async def test_copy_file(file_tools, tmp_path):
    """Test copying a file"""
    source = tmp_path / "source.txt"
    source.write_text("test content")
    dest = tmp_path / "dest.txt"
    
    result = await file_tools.copy_file(str(source), str(dest))
    
    assert not result.get("error")
    assert result["status"] == "copied"
    assert dest.exists()
    assert dest.read_text() == "test content"


# ==================== Terminal Tools Tests ====================

@pytest.mark.asyncio
async def test_terminal_allowed_command(terminal_tools):
    """Test executing allowed command"""
    result = await terminal_tools.execute_command("pwd")
    
    assert not result.get("error")
    assert result["success"]
    assert result["output"]


@pytest.mark.asyncio
async def test_terminal_blocked_command(terminal_tools):
    """Test that dangerous commands are blocked"""
    result = await terminal_tools.execute_command("rm -rf /")
    
    assert result.get("error")
    assert "not allowed" in result["message"].lower()


@pytest.mark.asyncio
async def test_terminal_dangerous_pattern(terminal_tools):
    """Test that dangerous patterns are blocked"""
    result = await terminal_tools.execute_command("ls && rm test.txt")
    
    assert result.get("error")
    assert "dangerous" in result["message"].lower()


@pytest.mark.asyncio
async def test_terminal_list_allowed(terminal_tools):
    """Test listing allowed commands"""
    result = await terminal_tools.list_allowed_commands()
    
    assert "allowed_commands" in result
    assert len(result["allowed_commands"]) > 0
    assert "pwd" in result["allowed_commands"]


# ==================== Browser Tools Tests ====================

@pytest.mark.asyncio
async def test_browser_open_url(browser_tools):
    """Test opening URL (just check it doesn't error)"""
    result = await browser_tools.open_url("https://www.google.com")
    
    assert not result.get("error")
    assert result["status"] == "opened"


@pytest.mark.asyncio
async def test_browser_search_google(browser_tools):
    """Test Google search"""
    result = await browser_tools.search_google("Python programming")
    
    assert not result.get("error")
    assert result["status"] == "searched"
    assert "google.com/search" in result["url"]
