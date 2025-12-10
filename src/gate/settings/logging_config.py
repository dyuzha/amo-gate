from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import logging
import sys
from pathlib import Path
from typing import Optional


NOISE_LOGGERS = [
    "uvicorn",
    "asyncio",
    # "uvicorn.error",
    # "uvicorn.access",
    # "urllib3",
    # "amocrm",
    # "requests",
]

# 🎨 базовые ANSI-цвета
PINK = "\033[95m"
DARK_BLUE = "\033[94m"
BLUE = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
GREY = "\033[90m"
VIOLET = "\033[35m"
IMPORTANT = "\033[97;41m",


MODULE_COLORS = dict(
    api= GREEN,
    amo_client = BLUE,
    mocker_lead_id = VIOLET,
    utils = GREY,
    queue_manager = YELLOW,
    )

class ColoredFormatter(logging.Formatter):
    """Цветной формат:
    - уровень — цвет по важности
    - текст — цвет по имени модуля
    """

    LEVEL_COLORS = {
        "DEBUG": "\033[90m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[97;41m",
    }

    RESET = "\033[0m"



    def format(self, record: logging.LogRecord) -> str:
        module_name = record.name.split('.')[-1]
        record.asctime = self.formatTime(record, self.datefmt)

        level_color = self.LEVEL_COLORS.get(record.levelname, self.RESET)
        module_color = MODULE_COLORS.get(module_name, self.RESET)
        text_color = level_color if record.levelname != 'INFO' else self.RESET

        level_block = f"{level_color}[{record.levelname}]{self.RESET} "
        module_block = f"{module_color}{module_name}{self.RESET}: "
        message_block = f"{text_color}{record.getMessage()}{self.RESET}"

        return f'{record.asctime} {level_block} {module_block} {message_block}'


def setup_logging(
        level=logging.INFO,
        log_dir: Optional[Path] = None,
        stream: bool = True,
        ):
    """Логирование в консоль и в файл вида logs/YYYY-MM-DD.log."""
    handlers: list[logging.Handler] = []

    if log_dir:

        # Создаем директорию
        log_dir.mkdir(exist_ok=True)

        # Добавляем вывод в файл по текущей дате
        # log_file = log_dir / f'{datetime.now():%Y-%m-%d}.log'
        log_file = log_dir / f'rdesk2amo-gate.log'

        # file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler = TimedRotatingFileHandler(
                filename=str(log_file),
                when="midnight",
                interval=1,
                backupCount=30,
                encoding="utf-8",
                utc=False,
                )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        handlers.append(file_handler)

    if stream:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(ColoredFormatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        handlers.append(stream_handler)


    logging.basicConfig(
        level=level,
        handlers=handlers,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    for ln in NOISE_LOGGERS:
        logging.getLogger(ln).setLevel(logging.CRITICAL)
        logging.getLogger(ln).propagate = False
