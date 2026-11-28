"""
Редактор пользовательских тем.
"""
import customtkinter as ctk
import json
import os


class ThemeEditorWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, on_save_callback, font_size=13, 
                 theme=None, font_manager=None):
        super().__init__(parent)
        self.title("Редактор темы")
        self.theme = theme or {}
        self.font_manager = font_manager
        self.on_save = on_save_callback

        self.geometry("400x500")
        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))

        ctk.CTkLabel(
            self, text="Название темы:",
            font=self._get_font("font_size_label"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        ).pack(pady=(10, 5), padx=10, anchor="w")

        self.name_entry = ctk.CTkEntry(
            self, placeholder_text="Моя тема",
            font=self._get_font("font_size_label"),
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        )
        self.name_entry.pack(pady=(0, 10), padx=10, fill="x")

        # Пример цветов (упрощённо)
        self.color_vars = {}
        color_keys = ["bg_main", "bg_panel", "bg_button_primary", "text_primary"]
        
        for key in color_keys:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", padx=10, pady=2)
            
            ctk.CTkLabel(
                frame, text=key, width=150, anchor="w",
                font=self._get_font("font_size_label"),
                text_color=self.theme.get("text_primary", "#e0e0e0")
            ).pack(side="left")
            
            var = ctk.StringVar(value=self.theme.get(key, "#ffffff"))
            self.color_vars[key] = var
            
            entry = ctk.CTkEntry(
                frame, textvariable=var, width=100,
                font=self._get_font("font_size_label"),
                fg_color=self.theme.get("bg_panel", "#2a3142")
            )
            entry.pack(side="right")

        # Кнопки
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", padx=10)

        ctk.CTkButton(
            btn_frame, text="💾 Сохранить",
            font=self._get_font("font_size_button_primary", "bold"),
            fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            command=self._save
        ).pack(side="left", expand=True, fill="x", padx=5)

        ctk.CTkButton(
            btn_frame, text="✕ Отмена",
            font=self._get_font("font_size_button_secondary"),
            fg_color=self.theme.get("bg_button_close", "#6c757d"),
            command=self.destroy
        ).pack(side="right", expand=True, fill="x", padx=5)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=13, weight=weight)

    def _save(self):
        name = self.name_entry.get().strip()
        if not name:
            return
        
        theme_data = {"name": name}
        for key, var in self.color_vars.items():
            theme_data[key] = var.get()
        
        # Сохранение в custom_themes.json
        custom_file = "custom_themes.json"
        custom_themes = {}
        if os.path.exists(custom_file):
            try:
                with open(custom_file, "r", encoding="utf-8") as f:
                    custom_themes = json.load(f)
            except Exception:
                pass
        
        key = name.lower().replace(" ", "_")
        custom_themes[key] = theme_data
        
        with open(custom_file, "w", encoding="utf-8") as f:
            json.dump(custom_themes, f, indent=2, ensure_ascii=False)
        
        if self.on_save:
            self.on_save(key, theme_data)
        
        self.destroy()