#!/bin/bash

# Andy — Assistant Launcher

echo "🎣 Запуск Andy..."

# Активация виртуального окружения
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ Venv активирован"
else
    echo "⚠ Venv не найден! Создай: python3 -m venv venv"
    exit 1
fi

# Проверка DISPLAY
if [ -z "$DISPLAY" ]; then
    echo "⚠ DISPLAY не установлен. Пробую :0"
    export DISPLAY=:0
fi

# Запуск
python main.py

echo "👋 Andy завершён"