import tkinter as tk

class Tooltip:
    """Всплывающая подсказка для виджетов."""
    def __init__(self, widget, text, delay=1000):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()
    
    def show_tooltip(self):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 5
        y = self.widget.winfo_rooty() + self.widget.winfo_height() // 2
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(self.tooltip, text=self.text, 
                        background="#ffffe0", foreground="black",
                        relief="solid", borderwidth=1,
                        font=("Arial", 10))
        label.pack()
    
    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def update_delay(self, delay):
        self.delay = delay
