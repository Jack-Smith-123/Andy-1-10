"""
Современный GUI для Andy-1-3 на customtkinter.
Главное окно + отдельные окна Видео, Лог, Настройки воды.
"""
import customtkinter as ctk
import time
import os
import sys
import signal
from datetime import datetime
from PIL import Image, ImageTk
import cv2


# === ОКНО ВИДЕО ===
class PreviewWindow(ctk.CTkToplevel):
    def __init__(self, parent, font_size=13):
        super().__init__(parent)
        self.title("Видео — Andy-1-3")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_width = 420
        window_height = 320
        x_pos = 0
        y_pos = screen_h - window_height - 50
        self.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.resizable(True, True)
        self.is_open = True
        self.font_size = font_size
        self._frame_times = []
        self._canvas = None

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(5, 0), padx=10, fill="x")
        ctk.CTkLabel(header, text="🟢 поплавок  🔴 клёв  🟡 зоны мини-игры",
                     font=ctk.CTkFont(size=self.font_size - 1)).pack(side="left")
        self.fps_label = ctk.CTkLabel(header, text="FPS: --",
                                      font=ctk.CTkFont(size=self.font_size, weight="bold"),
                                      text_color="#4ade80")
        self.fps_label.pack(side="right")

        self._canvas = ctk.CTkLabel(self, text="Ожидание запуска...",
                                     width=400, height=260)
        self._canvas.pack(pady=5, padx=10, fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def update_frame(self, tk_image):
        if self.is_open and self._canvas:
            self._canvas.configure(image=tk_image, text="")
            self._canvas.image = tk_image
            now = time.time()
            self._frame_times.append(now)
            self._frame_times = [t for t in self._frame_times if now - t < 2.0]
            if len(self._frame_times) >= 2:
                fps = len(self._frame_times) / (self._frame_times[-1] - self._frame_times[0])
                self.fps_label.configure(text=f"FPS: {fps:.1f}")

    def _on_close(self):
        self.is_open = False
        self.destroy()


# === ОКНО ЛОГА ===
class LogWindow(ctk.CTkToplevel):
    def __init__(self, parent, font_size=13):
        super().__init__(parent)
        self.title("📜 Лог — Andy-1-3")
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_width = 420
        window_height = 320
        x_pos = 0
        y_pos = screen_h - window_height - 50
        self.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.resizable(True, True)
        self.is_open = True
        self.font_size = font_size

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5, padx=10, fill="x")
        self.copy_btn = ctk.CTkButton(
            btn_frame, text="📋 Копировать всё", width=140, height=30,
            fg_color="#2c3e50", hover_color="#34495e", command=self._copy_all
        )
        self.copy_btn.pack(side="left", padx=5)
        self.clear_btn = ctk.CTkButton(
            btn_frame, text="🗑 Очистить", width=100, height=30,
            fg_color="#e74c3c", hover_color="#c0392b", command=self._clear_log
        )
        self.clear_btn.pack(side="right", padx=5)
        self.count_label = ctk.CTkLabel(
            btn_frame, text="0 строк", font=ctk.CTkFont(size=font_size - 1), text_color="gray"
        )
        self.count_label.pack(side="right", padx=10)

        self.text = ctk.CTkTextbox(self, font=ctk.CTkFont(size=self.font_size))
        self.text.pack(pady=5, padx=10, fill="both", expand=True)
        self._line_count = 0

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def append_log(self, message):
        if self.is_open:
            self.text.insert("end", f"{message}\n")
            self.text.see("end")
            self._line_count += 1
            self.count_label.configure(text=f"{self._line_count} строк")

    def _copy_all(self):
        try:
            content = self.text.get("1.0", "end-1c")
            self.clipboard_clear()
            self.clipboard_append(content)
            self.update()
            old_text = self.copy_btn.cget("text")
            self.copy_btn.configure(text="✓ Скопировано!", fg_color="#27ae60")
            self.after(1500, lambda: self.copy_btn.configure(text=old_text, fg_color="#2c3e50"))
        except Exception as e:
            print(f"[LOG] Ошибка копирования: {e}")

    def _clear_log(self):
        self.text.delete("1.0", "end")
        self._line_count = 0
        self.count_label.configure(text="0 строк")

    def _on_close(self):
        self.is_open = False
        self.destroy()


# === 🆕 ОКНО НАСТРОЕК ВОДЫ ===
class WaterSettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config, on_apply_callback, font_size=13):
        super().__init__(parent)
        self.title("⚙ Настройки воды")
        self.geometry("480x720")
        self.resizable(False, False)
        self.is_open = True
        self.config = config
        self.on_apply = on_apply_callback
        self.font_size = font_size

        ctk.CTkLabel(self, text="⚙ Настройки детекта воды",
                     font=ctk.CTkFont(size=self.font_size + 4, weight="bold")).pack(pady=10)

        info = ctk.CTkLabel(self,
            text="💡 Настрой параметры детекта воды.\n"
                 "Меньше порог = агрессивнее поиск.\n"
                 "Больше радиус центра = больше зоны персонажа исключается.",
            font=ctk.CTkFont(size=self.font_size - 1), text_color="gray", justify="left")
        info.pack(pady=5, padx=15)

        # --- Порог % воды ---
        f1 = ctk.CTkFrame(self); f1.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f1, text="🌊 Порог % воды:", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.thr_slider = ctk.CTkSlider(f1, from_=1, to=30, number_of_steps=29, width=180)
        self.thr_slider.set(config.get("water_threshold_percent", 8.0))
        self.thr_slider.pack(side="left", padx=5)
        self.thr_label = ctk.CTkLabel(f1, text=f"{config.get('water_threshold_percent', 8.0):.1f}",
                                      font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.thr_label.pack(side="left", padx=5)
        self.thr_slider.configure(command=lambda v: (
            self.thr_label.configure(text=f"{float(v):.1f}"),
            self.config.update({"water_threshold_percent": float(v)})
        ))

        # --- Интервал проверки ---
        f2 = ctk.CTkFrame(self); f2.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f2, text="⏱ Интервал проверки (сек):", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.interval_slider = ctk.CTkSlider(f2, from_=0.5, to=10.0, number_of_steps=19, width=180)
        self.interval_slider.set(config.get("water_check_interval", 2.0))
        self.interval_slider.pack(side="left", padx=5)
        self.interval_label = ctk.CTkLabel(f2, text=f"{config.get('water_check_interval', 2.0):.1f}",
                                           font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.interval_label.pack(side="left", padx=5)
        self.interval_slider.configure(command=lambda v: (
            self.interval_label.configure(text=f"{float(v):.1f}"),
            self.config.update({"water_check_interval": float(v)})
        ))

        # --- HSV H min ---
        f3 = ctk.CTkFrame(self); f3.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f3, text="🎨 HSV H min:", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.hmin_slider = ctk.CTkSlider(f3, from_=80, to=120, number_of_steps=40, width=180)
        self.hmin_slider.set(config.get("water_h_min", 95))
        self.hmin_slider.pack(side="left", padx=5)
        self.hmin_label = ctk.CTkLabel(f3, text=str(int(config.get("water_h_min", 95))),
                                       font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.hmin_label.pack(side="left", padx=5)
        self.hmin_slider.configure(command=lambda v: (
            self.hmin_label.configure(text=str(int(v))),
            self.config.update({"water_h_min": int(v)})
        ))

        # --- HSV H max ---
        f4 = ctk.CTkFrame(self); f4.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f4, text="🎨 HSV H max:", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.hmax_slider = ctk.CTkSlider(f4, from_=110, to=160, number_of_steps=50, width=180)
        self.hmax_slider.set(config.get("water_h_max", 135))
        self.hmax_slider.pack(side="left", padx=5)
        self.hmax_label = ctk.CTkLabel(f4, text=str(int(config.get("water_h_max", 135))),
                                       font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.hmax_label.pack(side="left", padx=5)
        self.hmax_slider.configure(command=lambda v: (
            self.hmax_label.configure(text=str(int(v))),
            self.config.update({"water_h_max": int(v)})
        ))

        # --- HSV S min ---
        f5 = ctk.CTkFrame(self); f5.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f5, text="🎨 HSV S min:", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.smin_slider = ctk.CTkSlider(f5, from_=10, to=100, number_of_steps=90, width=180)
        self.smin_slider.set(config.get("water_s_min", 30))
        self.smin_slider.pack(side="left", padx=5)
        self.smin_label = ctk.CTkLabel(f5, text=str(int(config.get("water_s_min", 30))),
                                       font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.smin_label.pack(side="left", padx=5)
        self.smin_slider.configure(command=lambda v: (
            self.smin_label.configure(text=str(int(v))),
            self.config.update({"water_s_min": int(v)})
        ))

        # --- HSV V min ---
        f6 = ctk.CTkFrame(self); f6.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f6, text="🎨 HSV V min:", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.vmin_slider = ctk.CTkSlider(f6, from_=10, to=100, number_of_steps=90, width=180)
        self.vmin_slider.set(config.get("water_v_min", 30))
        self.vmin_slider.pack(side="left", padx=5)
        self.vmin_label = ctk.CTkLabel(f6, text=str(int(config.get("water_v_min", 30))),
                                       font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.vmin_label.pack(side="left", padx=5)
        self.vmin_slider.configure(command=lambda v: (
            self.vmin_label.configure(text=str(int(v))),
            self.config.update({"water_v_min": int(v)})
        ))

        # --- HSV V max ---
        f7 = ctk.CTkFrame(self); f7.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f7, text="🎨 HSV V max:", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.vmax_slider = ctk.CTkSlider(f7, from_=150, to=255, number_of_steps=105, width=180)
        self.vmax_slider.set(config.get("water_v_max", 220))
        self.vmax_slider.pack(side="left", padx=5)
        self.vmax_label = ctk.CTkLabel(f7, text=str(int(config.get("water_v_max", 220))),
                                       font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.vmax_label.pack(side="left", padx=5)
        self.vmax_slider.configure(command=lambda v: (
            self.vmax_label.configure(text=str(int(v))),
            self.config.update({"water_v_max": int(v)})
        ))

        # --- Фильтр синевы (B-R) ---
        f8 = ctk.CTkFrame(self); f8.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f8, text="💙 Фильтр синевы (B-R):", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.br_slider = ctk.CTkSlider(f8, from_=5, to=60, number_of_steps=55, width=180)
        self.br_slider.set(config.get("water_blue_red_diff", 20))
        self.br_slider.pack(side="left", padx=5)
        self.br_label = ctk.CTkLabel(f8, text=str(int(config.get("water_blue_red_diff", 20))),
                                     font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.br_label.pack(side="left", padx=5)
        self.br_slider.configure(command=lambda v: (
            self.br_label.configure(text=str(int(v))),
            self.config.update({"water_blue_red_diff": int(v)})
        ))

        # --- Радиус исключения центра ---
        f9 = ctk.CTkFrame(self); f9.pack(pady=5, padx=15, fill="x")
        ctk.CTkLabel(f9, text="⭕ Радиус центра (px):", font=ctk.CTkFont(size=self.font_size)).pack(side="left", padx=10)
        self.radius_slider = ctk.CTkSlider(f9, from_=50, to=300, number_of_steps=25, width=180)
        self.radius_slider.set(config.get("water_exclude_center_radius", 150))
        self.radius_slider.pack(side="left", padx=5)
        self.radius_label = ctk.CTkLabel(f9, text=str(int(config.get("water_exclude_center_radius", 150))),
                                         font=ctk.CTkFont(size=self.font_size, weight="bold"), width=40)
        self.radius_label.pack(side="left", padx=5)
        self.radius_slider.configure(command=lambda v: (
            self.radius_label.configure(text=str(int(v))),
            self.config.update({"water_exclude_center_radius": int(v)})
        ))

        # --- Кнопка Применить ---
        apply_btn = ctk.CTkButton(self, text="✅ Применить",
                                  font=ctk.CTkFont(size=self.font_size + 1, weight="bold"),
                                  height=45, fg_color="#1f6aa5", hover_color="#1a5a8a",
                                  command=self._apply)
        apply_btn.pack(pady=15, padx=15, fill="x")

        hint = ctk.CTkLabel(self,
            text="💡 H: оттенок (95-135 = бирюзовый/синий)\n"
                 "S: насыщенность (выше = чище цвет)\n"
                 "V: яркость (ниже = темнее вода)\n"
                 "B-R: разница синий-красный (отсекает траву)\n"
                 "Радиус: зона персонажа (исключается из анализа)",
            font=ctk.CTkFont(size=self.font_size - 1), text_color="gray", justify="left")
        hint.pack(pady=5, padx=15)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply(self):
        self.on_apply(self.config)

    def _on_close(self):
        self.is_open = False
        self.destroy()


# === ГЛАВНЫЙ GUI ===
class Andy1GUI:
    def __init__(self, app_instance):
        self.app = app_instance
        self.root = self.app.root
        self.font_size = self.app.config.get("font_size", 13)

        self.preview_window = None
        self.log_window = None
        self.settings_window = None

        self._build_ui()
        self._start_update_loop()

    def _build_ui(self):
        fs = self.font_size

        # Заголовок с кружком-индикатором и кнопкой закрытия
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(pady=(10, 5), padx=15, fill="x")
        
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.pack(side="left")
        self.indicator = ctk.CTkLabel(
            left_frame, text="●",
            font=ctk.CTkFont(size=fs + 8, weight="bold"),
            text_color="#5a6a5a"
        )
        self.indicator.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(left_frame, text="Andy-1-3",
                     font=ctk.CTkFont(size=fs + 6, weight="bold")).pack(side="left")

        self.close_btn = ctk.CTkButton(
            header_frame, text="X", width=36, height=36,
            font=ctk.CTkFont(size=fs + 4, weight="bold"),
            fg_color="#6c757d", hover_color="#5a6268",
            command=self._close_terminal
        )
        self.close_btn.pack(side="right")

        # Настройки (серая подложка)
        settings_frame = ctk.CTkFrame(self.root)
        settings_frame.pack(pady=5, padx=15, fill="x")

        # Порог совпадения
        f_thr = ctk.CTkFrame(settings_frame, fg_color="transparent")
        f_thr.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(f_thr, text="Порог совпадения:", font=ctk.CTkFont(size=fs)).pack(side="left")
        self.thr_slider = ctk.CTkSlider(f_thr, from_=0.30, to=0.95, number_of_steps=65, width=150)
        self.thr_slider.set(self.app.config.get("match_threshold", 0.62))
        self.thr_slider.pack(side="left", padx=5)
        self.thr_label = ctk.CTkLabel(f_thr, text=f"{self.app.config.get('match_threshold', 0.62):.2f}",
                                      font=ctk.CTkFont(size=fs, weight="bold"), width=40)
        self.thr_label.pack(side="left")
        self.thr_slider.configure(command=lambda v: (
            self.thr_label.configure(text=f"{float(v):.2f}"),
            self.app.config.update({"match_threshold": float(v)})
        ))

        # Рывок по Y
        f_bite = ctk.CTkFrame(settings_frame, fg_color="transparent")
        f_bite.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(f_bite, text="Рывок по Y (клёв):", font=ctk.CTkFont(size=fs)).pack(side="left")
        self.bite_slider = ctk.CTkSlider(f_bite, from_=1, to=100, number_of_steps=99, width=150)
        self.bite_slider.set(self.app.config.get("bite_y_threshold", 7))
        self.bite_slider.pack(side="left", padx=5)
        self.bite_label = ctk.CTkLabel(f_bite, text=str(int(self.app.config.get('bite_y_threshold', 7))),
                                       font=ctk.CTkFont(size=fs, weight="bold"), width=40)
        self.bite_label.pack(side="left")
        self.bite_slider.configure(command=lambda v: (
            self.bite_label.configure(text=str(int(v))),
            self.app.config.update({"bite_y_threshold": int(v)})
        ))

        # === Сетка кнопок 2x3 ===
        btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        btn_frame.pack(pady=10, padx=15, fill="x")

        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        # Ряд 1: Старт, Стоп
        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶ Старт", font=ctk.CTkFont(size=fs+2, weight="bold"),
            height=45, fg_color="#1f6aa5",
            command=self.app.start_bot
        )
        self.start_btn.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        self.stop_btn = ctk.CTkButton(
            btn_frame, text="⏹ Стоп", font=ctk.CTkFont(size=fs+2, weight="bold"),
            height=45, fg_color="#1f6aa5",
            command=self.app.stop_bot
        )
        self.stop_btn.grid(row=0, column=1, padx=4, pady=4, sticky="ew")

        # Ряд 2: Видео, Лог
        self.video_btn = ctk.CTkButton(
            btn_frame, text="🎥 Видео", font=ctk.CTkFont(size=fs),
            height=45, fg_color="#2c3e50", hover_color="#34495e",
            command=self._toggle_preview
        )
        self.video_btn.grid(row=1, column=0, padx=4, pady=4, sticky="ew")

        self.log_btn = ctk.CTkButton(
            btn_frame, text="📜 Лог", font=ctk.CTkFont(size=fs),
            height=45, fg_color="#2c3e50", hover_color="#34495e",
            command=self._toggle_log
        )
        self.log_btn.grid(row=1, column=1, padx=4, pady=4, sticky="ew")

        # 🆕 Ряд 3: (пусто), Настройки
        self.settings_btn = ctk.CTkButton(
            btn_frame, text="⚙ Настройки", font=ctk.CTkFont(size=fs),
            height=45, fg_color="#2c3e50", hover_color="#34495e",
            command=self._toggle_settings
        )
        self.settings_btn.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

        # Статус
        status_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        status_frame.pack(pady=5, padx=15, fill="x")
        self.status_label = ctk.CTkLabel(status_frame, text="⏸ Остановлен",
                                         font=ctk.CTkFont(size=fs, weight="bold"), text_color="gray")
        self.status_label.pack(side="left")

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
        try:
            if self.preview_window:
                self.preview_window.destroy()
        except Exception:
            pass
        try:
            if self.log_window:
                self.log_window.destroy()
        except Exception:
            pass
        try:
            if self.settings_window:
                self.settings_window.destroy()
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
        if self.preview_window and getattr(self.preview_window, "is_open", False):
            self.preview_window.destroy()
            self.preview_window = None
        else:
            self.preview_window = PreviewWindow(self.root, self.font_size)
            self.preview_window.transient(self.root)

    def _toggle_log(self):
        if self.log_window and getattr(self.log_window, "is_open", False):
            self.log_window.destroy()
            self.log_window = None
        else:
            self.log_window = LogWindow(self.root, self.font_size)
            self.log_window.transient(self.root)

    def _toggle_settings(self):
        if self.settings_window and getattr(self.settings_window, "is_open", False):
            self.settings_window.destroy()
            self.settings_window = None
        else:
            self.settings_window = WaterSettingsWindow(
                self.root, self.app.config, self._on_settings_applied, self.font_size
            )
            self.settings_window.transient(self.root)

    def _on_settings_applied(self, new_config):
        """Применяет настройки воды на лету."""
        self.app.config.update(new_config)
        self.app._save_config()
        # Сбрасываем таймер проверки, чтобы новый интервал применился сразу
        if hasattr(self.app, 'fishing') and self.app.fishing:
            self.app.fishing._last_water_check_time = 0
        print("[GUI] ✓ Настройки воды применены")

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg)
        if self.log_window and getattr(self.log_window, "is_open", False):
            self.log_window.append_log(msg)

    def update_status(self, state, active):
        if active:
            self.indicator.configure(text_color="#4ade80")
            self.status_label.configure(text=f"🟢 Активен: {state}", text_color="#4ade80")
        else:
            self.indicator.configure(text_color="#5a6a5a")
            self.status_label.configure(text="⏸ Остановлен", text_color="gray")

    def send_frame_to_preview(self, frame_bgr):
        if self.preview_window and getattr(self.preview_window, "is_open", False):
            try:
                rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                pil = Image.fromarray(rgb)
                pw = self.preview_window.winfo_width()
                ph = self.preview_window.winfo_height()
                if pw > 100 and ph > 100:
                    target_w = max(100, pw - 20)
                    target_h = max(100, ph - 60)
                    pil = pil.resize((target_w, target_h), Image.LANCZOS)
                tk_img = ImageTk.PhotoImage(pil)
                self.preview_window.update_frame(tk_img)
            except Exception:
                pass

    def _start_update_loop(self):
        self._update_gui_state()

    def _update_gui_state(self):
        if self.app.bot_running and hasattr(self.app, 'fishing') and self.app.fishing:
            self.update_status(self.app.fishing.state, True)
        else:
            self.update_status("IDLE", False)
        self.root.after(200, self._update_gui_state)
