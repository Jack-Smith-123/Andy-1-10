with open('gui/panels/base_panel.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем автосохранение в метод _on_change
if 'def _on_change' in content:
    # Находим метод и добавляем сохранение
    old_on_change = '''    def _on_change(self, key, value):
        """Callback при изменении настройки."""
        self.config[key] = value
        if self.on_change:
            self.on_change(key, value)'''

    new_on_change = '''    def _on_change(self, key, value):
        """Callback при изменении настройки."""
        self.config[key] = value
        if self.on_change:
            self.on_change(key, value)
        # Автосохранение
        self._autosave()

    def _autosave(self):
        """Автосохранение конфига."""
        import json
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings.dat")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass'''

    if old_on_change in content:
        content = content.replace(old_on_change, new_on_change)
        with open('gui/panels/base_panel.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('✓ Добавлено автосохранение')
    else:
        print('⚠ Метод _on_change не найден в старом формате')
else:
    print('⚠ Метод _on_change не существует')
