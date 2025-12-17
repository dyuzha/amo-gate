import logging, sys, uvicorn, signal
from typing import Any
from pathlib import Path
from gate.amo.amo_register import amo_register
from gate.settings.config import register_settings
from gate.settings.logging_config import setup_logging
from gate.utils.parse_args import parse_args
from gate.workers.queue_manager import TaskQueue
from gate.app.api import app_register


logger = logging.getLogger("main")

args = parse_args()

root_path = Path(__file__).resolve().parent.parent


# Загрузка настроек
settings = register_settings(root_path)
amo_settings = settings.amo
app_settings = settings.app
mock_pipeline_settings = settings.mock_pipeline

booked_fields=settings.booked_fields
shared_fields=settings.shared_fields

# Настройка логирования
setup_logging(level=logging.DEBUG, log_dir=app_settings.log_dir)


def handle_shutdown(signum, frame):
    logger.info(f"Получен сигнал {signum}. Завершение работы приложения...")

    # Останавливаем воркер, если он есть
    try:
        task_queue.stop_worker()
    except Exception as e:
        logger.error(f"Ошибка при остановке воркера: {e}")

    logger.info("Приложение завершено.")
    sys.exit(0)


# Подключаем обработчики сигналов
signal.signal(signal.SIGINT, handle_shutdown)   # Ctrl-C
signal.signal(signal.SIGTERM, handle_shutdown)  # systemd/docker/k8s


# Регистрируем амо клиент
amo_client = amo_register(
        tokens_path=root_path / ".tokens",
        mocked_lead_id=args.mocked_lead_id,
        amo_settings=amo_settings,
        shared_fields=shared_fields,
        booked_fields=booked_fields,
        booked_id=mock_pipeline_settings.booked_id,
        booked_status_id=mock_pipeline_settings.booked_status_id,
        )


# Создаем очередь
task_queue = TaskQueue()
# запускаем воркер в отдельном потоке/процессе
task_queue.start_worker(amo_client)


# Запускаем API
app = app_register(
        incoming_booked=app_settings.incoming_booked,
        incoming_mc=app_settings.incoming_mc,
        )


# Связываем очередь с FastAPI
app.state.task_queue = task_queue
app.state.amo_client = amo_client
logger.info("API успешно подключилось к менеджеру очереди.")



uvicorn_settings: dict[str, Any] = dict(
        app=app,
        host=app_settings.host,
        port=app_settings.port,
        )


if app_settings.ssl_enabled:
    uvicorn_settings.update(
            ssl_keyfile=app_settings.ssl_key,
            ssl_certfile=app_settings.ssl_cert,
            )

if __name__ == "__main__":
    uvicorn.run(**uvicorn_settings)
