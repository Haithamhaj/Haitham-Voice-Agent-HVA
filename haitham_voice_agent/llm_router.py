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
from .token_tracker import get_tracker

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
        logical_model: str = "logical.gemini.pro",
        usage_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate response using Gemini
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Sampling temperature
            logical_model: Logical model name to use (default: logical.gemini.pro)
            usage_context: Optional context for usage tracking
            
        Returns:
            dict: {"content": str, "model": str}
        """
        # Resolve model at runtime
        model_name = Config.resolve_gemini_model(logical_model)
        logger.info(f"[LLMRouter] Gemini: {logical_model} -> {model_name}")
        
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
            
            # Track Usage
            usage_data = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
            try:
                # Gemini doesn't always return token counts in simple response, 
                # but we can estimate or check usage_metadata if available.
                # usage_metadata is available in recent versions.
                usage = response.usage_metadata
                input_tokens = usage.prompt_token_count if usage else len(full_prompt) // 4
                output_tokens = usage.candidates_token_count if usage else len(result) // 4
                
                context = {"method": "generate_with_gemini"}
                if usage_context:
                    context.update(usage_context)

                tracker = get_tracker()
                cost = tracker.calculate_cost(model_name, input_tokens, output_tokens)
                
                await tracker.track_usage(
                    model=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    context=context
                )
                
                usage_data = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": cost
                }
            except Exception as e:
                logger.warning(f"Failed to track Gemini usage: {e}")

            logger.debug(f"Gemini response: {result[:100]}...")
            return {"content": result, "model": model_name, "usage": usage_data}
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    async def generate_with_gpt(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        response_format: Optional[str] = None,
        logical_model: str = "logical.mini",
        usage_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate response using GPT
        
        Args:
            prompt: User prompt
            system_instruction: System instruction (optional)
            temperature: Sampling temperature
            response_format: "json_object" for JSON responses
            logical_model: Logical model name (default: logical.mini -> gpt-4o)
            usage_context: Optional context for usage tracking
            
        Returns:
            dict: {"content": str, "model": str}
        """
        # Resolve model
        model_name = Config.resolve_model(logical_model)
        logger.info(f"Generating with GPT ({logical_model} -> {model_name})...")
        
        try:
            messages = []
            
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            messages.append({"role": "user", "content": prompt})
            
            # Prepare kwargs
            kwargs = {
                "model": model_name,
                "messages": messages,
            }
            
            # OpenAI o1 models (and gpt-5 placeholder if aliased) do not support temperature != 1
            # They also don't support system messages in some versions, but the error here is specific to temperature.
            is_reasoning_model = model_name.startswith("o1") or model_name.startswith("gpt-5")
            
            if not is_reasoning_model:
                kwargs["temperature"] = temperature
            else:
                logger.info(f"Skipping temperature for reasoning model: {model_name}")
            
            if response_format == "json_object":
                # o1 models currently don't support response_format="json_object" in all tiers
                # But if it's gpt-4o it does.
                # If it's o1, we should probably rely on prompt engineering for JSON or use a different model for structured output.
                # For now, let's keep it but be aware.
                if not is_reasoning_model:
                     kwargs["response_format"] = {"type": "json_object"}
                else:
                    # For o1, we append "Respond in JSON" to the prompt if not already there
                    # But generate_execution_plan uses system prompt for that.
                    pass
            
            # Generate response
            client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
            response = await client.chat.completions.create(**kwargs)
            
            result = response.choices[0].message.content
            
            # Track Usage
            usage_data = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
            try:
                usage = response.usage
                if usage:
                    context = {"method": "generate_with_gpt"}
                    if usage_context:
                        context.update(usage_context)

                    tracker = get_tracker()
                    cost = tracker.calculate_cost(model_name, usage.prompt_tokens, usage.completion_tokens)
                    
                    await tracker.track_usage(
                        model=model_name,
                        input_tokens=usage.prompt_tokens,
                        output_tokens=usage.completion_tokens,
                        context=context
                    )
                    
                    usage_data = {
                        "input_tokens": usage.prompt_tokens,
                        "output_tokens": usage.completion_tokens,
                        "cost": cost
                    }
            except Exception as e:
                logger.warning(f"Failed to track GPT usage: {e}")

            logger.debug(f"GPT response: {result[:100]}...")
            return {"content": result, "model": model_name, "usage": usage_data}
            
        except Exception as e:
            logger.error(f"GPT generation failed: {e}")
            raise
    
    async def generate_execution_plan(self, user_intent: str) -> Dict[str, Any]:
        system_instruction = """
You are the Executive Planner for Haitham Voice Agent.
Your job is to break down user requests into a sequence of tool executions.

AVAILABLE TOOLS:
1. files: open_file (for files AND folders), list_files, move_file, delete_file, read_file, organize_documents
2. system: open_app, system_status, set_volume, mute, unmute
3. memory: save_note, search_memory, get_last_note
4. gmail: fetch_latest_email, send_email, draft_email
5. calendar: list_events, create_event, check_availability
6. tasks: list_tasks, add_task, complete_task
7. advisor: ask_advisor (for safety checks or opinions)
8. system_sentry: check_health, find_hogs, clean_cache
9. pricing_tools: update_pricing, check_pricing_updates

RESPONSE FORMAT:
Respond with a JSON object:
{
    "intent": "Short description of intent",
    "steps": [
        {
            "tool": "tool_name",
            "action": "action_name",
            "params": { ... }
        }
    ],
    "tools": ["tool1", "tool2"],
    "requires_confirmation": boolean
}
"""
        prompt = f"User Request: {user_intent}\n\nCreate an execution plan."
        try:
            response_data = await self.generate_with_gpt(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.3,
                response_format="json_object",
                usage_context={"intent": user_intent, "action": "planning"}
            )
            # ...
            
            plan = json.loads(response_data["content"])
            
            # Validate plan structure
            required_keys = ["intent", "steps", "tools", "requires_confirmation"]
            if not all(key in plan for key in required_keys):
                raise ValueError(f"Invalid plan structure. Missing keys: {required_keys}")
            
            logger.info(f"Execution plan generated: {plan['intent']}")
            return plan
            
        except Exception as e:
            logger.error(f"Failed to generate execution plan: {e}")
            raise
    
    async def summarize_with_gemini(self, text: str, summary_type: str = "brief") -> Dict[str, str]:
        """
        Summarize text using Gemini
        
        Args:
            text: Text to summarize
            summary_type: "brief", "detailed", or "multi-level"
            
        Returns:
            dict: {"content": str, "model": str}
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
    
    async def translate_with_gemini(self, text: str, target_language: str) -> Dict[str, str]:
        """
        Translate text using Gemini
        
        Args:
            text: Text to translate
            target_language: Target language code (ar, en, etc.)
            
        Returns:
            dict: {"content": str, "model": str}
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
