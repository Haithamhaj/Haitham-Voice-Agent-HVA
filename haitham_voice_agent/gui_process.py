import tkinter as tk
from tkinter import scrolledtext, font
from datetime import datetime
import threading
import queue
import time
import webbrowser
import math

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
    'link': '#89b4fa',        # Link color
    'timestamp': '#6c7086',   # Muted grey
    'button_bg': '#313244',   # Dark button background
    'button_fg': '#cdd6f4',   # Button text
    'button_hover': '#45475a', # Lighter button on hover
    'input_bg': '#313244',    # Input box background
    'pulse_active': '#f38ba8', # Red for active recording
    'pulse_passive': '#45475a' # Grey for idle
}

class HVAWindow:
    def __init__(self, msg_queue, cmd_queue):
        self.msg_queue = msg_queue
        self.cmd_queue = cmd_queue
        self.window = None
        self.text_area = None
        self.input_field = None
        self.canvas = None
        self.auto_close_timer = None
        self.is_pinned = False
        self.custom_font = None
        self.bold_font = None
        self.pulse_anim_id = None
        self.pulse_radius = 20
        self.pulse_growing = True
        
    def create_window(self):
        """Create the main window"""
        if self.window:
            return
            
        self.window = tk.Tk()
        self.window.title("🎤 Haitham Voice Agent")
        self.window.geometry("650x600")
        
        # Configure fonts
        self.custom_font = font.Font(family="Helvetica", size=14)
        self.bold_font = font.Font(family="Helvetica", size=14, weight="bold")
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        self.window.configure(bg=COLORS['bg'])
        self.window.attributes('-topmost', True)
        
        # --- Header ---
        header = tk.Frame(self.window, bg=COLORS['header_bg'], height=70)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Pulsing Animation Canvas (Left)
        self.canvas = tk.Canvas(header, width=50, height=50, bg=COLORS['header_bg'], highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=15, pady=10)
        self.draw_pulse(active=False)
        
        # Title (Center)
        title_label = tk.Label(
            header,
            text="🎤 Haitham Voice Agent",
            font=('Helvetica', 18, 'bold'),
            bg=COLORS['header_bg'],
            fg=COLORS['text_fg']
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # --- Chat Area ---
        self.text_area = scrolledtext.ScrolledText(
            self.window,
            wrap=tk.WORD,
            font=self.custom_font,
            bg=COLORS['text_bg'],
            fg=COLORS['text_fg'],
            insertbackground=COLORS['text_fg'],
            relief=tk.FLAT,
            padx=20,
            pady=20,
            selectbackground=COLORS['button_hover']
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Tags
        self.text_area.tag_configure('user_label', foreground=COLORS['user_bubble'], font=self.bold_font, justify='right')
        self.text_area.tag_configure('user_text', foreground=COLORS['text_fg'], font=self.custom_font, justify='right')
        self.text_area.tag_configure('bot_label', foreground=COLORS['bot_bubble'], font=self.bold_font, justify='left')
        self.text_area.tag_configure('bot_text', foreground=COLORS['text_fg'], font=self.custom_font, justify='left')
        self.text_area.tag_configure('success', foreground=COLORS['bot_bubble'], font=self.custom_font)
        self.text_area.tag_configure('error', foreground=COLORS['error'], font=self.custom_font)
        self.text_area.tag_configure('info', foreground=COLORS['info'], font=('Helvetica', 12, 'italic'))
        self.text_area.tag_configure('link', foreground=COLORS['link'], underline=1)
        self.text_area.tag_bind('link', '<Button-1>', self.handle_link_click)
        self.text_area.tag_bind('link', '<Enter>', lambda e: self.text_area.configure(cursor="hand2"))
        self.text_area.tag_bind('link', '<Leave>', lambda e: self.text_area.configure(cursor="arrow"))
        
        self.text_area.configure(state='disabled')
        
        # Welcome Message
        self.add_message_internal('info', "👋 Welcome to HVA Smart GUI 2.0!\nReady to help. Speak or type below.", False)
        
        # --- Input Area ---
        input_frame = tk.Frame(self.window, bg=COLORS['header_bg'], height=60)
        input_frame.pack(fill=tk.X, padx=0, pady=0)
        input_frame.pack_propagate(False)
        
        self.input_field = tk.Entry(
            input_frame,
            bg=COLORS['input_bg'],
            fg=COLORS['text_fg'],
            insertbackground=COLORS['text_fg'],
            font=self.custom_font,
            relief=tk.FLAT,
            bd=5
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(15, 10), pady=10)
        self.input_field.bind("<Return>", self.send_command)
        
        send_btn = tk.Button(
            input_frame, text="➤", command=self.send_command,
            bg=COLORS['user_bubble'], fg=COLORS['header_bg'],
            font=('Helvetica', 14, 'bold'), relief=tk.FLAT, bd=0, padx=15
        )
        send_btn.pack(side=tk.RIGHT, padx=(0, 15), pady=10)
        
        # --- Footer ---
        footer = tk.Frame(self.window, bg=COLORS['header_bg'], height=40)
        footer.pack(fill=tk.X)
        
        def create_btn(parent, text, cmd, side):
            btn = tk.Button(
                parent, text=text, command=cmd,
                bg=COLORS['button_bg'], fg=COLORS['button_fg'],
                activebackground=COLORS['button_hover'], activeforeground=COLORS['button_fg'],
                font=('Helvetica', 10), relief=tk.FLAT, bd=0, padx=10, pady=2, cursor='hand2'
            )
            btn.pack(side=side, padx=10, pady=5)
            return btn

        self.pin_button = create_btn(footer, "📌 Pin", self.toggle_pin, tk.LEFT)
        create_btn(footer, "🗑️ Clear", self.clear_text, tk.LEFT)
        create_btn(footer, "✕ Close", self.close_window, tk.RIGHT)
        
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        self.check_queue()
        
    def draw_pulse(self, active=False):
        """Draw the pulsing circle"""
        if not self.canvas: return
        self.canvas.delete("all")
        
        color = COLORS['pulse_active'] if active else COLORS['pulse_passive']
        r = self.pulse_radius if active else 15
        
        # Center is 25, 25
        self.canvas.create_oval(25-r, 25-r, 25+r, 25+r, fill=color, outline="")
        
        if active:
            # Animate
            if self.pulse_growing:
                self.pulse_radius += 0.5
                if self.pulse_radius >= 22: self.pulse_growing = False
            else:
                self.pulse_radius -= 0.5
                if self.pulse_radius <= 18: self.pulse_growing = True
            
            self.pulse_anim_id = self.window.after(50, lambda: self.draw_pulse(True))
        elif self.pulse_anim_id:
            self.window.after_cancel(self.pulse_anim_id)
            self.pulse_anim_id = None

    def send_command(self, event=None):
        """Send text from input field to main process"""
        text = self.input_field.get().strip()
        if text:
            self.cmd_queue.put(('command', text))
            self.input_field.delete(0, tk.END)
            # Show user message immediately
            self.add_message_internal('user', text, False)
            self.show_processing_internal()

    def handle_link_click(self, event):
        """Handle clicking on a file link"""
        try:
            index = self.text_area.index(f"@{event.x},{event.y}")
            tags = self.text_area.tag_names(index)
            
            if "link" in tags:
                # Get the line text
                line_start = f"{index.split('.')[0]}.0"
                line_end = f"{index.split('.')[0]}.end"
                line_text = self.text_area.get(line_start, line_end).strip()
                
                # Check if it's a file path
                import os
                if os.path.exists(line_text):
                    webbrowser.open(f"file://{line_text}")
                    self.add_message_internal('info', f"Opening: {line_text}", False)
                elif line_text.startswith("http"):
                    webbrowser.open(line_text)
                    self.add_message_internal('info', f"Opening: {line_text}", False)
        except Exception as e:
            print(f"Link click error: {e}")

    def check_queue(self):
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                self.process_message(msg)
        except queue.Empty:
            pass
        finally:
            if self.window:
                self.window.after(100, self.check_queue)
    
    def process_message(self, msg):
        cmd = msg[0]
        
        if cmd == 'show':
            if not self.window: self.create_window()
            self.window.deiconify()
            self.window.lift()
            
        elif cmd == 'close':
            self.close_window()
            
        elif cmd == 'clear':
            self.clear_text()
            
        elif cmd == 'add_message':
            _, msg_type, text, auto_close = msg
            self.add_message_internal(msg_type, text, auto_close)
            
        elif cmd == 'show_listening':
            self.show_listening_internal()
            
        elif cmd == 'show_processing':
            self.show_processing_internal()
            
    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.pin_button.configure(text="📍 Pinned", bg=COLORS['user_bubble'], fg=COLORS['header_bg'])
            if self.auto_close_timer:
                self.window.after_cancel(self.auto_close_timer)
                self.auto_close_timer = None
        else:
            self.pin_button.configure(text="📌 Pin", bg=COLORS['button_bg'], fg=COLORS['button_fg'])
            
    def clear_text(self):
        if self.text_area:
            self.text_area.configure(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.configure(state='disabled')
            
    def close_window(self):
        if self.auto_close_timer:
            self.window.after_cancel(self.auto_close_timer)
            self.auto_close_timer = None
        if self.window:
            self.window.withdraw()
            
    def add_message_internal(self, message_type, text, auto_close):
        if not self.window: self.create_window()
        self.window.deiconify()
        self.window.lift()
        
        # Stop pulsing if it was active
        self.draw_pulse(active=False)
        
        timestamp = datetime.now().strftime("%H:%M")
        self.text_area.configure(state='normal')
        
        if self.text_area.get(1.0, tk.END).strip():
            self.text_area.insert(tk.END, "\n\n")
            
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
        elif message_type == 'file_list':
            # Special handling for file lists to make them clickable
            self.text_area.insert(tk.END, f"📂 Found Files:\n", 'bot_label')
            files = text.split('\n')
            for f in files:
                self.text_area.insert(tk.END, f"{f}\n", 'link')
            
        self.text_area.configure(state='disabled')
        self.text_area.see(tk.END)
        
        if auto_close and not self.is_pinned:
            if self.auto_close_timer: self.window.after_cancel(self.auto_close_timer)
            self.auto_close_timer = self.window.after(15000, self.close_window)

    def show_listening_internal(self):
        if not self.window: self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.draw_pulse(active=True)
        # We don't need text anymore, the pulse is enough
        # But we can show a small status
        self.window.title("🎤 Listening...")

    def show_processing_internal(self):
        self.draw_pulse(active=False)
        self.window.title("⚙️ Processing...")
        if self.text_area:
            self.text_area.configure(state='normal')
            self.text_area.insert(tk.END, "\n⚙️  Processing...\n", 'info')
            self.text_area.configure(state='disabled')
            self.text_area.see(tk.END)

    def run(self):
        self.create_window()
        self.window.withdraw()
        self.window.mainloop()

def run_gui_process(msg_queue, cmd_queue=None):
    """Entry point for the GUI process"""
    # Handle case where cmd_queue is not passed (backward compatibility)
    if cmd_queue is None:
        cmd_queue = queue.Queue() # Dummy queue
        
    app = HVAWindow(msg_queue, cmd_queue)
    app.run()
