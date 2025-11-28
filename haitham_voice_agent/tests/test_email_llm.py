"""
Tests for Email LLM Helpers
"""

import pytest
import asyncio
from haitham_voice_agent.tools.gmail.email_llm import get_email_llm_helpers


# Test data
TEST_EMAIL = """
Hi Team,

I wanted to follow up on the Q4 project timeline we discussed in yesterday's meeting.

Action Items:
1. Sarah - Complete the design mockups by Friday, December 1st
2. Mike - Review and update the API documentation by next Monday
3. Everyone - Please review the requirements doc I sent earlier

We also need to schedule a client meeting for next Tuesday at 2 PM to present our progress.

Let me know if you have any questions or concerns.

Best regards,
John Smith
Project Manager
"""

TEST_THREAD = [
    {
        "from": "john@example.com",
        "date": "2024-11-20",
        "body": "Hi team, we need to finalize the project scope by Friday."
    },
    {
        "from": "sarah@example.com",
        "date": "2024-11-21",
        "body": "I can have the design ready by Thursday. Mike, can you review?"
    },
    {
        "from": "mike@example.com",
        "date": "2024-11-22",
        "body": "Yes, I'll review on Thursday evening and provide feedback Friday morning."
    }
]


@pytest.fixture
def llm_helpers():
    """Get EmailLLMHelpers instance"""
    return get_email_llm_helpers()


# ==================== SUMMARIZATION TESTS ====================

@pytest.mark.asyncio
async def test_summarize_email_basic(llm_helpers):
    """Test basic email summarization"""
    result = await llm_helpers.summarize_email_content(TEST_EMAIL)
    
    assert not result.get("error"), f"Summarization failed: {result.get('message')}"
    assert "summary" in result
    assert result["model"] == "gemini"
    assert len(result["summary"]) > 0
    assert len(result["summary"]) < len(TEST_EMAIL)  # Summary should be shorter
    
    print(f"\n✓ Basic Summary: {result['summary'][:100]}...")


@pytest.mark.asyncio
async def test_summarize_email_detailed(llm_helpers):
    """Test detailed email summarization"""
    result = await llm_helpers.summarize_email_content(TEST_EMAIL, detailed=True)
    
    assert not result.get("error")
    assert "summary" in result
    assert result["model"] == "gemini"
    assert result["detailed"] is True
    
    # Detailed summary should be longer
    basic_result = await llm_helpers.summarize_email_content(TEST_EMAIL, detailed=False)
    assert len(result["summary"]) >= len(basic_result["summary"])
    
    print(f"\n✓ Detailed Summary generated")


@pytest.mark.asyncio
async def test_summarize_thread(llm_helpers):
    """Test thread summarization"""
    result = await llm_helpers.summarize_thread(TEST_THREAD)
    
    assert not result.get("error")
    assert "summary" in result
    assert result["model"] == "gemini"
    assert result["message_count"] == 3
    
    print(f"\n✓ Thread Summary: {result['summary'][:100]}...")


# ==================== ACTION EXTRACTION TESTS ====================

@pytest.mark.asyncio
async def test_extract_actions(llm_helpers):
    """Test action item extraction"""
    result = await llm_helpers.extract_email_actions(TEST_EMAIL)
    
    assert not result.get("error")
    assert "actions" in result
    assert result["model"] == "gemini"
    assert result["has_actions"] is True
    
    # Check that key action items are mentioned
    actions_text = result["actions"].lower()
    assert "sarah" in actions_text or "design" in actions_text
    assert "mike" in actions_text or "api" in actions_text
    
    print(f"\n✓ Actions extracted: {result['has_actions']}")


@pytest.mark.asyncio
async def test_extract_actions_none(llm_helpers):
    """Test action extraction with no actions"""
    no_action_email = "Hi, just wanted to say thanks for the update. Have a great day!"
    
    result = await llm_helpers.extract_email_actions(no_action_email)
    
    assert not result.get("error")
    assert "actions" in result
    # Should detect no actions
    assert result["has_actions"] is False or "no action" in result["actions"].lower()
    
    print(f"\n✓ No actions detected correctly")


@pytest.mark.asyncio
async def test_extract_thread_actions(llm_helpers):
    """Test action extraction from thread"""
    result = await llm_helpers.extract_thread_actions(TEST_THREAD)
    
    assert not result.get("error")
    assert "actions" in result
    assert result["model"] == "gemini"
    assert result["message_count"] == 3
    
    print(f"\n✓ Thread actions extracted")


# ==================== SMART REPLY TESTS ====================

@pytest.mark.asyncio
async def test_generate_reply_professional(llm_helpers):
    """Test professional reply generation"""
    result = await llm_helpers.generate_reply_suggestion(
        from_email="john@example.com",
        subject="Project Timeline",
        body=TEST_EMAIL,
        style="professional",
        tone="neutral"
    )
    
    assert not result.get("error")
    assert "reply" in result
    assert result["model"] == "gpt"
    assert result["style"] == "professional"
    assert result["tone"] == "neutral"
    assert len(result["reply"]) > 0
    
    # Reply should not contain hallucinated links or tools
    assert "http://" not in result["reply"] or "example.com" in result["reply"]
    
    print(f"\n✓ Professional reply generated")


@pytest.mark.asyncio
async def test_generate_reply_styles(llm_helpers):
    """Test different reply styles"""
    styles = ["professional", "casual", "brief"]
    
    for style in styles:
        result = await llm_helpers.generate_reply_suggestion(
            from_email="test@example.com",
            subject="Test",
            body="Quick question about the project.",
            style=style,
            tone="neutral"
        )
        
        assert not result.get("error"), f"Failed for style: {style}"
        assert result["style"] == style
        
        print(f"\n✓ {style.capitalize()} reply generated")


@pytest.mark.asyncio
async def test_generate_reply_types(llm_helpers):
    """Test different reply types"""
    reply_types = ["accept", "decline", "acknowledge"]
    
    for reply_type in reply_types:
        result = await llm_helpers.generate_reply_suggestion(
            from_email="test@example.com",
            subject="Meeting Invitation",
            body="Would you like to join our meeting on Friday?",
            reply_type=reply_type
        )
        
        assert not result.get("error"), f"Failed for type: {reply_type}"
        assert result["reply_type"] == reply_type
        
        print(f"\n✓ {reply_type.capitalize()} reply generated")


# ==================== TRANSLATION TESTS ====================

@pytest.mark.asyncio
async def test_translate_to_arabic(llm_helpers):
    """Test translation to Arabic"""
    english_text = "Hello, how are you? I hope you are doing well."
    
    result = await llm_helpers.translate_email_content(english_text, "ar")
    
    assert not result.get("error")
    assert "translated_text" in result
    assert result["model"] == "gemini"
    assert result["target_language"] == "ar"
    assert result["language_name"] == "Arabic"
    
    # Translated text should be different from original
    assert result["translated_text"] != english_text
    
    print(f"\n✓ Translated to Arabic")


@pytest.mark.asyncio
async def test_translate_to_spanish(llm_helpers):
    """Test translation to Spanish"""
    english_text = "Thank you for your email. I will review it soon."
    
    result = await llm_helpers.translate_email_content(english_text, "es")
    
    assert not result.get("error")
    assert result["target_language"] == "es"
    assert result["language_name"] == "Spanish"
    
    print(f"\n✓ Translated to Spanish")


# ==================== SENTIMENT ANALYSIS TESTS ====================

@pytest.mark.asyncio
async def test_analyze_sentiment(llm_helpers):
    """Test sentiment analysis"""
    result = await llm_helpers.analyze_email_sentiment(TEST_EMAIL)
    
    assert not result.get("error")
    assert "analysis" in result
    assert result["model"] == "gemini"
    assert len(result["analysis"]) > 0
    
    print(f"\n✓ Sentiment analyzed")


@pytest.mark.asyncio
async def test_analyze_sentiment_positive(llm_helpers):
    """Test sentiment analysis on positive email"""
    positive_email = "Thank you so much! This is exactly what we needed. Great work!"
    
    result = await llm_helpers.analyze_email_sentiment(positive_email)
    
    assert not result.get("error")
    # Should detect positive sentiment
    analysis_lower = result["analysis"].lower()
    assert "positive" in analysis_lower or "enthusiastic" in analysis_lower
    
    print(f"\n✓ Positive sentiment detected")


@pytest.mark.asyncio
async def test_analyze_sentiment_urgent(llm_helpers):
    """Test sentiment analysis on urgent email"""
    urgent_email = "URGENT: We need this completed by end of day today!"
    
    result = await llm_helpers.analyze_email_sentiment(urgent_email)
    
    assert not result.get("error")
    # Should detect urgency
    analysis_lower = result["analysis"].lower()
    assert "urgent" in analysis_lower or "high" in analysis_lower
    
    print(f"\n✓ Urgency detected")


# ==================== ERROR HANDLING TESTS ====================

@pytest.mark.asyncio
async def test_empty_email_handling(llm_helpers):
    """Test handling of empty email"""
    result = await llm_helpers.summarize_email_content("")
    
    # Should handle gracefully (either error or empty summary)
    assert "summary" in result or "error" in result
    
    print(f"\n✓ Empty email handled")


@pytest.mark.asyncio
async def test_very_long_email(llm_helpers):
    """Test handling of very long email"""
    long_email = "This is a test email. " * 1000  # Very long email
    
    result = await llm_helpers.summarize_email_content(long_email)
    
    assert not result.get("error")
    assert "summary" in result
    # Summary should be much shorter than original
    assert len(result["summary"]) < len(long_email) / 10
    
    print(f"\n✓ Long email summarized")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
