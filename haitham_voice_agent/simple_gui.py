"""
Simple GUI Window for HVA
Shows command and response in a clean text window
"""

import tkinter as tk
from tkinter import scrolledtext, font
from datetime import datetime
import threading

# Modern Color Palette
COLORS = {
    'bg': '#1e1e2e',          # Dark blue-grey background
    'header_bg': '#181825',   # Slightly darker header
    'text_bg': '#1e1e2e',     # Matching text area background
    'text_fg': '#cdd6f4',     # Soft white text
    'user_bubble': '#89b4fa', # Light blue for user
    'bot_bubble': '#a6e3a1',  # Soft green for bot
    'error': '#f38ba8',       # Soft red
    'info': '#f9e2af',        # Soft yellow
    'timestamp': '#6c7086',   # Muted grey
    'button_bg': '#313244',   # Dark button background
    'button_fg': '#cdd6f4',   # Button text
    'button_hover': '#45475a' # Lighter button on hover
}

class HVAWindow:
    def __init__(self):
        self.window = None
        self.text_area = None
        self.auto_close_timer = None
        self.custom_font = None
        self.bold_font = None
        
    def create_window(self):
        """Create the main window"""
        if self.window:
            try:
                self.window.destroy()
            except:
                pass
            
        self.window = tk.Tk()
        self.window.title("🎤 Haitham Voice Agent")
        self.window.geometry("650x500")
        
        # Configure fonts
        self.custom_font = font.Font(family="Helvetica", size=14)
        self.bold_font = font.Font(family="Helvetica", size=14, weight="bold")
        
        # Set window position (center of screen)
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Configure window
        self.window.configure(bg=COLORS['bg'])
        
        # Always on top
        self.window.attributes('-topmost', True)
        
        # Create header
        header = tk.Frame(self.window, bg=COLORS['header_bg'], height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False) # Prevent shrinking
        
        title_label = tk.Label(
            header,
            text="🎤 Haitham Voice Agent",
            font=('Helvetica', 18, 'bold'),
            bg=COLORS['header_bg'],
            fg=COLORS['text_fg']
        )
        title_label.pack(expand=True)
        
        # Create text area with scrollbar
        self.text_area = scrolledtext.ScrolledText(
            self.window,
            wrap=tk.WORD,
            font=self.custom_font,
            bg=COLORS['text_bg'],
            fg=COLORS['text_fg'],
            insertbackground=COLORS['text_fg'],
            relief=tk.FLAT,
            padx=25,
            pady=25,
            selectbackground=COLORS['button_hover']
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Configure text tags for styling
        self.text_area.tag_configure('user_label', foreground=COLORS['user_bubble'], font=self.bold_font, justify='right')
        self.text_area.tag_configure('user_text', foreground=COLORS['text_fg'], font=self.custom_font, justify='right')
        
        self.text_area.tag_configure('bot_label', foreground=COLORS['bot_bubble'], font=self.bold_font, justify='left')
        self.text_area.tag_configure('bot_text', foreground=COLORS['text_fg'], font=self.custom_font, justify='left')
        
        self.text_area.tag_configure('success', foreground=COLORS['bot_bubble'], font=self.custom_font)
        self.text_area.tag_configure('error', foreground=COLORS['error'], font=self.custom_font)
        self.text_area.tag_configure('info', foreground=COLORS['info'], font=('Helvetica', 12, 'italic'))
        self.text_area.tag_configure('timestamp', foreground=COLORS['timestamp'], font=('Helvetica', 10))
        self.text_area.tag_configure('center', justify='center')
        
        # Make read-only
        self.text_area.configure(state='disabled')
        
        # Create footer with buttons
        footer = tk.Frame(self.window, bg=COLORS['header_bg'], height=50)
        footer.pack(fill=tk.X, padx=0, pady=0)
        footer.pack_propagate(False)
        
        # Helper to create styled buttons
        def create_btn(parent, text, cmd, side):
            btn = tk.Button(
                parent,
                text=text,
                command=cmd,
                bg=COLORS['button_bg'],
                fg=COLORS['button_fg'],
                activebackground=COLORS['button_hover'],
                activeforeground=COLORS['button_fg'],
                font=('Helvetica', 11),
                relief=tk.FLAT,
                bd=0,
                padx=15,
                pady=5,
                cursor='hand2'
            )
            btn.pack(side=side, padx=15, pady=10)
            return btn

        self.pin_button = create_btn(footer, "📌 Pin", self.toggle_pin, tk.LEFT)
        create_btn(footer, "🗑️ Clear", self.clear_text, tk.LEFT)
        create_btn(footer, "✕ Close", self.close_window, tk.RIGHT)
        
        self.is_pinned = False
        
    def toggle_pin(self):
        """Toggle window pin state"""
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.pin_button.configure(text="📍 Pinned", bg=COLORS['user_bubble'], fg=COLORS['header_bg'])
            if self.auto_close_timer:
                self.auto_close_timer.cancel()
        else:
            self.pin_button.configure(text="📌 Pin", bg=COLORS['button_bg'], fg=COLORS['button_fg'])
    
    def clear_text(self):
        """Clear all text"""
        self.text_area.configure(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state='disabled')
    
    def close_window(self):
        """Close the window"""
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
        if self.window:
            self.window.destroy()
            self.window = None
    
    def add_message(self, message_type, text, auto_close=True):
        """
        Add a message to the window
        message_type: 'user', 'assistant', 'success', 'error', 'info'
        """
        if not self.window:
            self.create_window()
        
        try:
            # Show window if hidden
            self.window.deiconify()
            self.window.lift()
            
            # Timestamp
            timestamp = datetime.now().strftime("%H:%M")
            
            # Enable editing
            self.text_area.configure(state='normal')
            
            # Add separator if not first message
            if self.text_area.get(1.0, tk.END).strip():
                self.text_area.insert(tk.END, "\n\n")
            
            # Add message with appropriate styling
            if message_type == 'user':
                self.text_area.insert(tk.END, f"You ({timestamp})\n", 'user_label')
                self.text_area.insert(tk.END, f"{text}", 'user_text')
                
            elif message_type == 'assistant':
                self.text_area.insert(tk.END, f"Haitham ({timestamp})\n", 'bot_label')
                self.text_area.insert(tk.END, f"{text}", 'bot_text')
                
            elif message_type == 'success':
                self.text_area.insert(tk.END, f"✅ {text}", 'success')
                
            elif message_type == 'error':
                self.text_area.insert(tk.END, f"❌ {text}", 'error')
                
            elif message_type == 'info':
                self.text_area.insert(tk.END, f"ℹ️ {text}", 'info')
            
            # Disable editing
            self.text_area.configure(state='disabled')
            
            # Auto-scroll to bottom
            self.text_area.see(tk.END)
            
            # Auto-close logic
            if auto_close and not self.is_pinned:
                if self.auto_close_timer:
                    self.auto_close_timer.cancel()
                # Longer timeout for better readability
                self.auto_close_timer = threading.Timer(15.0, self.close_window)
                self.auto_close_timer.start()
                
        except Exception as e:
            print(f"GUI Error: {e}")
    
    def show_listening(self):
        """Show listening indicator"""
        if not self.window:
            self.create_window()
        
        self.window.deiconify()
        self.window.lift()
        
        self.text_area.configure(state='normal')
        # Clear previous temporary messages if any (simple approach: just append)
        self.text_area.insert(tk.END, "\n\n🎤 Listening...\n", 'info')
        self.text_area.configure(state='disabled')
        self.text_area.see(tk.END)
    
    def show_processing(self):
        """Show processing indicator"""
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, "⚙️  Processing...\n", 'info')
        self.text_area.configure(state='disabled')
        self.text_area.see(tk.END)
    
    def run(self):
        """Run the GUI main loop"""
        if self.window:
            self.window.mainloop()


# Singleton instance
_window_instance = None

def get_window():
    """Get or create the singleton window instance"""
    global _window_instance
    if _window_instance is None:
        _window_instance = HVAWindow()
    return _window_instance


if __name__ == "__main__":
    # Test the window
    window = get_window()
    window.create_window()
    
    # Add some test messages
    window.add_message('user', 'احفظ ملاحظة عن الاجتماع', auto_close=False)
    window.add_message('assistant', 'تم حفظ الملاحظة بنجاح')
    window.add_message('success', 'الملاحظة: اجتماع المشروع غداً الساعة 3')
    
    window.run()
