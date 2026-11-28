"""
Модуль для маскировки процесса Andy-1 от античита.
"""
import sys
import ctypes


def hide_console():
    """Скрывает консольное окно."""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.ShowWindow(
                ctypes.windll.kernel32.GetConsoleWindow(), 0
            )
        except:
            pass


def set_process_name(name="Andy-1"):
    """Меняет название процесса."""
    try:
        from multiprocessing import current_process
        current_process().name = name
    except:
        pass


def set_low_priority():
    """Устанавливает низкий приоритет процесса."""
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except:
        pass


def hide_from_taskbar():
    """Скрывает окно из панели задач."""
    if sys.platform == "win32":
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            ctypes.windll.user32.SetWindowLong(
                hwnd, -20,
                ctypes.windll.user32.GetWindowLong(hwnd, -20) | 0x00000080
            )
        except:
            pass