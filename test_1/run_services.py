import sys
from pathlib import Path
import subprocess


def run_services():
    """Запуск обоих сервисов одновременно"""
    # Проверка наличия файлов
    if not Path("processing_service.py").exists():
        print("Ошибка: Файл processing_service.py не найден")
        return
    if not Path("objects_service.py").exists():
        print("Ошибка: Файл objects_service.py не найден")
        return

    try:
        # Запуск сервиса обработки на порту 8000
        processing_service = subprocess.Popen(
            [sys.executable, "processing_service.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Сервис обработки запущен на порту 8000")

        # Запуск сервиса объектов на порту 8001
        objects_service = subprocess.Popen(
            [sys.executable, "objects_service.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Сервис управления объектами запущен на порту 8001")

        print("\nОба сервиса запущены. Нажмите Ctrl+C для завершения.")

        # Ожидание завершения процессов
        processing_service.wait()
        objects_service.wait()

    except KeyboardInterrupt:
        print("\nЗавершение работы сервисов...")
        if processing_service:
            processing_service.terminate()
        if objects_service:
            objects_service.terminate()
        print("Сервисы остановлены.")

    except Exception as e:
        print(f"Ошибка при запуске сервисов: {e!s}")


if __name__ == "__main__":
    run_services()
