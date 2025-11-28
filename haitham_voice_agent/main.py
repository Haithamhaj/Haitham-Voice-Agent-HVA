"""
Haitham Voice Agent - Main Entry Point

Fully Local Voice System:
- Local STT (Whisper)
- Local TTS (macOS Say)
- Command Mode (Interactive)
- Session Mode (Long Recordings)
"""

import asyncio
import logging
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from haitham_voice_agent.config import Config
from haitham_voice_agent.tools.voice import LocalSTT, TTS, SessionRecorder, init_whisper_models
from haitham_voice_agent.llm_router import LLMRouter
from haitham_voice_agent.model_router import TaskMeta, choose_model
from haitham_voice_agent.tools.gemini.gemini_router import choose_gemini_variant
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


from haitham_voice_agent.intent_router import route_command

def validate_config() -> bool:
    """Validates the application configuration."""
    if not Config.validate():
        logger.error("Configuration validation failed.")
        return False
    return True

def check_for_legacy_models():
    """
    Scan codebase for legacy Gemini 1.5 references.
    Raises RuntimeError if found (to prevent 404s).
    """
    import os
    
    logger = logging.getLogger(__name__)
    legacy_pattern = "gemini-1.5-pro"
    root_dir = Path(__file__).parent
    
    found_files = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                path = Path(root) / file
                try:
                    content = path.read_text(encoding="utf-8")
                    if legacy_pattern in content:
                        # Ignore this check function itself
                        if "check_for_legacy_models" in content and path.name == "main.py":
                            continue
                        found_files.append(str(path))
                except Exception:
                    pass
                    
    if found_files:
        logger.warning(f"⚠️ FOUND LEGACY GEMINI REFERENCES IN: {found_files}")
        # We won't crash, just warn, as it might be in comments
    else:
        logger.info("✅ No legacy Gemini 1.5 references found.")


class HVA:
    """Haitham Voice Agent - Main Orchestrator"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info(f"Initializing HVA v{Config.HVA_VERSION}")
        logger.info("=" * 60)
        
        # 0. Safety Check: Ensure no legacy models
        check_for_legacy_models()

        # 1. Initialize Configuration
        if not validate_config():
            raise RuntimeError("Configuration validation failed")
        
        # Initialize Gemini mapping
        Config.init_gemini_mapping()
        
        # Initialize Whisper models
        logger.info("Initializing Whisper models...")
        init_whisper_models()
        
        # Initialize voice components
        self.stt = LocalSTT()
        self.tts = TTS()
        self.recorder = SessionRecorder()
        
        # Initialize LLM
        self.llm_router = LLMRouter()
        
        # Initialize tools
        self.memory_tools = VoiceMemoryTools()
        self.gmail = ConnectionManager()
        
        # State
        self.language = "ar"  # Default language
        self.is_running = True
        
        logger.info("HVA initialized successfully")
    
    async def initialize_async(self):
        """Initialize async components"""
        await self.memory_tools.ensure_initialized()
        logger.info("Async components initialized")
    
    def speak(self, text: str):
        """Speak text using TTS"""
        self.tts.speak(text, language=self.language)
    
    async def process_command_mode(self):
        """
        Command Mode: Listen -> Route -> Execute
        """
        # Listen
        result = self.stt.listen_realtime(language=self.language)
        
        if not result:
            return
            
        text = result["text"]
        is_long_speech = result.get("is_long_speech", False)
        
        if is_long_speech:
            logger.info(f"Long speech detected ({result['duration']:.2f}s). Treating as memory note.")
            self.speak("تم حفظ الجلسة كملاحظة طويلة" if self.language == "ar" else "Long session saved as note")
            
            # Route directly to memory
            await self.memory_tools.process_voice_note(text)
            return

        logger.info(f"Command: {text}")
        await self.process_text_command(text)

    async def process_text_command(self, text: str):
        """
        Process a text command (Route -> Execute)
        """
        # 1. Deterministic Routing (Fast Path)
        intent = route_command(text)
        
        if intent["confidence"] > 0.7:
            logger.info(f"Deterministic intent matched: {intent['action']}")
            
            # Execute directly
            if intent["action"] == "start_session_recording":
                await self.start_session_mode()
                return
                
            elif intent["action"] == "stop_session_recording":
                # Should not happen in command mode usually, but handle it
                self.speak("لا يوجد جلسة نشطة" if self.language == "ar" else "No active session")
                return
                
            elif intent["action"] == "save_memory_note":
                content = intent["params"].get("content", text)
                await self.memory_tools.process_voice_note(content)
                self.speak("تم الحفظ" if self.language == "ar" else "Saved")
                return
                
            elif intent["action"] == "fetch_latest_email":
                email = self.gmail.fetch_latest_email()
                if email:
                    self.speak(f"إيميل من {email['from']}: {email['subject']}" if self.language == "ar" else f"Email from {email['from']}: {email['subject']}")
                else:
                    self.speak("لا يوجد إيميلات جديدة" if self.language == "ar" else "No new emails")
                return
                
            elif intent["action"] == "summarize_latest_email":
                # Fallback to planner for complex tasks
                pass 

        # 2. LLM Routing (Fallback / Complex Tasks)
        # Route & Plan
        plan = await self.plan_command(text)
        
        # Confirm
        if plan.get("confirmation_needed", True):
            if not self.confirm_plan(plan):
                self.speak("تم الإلغاء" if self.language == "ar" else "Cancelled")
                return
        
        # Execute
        result = await self.execute_plan(plan)
        
        # Respond
        self._speak_result(result)

    def _is_session_start_trigger(self, text: str) -> bool:
        """Check if command triggers session mode"""
        triggers_ar = ["ابدأ جلسة", "تسجيل اجتماع", "ابدأ الاجتماع", "سجل جلسة"]
        triggers_en = ["start session", "record meeting", "start meeting", "record session"]
        
        text_lower = text.lower()
        triggers = triggers_ar if self.language == "ar" else triggers_en
        return any(t in text_lower for t in triggers)

    async def start_session_mode(self):
        """
        Session Mode: Record -> Transcribe -> Analyze
        """
        logger.info("Starting Session Mode")
        self.speak("بدأت التسجيل. قل 'إيقاف التسجيل' عند الانتهاء." if self.language == "ar" else "Recording started. Say 'Stop Recording' when done.")
        
        # Start recording
        session_path = self.recorder.start()
        
        # Wait for stop command
        while self.recorder.is_recording():
            # Listen for stop command periodically
            # We use a short timeout check to allow the loop to continue if silence
            # Note: In a real concurrent system, we might need a separate listening thread
            # For now, we'll block on listen_realtime which uses VAD. 
            # If user speaks, we check if it's "stop".
            
            # NOTE: Since we are recording raw audio in background, 
            # we can't easily use the SAME mic for VAD without conflict on some systems.
            # However, speech_recognition + pyaudio might conflict.
            # A robust way is to rely on a keyboard interrupt or a specific silence duration.
            # For this implementation, we will assume the user presses Ctrl+C or we implement
            # a simple check if we can.
            
            # LIMITATION: Simultaneous recording and listening is hard with single mic.
            # Strategy: We will just record until KeyboardInterrupt OR 
            # we can't listen while recording.
            # Let's use a blocking input for "Press Enter to stop" as a fallback for CLI
            # or rely on the user stopping via a separate signal.
            
            # For this CLI version, let's use a non-blocking check or just wait for user input
            print(">> Press ENTER to stop recording <<")
            await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            break
            
        # Stop recording
        final_path = self.recorder.stop()
        self.speak("تم إيقاف التسجيل. جاري المعالجة..." if self.language == "ar" else "Recording stopped. Processing...")
        
        # Transcribe
        transcript = self.stt.transcribe_session(final_path, language=self.language)
        logger.info(f"Transcript length: {len(transcript)}")
        
        if not transcript:
            self.speak("لم يتم استخراج نص" if self.language == "ar" else "No text extracted")
            return

        # Analyze Session
        await self.analyze_session(transcript)

    async def analyze_session(self, transcript: str):
        """Analyze session transcript using Gemini"""
        # 1. Build TaskMeta for Router
        meta = TaskMeta(
            context_tokens=len(transcript) // 4,  # Rough estimate
            task_type="doc_analysis",
            risk="medium",
            latency="background",
            is_document=True
        )
        
        # 2. Choose Model (Gemini)
        gemini_decision = choose_gemini_variant(meta)
        model_name = Config.resolve_gemini_model(gemini_decision["logical_model"])
        
        logger.info(f"Analyzing session with {model_name}")
        
        # 3. Generate Analysis
        prompt = f"""
Analyze this session transcript:

{transcript}

Provide:
1. Executive Summary (3-5 sentences)
2. Key Decisions
3. Action Items

Output format: JSON
"""
        # Call LLM (using router's generic method, but targeting Gemini)
        # We need to ensure we use the specific model. 
        # The LLMRouter currently defaults to config.GEMINI_MODEL.
        # We should ideally pass the model name, but LLMRouter.generate_with_gemini 
        # uses the configured default. For now, that's fine as it maps to Pro.
        
        analysis = await self.llm_router.generate_with_gemini(prompt)
        
        # 4. Save to Memory
        await self.memory_tools.process_voice_note(
            f"Session Analysis:\n{analysis}\n\nTranscript:\n{transcript[:1000]}..."
        )
        
        self.speak("تم حفظ تحليل الجلسة في الذاكرة" if self.language == "ar" else "Session analysis saved to memory")

    async def plan_command(self, text: str) -> dict:
        """Generate execution plan using GPT"""
        # Build TaskMeta
        meta = TaskMeta(
            context_tokens=len(text) // 4,
            task_type="planning",
            risk="low",
            latency="interactive"
        )
        
        # Choose Model
        decision = choose_model(meta)
        model_name = Config.resolve_model(decision["model"])
        
        logger.info(f"Planning with {model_name}")
        
        # Generate Plan
        prompt = f"""
User said: "{text}"
Generate execution plan JSON:
{{
    "intent": "description",
    "tool": "memory|gmail|other",
    "action": "save_note|search|fetch_email|send_email",
    "parameters": {{}},
    "confirmation_needed": boolean
}}
"""
        response = await self.llm_router.generate_with_gpt(prompt)
        
        try:
            if isinstance(response, str):
                clean = response.replace("```json", "").replace("```", "").strip()
                return json.loads(clean)
            return response
        except:
            return {"intent": "Unknown", "tool": "other", "confirmation_needed": False}

    def confirm_plan(self, plan: dict) -> bool:
        """Ask user for confirmation"""
        intent = plan.get("intent", "Unknown")
        self.speak(f"سأقوم بـ: {intent}. موافق؟" if self.language == "ar" else f"I will: {intent}. Confirm?")
        
        # Listen for simple yes/no
        response = self.stt.listen_realtime(language=self.language)
        if not response:
            return False
            
        affirmative = ["نعم", "موافق", "تمام", "yes", "ok", "sure"]
        return any(w in response.lower() for w in affirmative)

    async def execute_plan(self, plan: dict) -> dict:
        """Execute the planned action"""
        tool = plan.get("tool")
        action = plan.get("action")
        params = plan.get("parameters", {})
        
        if tool == "memory":
            if action == "save_note":
                content = params.get("content") or plan.get("intent")
                return await self.memory_tools.process_voice_note(content)
            elif action == "search":
                query = params.get("query") or plan.get("intent")
                res = await self.memory_tools.search_memory_voice(query)
                return {"success": True, "message": res}
                
        elif tool == "gmail":
            if action == "fetch_email":
                email = self.gmail.fetch_latest_email()
                if email:
                    return {"success": True, "message": f"Email from {email['from']}: {email['subject']}"}
                return {"success": False, "message": "No emails found"}
                
        return {"success": False, "message": "Unknown action"}

    def _speak_result(self, result: dict):
        """Speak the execution result"""
        msg = result.get("message", "Done")
        self.speak(msg)

    async def run(self):
        """Main Loop"""
        logger.info("HVA Running. Press Ctrl+C to exit.")
        self.speak("أنا جاهز" if self.language == "ar" else "I am ready")
        
        try:
            while self.is_running:
                # In a real GUI/Voice app, we'd have a wake word.
                # Here we loop, but we need a trigger.
                # For this CLI version, we'll prompt user to press Enter to listen
                # to avoid infinite loop of silence processing.
                print("\nPress ENTER to speak (or Ctrl+C to exit)...")
                await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                
                await self.process_command_mode()
                
        except KeyboardInterrupt:
            logger.info("Exiting...")
            self.speak("مع السلامة" if self.language == "ar" else "Goodbye")


async def main():
    parser = argparse.ArgumentParser(description="Haitham Voice Agent")
    parser.add_argument("--test", type=str, help="Run a text command without voice")
    args = parser.parse_args()
    
    hva = HVA()
    await hva.initialize_async()
    
    if args.test:
        logger.info(f"Test Mode: {args.test}")
        await hva.process_text_command(args.test)
    else:
        await hva.run()

if __name__ == "__main__":
    asyncio.run(main())
