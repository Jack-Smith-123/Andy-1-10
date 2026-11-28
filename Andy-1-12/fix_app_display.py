with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим место после создания app_locator и добавляем set_window_id
old = '''        self.app_locator = AppLocator()
        if self.app_locator.find_window():
            monitor = self.app_locator.get_monitor()
            if monitor:
                self.display.set_monitor(monitor)
                print(f"Окно найдено: {self.app_locator.get_rect()}")'''

new = '''        self.app_locator = AppLocator()
        if self.app_locator.find_window():
            monitor = self.app_locator.get_monitor()
            if monitor:
                self.display.set_monitor(monitor)
                self.display.set_window_id(self.app_locator.window_id)
                print(f"Окно найдено: {self.app_locator.get_rect()}")'''

if old in content:
    content = content.replace(old, new)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✓ app.py обновлён - добавлен set_window_id')
else:
    print('⚠ Не найдено место для вставки')
