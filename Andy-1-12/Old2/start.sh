#!/bin/bash

# Переходим в папку, где лежит этот скрипт
cd "$(dirname "$0")"

# Проверяем, есть ли виртуальное окружение, если нет — создаем
if [ ! -d "venv" ]; then
    echo "⚙️ Создаю виртуальное окружение (это займет минуту)..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install opencv-python pyautogui pynput numpy
else
    source venv/bin/activate
fi

# Запускаем интерфейс бота
echo "🎣 Запуск Andy-1..."
python3 gui.py
