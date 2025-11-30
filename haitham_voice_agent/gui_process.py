import tkinter as tk
from tkinter import font
from datetime import datetime
import threading
import queue
import time
import webbrowser
import math
import psutil  # For system stats

from .gui_widgets import COLORS, SystemStatusWidget, WeatherWidget, ChatWidget

class HVAWindow:
    def __init__(self, msg_queue, cmd_queue):
        self.msg_queue = msg_queue
        self.cmd_queue = cmd_queue
        self.window = None
        self.auto_close_timer = None
        self.is_pinned = False
        self.pulse_anim_id = None
        self.pulse_radius = 20
        self.pulse_growing = True
        
        # Widgets
        self.chat_widget = None
        self.status_widget = None
        self.weather_widget = None
        self.input_field = None
        self.pulse_canvas = None
        
    def create_window(self):
        """Create the main dashboard window"""
        if self.window:
            return
            
        self.window = tk.Tk()
        self.window.title("🎤 Haitham Voice Agent - Dashboard")
        self.window.geometry("1000x700")
        self.window.configure(bg=COLORS['bg'])
        
        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        # --- Layout Configuration ---
        self.window.grid_columnconfigure(1, weight=1) # Main content expands
        self.window.grid_rowconfigure(0, weight=1)    # Full height
        
        # --- Sidebar (Left) ---
        sidebar = tk.Frame(self.window, bg=COLORS['header_bg'], width=250)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.pack_propagate(False)
        
        # Profile / Header
        tk.Label(
            sidebar, 
            text="HVA", 
            font=('Helvetica', 24, 'bold'), 
            bg=COLORS['header_bg'], 
            fg=COLORS['accent']
        ).pack(pady=(30, 10))
        
        tk.Label(
            sidebar, 
            text="Executive Assistant", 
            font=('Helvetica', 10), 
            bg=COLORS['header_bg'], 
            fg=COLORS['text_sub']
        ).pack(pady=(0, 30))
        
        # Sidebar Menu Buttons
        def create_menu_btn(text, icon="•", command=None):
            btn = tk.Button(
                sidebar, 
                text=f"{icon}  {text}", 
                font=('Helvetica', 11),
                bg=COLORS['header_bg'], 
                fg=COLORS['text_fg'],
                activebackground=COLORS['card_bg'],
                activeforeground=COLORS['accent'],
                relief=tk.FLAT, 
                bd=0, 
                anchor="w",
                padx=20,
                pady=10,
                cursor="hand2",
                command=command
            )
            btn.pack(fill=tk.X, pady=2)
            return btn
            
        create_menu_btn("Dashboard", "📊", lambda: self.show_view("dashboard"))
        create_menu_btn("Files", "📁", lambda: self.show_view("files"))
        create_menu_btn("Settings", "⚙️", lambda: self.show_view("settings"))
        
        # Spacer
        tk.Frame(sidebar, bg=COLORS['header_bg']).pack(fill=tk.Y, expand=True)
        
        # Bottom Actions
        self.pin_btn = tk.Button(
            sidebar, text="📌 Pin Window", command=self.toggle_pin,
            bg=COLORS['header_bg'], fg=COLORS['text_sub'], relief=tk.FLAT, bd=0
        )
        self.pin_btn.pack(side=tk.BOTTOM, pady=10)
        
        # --- Main Content Area (Right) ---
        self.main_area = tk.Frame(self.window, bg=COLORS['bg'])
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Views Container
        self.views = {}
        self.current_view = None
        
        # Initialize Views
        self.init_dashboard_view()
        self.init_files_view()
        self.init_settings_view()
        
        # Show default view
        self.show_view("dashboard")
        
        # Start background updates
        self.update_system_stats()
        self.check_queue()
        
    def init_dashboard_view(self):
        """Initialize Dashboard View"""
        frame = tk.Frame(self.main_area, bg=COLORS['bg'])
        self.views["dashboard"] = frame
        
        # Top Row: Widgets
        widgets_frame = tk.Frame(frame, bg=COLORS['bg'])
        widgets_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.weather_widget = WeatherWidget(widgets_frame, width=200, height=120)
        self.weather_widget.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_widget = SystemStatusWidget(widgets_frame, width=200, height=120)
        self.status_widget.pack(side=tk.LEFT, padx=10)
        
        # Pulse Indicator
        self.pulse_canvas = tk.Canvas(widgets_frame, width=60, height=60, bg=COLORS['bg'], highlightthickness=0)
        self.pulse_canvas.pack(side=tk.RIGHT, padx=20)
        self.draw_pulse(active=False)
        
        # Center: Chat History
        self.chat_widget = ChatWidget(frame)
        self.chat_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Welcome Message
        self.chat_widget.add_message('assistant', "👋 Welcome back, Haitham.\nSystem is ready.", datetime.now().strftime("%H:%M"))
        
        # Bottom: Input Bar
        input_frame = tk.Frame(frame, bg=COLORS['card_bg'], height=60)
        input_frame.pack(fill=tk.X)
        input_frame.pack_propagate(False)
        
        self.input_field = tk.Entry(
            input_frame,
            bg=COLORS['card_bg'],
            fg=COLORS['text_fg'],
            insertbackground=COLORS['text_fg'],
            font=('Helvetica', 12),
            relief=tk.FLAT,
            bd=0
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 10), pady=15)
        self.input_field.bind("<Return>", self.send_command)
        
        # Mic Button
        mic_btn = tk.Button(
            input_frame, text="🎤", command=self.send_listen_command,
            bg=COLORS['card_bg'], fg=COLORS['accent'],
            font=('Helvetica', 16), relief=tk.FLAT, bd=0,
            cursor="hand2"
        )
        mic_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=10, fill=tk.Y)
        
        send_btn = tk.Button(
            input_frame, text="➤", command=self.send_command,
            bg=COLORS['accent'], fg=COLORS['bg'],
            font=('Helvetica', 14, 'bold'), relief=tk.FLAT, bd=0,
            cursor="hand2"
        )
        send_btn.pack(side=tk.RIGHT, padx=(0, 20), pady=10, fill=tk.Y)

    def send_listen_command(self):
        """Send listen command to main process"""
        self.cmd_queue.put(('listen', None))

    def init_files_view(self):
        """Initialize Files View"""
        frame = tk.Frame(self.main_area, bg=COLORS['bg'])
        self.views["files"] = frame
        
        tk.Label(frame, text="Recent Files", font=('Helvetica', 18, 'bold'), bg=COLORS['bg'], fg=COLORS['text_fg']).pack(anchor="w", pady=(0, 20))
        
        # Simple list of files in Home
        import os
        home = os.path.expanduser("~")
        files_frame = tk.Frame(frame, bg=COLORS['card_bg'])
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            files = [f for f in os.listdir(home) if not f.startswith('.')]
            for i, f in enumerate(files[:15]): # Show top 15
                path = os.path.join(home, f)
                lbl = tk.Label(files_frame, text=f"📄 {f}", bg=COLORS['card_bg'], fg=COLORS['text_fg'], anchor="w", cursor="hand2")
                lbl.pack(fill=tk.X, padx=10, pady=5)
                # Bind click to open file
                lbl.bind("<Button-1>", lambda e, p=path: self.open_file(p))
        except:
            tk.Label(files_frame, text="Error loading files", bg=COLORS['card_bg'], fg=COLORS['error']).pack()

    def open_file(self, path):
        """Open a file with default application"""
        import subprocess
        try:
            subprocess.call(['open', path])
        except Exception as e:
            print(f"Error opening file: {e}")

    def init_settings_view(self):
        """Initialize Settings View"""
        frame = tk.Frame(self.main_area, bg=COLORS['bg'])
        self.views["settings"] = frame
        
        tk.Label(frame, text="Settings", font=('Helvetica', 18, 'bold'), bg=COLORS['bg'], fg=COLORS['text_fg']).pack(anchor="w", pady=(0, 20))
        
        def create_toggle(parent, text, default=True):
            f = tk.Frame(parent, bg=COLORS['card_bg'], pady=10, padx=10)
            f.pack(fill=tk.X, pady=5)
            tk.Label(f, text=text, bg=COLORS['card_bg'], fg=COLORS['text_fg'], font=('Helvetica', 12)).pack(side=tk.LEFT)
            btn = tk.Button(f, text="ON" if default else "OFF", bg=COLORS['accent'], fg=COLORS['bg'], width=6)
            btn.pack(side=tk.RIGHT)
            return btn
            
        create_toggle(frame, "Voice Output (TTS)")
        create_toggle(frame, "Sound Effects")
        create_toggle(frame, "Auto-Close Window")
        create_toggle(frame, "Dark Mode")

    def show_view(self, view_name):
        """Switch visible view"""
        if self.current_view:
            self.current_view.pack_forget()
        
        if view_name in self.views:
            self.views[view_name].pack(fill=tk.BOTH, expand=True)
            self.current_view = self.views[view_name]
        
    def update_system_stats(self):
        """Update CPU/RAM widgets"""
        if self.window and self.status_widget:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.status_widget.update_stats(cpu, ram)
            
        if self.window:
            self.window.after(2000, self.update_system_stats)

    def draw_pulse(self, active=False):
        """Draw the pulsing circle"""
        if not self.pulse_canvas: return
        self.pulse_canvas.delete("all")
        
        color = COLORS['error'] if active else COLORS['border']
        r = self.pulse_radius if active else 15
        
        # Center is 30, 30
        self.pulse_canvas.create_oval(30-r, 30-r, 30+r, 30+r, fill=color, outline="")
        
        if active:
            # Animate
            if self.pulse_growing:
                self.pulse_radius += 0.5
                if self.pulse_radius >= 25: self.pulse_growing = False
            else:
                self.pulse_radius -= 0.5
                if self.pulse_radius <= 15: self.pulse_growing = True
            
            self.pulse_anim_id = self.window.after(50, lambda: self.draw_pulse(True))
        elif self.pulse_anim_id:
            self.window.after_cancel(self.pulse_anim_id)
            self.pulse_anim_id = None

    def send_command(self, event=None):
        text = self.input_field.get().strip()
        if text:
            self.cmd_queue.put(('command', text))
            self.input_field.delete(0, tk.END)
            self.chat_widget.add_message('user', text, datetime.now().strftime("%H:%M"))
            self.show_processing_internal()

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
            self.pin_btn.configure(text="📍 Pinned", fg=COLORS['accent'])
            if self.auto_close_timer:
                self.window.after_cancel(self.auto_close_timer)
                self.auto_close_timer = None
        else:
            self.pin_btn.configure(text="📌 Pin Window", fg=COLORS['text_sub'])
            
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
        
        self.draw_pulse(active=False)
        timestamp = datetime.now().strftime("%H:%M")
        
        sender = 'user' if message_type == 'user' else 'assistant'
        self.chat_widget.add_message(sender, text, timestamp)
        
        if auto_close and not self.is_pinned:
            # Default to NOT auto-closing for now to prevent "disappearing" issues
            # Only auto-close if explicitly requested and pinned is false
            pass 
            # if self.auto_close_timer: self.window.after_cancel(self.auto_close_timer)
            # self.auto_close_timer = self.window.after(60000, self.close_window)

    def show_listening_internal(self):
        if not self.window: self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.draw_pulse(active=True)

    def show_processing_internal(self):
        self.draw_pulse(active=False)
        # Maybe show a spinner later

    def run(self):
        self.create_window()
        # self.window.withdraw() # Don't hide initially for testing/dashboard feel
        self.window.mainloop()

def run_gui_process(msg_queue, cmd_queue=None):
    if cmd_queue is None:
        cmd_queue = queue.Queue()
    app = HVAWindow(msg_queue, cmd_queue)
    app.run()
