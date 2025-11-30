"""
HVA Menu Bar App
Simple menu bar application with global keyboard shortcut
"""

import rumps
import threading
import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from haitham_voice_agent.simple_gui import get_window
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
        
        self.window = get_window()
        self.detector = get_detector()
        self.is_listening = False
        
        # Menu items
        self.menu = [
            rumps.MenuItem("🎤 Listen (⌘⇧H)", callback=self.start_listening),
            rumps.separator,
            rumps.MenuItem("📝 Show Window", callback=self.show_window),
            rumps.MenuItem("🗑️ Clear History", callback=self.clear_history),
            rumps.separator,
            rumps.MenuItem("ℹ️  About", callback=self.show_about),
            rumps.separator,
            rumps.MenuItem("⏹️  Quit", callback=self.quit_app),
        ]
        
    def start_listening(self, _):
        """Start listening for voice command"""
        if self.is_listening:
            return
        
        self.is_listening = True
        
        # Run in separate thread to not block UI
        thread = threading.Thread(target=self._listen_and_process)
        thread.daemon = True
        thread.start()
    
    def _listen_and_process(self):
        """Listen for voice and process command"""
        try:
            # Show listening indicator
            rumps.notification(
                title="🎤 HVA Listening",
                subtitle="",
                message="تحدث الآن... Speak now..."
            )
            
            self.window.create_window()
            self.window.show_listening()
            
            # Listen for voice
            print("🎤 Listening...")
            text = stt.listen_once()
            
            if not text:
                self.window.add_message('error', 'لم أسمع شيئاً / No speech detected')
                self.is_listening = False
                return
            
            print(f"📝 Transcribed: {text}")
            
            # Detect wake word
            has_wake_word, command = self.detector.detect(text)
            
            if has_wake_word:
                self.window.add_message('user', command)
            else:
                # No wake word, use full text as command
                self.window.add_message('user', text)
                command = text
            
            # Show processing
            self.window.show_processing()
            
            # Process command
            print(f"⚙️  Processing: {command}")
            
            try:
                # Get router instance
                router = llm_router.get_router()
                
                # Generate execution plan (run async in sync context)
                # We need a new loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    plan = loop.run_until_complete(router.generate_execution_plan(command))
                finally:
                    loop.close()
                
                if not plan:
                    self.window.add_message('error', 'لم أفهم الأمر / Could not understand command')
                    self.is_listening = False
                    return
                
                # Show plan intent
                intent = plan.get('intent', 'unknown')
                self.window.add_message('info', f"Intent: {intent}")
                
                # Execute action
                result = dispatch_action(plan)
                
                # Show result
                if result.get('success'):
                    response = result.get('message', 'تم التنفيذ بنجاح')
                    self.window.add_message('assistant', response)
                    
                    # Show additional info if available
                    if 'data' in result:
                        data_str = str(result['data'])[:200]  # Limit length
                        self.window.add_message('success', data_str)
                else:
                    error_msg = result.get('message', 'حدث خطأ')
                    self.window.add_message('error', error_msg)
                
                # Notification
                rumps.notification(
                    title="✅ HVA Done",
                    subtitle="",
                    message="تم تنفيذ الأمر / Command executed"
                )
                
            except Exception as e:
                print(f"❌ Error processing command: {e}")
                self.window.add_message('error', f'خطأ: {str(e)}')
                
        except Exception as e:
            print(f"❌ Error in listen_and_process: {e}")
            self.window.add_message('error', f'خطأ: {str(e)}')
        
        finally:
            self.is_listening = False
    
    def show_window(self, _):
        """Show the GUI window"""
        if not self.window.window:
            self.window.create_window()
        self.window.window.deiconify()
        self.window.window.lift()
    
    def clear_history(self, _):
        """Clear the window history"""
        self.window.clear_text()
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
        rumps.quit_application()


def main():
    """Main entry point"""
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
