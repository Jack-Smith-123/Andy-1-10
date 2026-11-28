import re

with open('gui/config_panel.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим метод _apply и добавляем сохранение
old_apply = '''    def _apply(self):
        self.config["theme"] = self.app_tab.get_pending_theme()
        self.config["font_family"] = self.app_tab.get_pending_font_family()
        if self.font_manager:
            self.font_manager.clear_cache()
        self.on_apply(self.config)
        print(f"[SETTINGS] ✓ Применено: тема={self.config.get('theme')}")'''

new_apply = '''    def _apply(self):
        self.config["theme"] = self.app_tab.get_pending_theme()
        self.config["font_family"] = self.app_tab.get_pending_font_family()
        if self.font_manager:
            self.font_manager.clear_cache()
        # Сохраняем конфиг
        self._save_config()
        self.on_apply(self.config)
        print(f"[SETTINGS] ✓ Применено и сохранено: тема={self.config.get('theme')}")

    def _save_config(self):
        """Сохраняет конфиг в settings.dat."""
        import json
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.dat")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"[CONFIG] ✓ Сохранено: {config_path}")
        except Exception as e:
            print(f"[CONFIG] ✗ Ошибка сохранения: {e}")'''

if old_apply in content:
    content = content.replace(old_apply, new_apply)
    with open('gui/config_panel.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✓ Добавлено сохранение в _apply')
else:
    print('⚠ Не найден метод _apply в старом формате')
