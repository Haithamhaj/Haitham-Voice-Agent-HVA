import tkinter as tk
from tkinter import ttk, font
import math

# Modern Color Palette (Shared)
# Modern Color Palette (Shared) - High Contrast
COLORS = {
    'bg': '#1e1e2e',          # Dark blue-grey background
    'header_bg': '#11111b',   # Darker header for contrast
    'card_bg': '#313244',     # Card background
    'text_fg': '#ffffff',     # Pure white text for maximum readability
    'text_sub': '#bac2de',    # Lighter grey for subtext
    'accent': '#89b4fa',      # Blue accent
    'success': '#a6e3a1',     # Green
    'warning': '#f9e2af',     # Yellow
    'error': '#f38ba8',       # Red
    'border': '#45475a'       # Border color
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
            self.title_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            self.title_label = tk.Label(
                self.title_frame, 
                text=title.upper(), 
                font=('Helvetica', 10, 'bold'),
                bg=COLORS['card_bg'], 
                fg=COLORS['text_sub']
            )
            self.title_label.pack(side=tk.LEFT)
            
        # Content Frame
        self.content = tk.Frame(self, bg=COLORS['card_bg'])
        self.content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

class SystemStatusWidget(HVAWidget):
    """Widget to display CPU and RAM usage"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title="SYSTEM STATUS", **kwargs)
        
        # CPU Row
        self.cpu_frame = tk.Frame(self.content, bg=COLORS['card_bg'])
        self.cpu_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.cpu_frame, text="CPU", font=('Helvetica', 12), bg=COLORS['card_bg'], fg=COLORS['text_fg']).pack(side=tk.LEFT)
        self.cpu_val = tk.Label(self.cpu_frame, text="0%", font=('Helvetica', 12, 'bold'), bg=COLORS['card_bg'], fg=COLORS['accent'])
        self.cpu_val.pack(side=tk.RIGHT)
        
        # RAM Row
        self.ram_frame = tk.Frame(self.content, bg=COLORS['card_bg'])
        self.ram_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(self.ram_frame, text="RAM", font=('Helvetica', 12), bg=COLORS['card_bg'], fg=COLORS['text_fg']).pack(side=tk.LEFT)
        self.ram_val = tk.Label(self.ram_frame, text="0%", font=('Helvetica', 12, 'bold'), bg=COLORS['card_bg'], fg=COLORS['accent'])
        self.ram_val.pack(side=tk.RIGHT)

    def update_stats(self, cpu, ram):
        self.cpu_val.configure(text=f"{cpu}%")
        self.ram_val.configure(text=f"{ram}%")

class WeatherWidget(HVAWidget):
    """Widget to display Weather (Mock for now)"""
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
            font=('Helvetica', 12),
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
        
        self.chat_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=parent.winfo_width()) # Initial width guess
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind resize to update inner frame width
        self.chat_canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        self.chat_canvas.itemconfig(self.chat_canvas.find_withtag("all")[0], width=event.width)

    def add_message(self, sender, text, timestamp):
        """Add a message bubble"""
        bubble_bg = COLORS['accent'] if sender == 'user' else COLORS['card_bg']
        text_fg = COLORS['header_bg'] if sender == 'user' else COLORS['text_fg']
        align = tk.E if sender == 'user' else tk.W
        
        frame = tk.Frame(self.scrollable_frame, bg=COLORS['bg'])
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Bubble
        bubble = tk.Label(
            frame, 
            text=text, 
            wraplength=350, 
            justify=tk.LEFT,
            bg=bubble_bg, 
            fg=text_fg,
            font=('Helvetica', 12),
            padx=10, 
            pady=8,
            relief=tk.FLAT
        )
        bubble.pack(anchor=align)
        
        # Timestamp
        ts = tk.Label(
            frame, 
            text=timestamp, 
            font=('Helvetica', 8), 
            bg=COLORS['bg'], 
            fg=COLORS['text_sub']
        )
        ts.pack(anchor=align)
        
        # Auto scroll
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def clear(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
