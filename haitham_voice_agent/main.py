"""
Main HVA Module

Implements the main orchestration loop:
Voice Input → STT → LLM Router → Plan Generation → 
User Confirmation → Dispatcher → Tools → TTS Response
"""

import asyncio
import logging
import sys
from pathlib import Path

from .config import Config, validate_config
from .stt import get_stt
from .tts import get_tts
from .llm_router import get_router
from .dispatcher import get_dispatcher

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
    """Haitham Voice Agent - Main orchestrator"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info(f"Initializing HVA v{Config.HVA_VERSION}")
        logger.info("=" * 60)
        
        # Validate configuration
        if not validate_config():
            raise RuntimeError("Configuration validation failed")
        
        # Initialize modules
        self.stt = get_stt()
        self.tts = get_tts()
        self.router = get_router()
        self.dispatcher = get_dispatcher()
        
        # Register tools (will be implemented in later phases)
        # self._register_tools()
        
        logger.info("HVA initialized successfully")
    
    def _register_tools(self):
        """Register all tool modules with dispatcher"""
        # TODO: Implement in Phase 2-4
        # from .tools.files import FileTools
        # from .tools.docs import DocTools
        # from .tools.browser import BrowserTools
        # from .tools.terminal import TerminalTools
        # from .tools.gmail import GmailModule
        # from .tools.memory import MemoryModule
        
        # self.dispatcher.register_tool("files", FileTools())
        # self.dispatcher.register_tool("docs", DocTools())
        # self.dispatcher.register_tool("browser", BrowserTools())
        # self.dispatcher.register_tool("terminal", TerminalTools())
        # self.dispatcher.register_tool("gmail", GmailModule())
        # self.dispatcher.register_tool("memory", MemoryModule())
        
        logger.info("All tools registered")
    
    async def process_voice_command(self, duration: int = 5) -> bool:
        """
        Process a single voice command through the full pipeline
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            bool: True if command processed successfully, False otherwise
        """
        try:
            # 1. Listen for voice input
            logger.info("Listening for voice command...")
            await self.tts.speak("أنا جاهز، تفضل")  # "I'm ready, go ahead"
            
            # 2. Transcribe
            text = await self.stt.listen_and_transcribe(duration=duration)
            logger.info(f"Transcribed: {text}")
            
            if not text or text == "placeholder transcription":
                await self.tts.speak("لم أفهم، من فضلك أعد المحاولة")  # "I didn't understand, please try again"
                return False
            
            # 3. Generate execution plan
            logger.info("Generating execution plan...")
            plan = await self.router.generate_execution_plan(text)
            
            # 4. Confirm with user
            logger.info("Requesting user confirmation...")
            confirmation_text = self._format_plan_for_confirmation(plan)
            await self.tts.speak(confirmation_text)
            
            # Ask for confirmation
            await self.tts.speak("هل تؤكد التنفيذ؟")  # "Do you confirm execution?"
            confirmed = await self.stt.listen_for_confirmation(timeout=10)
            
            if not confirmed:
                logger.info("User rejected execution")
                await self.tts.speak("تم الإلغاء")  # "Cancelled"
                return False
            
            # 5. Execute plan
            logger.info("Executing plan...")
            results = await self.dispatcher.execute_plan(plan)
            
            # 6. Respond with results
            response_text = self._format_results_for_response(results)
            await self.tts.speak(response_text)
            
            logger.info("Command processed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing command: {e}", exc_info=True)
            await self.tts.speak("حدث خطأ، من فضلك حاول مرة أخرى")  # "An error occurred, please try again"
            return False
    
    def _format_plan_for_confirmation(self, plan: dict) -> str:
        """
        Format execution plan for TTS confirmation
        
        Args:
            plan: Execution plan dictionary
            
        Returns:
            str: Formatted text for TTS
        """
        intent = plan.get("intent", "Unknown intent")
        steps_count = len(plan.get("steps", []))
        risks = plan.get("risks", [])
        
        # Detect language from intent
        language = self.stt.detect_language(intent)
        
        if language == "ar":
            text = f"سأقوم بـ: {intent}. "
            text += f"عدد الخطوات: {steps_count}. "
            
            if risks:
                text += f"تحذير: {', '.join(risks)}. "
        else:
            text = f"I will: {intent}. "
            text += f"Number of steps: {steps_count}. "
            
            if risks:
                text += f"Warning: {', '.join(risks)}. "
        
        return text
    
    def _format_results_for_response(self, results: list) -> str:
        """
        Format execution results for TTS response
        
        Args:
            results: List of result dictionaries
            
        Returns:
            str: Formatted text for TTS
        """
        if not results:
            return "لم يتم تنفيذ أي خطوات"  # "No steps executed"
        
        # Check if any errors occurred
        errors = [r for r in results if r.get("error", False)]
        
        if errors:
            error_msg = errors[0].get("message", "Unknown error")
            return f"حدث خطأ: {error_msg}"  # "An error occurred: ..."
        
        # Success
        success_count = len([r for r in results if not r.get("error", False)])
        return f"تم التنفيذ بنجاح. عدد الخطوات المنفذة: {success_count}"  # "Executed successfully. Steps completed: ..."
    
    async def run_interactive(self):
        """
        Run HVA in interactive mode (continuous listening)
        """
        logger.info("Starting interactive mode...")
        await self.tts.speak("مرحبا، أنا HVA جاهز للمساعدة")  # "Hello, I'm HVA ready to help"
        
        try:
            while True:
                success = await self.process_voice_command()
                
                # Small pause between commands
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            await self.tts.speak("إلى اللقاء")  # "Goodbye"
    
    async def run_single_command(self, command_text: str):
        """
        Run a single text command (for testing without voice)
        
        Args:
            command_text: Command text
        """
        logger.info(f"Processing text command: {command_text}")
        
        try:
            # Generate execution plan
            plan = await self.router.generate_execution_plan(command_text)
            logger.info(f"Plan: {plan}")
            
            # Execute (skip confirmation for testing)
            results = await self.dispatcher.execute_plan(plan)
            logger.info(f"Results: {results}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return {"error": True, "message": str(e)}


async def main():
    """Main entry point"""
    try:
        hva = HVA()
        
        # Check if running in test mode
        if len(sys.argv) > 1 and sys.argv[1] == "--test":
            # Test mode: process a single command
            test_command = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "List files in Downloads"
            logger.info(f"Test mode: {test_command}")
            await hva.run_single_command(test_command)
        else:
            # Interactive mode
            await hva.run_interactive()
            
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
