"""
Email LLM Helpers

LLM-enhanced email operations using Gemini and GPT.
From Gmail Module SRS Section 4.7.

Routing:
- Gemini: Summarization, action extraction, translation, sentiment analysis
- GPT: Smart reply generation (JSON-friendly outputs)
"""

import logging
from typing import Dict, Any, List, Optional
import json

from ...llm_router import get_router
from . import email_prompts as prompts

logger = logging.getLogger(__name__)


class EmailLLMHelpers:
    """
    LLM-enhanced email operations
    
    Public Functions:
    - summarize_email_content: Summarize email (Gemini)
    - extract_email_actions: Extract action items (Gemini)
    - generate_reply_suggestion: Generate smart reply (GPT)
    - translate_email_content: Translate email (Gemini)
    - analyze_email_sentiment: Analyze sentiment (Gemini)
    """
    
    def __init__(self):
        self.router = get_router()
        logger.info("EmailLLMHelpers initialized")
    
    # ==================== SUMMARIZATION (Gemini) ====================
    
    async def summarize_email_content(
        self,
        email_text: str,
        detailed: bool = False
    ) -> Dict[str, Any]:
        """
        Summarize email content using Gemini
        
        Args:
            email_text: Email body text
            detailed: If True, provide detailed summary
            
        Returns:
            dict: Summary result with text and metadata
        """
        try:
            logger.info("Summarizing email with Gemini...")
            
            # Select prompt
            if detailed:
                prompt = prompts.SUMMARIZE_EMAIL_DETAILED_PROMPT.format(
                    email_text=email_text
                )
            else:
                prompt = prompts.SUMMARIZE_EMAIL_PROMPT.format(
                    email_text=email_text
                )
            
            # Generate summary using Gemini
            summary = await self.router.generate_with_gemini(
                prompt=prompt,
                temperature=0.5
            )
            
            logger.info("Email summarization complete")
            logger.debug(f"Used model: Gemini")
            
            return {
                "summary": summary.strip(),
                "model": "gemini",
                "detailed": detailed
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def summarize_thread(
        self,
        thread_messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Summarize email thread using Gemini
        
        Args:
            thread_messages: List of messages with 'from', 'date', 'body'
            
        Returns:
            dict: Thread summary
        """
        try:
            logger.info(f"Summarizing thread with {len(thread_messages)} messages...")
            
            # Format thread
            thread_text = "\n\n---\n\n".join([
                f"From: {msg.get('from', 'Unknown')}\nDate: {msg.get('date', 'Unknown')}\n\n{msg.get('body', '')}"
                for msg in thread_messages
            ])
            
            prompt = prompts.SUMMARIZE_THREAD_PROMPT.format(
                thread_text=thread_text
            )
            
            # Generate summary using Gemini
            summary = await self.router.generate_with_gemini(
                prompt=prompt,
                temperature=0.5
            )
            
            logger.info("Thread summarization complete")
            logger.debug(f"Used model: Gemini")
            
            return {
                "summary": summary.strip(),
                "model": "gemini",
                "message_count": len(thread_messages)
            }
            
        except Exception as e:
            logger.error(f"Thread summarization failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    # ==================== ACTION EXTRACTION (Gemini) ====================
    
    async def extract_email_actions(
        self,
        email_text: str
    ) -> Dict[str, Any]:
        """
        Extract action items from email using Gemini
        
        Args:
            email_text: Email body text
            
        Returns:
            dict: Extracted actions with metadata
        """
        try:
            logger.info("Extracting action items with Gemini...")
            
            prompt = prompts.EXTRACT_ACTIONS_PROMPT.format(
                email_text=email_text
            )
            
            # Extract actions using Gemini
            actions_text = await self.router.generate_with_gemini(
                prompt=prompt,
                temperature=0.3
            )
            
            logger.info("Action extraction complete")
            logger.debug(f"Used model: Gemini")
            
            return {
                "actions": actions_text.strip(),
                "model": "gemini",
                "has_actions": "No action items" not in actions_text
            }
            
        except Exception as e:
            logger.error(f"Action extraction failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    async def extract_thread_actions(
        self,
        thread_messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Extract action items from email thread using Gemini
        
        Args:
            thread_messages: List of messages
            
        Returns:
            dict: Extracted actions
        """
        try:
            logger.info(f"Extracting actions from thread with {len(thread_messages)} messages...")
            
            # Format thread
            thread_text = "\n\n---\n\n".join([
                f"From: {msg.get('from', 'Unknown')}\nDate: {msg.get('date', 'Unknown')}\n\n{msg.get('body', '')}"
                for msg in thread_messages
            ])
            
            prompt = prompts.EXTRACT_ACTIONS_THREAD_PROMPT.format(
                thread_text=thread_text
            )
            
            # Extract actions using Gemini
            actions_text = await self.router.generate_with_gemini(
                prompt=prompt,
                temperature=0.3
            )
            
            logger.info("Thread action extraction complete")
            logger.debug(f"Used model: Gemini")
            
            return {
                "actions": actions_text.strip(),
                "model": "gemini",
                "message_count": len(thread_messages)
            }
            
        except Exception as e:
            logger.error(f"Thread action extraction failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    # ==================== SMART REPLY (GPT) ====================
    
    async def generate_reply_suggestion(
        self,
        from_email: str,
        subject: str,
        body: str,
        style: str = "professional",
        tone: str = "neutral",
        reply_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate smart reply suggestion using GPT
        
        Args:
            from_email: Sender email
            subject: Email subject
            body: Email body
            style: Reply style (professional, casual, brief, detailed)
            tone: Reply tone (positive, neutral, apologetic, grateful)
            reply_type: Type of reply (accept, decline, acknowledge, request_info, general)
            
        Returns:
            dict: Reply suggestion with metadata
        """
        try:
            logger.info(f"Generating {style} reply with GPT...")
            
            # Get style descriptions
            style_desc = prompts.get_reply_style_description(style)
            tone_desc = prompts.get_reply_tone_description(tone)
            reply_type_desc = prompts.get_reply_type_description(reply_type)
            
            prompt = prompts.GENERATE_REPLY_PROMPT.format(
                from_email=from_email,
                subject=subject,
                body=body,
                style=style_desc,
                tone=tone_desc,
                reply_type=reply_type_desc
            )
            
            # Generate reply using GPT
            reply = await self.router.generate_with_gpt(
                prompt=prompt,
                temperature=0.7
            )
            
            logger.info("Reply generation complete")
            logger.debug(f"Used model: GPT")
            
            return {
                "reply": reply.strip(),
                "model": "gpt",
                "style": style,
                "tone": tone,
                "reply_type": reply_type
            }
            
        except Exception as e:
            logger.error(f"Reply generation failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    # ==================== TRANSLATION (Gemini) ====================
    
    async def translate_email_content(
        self,
        email_text: str,
        target_language: str
    ) -> Dict[str, Any]:
        """
        Translate email content using Gemini
        
        Args:
            email_text: Email body text
            target_language: Target language code (ar, en, es, fr, etc.)
            
        Returns:
            dict: Translation result
        """
        try:
            logger.info(f"Translating email to {target_language} with Gemini...")
            
            # Get language name
            lang_name = prompts.get_language_name(target_language)
            
            prompt = prompts.TRANSLATE_EMAIL_PROMPT.format(
                target_language=lang_name,
                email_text=email_text
            )
            
            # Translate using Gemini
            translated = await self.router.generate_with_gemini(
                prompt=prompt,
                temperature=0.3
            )
            
            logger.info("Email translation complete")
            logger.debug(f"Used model: Gemini")
            
            return {
                "translated_text": translated.strip(),
                "model": "gemini",
                "target_language": target_language,
                "language_name": lang_name
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }
    
    # ==================== SENTIMENT ANALYSIS (Gemini) ====================
    
    async def analyze_email_sentiment(
        self,
        email_text: str
    ) -> Dict[str, Any]:
        """
        Analyze email sentiment using Gemini
        
        Args:
            email_text: Email body text
            
        Returns:
            dict: Sentiment analysis result
        """
        try:
            logger.info("Analyzing email sentiment with Gemini...")
            
            prompt = prompts.ANALYZE_SENTIMENT_PROMPT.format(
                email_text=email_text
            )
            
            # Analyze using Gemini
            analysis = await self.router.generate_with_gemini(
                prompt=prompt,
                temperature=0.3
            )
            
            logger.info("Sentiment analysis complete")
            logger.debug(f"Used model: Gemini")
            
            return {
                "analysis": analysis.strip(),
                "model": "gemini"
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "error": True,
                "message": str(e)
            }


# Singleton instance
_email_llm_helpers: Optional[EmailLLMHelpers] = None


def get_email_llm_helpers() -> EmailLLMHelpers:
    """Get singleton EmailLLMHelpers instance"""
    global _email_llm_helpers
    if _email_llm_helpers is None:
        _email_llm_helpers = EmailLLMHelpers()
    return _email_llm_helpers


if __name__ == "__main__":
    # Test email LLM helpers
    import asyncio
    
    async def test():
        helpers = get_email_llm_helpers()
        
        print("Testing EmailLLMHelpers...")
        
        # Test email text
        test_email = """
        Hi Team,
        
        I wanted to follow up on the project timeline we discussed last week.
        We need to:
        1. Complete the design mockups by Friday
        2. Review the API documentation
        3. Schedule a meeting with the client next Tuesday
        
        Please let me know if you have any questions.
        
        Best regards,
        John
        """
        
        # Test summarization
        print("\n1. Testing summarization (Gemini)...")
        result = await helpers.summarize_email_content(test_email)
        if not result.get("error"):
            print(f"✓ Summary: {result['summary'][:100]}...")
            print(f"  Model: {result['model']}")
        
        # Test action extraction
        print("\n2. Testing action extraction (Gemini)...")
        result = await helpers.extract_email_actions(test_email)
        if not result.get("error"):
            print(f"✓ Actions found: {result['has_actions']}")
            print(f"  Model: {result['model']}")
        
        # Test reply generation
        print("\n3. Testing reply generation (GPT)...")
        result = await helpers.generate_reply_suggestion(
            from_email="john@example.com",
            subject="Project Timeline",
            body=test_email,
            style="professional",
            tone="positive"
        )
        if not result.get("error"):
            print(f"✓ Reply generated")
            print(f"  Model: {result['model']}")
            print(f"  Style: {result['style']}")
        
        # Test translation
        print("\n4. Testing translation (Gemini)...")
        result = await helpers.translate_email_content(test_email, "ar")
        if not result.get("error"):
            print(f"✓ Translated to: {result['language_name']}")
            print(f"  Model: {result['model']}")
        
        print("\nEmailLLMHelpers test completed")
    
    asyncio.run(test())
