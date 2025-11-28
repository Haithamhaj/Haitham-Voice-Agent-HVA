"""
LLM Router Module

Implements hybrid LLM routing logic:
- Gemini for: PDFs, translation, summarization, image analysis, document processing
- GPT for: JSON outputs, execution plans, tool invocation, memory operations, classification

Follows the routing rules from the Master SRS.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

import openai
import google.generativeai as genai

from .config import Config

logger = logging.getLogger(__name__)


class LLMType(Enum):
    """LLM types"""
    GEMINI = "gemini"
    GPT = "gpt"


class LLMRouter:
    """Hybrid LLM routing system"""
    
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = Config.OPENAI_API_KEY
        self.gpt_model = Config.GPT_MODEL
        
        # Initialize Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Note: Gemini model is now resolved at runtime per request
        
        logger.info(f"LLM Router initialized: GPT={self.gpt_model}")
    
    def route(self, intent: str, context: Optional[Dict[str, Any]] = None) -> LLMType:
        """
        Route request to appropriate LLM based on intent
        
        Args:
            intent: User intent/request
            context: Additional context (e.g., file types, operations)
            
        Returns:
            LLMType: Which LLM to use
        """
        intent_lower = intent.lower()
        
        # Gemini routing rules (from Master SRS)
        gemini_keywords = [
            "pdf", "translate", "translation", "summarize", "summary",
            "compare", "comparison", "analyze", "analysis", "image",
            "photo", "picture", "document", "extract tasks", "read file"
        ]
        
        # GPT routing rules (from Master SRS)
        gpt_keywords = [
            "plan", "execute", "tool", "email", "gmail", "draft",
            "memory", "save", "remember", "classify", "organize",
            "json", "structure", "action", "command"
        ]
        
        # Check for Gemini keywords
        if any(keyword in intent_lower for keyword in gemini_keywords):
            logger.info(f"Routing to Gemini (analytical task): {intent[:50]}...")
            return LLMType.GEMINI
        
        # Check for GPT keywords
        if any(keyword in intent_lower for keyword in gpt_keywords):
            logger.info(f"Routing to GPT (action task): {intent[:50]}...")
            return LLMType.GPT
        
        # Check context for additional hints
        if context:
            if context.get("file_type") in ["pdf", "docx", "image"]:
                return LLMType.GEMINI
            if context.get("requires_json", False):
                return LLMType.GPT
        
        # Default to GPT for ambiguous cases
        logger.info(f"Routing to GPT (default): {intent[:50]}...")
        return LLMType.GPT
    
    async def generate_with_gemini(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        logical_model: str = "logical.gemini.pro"
    ) -> str:
        """
        Generate response using Gemini
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Sampling temperature
            logical_model: Logical model name to use (default: logical.gemini.pro)
            
        Returns:
            str: Generated response
        """
        # Resolve model at runtime
        model_name = Config.resolve_gemini_model(logical_model)
        logger.info(f"Generating with Gemini ({logical_model} -> {model_name})...")
        
        try:
            # Create client for the specific model
            model = genai.GenerativeModel(model_name)
            
            # Combine system instruction and prompt if provided
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature
                )
            )
            
            result = response.text
            logger.debug(f"Gemini response: {result[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    async def generate_with_gpt(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        response_format: Optional[str] = None
    ) -> str:
        """
        Generate response using GPT
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Sampling temperature
            response_format: "json_object" for JSON responses
            
        Returns:
            str: Generated response
        """
        logger.info("Generating with GPT...")
        
        try:
            messages = []
            
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            messages.append({"role": "user", "content": prompt})
            
            # Prepare kwargs
            kwargs = {
                "model": self.gpt_model,
                "messages": messages,
                "temperature": temperature
            }
            
            if response_format == "json_object":
                kwargs["response_format"] = {"type": "json_object"}
            
            # Generate response
            client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
            response = await client.chat.completions.create(**kwargs)
            
            result = response.choices[0].message.content
            logger.debug(f"GPT response: {result[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"GPT generation failed: {e}")
            raise
    
    async def generate_execution_plan(self, user_intent: str) -> Dict[str, Any]:
        """
        Generate execution plan using GPT (always JSON format)
        
        Args:
            user_intent: User's voice command or request
            
        Returns:
            dict: Execution plan with structure:
                {
                    "intent": "...",
                    "steps": [...],
                    "tools": [...],
                    "risks": [...],
                    "requires_confirmation": true
                }
        """
        logger.info(f"Generating execution plan for: {user_intent}")
        
        system_instruction = """
You are an execution planner for HVA (Haitham Voice Agent).
Generate a structured execution plan in JSON format.

The plan must include:
- intent: Clear description of what the user wants
- steps: Array of step objects with {tool, action, params}
- tools: Array of tool names needed
- risks: Array of potential risks or destructive actions
- requires_confirmation: Boolean (true if any destructive action)

Available tools:
- files: list_files, search_files, create_folder, delete_folder, move_file, copy_file
- docs: summarize_file, translate_file, compare_files, extract_tasks, read_pdf
- browser: open_url, search_google
- terminal: (safe commands only: ls, pwd, echo, whoami, df)
- gmail: fetch_latest_email, search_emails, create_draft, send_draft (requires confirmation)
- memory: save_note_local, get_notes_local, semantic_query_local

CRITICAL RULES:
- ALWAYS set requires_confirmation=true for: delete, send email, destructive operations
- NEVER auto-send emails
- Keep steps clear and sequential
"""
        
        prompt = f"""
User request: "{user_intent}"

Generate an execution plan in JSON format.
"""
        
        try:
            response = await self.generate_with_gpt(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.3,  # Lower temperature for structured output
                response_format="json_object"
            )
            
            plan = json.loads(response)
            
            # Validate plan structure
            required_keys = ["intent", "steps", "tools", "requires_confirmation"]
            if not all(key in plan for key in required_keys):
                raise ValueError(f"Invalid plan structure. Missing keys: {required_keys}")
            
            logger.info(f"Execution plan generated: {plan['intent']}")
            return plan
            
        except Exception as e:
            logger.error(f"Failed to generate execution plan: {e}")
            raise
    
    async def summarize_with_gemini(self, text: str, summary_type: str = "brief") -> str:
        """
        Summarize text using Gemini
        
        Args:
            text: Text to summarize
            summary_type: "brief", "detailed", or "multi-level"
            
        Returns:
            str: Summary
        """
        logger.info(f"Summarizing text ({summary_type})...")
        
        if summary_type == "multi-level":
            prompt = f"""
Summarize the following text at 3 levels:

1. Ultra-brief (1 sentence, <20 words)
2. Executive (3-5 bullet points)
3. Detailed (1-2 paragraphs)

Text:
{text}

Format your response as:
ULTRA-BRIEF: ...
EXECUTIVE:
- ...
- ...
DETAILED: ...
"""
        else:
            length = "concise" if summary_type == "brief" else "detailed"
            prompt = f"Provide a {length} summary of the following text:\n\n{text}"
        
        return await self.generate_with_gemini(prompt, temperature=0.5)
    
    async def translate_with_gemini(self, text: str, target_language: str) -> str:
        """
        Translate text using Gemini
        
        Args:
            text: Text to translate
            target_language: Target language code (ar, en, etc.)
            
        Returns:
            str: Translated text
        """
        logger.info(f"Translating to {target_language}...")
        
        lang_names = {"ar": "Arabic", "en": "English", "es": "Spanish", "fr": "French"}
        target_lang_name = lang_names.get(target_language, target_language)
        
        prompt = f"Translate the following text to {target_lang_name}:\n\n{text}"
        
        return await self.generate_with_gemini(prompt, temperature=0.3)
    
    async def classify_with_gpt(self, text: str, categories: List[str]) -> Dict[str, Any]:
        """
        Classify text using GPT
        
        Args:
            text: Text to classify
            categories: List of possible categories
            
        Returns:
            dict: Classification result with category and confidence
        """
        logger.info("Classifying text...")
        
        prompt = f"""
Classify the following text into one of these categories: {', '.join(categories)}

Text: {text}

Respond in JSON format:
{{
    "category": "...",
    "confidence": 0.0-1.0,
    "reasoning": "..."
}}
"""
        
        response = await self.generate_with_gpt(
            prompt=prompt,
            temperature=0.3,
            response_format="json_object"
        )
        
        return json.loads(response)


# Singleton instance
_router_instance: Optional[LLMRouter] = None


def get_router() -> LLMRouter:
    """Get singleton LLM router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance


if __name__ == "__main__":
    # Test LLM router
    async def test():
        router = get_router()
        
        print("Testing LLM Router...")
        
        # Test routing
        test_intents = [
            "Summarize this PDF file",
            "Create a draft email to John",
            "Translate this text to Arabic",
            "Save this idea to memory",
            "List files in Downloads folder"
        ]
        
        print("\nTesting routing logic:")
        for intent in test_intents:
            llm_type = router.route(intent)
            print(f"  '{intent}' -> {llm_type.value}")
        
        # Test execution plan generation
        print("\nTesting execution plan generation:")
        plan = await router.generate_execution_plan("Read my latest email and save important points to memory")
        print(json.dumps(plan, indent=2))
        
        print("\nLLM Router test completed")
    
    asyncio.run(test())
