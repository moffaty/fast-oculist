import os
import logging
from datetime import datetime
import logging.config

from uvicorn.config import LOGGING_CONFIG

from .settings import APP_SETTINGS


class TimeStructuredFileHandler(logging.FileHandler):
    def __init__(self, base_dir: str = "logs", filename: str = "log.txt", encoding: str = "utf-8") -> None:
        self.base_dir = base_dir
        self.filename = filename
        self.encoding = encoding
        filepath = self._get_log_file_path()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        super().__init__(filepath, encoding=self.encoding)

    def _get_log_file_path(self) -> str:
        now = datetime.now()
        path = os.path.join(self.base_dir, now.strftime("%Y-%m"), now.strftime("%d"), now.strftime("%H"), self.filename)
        return path


# Копируем базовую конфигурацию uvicorn
LOG_CONFIG = LOGGING_CONFIG.copy()

# Настройка форматтеров
LOG_CONFIG["formatters"]["access"]["fmt"] = (
    "%(levelprefix)s %(asctime)s - %(client_addr)s - %(request_line)s %(status_code)s"
)
LOG_CONFIG["formatters"]["default"]["fmt"] = "%(levelprefix)s %(asctime)s [%(name)s] - %(message)s"

# Настройка кастомного хендлера
log_file_handler = TimeStructuredFileHandler()

LOG_CONFIG["handlers"]["structured_file"] = {
    "class": "logging.StreamHandler",  # мы используем stream из кастомного хендлера
    "formatter": "default",
    "level": "DEBUG",
    "stream": log_file_handler.stream,
}

# Логгер приложения
LOG_CONFIG["loggers"][APP_SETTINGS.PROJECT_NAME] = {
    "handlers": ["default", "structured_file"],
    "level": "DEBUG",
    "propagate": False,
}

# Применяем конфигурацию
logging.config.dictConfig(LOG_CONFIG)

# Готовый логгер, который можно импортировать
logger = logging.getLogger(APP_SETTINGS.PROJECT_NAME)
