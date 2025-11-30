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


class HVAMenuBarApp(rumps.App):
    def __init__(self):
        super(HVAMenuBarApp, self).__init__(
            "🎤 HVA",
            icon=None,
            quit_button=None
        )
        
        # Start GUI Process
        self.gui_queue = multiprocessing.Queue()
        self.gui_process = multiprocessing.Process(target=run_gui_process, args=(self.gui_queue,))
        self.gui_process.daemon = True
        self.gui_process.start()
        
        self.detector = get_detector()
        self.is_listening = False
        
        self.listen_thread = None
        
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
            # Show listening indicator
            rumps.notification(
                title="🎤 HVA Listening",
                subtitle="",
                message="تحدث الآن... Speak now..."
            )
            
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
                        data_str = str(result['data'])[:200]  # Limit length
                        self.gui_queue.put(('add_message', 'success', data_str, True))
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
