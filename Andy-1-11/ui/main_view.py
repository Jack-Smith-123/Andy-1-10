"""
Главное окно приложения.
"""
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from datetime import datetime
from .video_view import VideoView
from .log_view import OutputView
from .settings_view import OptionsView
from .themes import get_theme


class MainView:
    """Главное окно приложения."""

    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.font_size = app.config.get("font_size", 13)
        self.theme_key = app.config.get("theme", "albion_dark")
        self.theme = get_theme(self.theme_key)
        self.font_manager = app.font_manager

        self.video_view = None
        self.output_view = None
        self.options_view = None
        self._log_history = []  # [(category, message), ...]

        self._build_ui()
        self._start_update_loop()

    def _build_ui(self):
        self.root.configure(fg_color=self.theme["bg_main"])
        t = self.theme
        fm = self.font_manager

        # Заголовок
        header_frame = ctk.CTkFrame(self.root, fg_color=t["bg_panel_transparent"])
        header_frame.pack(pady=(10, 5), padx=15, fill="x")

        left_frame = ctk.CTkFrame(header_frame, fg_color=t["bg_panel_transparent"])
        left_frame.pack(side="left")

        self.indicator = ctk.CTkLabel(
            left_frame, text="●",
            font=fm.get_font("font_size_title", "bold"),
            text_color=t["indicator_off"]
        )
        self.indicator.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            left_frame, text="Andy",
            font=fm.get_font("font_size_header", "bold"),
            text_color=t["text_primary"]
        ).pack(side="left")

        self.close_btn = ctk.CTkButton(
            header_frame, text="X", width=36, height=36,
            font=fm.get_font("font_size_button_close", "bold"),
            fg_color=t["bg_button_close"], hover_color=t["bg_button_close_hover"],
            text_color=t["text_primary"],
            command=self._close_app
        )
        self.close_btn.pack(side="right")

        # Сетка кнопок
        btn_frame = ctk.CTkFrame(self.root, fg_color=t["bg_panel_transparent"])
        btn_frame.pack(pady=10, padx=15, fill="x")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        # Ряд 1: Старт, Стоп
        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶ Старт",
            font=fm.get_font("font_size_button_primary", "bold"),
            height=45, fg_color=t["bg_button_primary"], hover_color=t["bg_button_primary_hover"],
            text_color=t["text_primary"],
            command=self.app.start_task
        )
        self.start_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.stop_btn = ctk.CTkButton(
            btn_frame, text="⏹ Стоп",
            font=fm.get_font("font_size_button_primary", "bold"),
            height=45, fg_color=t["bg_button_primary"], hover_color=t["bg_button_primary_hover"],
            text_color=t["text_primary"],
            command=self.app.stop_task
        )
        self.stop_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Ряд 2: Действует/Ждёт, Настройки
        acting = self.app.engine.acting if hasattr(self.app, 'engine') else True
        acting_text = "▶ Действует" if acting else "⏸ Ждёт"
        acting_color = t["bg_button_primary"] if acting else t["bg_button_secondary"]
        acting_hover = t["bg_button_primary_hover"] if acting else t["bg_button_secondary_hover"]

        self.action_btn = ctk.CTkButton(
            btn_frame, text=acting_text,
            font=fm.get_font("font_size_button_action", "bold"),
            height=45, fg_color=acting_color, hover_color=acting_hover,
            text_color=t["text_primary"],
            command=self._toggle_acting
        )
        self.action_btn.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

        self.settings_btn = ctk.CTkButton(
            btn_frame, text="⚙ Options",
            font=fm.get_font("font_size_button_secondary"),
            height=45, fg_color=t["bg_button_secondary"], hover_color=t["bg_button_secondary_hover"],
            text_color=t["text_primary"],
            command=self._toggle_settings
        )
        self.settings_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # Ряд 3: Display, Output
        self.video_btn = ctk.CTkButton(
            btn_frame, text="🎥 Display",
            font=fm.get_font("font_size_button_secondary"),
            height=45, fg_color=t["bg_button_secondary"], hover_color=t["bg_button_secondary_hover"],
            text_color=t["text_primary"],
            command=self._toggle_video
        )
        self.video_btn.grid(row=2, column=0, padx=4, pady=4, sticky="ew")

        self.log_btn = ctk.CTkButton(
            btn_frame, text="📜 Output",
            font=fm.get_font("font_size_button_secondary"),
            height=45, fg_color=t["bg_button_secondary"], hover_color=t["bg_button_secondary_hover"],
            text_color=t["text_primary"],
            command=self._toggle_output
        )
        self.log_btn.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        # Статус
        status_frame = ctk.CTkFrame(self.root, fg_color=t["bg_panel_transparent"])
        status_frame.pack(pady=5, padx=15, fill="x")

        self.status_label = ctk.CTkLabel(
            status_frame, text="⏸ Остановлен",
            font=fm.get_font("font_size_status", "bold"),
            text_color=t["status_text"]
        )
        self.status_label.pack(side="left")

    def _is_window_alive(self, win):
        """Проверяет, существует ли окно."""
        if win is None:
            return False
        try:
            return win.winfo_exists()
        except Exception:
            return False

    def _toggle_acting(self):
        if hasattr(self.app, 'engine') and self.app.engine:
            new_acting = not self.app.engine.acting
            self.app.engine.set_acting(new_acting)
            self._update_action_button()

    def _update_action_button(self):
        t = self.theme
        if hasattr(self.app, 'engine') and self.app.engine:
            if self.app.engine.acting:
                self.action_btn.configure(text="▶ Действует",
                                          fg_color=t["bg_button_primary"],
                                          hover_color=t["bg_button_primary_hover"])
            else:
                self.action_btn.configure(text="⏸ Ждёт",
                                          fg_color=t["bg_button_secondary"],
                                          hover_color=t["bg_button_secondary_hover"])

    def _close_app(self):
        print("[GUI] Закрытие приложения...")
        try:
            self.app.stop_task()
        except Exception:
            pass
        try:
            self.app.shortcuts.stop()
        except Exception:
            pass
        for win in [self.video_view, self.output_view, self.options_view]:
            try:
                if win:
                    win.destroy()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def _toggle_video(self):
        """Toggle: открыть/закрыть окно Display."""
        if self._is_window_alive(self.video_view):
            self.video_view._on_close()
            self.video_view = None
        else:
            self.video_view = VideoView(
                self.root, self.font_size, self.theme, self.font_manager,
                on_close_callback=self._on_video_closed,
                config=self.app.config  # ← передаём конфиг для галочек
            )
            self.video_view.transient(self.root)

    def _on_video_closed(self):
        self.video_view = None

    def _toggle_output(self):
        """Toggle: открыть/закрыть окно Output."""
        if self._is_window_alive(self.output_view):
            self.output_view._on_close()
            self.output_view = None
        else:
            self.output_view = OutputView(
                self.root, self.font_size, self.theme, self.font_manager,
                on_close_callback=self._on_output_closed,
                history=self._log_history
            )
            self.output_view.transient(self.root)

    def _on_output_closed(self):
        self.output_view = None

    def _toggle_settings(self):
        """Toggle: открыть/закрыть окно Options."""
        if self._is_window_alive(self.options_view):
            self.options_view._on_close()
            self.options_view = None
        else:
            self.options_view = OptionsView(
                self.root, self.app.config,
                self._on_settings_applied,
                self._on_water_setting_changed,
                self.font_size, self.theme, self.font_manager
            )
            self.options_view.set_save_callback(self.app._save_config)
            self.options_view.transient(self.root)

    def _on_water_setting_changed(self, key, value):
        self.app._save_config()
        if hasattr(self.app, 'engine') and self.app.engine:
            self.app.engine.water_analyzer._last_check_time = 0

    def _on_settings_applied(self, new_config):
        old_theme = self.theme_key
        old_font = self.font_size
        self.app.config.update(new_config)
        new_theme = new_config.get("theme", "albion_dark")
        new_font = new_config.get("font_size", 13)
        self.font_manager.clear_cache()
        if new_theme != old_theme or new_font != old_font:
            self.theme_key = new_theme
            self.theme = get_theme(new_theme)
            self.font_size = int(new_font) if isinstance(new_font, (int, float)) else 13
            self._rebuild_ui()
        else:
            self._rebuild_ui()
        print(f"[GUI] ✓ Настройки применены (тема: {self.theme_key}, шрифт: {self.font_size})")

    def _rebuild_ui(self):
        for win in [self.video_view, self.output_view, self.options_view]:
            try:
                if win and getattr(win, "is_open", False):
                    win.destroy()
            except Exception:
                pass
        self.video_view = None
        self.output_view = None
        self.options_view = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self._build_ui()

    def log(self, message, category="Система"):
        """Пишет лог в историю (всегда) и в окно Output (если открыто)."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = (category, f"[{timestamp}] {message}")
        self._log_history.append(entry)

        # Ограничиваем историю, чтобы не раздувать память
        if len(self._log_history) > 5000:
            self._log_history = self._log_history[-5000:]

        print(entry[1])
        if self._is_window_alive(self.output_view):
            self.output_view.refresh()

    def update_status(self, state, active, phase=True):
        t = self.theme
        if active:
            self.indicator.configure(text_color=t["indicator_on"])
            mode = "Действует" if phase else "Ждёт"
            self.status_label.configure(text=f"🟢 {mode}: {state}", text_color=t["status_active"])
        else:
            self.indicator.configure(text_color=t["indicator_off"])
            self.status_label.configure(text="⏸ Остановлен", text_color=t["status_text"])

    def send_frame_to_video(self, frame_bgr):
        if not self._is_window_alive(self.video_view):
            return
        try:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            pw = self.video_view.winfo_width()
            ph = self.video_view.winfo_height()
            if pw > 100 and ph > 100:
                target_w = max(100, pw - 20)
                target_h = max(100, ph - 60)
                pil = pil.resize((target_w, target_h), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil)
            self.video_view.update_frame(tk_img)
        except Exception:
            pass

    def send_stats_to_video(self):
        if not self._is_window_alive(self.video_view):
            return
        if hasattr(self.app, 'engine') and self.app.engine:
            e = self.app.engine
            cursor_pos = e.cursor_monitor.get_position()
            self.video_view.update_stats(
                e.state, e._last_score, cursor_pos,
                e.water_analyzer.has_water, e.water_analyzer.water_percent, e.water_analyzer.water_center,
            )

    def _start_update_loop(self):
        self._update_gui_state()

    def _update_gui_state(self):
        if self.app.active and hasattr(self.app, 'engine') and self.app.engine:
            self.update_status(self.app.engine.state, True, self.app.engine.acting)
            self._update_action_button()
            self.send_stats_to_video()
        else:
            self.update_status("IDLE", False)
        self.root.after(200, self._update_gui_state)