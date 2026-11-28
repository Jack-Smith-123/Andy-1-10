"""
Окно лога с вкладками по категориям.
🆕 Вкладки: Общий, Рыбалка, Вода, Визуал, Настройки, Система.
🆕 Автоматическое определение категории по эмодзи/ключевым словам.
🆕 "Общий" получает все сообщения.
🆕 Кнопка "Копировать лог" копирует только активную вкладку.
🆕 Счётчик строк показывает количество в активной вкладке.
"""
import customtkinter as ctk


# Маппинг категорий
CATEGORIES = {
    "general": "📋 Общий",
    "fishing": "🎣 Рыбалка",
    "water": "💧 Вода",
    "vision": "👁 Визуал",
    "settings": "⚙ Настройки",
    "system": "🔧 Система",
}


def detect_category(message):
    """Автоматически определяет категорию сообщения."""
    # Рыбалка
    if any(kw in message for kw in [
        "🎣", "✅ Поплавок", "🎯 КЛЮЁТ", "⚠️ Поплавок",
        "🔄 Отмена", "Рывок вниз", "Забрасываем",
        "➡️ STATE: HOOK", "➡️ STATE: CHECK_BOBBER",
        "➡️ STATE: MINI_GAME", "➡️ STATE: STARTING",
        "➡️ STATE: RESTART", "Поплавок не найден",
        "Поплавок потерян", "Поплавок так и не появился",
        "Мини-игра не найдена", "Мини-игра дольше",
    ]):
        return "fishing"

    # Вода
    if any(kw in message for kw in [
        "💧", "Вода не найдена", "Направление заброса",
        "Плавный клик по воде", "🎯 Направление",
    ]):
        return "water"

    # Настройки
    if any(kw in message for kw in [
        "⚙", "Настройки загружены", "Не удалось загрузить",
        "Не удалось сохранить", "✓ Применено",
        "Пользовательская тема", "Неизвестный ключ",
    ]):
        return "settings"

    # Визуал
    if any(kw in message for kw in [
        "👁", "Маска", "Визуализация",
    ]):
        return "vision"

    # Система
    if any(kw in message for kw in [
        "✓ Загружено", "[HOTKEY]", "Hotkey service",
        "▶️ Бот запущен", "⏹ Бот остановлен",
        "🔍 Поиск окна", "✓ Окно найдено",
        "✓ X-сервер", "Запуск Andy",
        "Exception", "Traceback", "Error",
    ]):
        return "system"

    return "general"


class LogWindow(ctk.CTkToplevel):
    def __init__(self, parent, font_size=13, theme=None, font_manager=None,
                 on_close_callback=None, log_buffer=None):
        super().__init__(parent)
        self.title("📜 Лог — Andy-1.8")
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self.on_close_callback = on_close_callback
        self.log_buffer = log_buffer or []
        self.is_open = True

        screen_h = self.winfo_screenheight()
        window_width = 520
        window_height = 400
        y_pos = screen_h - window_height - 50
        self.geometry(f"{window_width}x{window_height}+0+{y_pos}")
        self.resizable(True, True)
        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))

        # === Верхняя панель: кнопки + счётчик ===
        btn_frame = ctk.CTkFrame(self, fg_color=self.theme.get("bg_panel", "#2a3142"))
        btn_frame.pack(pady=5, padx=10, fill="x")

        self.copy_btn = ctk.CTkButton(
            btn_frame, text="📋 Копировать лог", width=150, height=30,
            font=self._get_font("font_size_button_secondary"),
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._copy_active_tab
        )
        self.copy_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(
            btn_frame, text="🗑 Очистить", width=100, height=30,
            font=self._get_font("font_size_button_secondary"),
            fg_color=self.theme.get("bg_button_close", "#6c757d"),
            hover_color=self.theme.get("bg_button_close_hover", "#5a6268"),
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

        # === Вкладки логов ===
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            segmented_button_fg_color=self.theme.get("bg_slider", "#3a4152"),
            segmented_button_selected_color=self.theme.get("bg_button_primary", "#1f6aa5"),
            segmented_button_selected_hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
            segmented_button_unselected_color=self.theme.get("bg_slider", "#3a4152"),
            segmented_button_unselected_hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            corner_radius=6,
            border_width=0,
            command=self._on_tab_changed,
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=5)

        # Создаём вкладки
        self.textboxes = {}
        for cat_key, cat_name in CATEGORIES.items():
            tab = self.tabview.add(cat_name)
            textbox = ctk.CTkTextbox(
                tab,
                font=self._get_font("font_size_log"),
                fg_color=self.theme.get("bg_main", "#1a1f2e"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                wrap="word",
            )
            textbox.pack(fill="both", expand=True, padx=2, pady=2)
            self.textboxes[cat_key] = textbox

        self._line_counts = {cat: 0 for cat in CATEGORIES}

        # Загружаем историю из буфера
        self._load_buffer()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _get_active_category_key(self):
        """Возвращает ключ категории активной вкладки."""
        current_tab_name = self.tabview.get()
        for cat_key, cat_name in CATEGORIES.items():
            if cat_name == current_tab_name:
                return cat_key
        return "general"

    def _load_buffer(self):
        """Загружает всю историю из буфера при открытии окна."""
        if not self.log_buffer:
            return
        for line in self.log_buffer:
            self._append_to_categories(line)
        self._update_counts()

    def _append_to_categories(self, message):
        """Добавляет сообщение во все нужные вкладки."""
        category = detect_category(message)

        # "Общий" получает ВСЕ сообщения
        if "general" in self.textboxes:
            self.textboxes["general"].insert("end", f"{message}\n")
            self._line_counts["general"] += 1

        # Специфичная категория
        if category in self.textboxes and category != "general":
            self.textboxes[category].insert("end", f"{message}\n")
            self._line_counts[category] += 1

    def append_log(self, message):
        """Публичный метод добавления лога."""
        if self.is_open:
            self._append_to_categories(message)
            self._update_counts()
            active_key = self._get_active_category_key()
            if active_key in self.textboxes:
                self.textboxes[active_key].see("end")

    # 🆕 Исправлено: tab_name=None (опциональный параметр)
    def _on_tab_changed(self, tab_name=None):
        """Вызывается при смене вкладки — обновляет счётчик."""
        self._update_counts()
        active_key = self._get_active_category_key()
        if active_key in self.textboxes:
            self.textboxes[active_key].see("end")

    def _update_counts(self):
        """Обновляет счётчик строк для АКТИВНОЙ вкладки."""
        active_key = self._get_active_category_key()
        count = self._line_counts.get(active_key, 0)
        self.count_label.configure(text=f"{count} строк")

    def _copy_active_tab(self):
        """Копирует содержимое ТОЛЬКО активной вкладки."""
        active_key = self._get_active_category_key()

        try:
            textbox = self.textboxes.get(active_key)
            if textbox:
                content = textbox.get("1.0", "end-1c")
                if not content.strip():
                    old_text = self.copy_btn.cget("text")
                    self.copy_btn.configure(text="⚠ Пусто!", fg_color="#e67e22")
                    self.after(1500, lambda: self.copy_btn.configure(
                        text="📋 Копировать лог",
                        fg_color=self.theme.get("bg_button_secondary", "#2c3e50")
                    ))
                    return
                self.clipboard_clear()
                self.clipboard_append(content)
                self.update()
                old_text = self.copy_btn.cget("text")
                self.copy_btn.configure(text="✓ Скопировано!", fg_color="#27ae60")
                self.after(1500, lambda: self.copy_btn.configure(
                    text="📋 Копировать лог",
                    fg_color=self.theme.get("bg_button_secondary", "#2c3e50")
                ))
        except Exception as e:
            print(f"[LOG] Ошибка копирования: {e}")

    def _clear_log(self):
        """Очищает ВСЕ вкладки."""
        for textbox in self.textboxes.values():
            textbox.delete("1.0", "end")
        for cat in self._line_counts:
            self._line_counts[cat] = 0
        self._update_counts()
        if hasattr(self, 'log_buffer'):
            self.log_buffer.clear()

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
