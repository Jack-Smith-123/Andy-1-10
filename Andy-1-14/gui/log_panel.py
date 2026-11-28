"""
Окно Output — лог с вкладками по категориям.
Читает историю из MainView, поэтому данные не теряются при закрытии окна.
"""
import customtkinter as ctk
import tkinter as tk


class OutputView(ctk.CTkToplevel):
    def __init__(self, parent, font_size=13, theme=None, font_manager=None,
                 on_close_callback=None, history=None):
        super().__init__(parent)
        self.title("Output — Andy")
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self.on_close_callback = on_close_callback
        self._history = history if history is not None else []

        screen_h = self.winfo_screenheight()
        window_width = 460
        window_height = 420
        y_pos = screen_h - window_height - 50
        self.geometry(f"{window_width}x{window_height}+0+{y_pos}")
        self.resizable(True, True)
        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))
        self.is_open = True

        # Вкладки категорий
        self._categories = ["Все", "Состояния", "Вода", "Поплавок", "Курсор", "Система"]
        self._current_category = "Все"

        tabs_frame = ctk.CTkFrame(self, fg_color="transparent")
        tabs_frame.pack(pady=(5, 2), padx=10, fill="x")

        self.category_switcher = ctk.CTkSegmentedButton(
            tabs_frame,
            values=self._categories,
            command=self._switch_category,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            unselected_color=self.theme.get("bg_slider", "#3a4152"),
            unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=6,
            border_width=0,
            font=self._get_font("font_size_button_secondary", "bold")
        )
        self.category_switcher.pack(fill="x")

        # Кнопки
        btn_frame = ctk.CTkFrame(self, fg_color=self.theme.get("bg_panel", "#2a3142"))
        btn_frame.pack(pady=2, padx=10, fill="x")

        self.copy_btn = ctk.CTkButton(
            btn_frame, text="📋 Скопировать", width=130, height=30,
            font=self._get_font("font_size_button_secondary"),
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._copy_all
        )
        self.copy_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(
            btn_frame, text="🗑 Очистить", width=100, height=30,
            font=self._get_font("font_size_button_secondary"),
            fg_color="#4a4a4a", hover_color="#5a5a5a",
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._clear_log
        )
        self.clear_btn.pack(side="right", padx=5)

        self.count_label = ctk.CTkLabel(
            btn_frame, text="0 строк",
            font=self._get_font("font_size_status"),
            text_color=self.theme.get("text_secondary", "#a0a8b8")
        )
        self.count_label.pack(side="right", padx=10)

        # Текст лога
        self.text = ctk.CTkTextbox(
            self,
            font=self._get_font("font_size_log"),
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        )
        self.text.pack(pady=5, padx=10, fill="both", expand=True)

        # Загружаем всю историю при открытии
        self.refresh()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _switch_category(self, category):
        self._current_category = category
        self.refresh()

    def refresh(self):
        """Перерисовывает лог из истории по текущей категории."""
        if not self.is_open:
            return
        self.text.delete("1.0", "end")
        count = 0
        for cat, msg in self._history:
            if self._current_category == "Все" or self._current_category == cat:
                self.text.insert("end", f"{msg}\n")
                count += 1
        self.text.see("end")
        self.count_label.configure(text=f"{count} строк")

    def append_log(self, message, category="Система"):
        """Совместимость со старым API — просто обновляем."""
        self.refresh()

    def _copy_all(self):
        """Копирует весь лог в буфер обмена."""
        try:
            content = self.text.get("1.0", "end-1c")
            if not content:
                return
            
            success = False
            
            # Способ 1: через pyperclip
            try:
                import pyperclip
                pyperclip.copy(content)
                success = True
            except Exception as e1:
                # Способ 2: через xclip (Linux)
                try:
                    import subprocess
                    process = subprocess.Popen(
                        ['xclip', '-selection', 'clipboard'],
                        stdin=subprocess.PIPE
                    )
                    process.communicate(content.encode('utf-8'))
                    success = True
                except Exception as e2:
                    # Способ 3: через tkinter
                    try:
                        root = self.master
                        while hasattr(root, 'master') and root.master is not None:
                            root = root.master
                        root.clipboard_clear()
                        root.clipboard_append(content)
                        root.update()
                        success = True
                    except Exception as e3:
                        print(f"[LOG] Все способы не сработали")
            
            if success:
                self.copy_btn.configure(text="✓ Скопировано!", fg_color="#27ae60")
                self.after(1500, lambda: self.copy_btn.configure(
                    text="📋 Скопировать",
                    fg_color=self.theme.get("bg_button_secondary", "#2c3e50")
                ))
        except Exception as e:
            print(f"[LOG] Ошибка копирования: {e}")

    def _clear_log(self):
        """Очищает историю (влияет на MainView)."""
        self._history.clear()
        self.refresh()

    def _on_close(self):
        self.is_open = False
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception:
                pass
        try:
            self.destroy()
        except Exception:
            pass