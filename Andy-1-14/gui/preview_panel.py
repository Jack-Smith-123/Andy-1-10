"""
Окно Display — превью с FPS-счётчиком и галочками отображения.
"""
import customtkinter as ctk
import time


class VideoView(ctk.CTkToplevel):
    def __init__(self, parent, font_size=13, theme=None, font_manager=None, 
                 on_close_callback=None, config=None):
        super().__init__(parent)
        self.title("Display — Andy")
        self.theme = theme or {}
        self.font_manager = font_manager
        self.font_size = font_size
        self.on_close_callback = on_close_callback
        self.config = config or {}

        screen_h = self.winfo_screenheight()
        self._small_height = 320
        self._big_height = 520
        self._window_width = 420
        self._is_expanded = False
        y_pos = screen_h - self._small_height - 50
        self.geometry(f"{self._window_width}x{self._small_height}+0+{y_pos}")
        self.resizable(True, True)
        self.configure(fg_color=self.theme.get("bg_main", "#1a1f2e"))
        self.is_open = True
        self._frame_times = []
        self._canvas = None

        # Шапка
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(5, 0), padx=10, fill="x")

        self.expand_btn = ctk.CTkButton(
            header, text="Подробно", width=85, height=28,
            font=self._get_font("font_size_button_secondary"),
            fg_color=self.theme.get("bg_button_secondary", "#2c3e50"),
            hover_color=self.theme.get("bg_button_secondary_hover", "#34495e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
            command=self._toggle_expand
        )
        self.expand_btn.pack(side="left")

        self.fps_label = ctk.CTkLabel(
            header, text="FPS: --",
            font=self._get_font("font_size_preview_fps", "bold"),
            text_color=self.theme.get("indicator_on", "#4ade80")
        )
        self.fps_label.pack(side="right", padx=5)

        # Область для кадра (зрение бота)
        self._canvas = ctk.CTkLabel(
            self, text="Ожидание запуска...\n(зрение бота)",
            width=400, height=260,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            text_color=self.theme.get("text_secondary", "#a0a8b8")
        )
        self._canvas.pack(pady=5, padx=10, fill="both", expand=True)

        # Раскрывающаяся панель с галочками
        self._expand_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            corner_radius=6
        )
        self._expand_frame.pack_forget()

        ctk.CTkLabel(
            self._expand_frame, text="Что показывать в Display:",
            font=self._get_font("font_size_label", "bold"),
            text_color=self.theme.get("text_primary", "#e0e0e0")
        ).pack(anchor="w", padx=10, pady=(5, 5))

        # Галочки дублируются из настроек
        self.show_vars = {}
        show_items = [
            ("show_water", "Показать воду"),
            ("show_zones", "Показать зоны"),
            ("show_cursor", "Показать курсор"),
            ("show_bobber_mask", "Показать маску поплавка"),
        ]
        for key, label in show_items:
            var = ctk.BooleanVar(value=self.config.get(key, True))
            self.show_vars[key] = var
            cb = ctk.CTkCheckBox(
                self._expand_frame, text=label,
                variable=var,
                font=self._get_font("font_size_label"),
                text_color=self.theme.get("text_primary", "#e0e0e0"),
                fg_color=self.theme.get("bg_button_primary", "#1f6aa5"),
                hover_color=self.theme.get("bg_button_primary_hover", "#1a5a8a"),
                command=lambda k=key: self._on_show_change(k)
            )
            cb.pack(anchor="w", padx=10, pady=2)

        # Статистика
        self._stats_text = ctk.CTkTextbox(
            self._expand_frame,
            font=self._get_font("font_size_preview_stats"),
            height=110, state="disabled",
            fg_color=self.theme.get("bg_main", "#1a1f2e"),
            text_color=self.theme.get("text_primary", "#e0e0e0"),
        )
        self._stats_text.pack(pady=(5, 5), padx=10, fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_font(self, key, weight="normal"):
        if self.font_manager:
            return self.font_manager.get_font(key, weight)
        return ctk.CTkFont(size=self.font_size, weight=weight)

    def _toggle_expand(self):
        self._is_expanded = not self._is_expanded
        screen_h = self.winfo_screenheight()
        if self._is_expanded:
            y_pos = screen_h - self._big_height - 50
            self.geometry(f"{self._window_width}x{self._big_height}+0+{y_pos}")
            self._expand_frame.pack(pady=5, padx=10, fill="x")
        else:
            y_pos = screen_h - self._small_height - 50
            self.geometry(f"{self._window_width}x{self._small_height}+0+{y_pos}")
            self._expand_frame.pack_forget()

    def update_frame(self, tk_image):
        """Обновляет кадр (зрение бота с оверлеями)."""
        if self.is_open and self._canvas:
            self._canvas.configure(image=tk_image, text="")
            self._canvas.image = tk_image
            now = time.time()
            self._frame_times.append(now)
            self._frame_times = [t for t in self._frame_times if now - t < 2.0]
            if len(self._frame_times) >= 2:
                fps = len(self._frame_times) / (self._frame_times[-1] - self._frame_times[0])
                self.fps_label.configure(text=f"FPS: {fps:.1f}")

    def update_stats(self, state, score, cursor_pos, water_ok, water_percent, water_center):
        if not self.is_open or not self._is_expanded:
            return
        cursor_str = f"({cursor_pos[0]}, {cursor_pos[1]})" if cursor_pos else "OUT OF FRAME"
        center_str = f"({water_center[0]}, {water_center[1]})" if water_center else "N/A"
        lines = [
            f"STATE:        {state}",
            f"Score:        {score:.2f}",
            f"CURSOR:       {cursor_str}",
            f"WATER:        {'OK' if water_ok else 'NO'} ({water_percent:.1f}%)",
            f"WATER_CENTER: {center_str}",
        ]
        text = "\n".join(lines) + "\n"
        self._stats_text.configure(state="normal")
        self._stats_text.delete("1.0", "end")
        self._stats_text.insert("end", text)
        self._stats_text.configure(state="disabled")

    def _on_show_change(self, key):
        """Синхронизирует галочку Display с конфигом."""
        self.config[key] = self.show_vars[key].get()
        print(f"[DISPLAY] {key} = {self.config[key]}")

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