"""
Главное окно Andy-1.8 на customtkinter.
🆕 Убраны ползунки "Порог совпадения" и "Рывок по Y" (перенесены в настройки поплавка).
🆕 Переименовано в Andy-1.8.
🆕 Увеличен размер изображения в превью (480x300).
Все шрифты берутся из FontManager.
"""
import customtkinter as ctk
import os
import sys
import signal
from datetime import datetime
from PIL import Image, ImageTk
import cv2
from .preview_window import PreviewWindow
from .log_window import LogWindow
from ..settings.settings_window import SettingsWindow
from ..themes import get_theme


class Andy1GUI:
    def __init__(self, app_instance):
        self.app = app_instance
        self.root = self.app.root
        self.font_size = self.app.config.get("font_size", 13)
        if not isinstance(self.font_size, int):
            self.font_size = 13
        self.app.config["font_size"] = 13
        try:
            self.app._save_config()
        except Exception:
            pass
        self.theme_key = self.app.config.get("theme", "albion_dark")
        self.theme = get_theme(self.theme_key)
        self.font_manager = self.app.font_manager
        self.preview_window = None
        self.log_window = None
        self.settings_window = None
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
        ctk.CTkLabel(left_frame, text="Andy-1.8",
                     font=fm.get_font("font_size_header", "bold"),
                     text_color=t["text_primary"]).pack(side="left")
        self.close_btn = ctk.CTkButton(
            header_frame, text="X", width=36, height=36,
            font=fm.get_font("font_size_button_close", "bold"),
            fg_color=t["bg_button_close"], hover_color=t["bg_button_close_hover"],
            text_color=t["text_primary"],
            command=self._close_terminal
        )
        self.close_btn.pack(side="right")

        # Сетка кнопок (без ползунков порога и рывка)
        btn_frame = ctk.CTkFrame(self.root, fg_color=t["bg_panel_transparent"])
        btn_frame.pack(pady=10, padx=15, fill="x")
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶ Старт",
            font=fm.get_font("font_size_button_primary", "bold"),
            height=45, fg_color=t["bg_button_primary"], hover_color=t["bg_button_primary_hover"],
            text_color=t["text_primary"],
            command=self.app.start_bot
        )
        self.start_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        self.stop_btn = ctk.CTkButton(
            btn_frame, text="⏹ Стоп",
            font=fm.get_font("font_size_button_primary", "bold"),
            height=45, fg_color=t["bg_button_primary"], hover_color=t["bg_button_primary_hover"],
            text_color=t["text_primary"],
            command=self.app.stop_bot
        )
        self.stop_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        acting = self.app.fishing.acting if hasattr(self.app, 'fishing') else True
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
            btn_frame, text="⚙ Настройки",
            font=fm.get_font("font_size_button_secondary"),
            height=45, fg_color=t["bg_button_secondary"], hover_color=t["bg_button_secondary_hover"],
            text_color=t["text_primary"],
            command=self._toggle_settings
        )
        self.settings_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        self.video_btn = ctk.CTkButton(
            btn_frame, text="🎥 Видео",
            font=fm.get_font("font_size_button_secondary"),
            height=45, fg_color=t["bg_button_secondary"], hover_color=t["bg_button_secondary_hover"],
            text_color=t["text_primary"],
            command=self._toggle_preview
        )
        self.video_btn.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
        self.log_btn = ctk.CTkButton(
            btn_frame, text="📜 Лог",
            font=fm.get_font("font_size_button_secondary"),
            height=45, fg_color=t["bg_button_secondary"], hover_color=t["bg_button_secondary_hover"],
            text_color=t["text_primary"],
            command=self._toggle_log
        )
        self.log_btn.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        status_frame = ctk.CTkFrame(self.root, fg_color=t["bg_panel_transparent"])
        status_frame.pack(pady=5, padx=15, fill="x")
        self.status_label = ctk.CTkLabel(status_frame, text="⏸ Остановлен",
                                         font=fm.get_font("font_size_status", "bold"),
                                         text_color=t["status_text"])
        self.status_label.pack(side="left")

    def _is_window_alive(self, win):
        if win is None:
            return False
        try:
            return win.winfo_exists()
        except Exception:
            return False

    def _toggle_acting(self):
        if hasattr(self.app, 'fishing') and self.app.fishing:
            new_acting = not self.app.fishing.acting
            self.app.fishing.set_acting(new_acting)
            self._update_action_button()

    def _update_action_button(self):
        t = self.theme
        if hasattr(self.app, 'fishing') and self.app.fishing:
            if self.app.fishing.acting:
                self.action_btn.configure(text="▶ Действует",
                                          fg_color=t["bg_button_primary"],
                                          hover_color=t["bg_button_primary_hover"])
            else:
                self.action_btn.configure(text="⏸ Ждёт",
                                          fg_color=t["bg_button_secondary"],
                                          hover_color=t["bg_button_secondary_hover"])

    def _close_terminal(self):
        print("[GUI] Закрытие приложения и терминала...")
        try:
            self.app.stop_bot()
        except Exception:
            pass
        try:
            self.app.hotkey.stop()
        except Exception:
            pass
        for win in [self.preview_window, self.log_window, self.settings_window]:
            try:
                if win:
                    win.destroy()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass
        try:
            os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)
        except Exception:
            try:
                os.kill(os.getpid(), signal.SIGKILL)
            except Exception:
                sys.exit(1)

    def _toggle_preview(self):
        if self._is_window_alive(self.preview_window):
            self.preview_window._on_close()
            self.preview_window = None
        else:
            self.preview_window = PreviewWindow(
                self.root, self.font_size, self.theme, self.font_manager,
                on_close_callback=self._on_preview_closed,
                app=self.app
            )
            self.preview_window.transient(self.root)

    def _on_preview_closed(self):
        self.preview_window = None

    def _toggle_log(self):
        if self._is_window_alive(self.log_window):
            self.log_window._on_close()
            self.log_window = None
        else:
            self.log_window = LogWindow(
                self.root, self.font_size, self.theme, self.font_manager,
                on_close_callback=self._on_log_closed,
                log_buffer=self.app.log_buffer
            )
            self.log_window.transient(self.root)

    def _on_log_closed(self):
        self.log_window = None

    def _toggle_settings(self):
        if self._is_window_alive(self.settings_window):
            self.settings_window._on_close()
            self.settings_window = None
        else:
            self.settings_window = SettingsWindow(
                self.root, self.app.config,
                self._on_settings_applied,
                self._on_water_setting_changed,
                self.font_size, self.theme, self.font_manager
            )
            self.settings_window.set_save_callback(self.app._save_config)
            self.settings_window.transient(self.root)

    def _on_water_setting_changed(self, key, value):
        self.app._save_config()
        if hasattr(self.app, 'fishing') and self.app.fishing:
            self.app.fishing._last_water_check_time = 0

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
        for win in [self.preview_window, self.log_window, self.settings_window]:
            try:
                if win and getattr(win, "is_open", False):
                    win.destroy()
            except Exception:
                pass
        self.preview_window = None
        self.log_window = None
        self.settings_window = None
        for widget in self.root.winfo_children():
            widget.destroy()
        self._build_ui()

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        if self._is_window_alive(self.log_window):
            self.log_window.append_log(msg)

    def update_status(self, state, active, acting=True):
        t = self.theme
        if active:
            self.indicator.configure(text_color=t["indicator_on"])
            mode = "Действует" if acting else "Ждёт"
            self.status_label.configure(text=f"🟢 {mode}: {state}", text_color=t["status_active"])
        else:
            self.indicator.configure(text_color=t["indicator_off"])
            self.status_label.configure(text="⏸ Остановлен", text_color=t["status_text"])

    def send_frame_to_preview(self, frame_bgr):
        """🆕 Увеличенный размер изображения (480x300 вместо 400x260)."""
        if not self._is_window_alive(self.preview_window):
            return
        try:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            pil = pil.resize((480, 300), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil)
            self.preview_window.update_frame(tk_img)
        except Exception:
            pass

    def send_stats_to_preview(self):
        if not self._is_window_alive(self.preview_window):
            return
        if hasattr(self.app, 'fishing') and self.app.fishing:
            f = self.app.fishing
            cursor_pos = f.cursor_tracker.last_pos
            self.preview_window.update_stats(
                f.state, f._last_score, cursor_pos,
                f._has_water, f._water_percent, f._water_center,
            )

    def _start_update_loop(self):
        self._update_gui_state()

    def _update_gui_state(self):
        if self.app.bot_running and hasattr(self.app, 'fishing') and self.app.fishing:
            self.update_status(self.app.fishing.state, True, self.app.fishing.acting)
            self._update_action_button()
            self.send_stats_to_preview()
        else:
            self.update_status("IDLE", False)
        self.root.after(200, self._update_gui_state)
