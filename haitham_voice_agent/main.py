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
from haitham_voice_agent.tools.voice import TTS, SessionRecorder, init_whisper_models
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


from haitham_voice_agent.tools.voice.stt import STTHandler
from haitham_voice_agent.tools.voice.models import init_whisper_models
from haitham_voice_agent.ollama_orchestrator import get_orchestrator
from haitham_voice_agent.intent_router import route_command
from haitham_voice_agent.tools.arabic_normalizer import normalize_arabic_text
from haitham_voice_agent.tools.tasks.task_manager import task_manager
from haitham_voice_agent.tools.files import FileTools
from haitham_voice_agent.tools.system_tools import SystemTools
from haitham_voice_agent.tools.smart_organizer import get_organizer
from haitham_voice_agent.tools.secretary import get_secretary
from haitham_voice_agent.tools.advisor import get_advisor
from haitham_voice_agent.memory.manager import get_memory_manager

def validate_config() -> bool:
    """Validates the application configuration."""
    if not Config.validate():
        logger.error("Configuration validation failed.")
        return False
    return True




class HVA:
    """Haitham Voice Agent - Main Orchestrator"""
    
    def __init__(self):
        logger.info("=" * 60)
        logger.info(f"Initializing HVA v{Config.HVA_VERSION}")
        logger.info("=" * 60)
        
        # 1. Initialize Configuration
        if not validate_config():
            raise RuntimeError("Configuration validation failed")
        
        # Initialize Gemini mapping
        Config.init_gemini_mapping()
        
        # Initialize Whisper models
        logger.info("Initializing Whisper models...")
        init_whisper_models()
        
        # Initialize voice components
        self.stt = STTHandler()
        self.tts = TTS()
        self.recorder = SessionRecorder()
        
        # Initialize LLM
        self.llm_router = LLMRouter()
        
        # Initialize tools
        self.memory_tools = VoiceMemoryTools()
        self.gmail = ConnectionManager()
        self.file_tools = FileTools()
        self.system_tools = SystemTools()
        
        # Initialize System Awareness (New)
        from haitham_voice_agent.tools.system_awareness import get_system_awareness
        self.system_awareness = get_system_awareness()
        self.system_awareness.start()
        
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
        # Capture Audio
        capture = self.stt.capture_audio()
        if not capture:
            return
            
        audio_bytes, duration = capture
        
        # Check for long speech (treat as note)
        strict_config = getattr(Config, "STT_STRICT_CONFIG", {"max_realtime_seconds": 10.0})
        if duration > strict_config["max_realtime_seconds"]:
            logger.info(f"Long speech detected ({duration:.2f}s). Treating as memory note.")
            
            # Use session transcriber for better quality on long audio
            text = self.stt.transcribe_session(audio_bytes, duration)
            
            if text:
                self.speak("تم حفظ الجلسة كملاحظة طويلة" if self.language == "ar" else "Long session saved as note")
                await self.memory_tools.process_voice_note(text)
            else:
                self.speak("ما قدرت أفرغ الجلسة بشكل واضح." if self.language == "ar" else "Could not transcribe session clearly.")
            return

        # Short Command
        text = self.stt.transcribe_command(audio_bytes, duration)
        
        if not text:
            # Validation failed or garbage
            logger.info("STT returned None (unreliable speech). Asking user to repeat.")
            self.speak("ما فهمت كلامك، حاول تعيد الجملة بصوت أوضح وأقصر." if self.language == "ar" else "I didn't understand, please repeat clearly.")
            return

        logger.info(f"Command (Raw): {text}")
        
        # 1. Intent Router (Reflex Layer - Fastest)
        # Handles critical commands like "stop", "mute", "volume" instantly
        intent_result = route_command(text)
        if intent_result:
            logger.info(f"Intent Router caught command: {intent_result['intent']}")
            # Execute directly
            await self.execute_plan(intent_result)
            return

        # 2. Ollama Orchestrator (Local Intelligence Layer)
        # Classifies intent and handles simple queries
        orchestrator = get_orchestrator()
        classification = await orchestrator.classify_request(text)
        
        if classification.get("type") == "direct_response":
            logger.info("Ollama handled request directly.")
            response = classification["response"]
            self.speak(response)
            return
            
        elif classification.get("type") == "execute_command":
            logger.info(f"Ollama identified command: {classification['intent']}")
            plan = {
                "intent": classification["intent"],
                "tool": "system", 
                "action": classification["intent"],
                "parameters": classification.get("parameters", {}),
                "confirmation_needed": False
            }
            await self.execute_plan(plan)
            return
            
        # 3. LLM Router (Cloud Intelligence Layer)
        # Handles complex tasks (Planning, Gmail, Memory)
        logger.info(f"Ollama delegated to: {classification.get('delegate_to')}")
        
        # Generate execution plan using Cloud LLM (GPT/Gemini)
        plan = await self.llm_router.generate_execution_plan(text)
        
        if plan:
            await self.execute_plan(plan)
        else:
            self.speak("عذراً، لم أستطع فهم طلبك." if self.language == "ar" else "Sorry, I couldn't understand your request.")
        # Normalize if Arabic
        if self.language == "ar":
            text = await normalize_arabic_text(text, mode="command")
            logger.info(f"Command (Normalized): {text}")
            
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
                
            elif intent["action"] == "beautify_transcript":
                # On-demand normalization
                self.speak("جاري تحسين النص..." if self.language == "ar" else "Beautifying transcript...")
                # We assume the user wants to beautify the LAST session or note.
                # For now, let's just beautify the current text command if it was long, 
                # OR we need to fetch the last memory.
                # Given the prompt, let's just say we support it but maybe need a target.
                # If this was a voice command "beautify this", "this" is the command itself which is short.
                # Realistically, this would apply to a stored memory.
                # Let's implement a simple version that fetches the last voice note.
                last_note = await self.memory_tools.get_last_voice_note()
                if last_note:
                    normalized = await normalize_arabic_text(last_note, mode="session") # Force session mode for length
                    self.speak("النص المحسن:" if self.language == "ar" else "Beautified text:")
                    print(f"\n--- Beautified Transcript ---\n{normalized}\n-----------------------------")
                    # Optionally update the memory
                else:
                    self.speak("لا يوجد ملاحظات سابقة" if self.language == "ar" else "No previous notes")
                return 

            elif intent["action"] == "create_task":
                # Extract title from text (simple heuristic: everything after "add task" or similar)
                # For now, just use the whole text or ask LLM to parse. 
                # Let's use the planner to extract details properly if confidence is high but params are missing.
                # But since we are in deterministic block, we might not have params.
                # Let's fall through to planner for extraction OR do simple extraction here.
                # Simple extraction:
                pass # Fall through to planner to extract title/project/date

            elif intent["action"] == "list_tasks":
                tasks = task_manager.list_tasks(status="open")
                if not tasks:
                    self.speak("لا يوجد مهام مفتوحة" if self.language == "ar" else "No open tasks")
                else:
                    count = len(tasks)
                    self.speak(f"لديك {count} مهام مفتوحة." if self.language == "ar" else f"You have {count} open tasks.")
                    # List first 3
                    for t in tasks[:3]:
                        self.speak(f"- {t.title}")
                return
        
            elif intent["action"] == "search_notes":
                # Default search for "last notes" or just general listing
                # We can search for "*" or just fetch recent
                # For now, let's search for "note" or "ملاحظة" to get everything, or rely on empty query if supported
                # But search_memories usually needs a query.
                # Let's assume the user wants recent notes.
                query = "recent" # The memory system might not support this keyword specially, but let's try or use empty
                # Actually, let's just use the text itself as query if it's specific, or "note" if generic
                res = await self.memory_tools.search_memory_voice("note", language=self.language)
                self.speak(res)
                return

        # 2. LLM Routing (Fallback / Complex Tasks)
        # Route & Plan
        plan = await self.plan_command(text)
        
        # Fallback: If LLM failed to identify intent OR it's unknown, treat as note
        # This ensures we capture "short thoughts" that don't look like commands
        if (plan.get("intent") in ["Unknown", "unknown_action", None] or plan.get("action") == "unknown"):
             logger.info("Fallback intent: treating unknown text as save_memory_note")
             plan = {
                 "intent": "Save Note (Fallback)",
                 "tool": "memory",
                 "action": "save_note",
                 "parameters": {"content": text},
                 "confirmation_needed": False
             }
        
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

    def _looks_like_note(self, text: str) -> bool:
        """Check if text looks like a note (fallback heuristic)"""
        if not text:
            return False

        # REMOVED: Naive length check (len < 20)
        
        # Explicit triggers for notes
        note_markers = ["ملاحظة", "note", "تذكر", "remember", "save", "احفظ", "فكرة", "idea"]
        if any(marker in text.lower() for marker in note_markers):
            return True

        # Fallback: If it's not a clear command, treat as note
        # This is safer than rejecting short text
        return True

    def _resolve_path(self, path_name: str) -> str:
        """Resolve spoken path name to actual path"""
        if not path_name:
            return "~"
            
        name = path_name.lower().strip()
        
        # Common mappings
        mappings = {
            "development": "~/development",
            "ديفولوبمنت": "~/development",
            "تطوير": "~/development",
            "downloads": "~/Downloads",
            "تنزيلات": "~/Downloads",
            "documents": "~/Documents",
            "مستندات": "~/Documents",
            "desktop": "~/Desktop",
            "سطح المكتب": "~/Desktop",
            "home": "~",
            "الرئيسية": "~",
            "haitham": "~",
            "هيثم": "~",
            "هيَم": "~",
            "هيذام": "~",
            "root": "/",
            "projects": "~/HVA_Workspace/projects",
            "مشاريع": "~/HVA_Workspace/projects"
        }
        
        # Check exact match
        if name in mappings:
            return mappings[name]
            
        # Check partial match (e.g. "file development")
        for key, val in mappings.items():
            if key in name:
                return val
                
        # Default to home if unknown, or try to use as is relative to home
        # If it looks like a path, use it
        if "/" in name:
            return name
            
        # Fallback: assume it's a folder in home
        return f"~/{path_name}"

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
            # Non-blocking wait for stop signal
            try:
                print(">> Press Ctrl+C to stop recording <<", end="\r")
                await asyncio.sleep(0.5)
            except asyncio.CancelledError:
                break
            except KeyboardInterrupt:
                break
            
            # Check if file size is growing (optional sanity check)
            # if not self.recorder.is_recording(): break
            
        # Stop recording
        # Stop recording
        try:
            final_path = self.recorder.stop()
        except KeyboardInterrupt:
             # Handle Ctrl+C gracefully if caught during stop
             final_path = self.recorder.stop()
        self.speak("تم إيقاف التسجيل. جاري المعالجة..." if self.language == "ar" else "Recording stopped. Processing...")
        
        # Transcribe
        # Read file to bytes
        try:
            with open(final_path, "rb") as f:
                audio_bytes = f.read()
                
            # Calculate duration roughly (optional, or pass 0 if not needed by router logic except for logging)
            # We can get duration from file size / rate
            # Wav file header has size, but let's just pass 0 or estimate
            # Or use soundfile to get duration
            import soundfile as sf
            info = sf.info(final_path)
            duration = info.duration
            
            transcript = transcribe_session(audio_bytes, duration)
            
        except Exception as e:
            logger.error(f"Failed to read session file: {e}")
            transcript = None

        logger.info(f"Transcript length: {len(transcript) if transcript else 0}")
        
        if not transcript:
            logger.info("Session STT failed or was too noisy.")
            self.speak("ما قدرت أفرغ الجلسة بشكل واضح. حاول تعيد التسجيل في مكان أهدأ." if self.language == "ar" else "Could not transcribe session clearly. Please try again in a quieter place.")
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
        """Generate execution plan using Hybrid Intelligence (Ollama -> GPT)"""
        
        # --- 1. Ollama Orchestrator (Local Intelligence) ---
        from haitham_voice_agent.ollama_orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        
        classification = await orchestrator.classify_request(text)
        
        if classification.get("type") == "direct_response":
            logger.info("Ollama handled request directly.")
            return {
                "intent": "Direct Response",
                "tool": "system",
                "action": "speak",
                "parameters": {"text": classification["response"]},
                "confirmation_needed": False
            }
            
        elif classification.get("type") == "execute_command":
            logger.info(f"Ollama identified command: {classification['intent']}")
            
            intent = classification["intent"]
            params = classification.get("parameters", {})
            
            # Default mapping
            tool = "system"
            action = intent
            
            # Map intents to specific tools
            if intent in ["show_files", "list_files"]:
                tool = "files"
                action = "list_files"
                # Map 'path' param to 'directory' if needed
                if "path" in params:
                    params["directory"] = params.pop("path")
                    
            elif intent in ["open_folder"]:
                # If user wants to OPEN in Finder, use system.open_app or files.open_folder?
                # Usually "open folder" means open in UI.
                # Let's check if files tool has open_folder (it usually creates).
                # Actually, system.open_app can open folders on macOS via 'open' command.
                tool = "system" 
                action = "open_app"
                if "path" in params:
                    params["app_name"] = params.pop("path") # Hacky but works with 'open <path>'
                    
            elif intent in ["morning_briefing"]:
                tool = "secretary"
                action = "get_morning_briefing"
                
            elif intent in ["work_mode", "meeting_mode", "chill_mode"]:
                tool = "secretary"
                action = "set_work_mode"
                params["mode"] = intent.replace("_mode", "")
                
            elif intent in ["organize_downloads", "clean_desktop"]:
                tool = "organizer"
                
            elif intent in ["fetch_latest_email", "check_email"]:
                tool = "gmail"
                action = "fetch_email"
            
            return {
                "intent": intent,
                "tool": tool,
                "action": action,
                "parameters": params,
                "confirmation_needed": False
            }
            
        # If delegate, we continue to GPT/Gemini as usual
        logger.info(f"Ollama delegated to: {classification.get('delegate_to')} ({classification.get('reason')})")
        
        # --- 2. Cloud Intelligence (GPT/Gemini) ---
        
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
        
        prompt = f"""
أنت الدماغ الذكي لمساعد هيثم الصوتي (HVA).
مهمتك فهم نية المستخدم وتحويلها إلى أداة وإجراء محدد.

المستخدم قال: "{text}"

# الأدوات المتاحة:

## 1. memory (الذاكرة)
- save_note: حفظ ملاحظة أو فكرة أو معلومة
- search: البحث في الملاحظات المحفوظة
- الكلمات الدالة: "احفظ"، "سجّل"، "تذكّر"، "فكرة"، "ملاحظة"، "ابحث في ملاحظاتي"

## 2. files (الملفات)
- list_files: عرض الملفات في مجلد
- search_files: البحث عن ملف معين
- create_folder: إنشاء مجلد جديد ⬅️ مهم!
- الكلمات الدالة: "افتح مجلد"، "أنشئ مجلد"، "اصنع مجلد"، "مجلد جديد"، "اعرض الملفات"

## 3. gmail (البريد)
- fetch_email: قراءة آخر بريد إلكتروني
- search_email: البحث في البريد
- create_draft: إنشاء مسودة
- الكلمات الدالة: "إيميل"، "بريد"، "رسالة"

## 4. tasks (المهام)
- create_task: إضافة مهمة جديدة
- list_tasks: عرض المهام
- complete_task: إكمال مهمة
- الكلمات الدالة: "مهمة"، "أضف مهمة"، "قائمة المهام"

## 5. system (النظام)
- open_app: فتح تطبيق
- set_volume: التحكم بالصوت
- sleep_display: إطفاء الشاشة
- الكلمات الدالة: "افتح"، "شغّل"، "الصوت"، "الشاشة"

## 9. terminal (الطرفية الآمنة)
- execute_command: تنفيذ أوامر النظام (ls, git, python, pip)
- الكلمات الدالة: "نفذ أمر"، "شغل كود"، "git status", "ls", "pip install"
- ملاحظة: الأوامر الخطرة محظورة تلقائياً.

## 10. calendar (التقويم)
- list_events: عرض المواعيد القادمة
- create_event: إضافة موعد جديد
- الكلمات الدالة: "مواعيدي"، "جدول اليوم"، "احجز اجتماع"، "ذكرني بموعد"

## 11. drive (جوجل درايف)
- list_files: عرض ملفات درايف
- search_files: البحث في درايف
- الكلمات الدالة: "ملفات درايف"، "ابحث في السحابة"، "مستندات جوجل"

## 6. organizer (المنظم الذكي)
- organize_downloads: ترتيب مجلد التنزيلات
- clean_desktop: تنظيف سطح المكتب
- الكلمات الدالة: "رتب التنزيلات"، "نظف سطح المكتب"، "فرز الملفات"

## 7. secretary (السكرتير التنفيذي)
- get_morning_briefing: عرض الموجز الصباحي
- set_work_mode: تغيير وضع العمل (work, meeting, chill)
- الكلمات الدالة: "صباح الخير"، "وضع العمل"، "اجتماع"، "استراحة"

## 8. memory_manager (مدير الذاكرة)
- create_project: إنشاء مشروع جديد
- save_thought: حفظ فكرة أو ملاحظة (مع تلخيص تلقائي)
- search: البحث في الذاكرة (Semantic Search)
- الكلمات الدالة: "مشروع جديد"، "فكرة"، "احفظ"، "دون"، "ابحث في ذاكرتي"، "ماذا قلت عن"

# قواعد مهمة:
1. "افتح مجلد جديد" أو "أنشئ مجلد" = files.create_folder (ليس memory!)
2. "افتح تطبيق" أو "شغّل برنامج" = system.open_app
3. "احفظ ملاحظة" أو "سجّل فكرة" = memory_manager.save_thought
4. "مشروع جديد باسم X" = memory_manager.create_project(name='X')
5. "ماذا قلت عن X؟" = memory_manager.search(query='X')
6. "رتب التنزيلات" = organizer.organize_downloads
7. "صباح الخير" = secretary.get_morning_briefing
8. "وضع العمل" = secretary.set_work_mode(mode='work')
5. "نظف سطح المكتب" = organizer.clean_desktop
4. إذا ذكر اسم "هيثم" أو "هيم" كمجلد = يقصد مجلد المستخدم الرئيسي ~/
5. **"داخل" تعني مسار متداخل:** "ملف X داخل مجلد Y" = "Y/X" (مهم جداً!)
   - مثال: "ملف العمل داخل مجلد هيثم" → directory: "هيثم/العمل"
   - مثال: "مجلد المهام داخل التنزيلات" → directory: "~/Downloads/المهام"

# أمثلة:

مثال 1:
المستخدم: "افتح مجلد جديد داخل مجلد هيثم باسم المهام"
{
    "intent": "إنشاء مجلد جديد باسم المهام داخل المجلد الرئيسي",
    "tool": "files",
    "action": "create_folder",
    "parameters": {
        "directory": "هيثم/المهام"
    },
    "confirmation_needed": false
}

مثال 2:
المستخدم: "افتح ملف جديد باسم العمل داخل مجلد هيثم"
{
    "intent": "إنشاء ملف العمل داخل مجلد هيثم",
    "tool": "files",
    "action": "create_folder",
    "parameters": {
        "directory": "هيثم/العمل"
    },
    "confirmation_needed": false
}

مثال 3:
المستخدم: "أنشئ مجلداً جديداً باسم المشاريع في التنزيلات"
{
    "intent": "إنشاء مجلد المشاريع في Downloads",
    "tool": "files",
    "action": "create_folder",
    "parameters": {
        "directory": "~/Downloads/المشاريع"
    },
    "confirmation_needed": false
}

مثال 4:
المستخدم: "شغّل متصفح كروم"
{{
    "intent": "فتح متصفح Google Chrome",
    "tool": "system",
    "action": "open_app",
    "parameters": {{
        "app_name": "Google Chrome"
    }},
    "confirmation_needed": false
}}

مثال 4:
المستخدم: "احفظ هذه الفكرة: نحتاج إلى تحسين واجهة المستخدم"
{{
    "intent": "حفظ فكرة عن تحسين الواجهة",
    "tool": "memory",
    "action": "save_note",
    "parameters": {{
        "content": "نحتاج إلى تحسين واجهة المستخدم"
    }},
    "confirmation_needed": false
}}

مثال 5:
المستخدم: "اعرض الملفات الموجودة في مجلد التطوير"
{{
    "intent": "عرض ملفات مجلد development",
    "tool": "files",
    "action": "list_files",
    "parameters": {{
        "directory": "~/development"
    }},
    "confirmation_needed": false
}}

مثال 6:
المستخدم: "أضف مهمة: الاتصال بالعميل غداً"
{{
    "intent": "إضافة مهمة للاتصال بالعميل",
    "tool": "tasks",
    "action": "create_task",
    "parameters": {{
        "title": "الاتصال بالعميل",
        "due_date": "tomorrow"
    }},
    "confirmation_needed": false
}}

مثال 7:
المستخدم: "ابحث عن ملف main.py في مجلد التطوير"
{{
    "intent": "البحث عن ملف main.py",
    "tool": "files",
    "action": "search_files",
    "parameters": {{
        "directory": "~/development",
        "pattern": "main.py"
    }},
    "confirmation_needed": false
}}

مثال 8:
المستخدم: "اقرأ آخر بريد إلكتروني"
{{
    "intent": "قراءة آخر بريد وارد",
    "tool": "gmail",
    "action": "fetch_email",
    "parameters": {{}},
    "confirmation_needed": false
}}

# الآن حلل أمر المستخدم وأرجع JSON فقط:
"""

        response = await self.llm_router.generate_with_gpt(
            prompt,
            temperature=0.1,  # Lower temperature for more consistent parsing
            response_format="json_object"
        )
        
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
        
        # --- Safety Check (Advisor) ---
        advisor = get_advisor()
        validation = advisor.validate_action(tool, action, params)
        if not validation["safe"]:
            return {"success": False, "message": validation["warning"]}
        # ------------------------------
        
        if tool == "memory":
            if action == "save_note":
                content = params.get("content") or plan.get("intent")
                return await self.memory_tools.process_voice_note(content)
            elif action == "search":
                query = params.get("query") or plan.get("intent")
                res = await self.memory_tools.search_memory_voice(query, language=self.language)
                return {"success": True, "message": res}
                
        elif tool == "gmail":
            if action == "fetch_email":
                email = self.gmail.fetch_latest_email()
                if email:
                    return {"success": True, "message": f"Email from {email['from']}: {email['subject']}"}
                return {"success": False, "message": "No emails found"}
        
        elif tool == "tasks":
            if action == "create_task":
                title = params.get("title") or plan.get("intent")
                project = params.get("project_id", "inbox")
                t = task_manager.create_task(title=title, project_id=project, language=self.language)
                return {"success": True, "message": f"Task created in {project}" if self.language == "en" else f"تم إضافة المهمة في {project}"}
            
            elif action == "list_tasks":
                tasks = task_manager.list_tasks(status="open")
                if not tasks:
                    return {"success": True, "message": "No open tasks" if self.language == "en" else "لا يوجد مهام مفتوحة"}
                msg = f"Found {len(tasks)} tasks. " + ", ".join([t.title for t in tasks[:3]])
                return {"success": True, "message": msg}
                
            elif action == "complete_task":
                # This is tricky without ID. We need to find by title similarity.
                # For now, just say not implemented fully via voice without ID context.
                # Or try to match title.
                title = params.get("title")
                if title:
                    # Simple fuzzy match
                    tasks = task_manager.list_tasks(status="open")
                    for t in tasks:
                        if title.lower() in t.title.lower():
                            task_manager.complete_task(t.id, t.project_id or "inbox")
                            return {"success": True, "message": f"Completed task: {t.title}"}
                return {"success": False, "message": "Task not found"}

        elif tool == "files":
            directory = self._resolve_path(params.get("directory", "~"))
            
            if action == "list_files":
                res = await self.file_tools.list_files(directory)
                if res.get("error"):
                    return {"success": False, "message": res["message"]}
                
                files = res["files"]
                if not files:
                    return {"success": True, "message": "No files found" if self.language == "en" else "لا يوجد ملفات"}
                
                # Format output
                count = res["count"]
                msg = f"Found {count} files in {directory}. " if self.language == "en" else f"وجدت {count} ملفات في {directory}. "
                # List first 5 names
                names = [f["name"] for f in files[:5]]
                msg += ", ".join(names)
                if count > 5:
                    msg += "..."
                return {"success": True, "message": msg}
                
            elif action == "search_files":
                pattern = params.get("pattern") or params.get("query") or "*"
                
                # Use System Awareness (Layer 2 & 3)
                matches = self.system_awareness.find_file(pattern)
                
                if not matches:
                    return {"success": True, "message": "No matches found" if self.language == "en" else "لم أجد أي ملفات"}
                
                count = len(matches)
                msg = f"Found {count} matches. " if self.language == "en" else f"وجدت {count} ملفات. "
                names = [f["name"] for f in matches[:5]]
                msg += ", ".join(names)
                
                # Return list for GUI
                return {"success": True, "message": msg, "data": matches}
                
            elif action == "create_folder":
                # Handle nested paths: "folder X inside folder Y"
                # The LLM should ideally give us "Y/X" in the directory param.
                raw_dir = params.get("directory", "")
                
                # If the path already starts with ~/ or /, use it as-is
                if raw_dir.startswith("~/") or raw_dir.startswith("/"):
                    full_path = raw_dir
                else:
                    # Split and resolve
                    parts = raw_dir.split("/")
                    base = self._resolve_path(parts[0])
                    
                    if len(parts) > 1:
                        # If base already contains the first part (e.g. "~/Downloads"),
                        # just append the rest
                        full_path = f"{base}/{'/'.join(parts[1:])}"
                    else:
                        full_path = base
                    
                res = await self.file_tools.create_folder(full_path)
                if res.get("error"):
                    return {"success": False, "message": res["message"]}
                
                return {"success": True, "message": f"Created folder: {full_path}" if self.language == "en" else f"تم إنشاء المجلد: {full_path}"}

        elif tool == "system":
            if action == "open_app":
                app = params.get("app_name") or plan.get("intent")
                # Clean up intent if it contains "open"
                app = app.replace("open ", "").replace("افتح ", "").replace("شغل ", "")
                
                # Check System Profile (Layer 1)
                path = self.system_awareness.get_app_path(app)
                if path:
                    logger.info(f"Opening app from profile: {path}")
                    return await self.system_tools.open_app(path) # Pass full path
                    
                # Fallback to name
                return await self.system_tools.open_app(app)
            
            elif action == "set_volume":
                level = params.get("level")
                if level is None:
                    # Try to parse from intent
                    import re
                    nums = re.findall(r'\d+', plan.get("intent", ""))
                    if nums:
                        level = int(nums[0])
                    else:
                        # Default increments?
                        if "up" in plan.get("intent", "") or "ارفع" in plan.get("intent", ""):
                            return await self.system_tools.set_volume(50) # TODO: get current and +10
                        elif "down" in plan.get("intent", "") or "وطي" in plan.get("intent", ""):
                            return await self.system_tools.set_volume(20)
                        else:
                            level = 50
                return await self.system_tools.set_volume(int(level))

        elif tool == "terminal":
            from haitham_voice_agent.tools.terminal import TerminalTools
            term = TerminalTools()
            
            command = params.get("command") or plan.get("intent")
            
            # Execute (Traffic Light Logic handles safety)
            res = await term.execute_command(command)
            
            if res.get("status") == "confirmation_required":
                # For now, return as failure/blocked until interactive confirmation is implemented
                return {"success": False, "message": f"Confirmation required: {res['message']}"}
            
            if res.get("error"):
                return {"success": False, "message": res["message"]}
                
            output = res.get("output", "").strip()
            return {"success": True, "message": output if output else "Command executed."}
            
        elif tool == "calendar":
            from haitham_voice_agent.tools.calendar import CalendarTools
            cal = CalendarTools()
            
            if action == "list_events":
                res = await cal.list_events()
                if res.get("error"):
                    return {"success": False, "message": res["message"]}
                
                events = res["events"]
                if not events:
                    return {"success": True, "message": "No upcoming events found."}
                
                msg = f"Found {len(events)} events:\n"
                for e in events:
                    start = e['start'].replace('T', ' ').split('+')[0]
                    msg += f"- {e['summary']} at {start}\n"
                return {"success": True, "message": msg}
                
            elif action == "create_event":
                summary = params.get("summary") or plan.get("intent")
                start_time = params.get("start_time") # Expecting ISO or handled by LLM
                
                # If start_time is missing, we can't create.
                if not start_time:
                    return {"success": False, "message": "I need a start time for the event."}
                    
                res = await cal.create_event(summary, start_time)
                if res.get("error"):
                    return {"success": False, "message": res["message"]}
                return {"success": True, "message": res["message"]}
        
        elif tool == "drive":
            from haitham_voice_agent.tools.drive import DriveTools
            drive = DriveTools()
            
            if action == "list_files":
                res = await drive.list_files()
                if res.get("error"):
                    return {"success": False, "message": res["message"]}
                
                files = res["files"]
                if not files:
                    return {"success": True, "message": "No files found in Drive."}
                
                msg = f"Found {len(files)} files in Drive:\n"
                for f in files:
                    msg += f"- {f['name']} ({f['mimeType']})\n"
                return {"success": True, "message": msg}
                
            elif action == "search_files":
                query = params.get("query") or plan.get("intent")
                res = await drive.search_files(query)
                if res.get("error"):
                    return {"success": False, "message": res["message"]}
                
                files = res["files"]
                if not files:
                    return {"success": True, "message": "No matches found in Drive."}
                
                msg = f"Found {len(files)} matches in Drive:\n"
                for f in files:
                    msg += f"- {f['name']}\n"
                return {"success": True, "message": msg}
                
        elif tool == "organizer":
            organizer = get_organizer()
            
            if action == "organize_downloads":
                res = organizer.organize_downloads()
                if "error" in res:
                    return {"success": False, "message": res["error"]}
                    
                # Format report
                msg = f"Downloads Organized.\nTotal Moved: {res['total_moved']}\n"
                for cat, count in res["categories"].items():
                    msg += f"- {cat}: {count}\n"
                return {"success": True, "message": msg, "data": msg} # data for GUI
                
            elif action == "clean_desktop":
                res = organizer.clean_desktop()
                msg = f"Desktop Cleaned.\nTotal Moved: {res['total_moved']}\n"
                if res["screenshots_moved"] > 0:
                    msg += f"- Screenshots: {res['screenshots_moved']}\n"
                if res["misc_moved"] > 0:
                    msg += f"- Misc Files: {res['misc_moved']}\n"
                    msg += f"Moved to: {Path(res['dest_folder']).name}"
                return {"success": True, "message": msg, "data": msg}

        elif tool == "secretary":
            secretary = get_secretary()
            
            if action == "get_morning_briefing":
                res = await secretary.get_morning_briefing()
                # Return data for GUI to render nicely
                return {"success": True, "message": res["text"], "data": res["text"]}
                
            elif action == "set_work_mode":
                mode = params.get("mode") or plan.get("intent")
                msg = await secretary.set_work_mode(mode)
                return {"success": True, "message": msg, "data": msg}
            
            elif action == "mute":
                return await self.system_tools.mute_volume()
                
        elif tool == "memory_manager":
            manager = get_memory_manager()
            
            if action == "create_project":
                name = params.get("name") or plan.get("intent")
                desc = params.get("description", "")
                res = manager.create_project(name, desc)
                return res
                
            elif action == "save_thought":
                content = params.get("content") or plan.get("intent")
                project = params.get("project_name")
                res = await manager.save_thought(content, project)
                
                if res["success"]:
                    # Format nice message with summary
                    msg = f"Saved thought.\nSummary: {res.get('summary')}"
                    return {"success": True, "message": msg, "data": msg}
                return res

            elif action == "search":
                query = params.get("query") or plan.get("intent")
                results = await manager.search_memory(query)
                
                if not results:
                    return {"success": True, "message": "No relevant memories found.", "data": "No results."}
                
                msg = f"🔍 **Memory Search Results for '{query}'**\n\n"
                for r in results:
                    content = r['content'][:200].replace("\n", " ") + "..."
                    msg += f"- {content}\n"
                    
                return {"success": True, "message": msg, "data": msg}

            
            elif action == "unmute":
                return await self.system_tools.unmute_volume()
                
            elif action == "sleep_display":
                return await self.system_tools.sleep_display()

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
