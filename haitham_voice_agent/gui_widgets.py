import tkinter as tk
from tkinter import ttk, font
import math

# Premium Color Palette (Catppuccin Mocha Inspired + HVA Accents)
COLORS = {
    'bg': '#1e1e2e',          # Deep Dark Blue
    'header_bg': '#11111b',   # Darker Header
    'card_bg': '#313244',     # Surface 0
    'card_bg_hover': '#45475a', # Surface 1
    'text_fg': '#cdd6f4',     # Text
    'text_sub': '#a6adc8',    # Subtext
    'accent': '#89b4fa',      # Blue
    'accent_hover': '#b4befe', # Lavender
    'success': '#a6e3a1',     # Green
    'warning': '#f9e2af',     # Yellow
    'error': '#f38ba8',       # Red
    'border': '#45475a',      # Overlay 0
    'ollama': '#fab387',      # Peach (Local Brain)
    'gpt': '#cba6f7',         # Mauve (Cloud Brain)
    'tool': '#94e2d5'         # Teal (Tools)
}

class HVAWidget(tk.Frame):
    """Base class for HVA Dashboard Widgets"""
    def __init__(self, parent, title="", width=200, height=150, **kwargs):
        super().__init__(parent, bg=COLORS['card_bg'], bd=0, highlightthickness=0, **kwargs)
        self.pack_propagate(False)
        self.configure(width=width, height=height)
        
        # Title Bar
        if title:
            self.title_frame = tk.Frame(self, bg=COLORS['card_bg'], height=30)
            self.title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
            
            self.title_label = tk.Label(
                self.title_frame, 
                text=title.upper(), 
                font=('Helvetica', 9, 'bold'),
                bg=COLORS['card_bg'], 
                fg=COLORS['text_sub'],
                letterspacing=1 # Tkinter doesn't support this directly but font choice helps
            )
            self.title_label.pack(side=tk.LEFT)
            
        # Content Frame
        self.content = tk.Frame(self, bg=COLORS['card_bg'])
        self.content.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

class ModernButton(tk.Frame):
    """Custom styled button"""
    def __init__(self, parent, text, command, icon=None, bg=COLORS['accent'], fg=COLORS['bg'], width=None, height=40):
        super().__init__(parent, bg=bg, height=height, cursor="hand2")
        if width:
            self.configure(width=width)
        self.pack_propagate(False)
        
        self.command = command
        self.bg_color = bg
        self.hover_color = COLORS['accent_hover'] if bg == COLORS['accent'] else COLORS['card_bg_hover']
        
        # Inner label for text/icon
        display_text = f"{icon}  {text}" if icon else text
        self.lbl = tk.Label(
            self, 
            text=display_text, 
            bg=bg, 
            fg=fg, 
            font=('Helvetica', 11, 'bold'),
            cursor="hand2"
        )
        self.lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.lbl.bind("<Enter>", self.on_enter)
        self.lbl.bind("<Leave>", self.on_leave)
        self.lbl.bind("<Button-1>", self.on_click)
        
    def on_enter(self, e):
        self.configure(bg=self.hover_color)
        self.lbl.configure(bg=self.hover_color)
        
    def on_leave(self, e):
        self.configure(bg=self.bg_color)
        self.lbl.configure(bg=self.bg_color)
        
    def on_click(self, e):
        if self.command:
            self.command()

class AgentStatusWidget(HVAWidget):
    """Widget to display active agent status"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="ACTIVE AGENT", **kwargs)
        
        self.status_label = tk.Label(
            self.content,
            text="IDLE",
            font=('Helvetica', 16, 'bold'),
            bg=COLORS['card_bg'],
            fg=COLORS['text_sub']
        )
        self.status_label.pack(expand=True)
        
        self.detail_label = tk.Label(
            self.content,
            text="Ready for command",
            font=('Helvetica', 10),
            bg=COLORS['card_bg'],
            fg=COLORS['text_sub']
        )
        self.detail_label.pack(pady=(0, 10))
        
    def set_status(self, agent_type, detail=""):
        """
        agent_type: 'ollama', 'gpt', 'tool', 'idle'
        """
        color = COLORS['text_sub']
        text = "IDLE"
        
        if agent_type == 'ollama':
            color = COLORS['ollama']
            text = "OLLAMA (LOCAL)"
        elif agent_type == 'gpt':
            color = COLORS['gpt']
            text = "GPT-5 (CLOUD)"
        elif agent_type == 'tool':
            color = COLORS['tool']
            text = "EXECUTING TOOL"
            
        self.status_label.configure(text=text, fg=color)
        self.detail_label.configure(text=detail)

class SystemStatusWidget(HVAWidget):
    """Widget to display CPU and RAM usage"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="SYSTEM HEALTH", **kwargs)
        
        # CPU Row
        self.cpu_frame = tk.Frame(self.content, bg=COLORS['card_bg'])
        self.cpu_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(self.cpu_frame, text="CPU Load", font=('Helvetica', 10), bg=COLORS['card_bg'], fg=COLORS['text_sub']).pack(side=tk.LEFT)
        self.cpu_val = tk.Label(self.cpu_frame, text="0%", font=('Helvetica', 10, 'bold'), bg=COLORS['card_bg'], fg=COLORS['accent'])
        self.cpu_val.pack(side=tk.RIGHT)
        
        # RAM Row
        self.ram_frame = tk.Frame(self.content, bg=COLORS['card_bg'])
        self.ram_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(self.ram_frame, text="Memory", font=('Helvetica', 10), bg=COLORS['card_bg'], fg=COLORS['text_sub']).pack(side=tk.LEFT)
        self.ram_val = tk.Label(self.ram_frame, text="0%", font=('Helvetica', 10, 'bold'), bg=COLORS['card_bg'], fg=COLORS['accent'])
        self.ram_val.pack(side=tk.RIGHT)

    def update_stats(self, cpu, ram):
        self.cpu_val.configure(text=f"{cpu}%")
        self.ram_val.configure(text=f"{ram}%")
        
        # Color coding
        if cpu > 80: self.cpu_val.configure(fg=COLORS['error'])
        else: self.cpu_val.configure(fg=COLORS['accent'])
        
        if ram > 80: self.ram_val.configure(fg=COLORS['error'])
        else: self.ram_val.configure(fg=COLORS['accent'])

class WeatherWidget(HVAWidget):
    """Widget to display Weather"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="WEATHER", **kwargs)
        
        self.temp_label = tk.Label(
            self.content, 
            text="24°C", 
            font=('Helvetica', 28, 'bold'),
            bg=COLORS['card_bg'], 
            fg=COLORS['text_fg']
        )
        self.temp_label.pack(pady=5)
        
        self.desc_label = tk.Label(
            self.content, 
            text="Sunny", 
            font=('Helvetica', 11),
            bg=COLORS['card_bg'], 
            fg=COLORS['text_sub']
        )
        self.desc_label.pack()

class ChatWidget(HVAWidget):
    """Widget to display chat history"""
    def __init__(self, parent, **kwargs):
        # No title for chat widget to maximize space
        super().__init__(parent, title="", **kwargs)
        
        self.chat_canvas = tk.Canvas(self.content, bg=COLORS['bg'], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.content, orient="vertical", command=self.chat_canvas.yview)
        self.scrollable_frame = tk.Frame(self.chat_canvas, bg=COLORS['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        
        self.chat_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=parent.winfo_width()) 
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.chat_canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        self.chat_canvas.itemconfig(self.chat_canvas.find_withtag("all")[0], width=event.width)

    def add_message(self, sender, text, timestamp):
        """Add a message bubble"""
        bubble_bg = COLORS['accent'] if sender == 'user' else COLORS['card_bg']
        text_fg = COLORS['bg'] if sender == 'user' else COLORS['text_fg']
        align = tk.E if sender == 'user' else tk.W
        
        frame = tk.Frame(self.scrollable_frame, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=8, padx=10)
        
        # Sender Name
        sender_name = "You" if sender == 'user' else "HVA"
        name_lbl = tk.Label(
            frame,
            text=f"{sender_name} • {timestamp}",
            font=('Helvetica', 8),
            bg=COLORS['bg'],
            fg=COLORS['text_sub']
        )
        name_lbl.pack(anchor=align, padx=5)
        
        # Bubble
        bubble = tk.Label(
            frame, 
            text=text, 
            wraplength=450, 
            justify=tk.LEFT,
            bg=bubble_bg, 
            fg=text_fg,
            font=('Helvetica', 11),
            padx=15, 
            pady=10,
            relief=tk.FLAT
        )
        bubble.pack(anchor=align)
        
        # Auto scroll
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
