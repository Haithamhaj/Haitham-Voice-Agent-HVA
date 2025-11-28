"""
Haitham Voice Agent - Main Entry Point

The Voice Loop:
1. Listen: Capture audio via STT
2. Route: Send text to LLM Router  
3. Plan: Receive execution plan (JSON)
4. Confirm: Speak plan → Listen for "Yes"
5. Execute: Run tools → Speak result
"""

import asyncio
import logging
import sys
import json
from typing import Optional

from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.voice import STT, TTS
from haitham_voice_agent.llm_router import LLMRouter
from haitham_voice_agent.tools.memory.voice_tools import VoiceMemoryTools
from haitham_voice_agent.tools.gmail.connection_manager import ConnectionManager

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class HVA:
    """Haitham Voice Agent - Main Orchestrator"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info(f"Initializing HVA v{Config.HVA_VERSION}")
        logger.info("=" * 60)
        
        # Validate configuration
        if not Config.validate():
            raise RuntimeError("Configuration validation failed")
        
        # Initialize Gemini mapping at startup
        logger.info("Initializing Gemini model discovery...")
        Config.init_gemini_mapping()
        
        # Initialize voice
        self.stt = STT()
        self.tts = TTS()
        
        # Initialize LLM
        self.router = LLMRouter()
        
        # Initialize tools
        self.memory_tools = VoiceMemoryTools()
        self.gmail = ConnectionManager()
        
        # Default language
        self.language = "ar"  # Arabic by default
        
        logger.info("HVA initialized successfully")
    
    async def initialize_async(self):
        """Initialize async components"""
        await self.memory_tools.ensure_initialized()
        logger.info("Async components initialized")
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """
        Listen for voice input and transcribe.
        
        Returns:
            str: Transcribed text or None
        """
        logger.info("Listening...")
        text = self.stt.listen(language=self.language, timeout=timeout)
        
        if text:
            logger.info(f"Heard: {text}")
        else:
            logger.warning("No speech detected")
        
        return text
    
    def speak(self, text: str):
        """Speak text using TTS"""
        self.tts.speak(text, language=self.language)
    
    async def route_and_plan(self, user_text: str) -> dict:
        """
        Route user input to LLM and generate execution plan.
        
        Args:
            user_text: User's spoken command
            
        Returns:
            dict: Execution plan with intent, steps, and parameters
        """
        logger.info("Generating execution plan...")
        
        # Use GPT for planning (tool calling, JSON output)
        prompt = f"""
You are HVA, a voice assistant. The user said: "{user_text}"

Analyze the intent and generate an execution plan.

Return JSON:
{{
    "intent": "Brief description of what user wants",
    "tool": "memory|gmail|other",
    "action": "save_note|search|fetch_email|send_email|other",
    "parameters": {{}},
    "confirmation_needed": true/false
}}

Examples:
- "احفظ ملاحظة عن اجتماع اليوم" → {{"intent": "Save meeting note", "tool": "memory", "action": "save_note", ...}}
- "اجلب آخر إيميل" → {{"intent": "Fetch latest email", "tool": "gmail", "action": "fetch_email", ...}}
- "ابحث عن Mind-Q" → {{"intent": "Search memories about Mind-Q", "tool": "memory", "action": "search", ...}}
"""
        
        response = await self.router.generate_with_gpt(prompt, temperature=0.3)
        
        # Parse JSON
        try:
            if isinstance(response, str):
                # Clean markdown code blocks
                clean = response.replace("```json", "").replace("```", "").strip()
                plan = json.loads(clean)
            else:
                plan = response
            
            logger.info(f"Plan: {plan}")
            return plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan: {e}")
            return {
                "intent": "Unknown",
                "tool": "other",
                "action": "error",
                "parameters": {},
                "confirmation_needed": False
            }
    
    def confirm_plan(self, plan: dict) -> bool:
        """
        Speak the plan and ask for confirmation.
        
        Returns:
            bool: True if confirmed, False otherwise
        """
        intent = plan.get("intent", "Unknown action")
        
        # Speak intent
        if self.language == "ar":
            self.speak(f"سأقوم بـ: {intent}. هل تؤكد؟")
        else:
            self.speak(f"I will: {intent}. Do you confirm?")
        
        # Listen for confirmation
        response = self.listen(timeout=5)
        
        if not response:
            return False
        
        # Check for affirmative words
        affirmative_ar = ["نعم", "أكد", "موافق", "تمام", "اه"]
        affirmative_en = ["yes", "confirm", "ok", "sure", "yeah"]
        
        response_lower = response.lower()
        
        if self.language == "ar":
            return any(word in response_lower for word in affirmative_ar)
        else:
            return any(word in response_lower for word in affirmative_en)
    
    async def execute_plan(self, plan: dict) -> dict:
        """
        Execute the plan by calling appropriate tools.
        
        Returns:
            dict: Execution result
        """
        tool = plan.get("tool", "other")
        action = plan.get("action", "unknown")
        params = plan.get("parameters", {})
        
        logger.info(f"Executing: {tool}.{action}")
        
        try:
            # Route to appropriate tool
            if tool == "memory":
                return await self._execute_memory_action(action, params, plan)
            elif tool == "gmail":
                return await self._execute_gmail_action(action, params)
            else:
                return {"success": False, "message": "Unknown tool"}
                
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {"success": False, "message": str(e)}
    
    async def _execute_memory_action(self, action: str, params: dict, plan: dict) -> dict:
        """Execute memory-related actions"""
        if action == "save_note":
            # Extract content from plan intent or params
            content = params.get("content") or plan.get("intent", "")
            result = await self.memory_tools.process_voice_note(content)
            return result
        
        elif action == "search":
            query = params.get("query") or plan.get("intent", "")
            response = await self.memory_tools.search_memory_voice(query)
            return {"success": True, "message": response}
        
        else:
            return {"success": False, "message": f"Unknown memory action: {action}"}
    
    async def _execute_gmail_action(self, action: str, params: dict) -> dict:
        """Execute Gmail-related actions"""
        if action == "fetch_email":
            email = self.gmail.fetch_latest_email()
            if email:
                summary = f"From: {email['from']}, Subject: {email['subject']}"
                return {"success": True, "message": summary}
            else:
                return {"success": False, "message": "No emails found"}
        
        else:
            return {"success": False, "message": f"Unknown Gmail action: {action}"}
    
    async def process_command(self) -> bool:
        """
        Process a single voice command through the full pipeline.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # 1. Listen
            self.speak("نعم؟" if self.language == "ar" else "Yes?")
            user_text = self.listen()
            
            if not user_text:
                self.speak("لم أسمع شيئاً" if self.language == "ar" else "I didn't hear anything")
                return False
            
            # 2. Route & Plan
            plan = await self.route_and_plan(user_text)
            
            # 3. Confirm (if needed)
            if plan.get("confirmation_needed", True):
                if not self.confirm_plan(plan):
                    self.speak("تم الإلغاء" if self.language == "ar" else "Cancelled")
                    return False
            
            # 4. Execute
            result = await self.execute_plan(plan)
            
            # 5. Respond
            if result.get("success"):
                message = result.get("message", "تم" if self.language == "ar" else "Done")
                self.speak(message)
                return True
            else:
                error_msg = result.get("message", "خطأ" if self.language == "ar" else "Error")
                self.speak(f"خطأ: {error_msg}" if self.language == "ar" else f"Error: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Command processing error: {e}", exc_info=True)
            self.speak("حدث خطأ" if self.language == "ar" else "An error occurred")
            return False
    
    async def run_interactive(self):
        """Run HVA in interactive mode (continuous listening)"""
        logger.info("Starting interactive mode...")
        self.speak("مرحباً، أنا HVA جاهز للمساعدة" if self.language == "ar" else "Hello, I'm HVA ready to help")
        
        try:
            while True:
                await self.process_command()
                await asyncio.sleep(1)  # Brief pause between commands
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.speak("إلى اللقاء" if self.language == "ar" else "Goodbye")


async def main():
    """Main entry point"""
    try:
        hva = HVA()
        await hva.initialize_async()
        
        # Check for test mode
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            # Test mode: process a single text command
            test_text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "احفظ ملاحظة عن اجتماع اليوم"
            logger.info(f"Test mode: {test_text}")
            
            plan = await hva.route_and_plan(test_text)
            result = await hva.execute_plan(plan)
            logger.info(f"Result: {result}")
        else:
            # Interactive mode
            await hva.run_interactive()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
