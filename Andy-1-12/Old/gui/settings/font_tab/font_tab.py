"""
Вкладка "Шрифты" — компоновщик.
Левые границы выровнены по единой вертикали (padx=10 на уровне main_frame).
"""
import customtkinter as ctk
from .preview_panel import PreviewPanel
from .font_sizes_panel import FontSizesPanel


class FontTab:
    def __init__(self, parent, config, font_size=13, theme=None, font_manager=None):
        self.config = config
        self.font_size = font_size
        self.theme = theme or {}
        self.font_manager = font_manager
        self._build(parent)

    def _build(self, parent):
        main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)  # ✅ Единый отступ слева

        # === Верх: фиксированное превью (без внутренних отступов) ===
        preview_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent",
            corner_radius=8,
            height=145
        )
        preview_frame.pack(fill="x", pady=(0, 5))  # ✅ Убран padx
        preview_frame.pack_propagate(False)

        self.preview = PreviewPanel(
            preview_frame, self.config, self.theme, self.font_manager,
            on_change_callback=self._refresh
        )

        # === Низ: прокручиваемые ползунки (без внутренних отступов) ===
        scroll_frame = ctk.CTkFrame(
            main_frame,
            fg_color=self.theme.get("bg_panel", "#2a3142"),
            corner_radius=8
        )
        scroll_frame.pack(fill="both", expand=True)  # ✅ Убран padx

        self.sizes = FontSizesPanel(
            scroll_frame, self.config, self.theme, self.font_manager,
            on_change_callback=self._refresh
        )

    def _refresh(self):
        """Обновляет превью при изменении любого шрифта."""
        self.preview.update_fonts()

    def get_pending_font_family(self):
        return self.preview.get_pending_font_family()
