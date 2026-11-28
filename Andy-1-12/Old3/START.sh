#!/bin/bash
cd "$(dirname "$0")"
echo "Запуск бота..."
python3 gui.py
echo ""
echo "Бот остановлен. Закрой это окно или нажми Enter."
read -r
