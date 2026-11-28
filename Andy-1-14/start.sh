#!/bin/bash
# Запуск Andy-1

# Переходим в папку проекта
cd "$(dirname "$0")"

# Активируем виртуальное окружение
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ venv не найден! Создаём..."
    python3 -m venv venv
    source venv/bin/activate
    pip install customtkinter opencv-python numpy mss psutil pyautogui Pillow pynput
fi

# Устанавливаем DISPLAY если не задан
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
fi

# Запускаем
echo "🎣 Запуск Andy-1..."
python launcher.py
