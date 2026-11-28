#!/bin/bash
# Переходим в папку со скриптом
cd "$(dirname "$0")"

# Если нет виртуального окружения — создаем и ставим зависимости
if [ ! -d "venv" ]; then
    echo "⚙️ Создаю виртуальное окружение (это займет минуту)..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Запускаем главный файл бота (именно он открывает GUI)
echo "🎣 Запуск Andy-1..."
python3 main.py

# Если бот закрылся с ошибкой, ждем нажатия Enter, чтобы ты успел прочитать вывод
read -p "Нажми Enter для выхода..."
