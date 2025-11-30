"""
HVA Menu Bar App
Simple menu bar application with global keyboard shortcut
"""

import rumps
import threading
import sys
import os
import asyncio
import multiprocessing
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from haitham_voice_agent.gui_process import run_gui_process
from haitham_voice_agent.wake_word import get_detector
from haitham_voice_agent import stt, llm_router
from haitham_voice_agent.dispatcher import dispatch_action
from haitham_voice_agent.tts import get_tts
from haitham_voice_agent.tools.advisor import get_advisor
import time

class HVAMenuBarApp(rumps.App):
    def __init__(self):
        super(HVAMenuBarApp, self).__init__(
            "🎤 HVA",
            icon=None,
            quit_button=None
        )
        
        # Start GUI Process
        self.gui_queue = multiprocessing.Queue()
        self.cmd_queue = multiprocessing.Queue()
        self.gui_process = multiprocessing.Process(target=run_gui_process, args=(self.gui_queue, self.cmd_queue))
        self.gui_process.daemon = True
        self.gui_process.start()
        
        # Setup TTS Callback
        self.tts = get_tts()
        self.tts.set_callback(self._on_tts_speak)
        
        self.detector = get_detector()
        self.is_listening = False
        self.listen_thread = None
        
        # Start command listener thread
        self.cmd_thread = threading.Thread(target=self._listen_for_gui_commands)
        self.cmd_thread.daemon = True
        self.cmd_thread.start()
        
        # Start Advisor Background Thread
        self.advisor_thread = threading.Thread(target=self._run_advisor_checks)
        self.advisor_thread.daemon = True
        self.advisor_thread.start()
        
        # Start Ollama Warm-up Thread (to load model into VRAM)
        self.warmup_thread = threading.Thread(target=self._warmup_ollama)
        self.warmup_thread.daemon = True
        self.warmup_thread.start()
        
        # Menu items
        self.menu = [
            rumps.MenuItem("🎤 Listen (⌘⇧H)", callback=self.start_listening),
            rumps.separator,
            rumps.MenuItem("📝 Show Window", callback=self.show_window),
            rumps.MenuItem("🔄 Reset State", callback=self.reset_state),
            rumps.MenuItem("🗑️ Clear History", callback=self.clear_history),
            rumps.separator,
            rumps.MenuItem("ℹ️  About", callback=self.show_about),
            rumps.separator,
            rumps.MenuItem("⏹️  Quit", callback=self.quit_app),
        ]

    def _run_advisor_checks(self):
        """Run periodic advisor checks (Resources & Wellbeing)"""
        advisor = get_advisor()
        while True:
            try:
                # Check Resources
                res_alert = advisor.check_resources()
                if res_alert:
                    self.gui_queue.put(('add_message', 'error', res_alert, True))
                    
                # Check Wellbeing
                health_alert = advisor.check_wellbeing()
                if health_alert:
                    self.gui_queue.put(('add_message', 'info', health_alert, True))
                    
                # Sleep 5 minutes
                time.sleep(300)
            except Exception as e:
                print(f"Advisor check error: {e}")
                time.sleep(60)

    def _warmup_ollama(self):
        """Warm up Ollama model in background"""
        try:
            print("🔥 Warming up Ollama...")
            from haitham_voice_agent.ollama_orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
            
            # Simple hello to force model load
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(orchestrator.classify_request("hello"))
                print("✅ Ollama Warmed Up & Ready!")
            finally:
                loop.close()
        except Exception as e:
            print(f"⚠️ Ollama Warmup Failed: {e}")

    def _on_tts_speak(self, text):
        """Callback when TTS speaks (or would speak)"""
        # Forward to GUI as assistant message
        # We use auto_close=False so user can read it
        self.gui_queue.put(('add_message', 'assistant', text, False))
        
    def _listen_for_gui_commands(self):
        """Listen for commands sent from the GUI (Manual Input)"""
        while True:
            try:
                cmd_type, content = self.cmd_queue.get()
                if cmd_type == 'command':
                    print(f"⌨️  Manual Command: {content}")
                    # Process the command directly
                    threading.Thread(target=self._process_text_command, args=(content,)).start()
                elif cmd_type == 'listen':
                    print("🎤 GUI requested listening")
                    # Start listening in main thread context (or just call start_listening)
                    # We use rumps.timer or just call it directly since start_listening handles threading
                    self.start_listening(None)
            except Exception as e:
                print(f"Error in command listener: {e}")
                
    def _process_text_command(self, text):
        """Process a text command (same logic as voice but skips STT)"""
        try:
            # Detect wake word (optional for manual input, but good for consistency)
            has_wake_word, command = self.detector.detect(text)
            if not has_wake_word:
                command = text
                
            print(f"⚙️  Processing Manual: {command}")
            
            # --- 1. Ollama Orchestrator (Local Intelligence) ---
            from haitham_voice_agent.ollama_orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
            
            # Run async classification in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                classification = loop.run_until_complete(orchestrator.classify_request(command))
            finally:
                loop.close()
                
            plan = None
            
            if classification.get("type") == "direct_response":
                print("Ollama handled request directly.")
                self.gui_queue.put(('add_message', 'assistant', classification["response"], True))
                # Speak it too
                self.tts.speak(classification["response"])
                return
                
            elif classification.get("type") == "execute_command":
                print(f"Ollama identified command: {classification['intent']}")
                plan = {
                    "intent": classification["intent"],
                    "tool": "system", 
                    "action": classification["intent"],
                    "parameters": classification.get("parameters", {}),
                    "confirmation_needed": False
                }
            
            else:
                # Delegate to GPT
                print(f"Ollama delegated to: {classification.get('delegate_to')}")
                
                # Get router instance
                router = llm_router.get_router()
                
                # Generate execution plan
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    plan = loop.run_until_complete(router.generate_execution_plan(command))
                finally:
                    loop.close()
            
            if not plan:
                self.gui_queue.put(('add_message', 'error', 'لم أفهم الأمر / Could not understand command', True))
                return
            
            # Show plan intent
            intent = plan.get('intent', 'unknown')
            self.gui_queue.put(('add_message', 'info', f"Intent: {intent}", False))
            
            # Execute action
            result = dispatch_action(plan)
            
            # Show result
            if result.get('success'):
                response = result.get('message', 'تم التنفيذ بنجاح')
                self.gui_queue.put(('add_message', 'assistant', response, True))
                
                # Show additional info if available
                if 'data' in result:
                    data_str = str(result['data'])
                    # Check if it looks like a file list (contains newlines and filenames)
                    if '\n' in data_str and ('.txt' in data_str or '.pdf' in data_str or '.py' in data_str):
                         self.gui_queue.put(('add_message', 'file_list', data_str, True))
                    else:
                         self.gui_queue.put(('add_message', 'success', data_str[:200], True))
            else:
                error_msg = result.get('message', 'حدث خطأ')
                self.gui_queue.put(('add_message', 'error', error_msg, True))
            
            # Notification
            rumps.notification(
                title="✅ HVA Done",
                subtitle="",
                message="تم تنفيذ الأمر / Command executed"
            )
            
        except Exception as e:
            print(f"❌ Error processing manual command: {e}")
            import traceback
            traceback.print_exc()
            self.gui_queue.put(('add_message', 'error', f'حدث خطأ غير متوقع: {str(e)}', True))

    def start_listening(self, _):
        """Start listening for voice command"""
        print(f"🎤 start_listening called. is_listening={self.is_listening}")
        
        if self.is_listening:
            # Check if thread is actually alive
            if self.listen_thread and self.listen_thread.is_alive():
                print("⚠️ Already listening and thread is alive. Ignoring.")
                return
            else:
                print("⚠️ is_listening was True but thread is dead. Resetting.")
                self.is_listening = False
        
        self.is_listening = True
        
        # Run in separate thread to not block UI
        self.listen_thread = threading.Thread(target=self._listen_and_process)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def reset_state(self, _):
        """Force reset application state"""
        self.is_listening = False
        self.listen_thread = None
        rumps.notification("HVA", "", "State reset / تم إعادة تعيين الحالة")
    
    def _listen_and_process(self):
        """Listen for voice and process command"""
        try:
            # Show listening indicator (Pulse)
            self.gui_queue.put(('show_listening',))
            
            # Listen for voice
            print("🎤 Listening...")
            text = stt.listen_once()
            
            if not text:
                # Just a timeout, not a critical error
                self.gui_queue.put(('add_message', 'info', "Listening paused (Timeout) / انتهى الوقت", True))
                self.is_listening = False
                return
            
            print(f"📝 Transcribed: {text}")
            
            # Detect wake word
            has_wake_word, command = self.detector.detect(text)
            
            if has_wake_word:
                self.gui_queue.put(('add_message', 'user', command, False))
            else:
                # No wake word, use full text as command
                self.gui_queue.put(('add_message', 'user', text, False))
                command = text
            
            # Show processing
            self.gui_queue.put(('show_processing',))
            
            # Process command
            print(f"⚙️  Processing: {command}")
            
            try:
                # --- 1. Ollama Orchestrator (Local Intelligence) ---
                from haitham_voice_agent.ollama_orchestrator import get_orchestrator
                orchestrator = get_orchestrator()
                
                # Run async classification in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    classification = loop.run_until_complete(orchestrator.classify_request(command))
                finally:
                    loop.close()
                    
                plan = None
                
                if classification.get("type") == "direct_response":
                    print("Ollama handled request directly.")
                    self.gui_queue.put(('add_message', 'assistant', classification["response"], True))
                    # Speak it too
                    self.tts.speak(classification["response"])
                    self.is_listening = False # Reset listening state
                    return
                    
                elif classification.get("type") == "execute_command":
                    print(f"Ollama identified command: {classification['intent']}")
                    plan = {
                        "intent": classification["intent"],
                        "tool": "system", 
                        "action": classification["intent"],
                        "parameters": classification.get("parameters", {}),
                        "confirmation_needed": False
                    }
                
                else:
                    # Delegate to GPT
                    print(f"Ollama delegated to: {classification.get('delegate_to')}")
                    
                    # Get router instance
                    router = llm_router.get_router()
                    
                    # Generate execution plan (run async in sync context)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        plan = loop.run_until_complete(router.generate_execution_plan(command))
                    finally:
                        loop.close()
                
                if not plan:
                    self.gui_queue.put(('add_message', 'error', 'لم أفهم الأمر / Could not understand command', True))
                    self.is_listening = False
                    return
                
                # Show plan intent
                intent = plan.get('intent', 'unknown')
                self.gui_queue.put(('add_message', 'info', f"Intent: {intent}", False))
                
                # Execute action
                result = dispatch_action(plan)
                
                # Show result
                if result.get('success'):
                    response = result.get('message', 'تم التنفيذ بنجاح')
                    self.gui_queue.put(('add_message', 'assistant', response, True))
                    
                    # Show additional info if available
                    if 'data' in result:
                        data_str = str(result['data'])
                        # Check if it looks like a file list
                        if '\n' in data_str and ('.txt' in data_str or '.pdf' in data_str or '.py' in data_str):
                             self.gui_queue.put(('add_message', 'file_list', data_str, True))
                        elif "Organized" in data_str or "Cleaned" in data_str or "Briefing" in data_str:
                             # Show full report for organizer/briefing
                             self.gui_queue.put(('add_message', 'success', data_str, True))
                        else:
                             self.gui_queue.put(('add_message', 'success', data_str[:500], True))
                else:
                    error_msg = result.get('message', 'حدث خطأ')
                    self.gui_queue.put(('add_message', 'error', error_msg, True))
                
                # Notification
                rumps.notification(
                    title="✅ HVA Done",
                    subtitle="",
                    message="تم تنفيذ الأمر / Command executed"
                )
                
            except Exception as e:
                print(f"❌ Error processing command: {e}")
                self.gui_queue.put(('add_message', 'error', f'خطأ: {str(e)}', True))
                
        except Exception as e:
            print(f"❌ Error in listen_and_process: {e}")
            self.gui_queue.put(('add_message', 'error', f'خطأ: {str(e)}', True))
        
        finally:
            self.is_listening = False
    
    def show_window(self, _):
        """Show the GUI window"""
        self.gui_queue.put(('show',))
    
    def clear_history(self, _):
        """Clear the window history"""
        self.gui_queue.put(('clear',))
        rumps.notification(
            title="🗑️  HVA",
            subtitle="",
            message="تم مسح السجل / History cleared"
        )
    
    def show_about(self, _):
        """Show about dialog"""
        rumps.alert(
            title="🎤 Haitham Voice Agent",
            message=(
                "وكيلك الصوتي الذكي\n"
                "Your Smart Voice Assistant\n\n"
                "⌨️  اضغط ⌘⇧H للاستماع\n"
                "🎤 قل 'هيثم' + أمرك\n"
                "📝 شاهد النتائج في النافذة\n\n"
                "Made with ❤️ by Haitham"
            )
        )
    
    def quit_app(self, _):
        """Quit the application"""
        if self.gui_process:
            self.gui_process.terminate()
        rumps.quit_application()


def main():
    """Main entry point"""
    # Fix for multiprocessing on macOS
    multiprocessing.set_start_method('spawn', force=True)
    
    app = HVAMenuBarApp()
    
    # Register global hotkey (Cmd+Shift+H)
    try:
        from pynput import keyboard
        
        def on_activate():
            print("🎹 Hotkey pressed!")
            app.start_listening(None)
        
        # Define hotkey combination
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<cmd>+<shift>+h'),
            on_activate
        )
        
        def for_canonical(f):
            return lambda k: f(keyboard_listener.canonical(k))
        
        # Start keyboard listener in background
        keyboard_listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        )
        keyboard_listener.start()
        
        print("✅ Global hotkey registered: Cmd+Shift+H")
        
    except Exception as e:
        print(f"⚠️  Could not register global hotkey: {e}")
        print("You can still use the menu bar to activate listening.")
    
    # Show welcome notification
    rumps.notification(
        title="🎤 HVA Started",
        subtitle="",
        message="اضغط ⌘⇧H للبدء / Press ⌘⇧H to start"
    )
    
    # Run the app
    app.run()


if __name__ == "__main__":
    main()
