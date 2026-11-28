"""
Запуск приложения Andy-1 с маскировкой процесса.
"""
import sys
import os
import ctypes
import multiprocessing

# Скрываем консольное окно (Windows)
if sys.platform == "win32":
    try:
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    except:
        pass


def run_app():
    """Запуск основного приложения."""
    # Меняем название процесса
    try:
        from multiprocessing import current_process
        current_process().name = "Andy-1"
    except:
        pass
    
    # Добавляем текущую папку в путь импортов
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Импортируем и запускаем основное приложение
    from app import main
    main()


if __name__ == "__main__":
    # Запускаем в отдельном процессе с изменённым именем
    process = multiprocessing.Process(
        target=run_app, 
        name="Andy-1"
    )
    process.start()
    process.join()