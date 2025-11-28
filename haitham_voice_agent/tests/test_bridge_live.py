"""
Live Bridge Test: Gmail -> Memory Integration

Tests the complete flow of saving an email to the memory system
and retrieving it via semantic search.
"""

import asyncio
import pytest
import logging
from unittest.mock import Mock
from haitham_voice_agent.tools.gmail.memory_integration import GmailMemoryBridge
from haitham_voice_agent.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_bridge_live():
    """
    Test the Gmail -> Memory bridge with a mock email.
    Requires OPENAI_API_KEY and GEMINI_API_KEY to be set.
    """
    # 1. Check for API keys
    if not Config.OPENAI_API_KEY or not Config.GEMINI_API_KEY:
        print("❌ SKIPPED: API keys not found in environment")
        print("Please ensure OPENAI_API_KEY and GEMINI_API_KEY are set in .env")
        return False

    print("\n\n========== STARTING GMAIL-MEMORY BRIDGE TEST ==========")
    
    # 2. Initialize Bridge
    bridge = GmailMemoryBridge()
    await bridge.initialize()
    print("✓ Bridge Initialized")
    
    # 3. Mock an email (since we don't want to actually fetch from Gmail)
    mock_email = {
        "id": "test_email_123",
        "subject": "Q2 2025 Product Roadmap Discussion",
        "from": "sarah@mindq.com",
        "date": "2025-01-15",
        "body_text": """Hi team,

I wanted to share our preliminary thoughts on the Q2 2025 roadmap for Mind-Q.

Key Points:
1. Database Migration: We've decided to migrate from MongoDB to PostgreSQL with TimescaleDB extension for better time-series support.
2. AI Features: Planning to integrate advanced memory capabilities using vector embeddings.
3. Mobile App: iOS beta launch scheduled for April 2025.

Action Items:
- Sarah: Lead the database migration planning
- Ahmed: Research vector database options
- Haitham: Prototype the memory system

Let's discuss this in our next sync meeting.

Best,
Sarah
"""
    }
    
    # 4. Mock the Gmail handler's get_email_by_id method
    bridge.gmail_handler.get_email_by_id = Mock(return_value=mock_email)
    
    # 5. Save email to memory
    print(f"\nSaving email: {mock_email['subject'][:50]}...")
    result = await bridge.save_email_to_memory("test_email_123")
    
    if not result or not result.get("success"):
        print("❌ Failed to save email to memory")
        return False
    
    print(f"✓ Email saved as memory {result['memory_id']}")
    print(f"  - Project: {result['project']}")
    print(f"  - Summary: {result['summary']}")
    
    # 6. Query the memory system to verify retrieval
    query = "What database are we migrating to for Mind-Q?"
    print(f"\nSearching for: '{query}'")
    
    memories = await bridge.memory_system.search_memories(query, limit=3)
    
    found = False
    for mem in memories:
        if "PostgreSQL" in mem.raw_content or "TimescaleDB" in mem.raw_content:
            found = True
            print(f"✓ Found email via semantic search!")
            print(f"  - Match: {mem.ultra_brief}")
            print(f"  - Project: {mem.project}")
            break
    
    if not found:
        print("❌ Failed to retrieve email via semantic search")
        for mem in memories:
            print(f"  - Found: {mem.ultra_brief}")
        return False
    
    print("\n========== BRIDGE TEST PASSED ==========\n")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_bridge_live())
    exit(0 if success else 1)
