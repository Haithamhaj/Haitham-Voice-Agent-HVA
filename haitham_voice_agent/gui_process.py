import tkinter as tk
from tkinter import font
from datetime import datetime
import threading
import queue
import time
import webbrowser
import math
import psutil  # For system stats

from .gui_widgets import COLORS, SystemStatusWidget, WeatherWidget, ChatWidget, AgentStatusWidget, ModernButton

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
        self.agent_status_widget = None
        self.input_field = None
        self.pulse_canvas = None
        
    def create_window(self):
        """Create the main dashboard window"""
        if self.window:
            return
            
        self.window = tk.Tk()
        self.window.title("🎤 Haitham Voice Agent - Premium Dashboard")
        self.window.geometry("1100x750")
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
        sidebar = tk.Frame(self.window, bg=COLORS['header_bg'], width=260)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.pack_propagate(False)
        
        # Profile / Header
        tk.Label(
            sidebar, 
            text="HVA", 
            font=('Helvetica', 28, 'bold'), 
            bg=COLORS['header_bg'], 
            fg=COLORS['accent']
        ).pack(pady=(40, 5))
        
        tk.Label(
            sidebar, 
            text="INTELLIGENCE SYSTEM", 
            font=('Helvetica', 9, 'bold'), 
            bg=COLORS['header_bg'], 
            fg=COLORS['text_sub']
        ).pack(pady=(0, 40))
        
        # Sidebar Menu Buttons
        def create_menu_btn(text, icon="•", command=None):
            btn_frame = tk.Frame(sidebar, bg=COLORS['header_bg'])
            btn_frame.pack(fill=tk.X, pady=2, padx=10)
            
            lbl = tk.Label(
                btn_frame, 
                text=f"{icon}   {text}", 
                font=('Helvetica', 11),
                bg=COLORS['header_bg'], 
                fg=COLORS['text_fg'],
                anchor="w",
                padx=20,
                pady=12,
                cursor="hand2"
            )
            lbl.pack(fill=tk.X)
            
            def on_enter(e):
                lbl.configure(bg=COLORS['card_bg'], fg=COLORS['accent'])
                btn_frame.configure(bg=COLORS['card_bg'])
                
            def on_leave(e):
                lbl.configure(bg=COLORS['header_bg'], fg=COLORS['text_fg'])
                btn_frame.configure(bg=COLORS['header_bg'])
                
            def on_click(e):
                if command: command()
                
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", on_click)
            
            return lbl
            
        create_menu_btn("Dashboard", "📊", lambda: self.show_view("dashboard"))
        create_menu_btn("Files", "📁", lambda: self.show_view("files"))
        create_menu_btn("Settings", "⚙️", lambda: self.show_view("settings"))
        
        # Spacer
        tk.Frame(sidebar, bg=COLORS['header_bg']).pack(fill=tk.Y, expand=True)
        
        # Bottom Actions
        self.pin_btn = tk.Button(
            sidebar, text="📌 Pin Window", command=self.toggle_pin,
            bg=COLORS['header_bg'], fg=COLORS['text_sub'], relief=tk.FLAT, bd=0,
            activebackground=COLORS['header_bg'], activeforeground=COLORS['accent']
        )
        self.pin_btn.pack(side=tk.BOTTOM, pady=20)
        
        # --- Main Content Area (Right) ---
        self.main_area = tk.Frame(self.window, bg=COLORS['bg'])
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        
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
        """Initialize Premium Dashboard View"""
        frame = tk.Frame(self.main_area, bg=COLORS['bg'])
        self.views["dashboard"] = frame
        
        # --- Header Section ---
        header_frame = tk.Frame(frame, bg=COLORS['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Greeting
        hour = datetime.now().hour
        greeting = "Good Morning" if 5 <= hour < 12 else "Good Afternoon" if 12 <= hour < 18 else "Good Evening"
        
        tk.Label(
            header_frame, 
            text=f"{greeting}, Haitham.", 
            font=('Helvetica', 24, 'bold'), 
            bg=COLORS['bg'], 
            fg=COLORS['text_fg']
        ).pack(side=tk.LEFT)
        
        # Pulse Indicator (Top Right)
        self.pulse_canvas = tk.Canvas(header_frame, width=50, height=50, bg=COLORS['bg'], highlightthickness=0)
        self.pulse_canvas.pack(side=tk.RIGHT)
        self.draw_pulse(active=False)
        
        # --- Widgets Row ---
        widgets_frame = tk.Frame(frame, bg=COLORS['bg'])
        widgets_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 1. Weather
        self.weather_widget = WeatherWidget(widgets_frame, width=180, height=140)
        self.weather_widget.pack(side=tk.LEFT, padx=(0, 15))
        
        # 2. System Status
        self.status_widget = SystemStatusWidget(widgets_frame, width=180, height=140)
        self.status_widget.pack(side=tk.LEFT, padx=(0, 15))
        
        # 3. Agent Status (New!)
        self.agent_status_widget = AgentStatusWidget(widgets_frame, width=220, height=140)
        self.agent_status_widget.pack(side=tk.LEFT, padx=(0, 15))
        
        # 4. Quick Actions (New!)
        actions_frame = tk.Frame(widgets_frame, bg=COLORS['bg'])
        actions_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(actions_frame, text="QUICK ACTIONS", font=('Helvetica', 9, 'bold'), bg=COLORS['bg'], fg=COLORS['text_sub']).pack(anchor="w", pady=(0, 5))
        
        btn_grid = tk.Frame(actions_frame, bg=COLORS['bg'])
        btn_grid.pack(fill=tk.BOTH, expand=True)
        
        ModernButton(btn_grid, "Briefing", lambda: self.send_text_command("Morning Briefing"), icon="☀️", bg=COLORS['card_bg'], width=120).grid(row=0, column=0, padx=5, pady=5)
        ModernButton(btn_grid, "Calendar", lambda: self.send_text_command("Check Calendar"), icon="📅", bg=COLORS['card_bg'], width=120).grid(row=0, column=1, padx=5, pady=5)
        ModernButton(btn_grid, "Clear", lambda: self.chat_widget.clear(), icon="🗑️", bg=COLORS['card_bg'], width=120).grid(row=1, column=0, padx=5, pady=5)
        ModernButton(btn_grid, "Work Mode", lambda: self.send_text_command("Work Mode"), icon="💼", bg=COLORS['card_bg'], width=120).grid(row=1, column=1, padx=5, pady=5)
        
        # --- Chat Area ---
        chat_container = tk.Frame(frame, bg=COLORS['card_bg']) # Container for border effect
        chat_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.chat_widget = ChatWidget(chat_container)
        self.chat_widget.pack(fill=tk.BOTH, expand=True, padx=1, pady=1) # Thin border
        
        self.chat_widget.add_message('assistant', "System online. Intelligence modules active.", datetime.now().strftime("%H:%M"))
        
        # --- Input Area ---
        input_frame = tk.Frame(frame, bg=COLORS['card_bg'], height=60)
        input_frame.pack(fill=tk.X)
        input_frame.pack_propagate(False)
        
        self.input_field = tk.Entry(
            input_frame,
            bg=COLORS['card_bg'],
            fg=COLORS['text_fg'],
            insertbackground=COLORS['text_fg'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['bg'],
            font=('Helvetica', 13),
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
            cursor="hand2", activebackground=COLORS['card_bg'], activeforeground=COLORS['text_fg']
        )
        mic_btn.pack(side=tk.RIGHT, padx=(0, 10), pady=10, fill=tk.Y)
        
        send_btn = tk.Button(
            input_frame, text="➤", command=self.send_command,
            bg=COLORS['accent'], fg=COLORS['bg'],
            font=('Helvetica', 14, 'bold'), relief=tk.FLAT, bd=0,
            cursor="hand2", activebackground=COLORS['accent_hover']
        )
        send_btn.pack(side=tk.RIGHT, padx=(0, 20), pady=10, fill=tk.Y)

    def send_listen_command(self):
        """Send listen command to main process"""
        self.cmd_queue.put(('listen', None))

    def send_text_command(self, text):
        """Send text command directly"""
        self.cmd_queue.put(('command', text))
        self.chat_widget.add_message('user', text, datetime.now().strftime("%H:%M"))
        self.show_processing_internal()

    def init_files_view(self):
        """Initialize Files View"""
        frame = tk.Frame(self.main_area, bg=COLORS['bg'])
        self.views["files"] = frame
        
        tk.Label(frame, text="Recent Files", font=('Helvetica', 20, 'bold'), bg=COLORS['bg'], fg=COLORS['text_fg']).pack(anchor="w", pady=(0, 20))
        
        # Simple list of files in Home
        import os
        home = os.path.expanduser("~")
        files_frame = tk.Frame(frame, bg=COLORS['bg'])
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        try:
            files = [f for f in os.listdir(home) if not f.startswith('.')]
            for i, f in enumerate(files[:15]): # Show top 15
                path = os.path.join(home, f)
                
                # File Row
                row = tk.Frame(files_frame, bg=COLORS['card_bg'])
                row.pack(fill=tk.X, pady=2)
                
                icon = "📁" if os.path.isdir(path) else "📄"
                
                lbl = tk.Label(
                    row, 
                    text=f"{icon}  {f}", 
                    bg=COLORS['card_bg'], 
                    fg=COLORS['text_fg'], 
                    font=('Helvetica', 11),
                    anchor="w", 
                    padx=15,
                    pady=10,
                    cursor="hand2"
                )
                lbl.pack(fill=tk.X)
                # Bind click to open file
                lbl.bind("<Button-1>", lambda e, p=path: self.open_file(p))
        except:
            tk.Label(files_frame, text="Error loading files", bg=COLORS['bg'], fg=COLORS['error']).pack()

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
        
        tk.Label(frame, text="Settings", font=('Helvetica', 20, 'bold'), bg=COLORS['bg'], fg=COLORS['text_fg']).pack(anchor="w", pady=(0, 20))
        
        def create_toggle(parent, text, default=True):
            f = tk.Frame(parent, bg=COLORS['card_bg'], pady=15, padx=20)
            f.pack(fill=tk.X, pady=5)
            tk.Label(f, text=text, bg=COLORS['card_bg'], fg=COLORS['text_fg'], font=('Helvetica', 12)).pack(side=tk.LEFT)
            
            # Simulated Toggle Switch
            btn = tk.Label(f, text="ON", bg=COLORS['success'], fg=COLORS['bg'], font=('Helvetica', 10, 'bold'), width=6, padx=5, pady=2)
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
            self.window.after(5000, self.update_system_stats)

    def draw_pulse(self, active=False):
        """Draw the pulsing circle"""
        if not self.pulse_canvas: return
        self.pulse_canvas.delete("all")
        
        color = COLORS['accent'] if active else COLORS['border']
        r = self.pulse_radius if active else 10
        
        # Center is 25, 25
        self.pulse_canvas.create_oval(25-r, 25-r, 25+r, 25+r, fill=color, outline="")
        
        if active:
            # Animate
            if self.pulse_growing:
                self.pulse_radius += 0.5
                if self.pulse_radius >= 18: self.pulse_growing = False
            else:
                self.pulse_radius -= 0.5
                if self.pulse_radius <= 10: self.pulse_growing = True
            
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
            
        elif cmd == 'set_agent_status':
            _, agent_type, detail = msg
            if self.agent_status_widget:
                self.agent_status_widget.set_status(agent_type, detail)
            
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
        
        # Reset agent status to idle after response
        if message_type == 'assistant':
            if self.agent_status_widget:
                self.agent_status_widget.set_status('idle', 'Ready')
        
        if auto_close and not self.is_pinned:
            pass 

    def show_listening_internal(self):
        if not self.window: self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.draw_pulse(active=True)
        if self.agent_status_widget:
            self.agent_status_widget.set_status('idle', 'Listening...')

    def show_processing_internal(self):
        self.draw_pulse(active=False)
        if self.agent_status_widget:
            self.agent_status_widget.set_status('ollama', 'Thinking...')

    def run(self):
        self.create_window()
        self.window.mainloop()

def run_gui_process(msg_queue, cmd_queue=None):
    # Debug logging
    import sys
    import os
    try:
        with open("/tmp/hva_gui_debug.log", "w") as f:
            f.write(f"Starting GUI Process at {datetime.now()}\n")
            f.write(f"Python: {sys.executable}\n")
            f.write(f"CWD: {os.getcwd()}\n")
            
        if cmd_queue is None:
            cmd_queue = queue.Queue()
            
        app = HVAWindow(msg_queue, cmd_queue)
        
        with open("/tmp/hva_gui_debug.log", "a") as f:
            f.write("HVAWindow initialized. Calling run()...\n")
            
        app.run()
    except Exception as e:
        with open("/tmp/hva_gui_debug.log", "a") as f:
            f.write(f"CRASH: {e}\n")
            import traceback
            traceback.print_exc(file=f)

