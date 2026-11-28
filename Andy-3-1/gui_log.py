import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from logger import log_manager, CATEGORIES

class LogWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Лог бота")
        self.geometry("700x500")
        self.resizable(True, True)
        self.parent_ref = parent
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.tab_widgets = {}
        self.last_counter = {}
        self.setup_ui()
        log_manager.add_flag_listener(self._on_flag_change)
        self._poll()

    def setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=10, pady=5)

        self.var_enabled = tk.BooleanVar(value=log_manager.enabled)
        ctk.CTkCheckBox(top_frame, text="Вкл", variable=self.var_enabled,
                        command=self._toggle_enabled).pack(side="left", padx=5)

        self.btn_copy = ctk.CTkButton(top_frame, text="📋 Копировать", width=120,
                                      command=self.copy_current_tab)
        self.btn_copy.pack(side="left", padx=5)

        self.btn_clear = ctk.CTkButton(top_frame, text="🗑 Очистить", width=100,
                                       fg_color="gray", hover_color="darkgray",
                                       command=self.clear_current_tab)
        self.btn_clear.pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)

        for category in CATEGORIES:
            tab = ctk.CTkFrame(self.notebook)
            self.notebook.add(tab, text=f"  {category}  ")
            text_frame = ctk.CTkFrame(tab)
            text_frame.pack(fill="both", expand=True, padx=5, pady=5)
            text = tk.Text(text_frame, wrap="word", state="disabled",
                           bg="#1e1e1e", fg="#d4d4d4", insertbackground="white",
                           font=("Consolas", 10))
            scrollbar = ctk.CTkScrollbar(text_frame, command=text.yview)
            text.configure(yscrollcommand=scrollbar.set)
            text.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            self.tab_widgets[category] = text
            self.last_counter[category] = -1

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.render_current_tab())
        self.render_current_tab()

    def _toggle_enabled(self):
        log_manager.set_enabled(self.var_enabled.get())

    def _on_flag_change(self, value):
        self.var_enabled.set(value)

    def _poll(self):
        try:
            if self.winfo_exists():
                cat = self.current_category()
                if cat and log_manager.get_counter(cat) != self.last_counter.get(cat):
                    self.render_current_tab()
                self.after(300, self._poll)
        except tk.TclError:
            pass

    def current_category(self):
        try:
            return self.notebook.tab(self.notebook.select(), "text").strip()
        except Exception:
            return None

    def render_current_tab(self):
        cat = self.current_category()
        if not cat or cat not in self.tab_widgets:
            return
        entries = log_manager.get_all(cat)
        text = self.tab_widgets[cat]
        text.configure(state="normal")
        text.delete("1.0", "end")
        text.insert("end", "".join(entries))
        text.see("end")
        text.configure(state="disabled")
        self.last_counter[cat] = log_manager.get_counter(cat)

    def copy_current_tab(self):
        cat = self.current_category()
        if cat:
            content = "".join(log_manager.get_all(cat))
            self.clipboard_clear()
            self.clipboard_append(content)

    def clear_current_tab(self):
        cat = self.current_category()
        if cat:
            log_manager.clear(cat)
            self.render_current_tab()

    def on_close(self):
        log_manager.remove_flag_listener(self._on_flag_change)
        self.parent_ref.log_window = None
        self.destroy()
