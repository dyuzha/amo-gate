import threading
import queue
import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)


class TaskQueue:
    """Класс-обёртка для очереди задач и воркера."""

    def __init__(self, timeout: float=0.5):
        self._queue = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._running = False
        self.timeout = timeout
        logger.debug('Менеджер очереди успешно инициализирован.')


    def put(self, data: Any, method_name: str):
        """Добавляет задачу в очередь."""
        try:
            self._queue.put((data, method_name))
            logger.info(f'Задача: "{method_name}" успешно добавлена в очередь.')
        except Exception as e:
            logger.error(
                    f'При добавлении задачи: "{method_name}" '
                    f'произошла непредвиденная ошибка: {e}',
                    )


    def start_worker(self, amo_client):
        """Запускает воркер в отдельном потоке."""
        if self._running:
            logger.info('Менеджер очереди уже запущен.')
            return

        self._running = True

        if self._worker_thread is None:
            self._worker_thread = threading.Thread(
                target=self._worker_loop, args=(amo_client,), daemon=True
            )
        try:
            self._worker_thread.start()
            logger.info('Менеджер очереди запущен в отдельном потоке.')

        except Exception as e:
            self._running = False
            logger.error(
                    f'При запуске менеджера очереди, произошла '
                    f'непредвиденная ошибка: {e}',
                    )


    def _worker_loop(self, amo_client):
        """Основной цикл воркера."""
        while self._running:

            # Получаем задачу из очереди
            try:
                data, pipeline_name = self._queue.get(timeout=self.timeout)

                if data is None and pipeline_name is None:
                    logger.debug(
                            'Передан маркер "None, None", для остановки '
                            'менеджера очереди. Завершаем задачу...'
                            )
                    self._queue.task_done()
                    break

            except queue.Empty:
                continue

            try:
                succes = amo_client.load_pipeline_lead_data(data, pipeline_name)

                if succes:
                    logger.info(
                            'Успешная выполнение задачи для воронки: '
                            f'"{pipeline_name}"'
                            )
                else:
                    logger.info(
                        f'Выполнение задачи для воронки "{pipeline_name}" '
                        'завершено.'
                        )

            except Exception as e:
                logger.error(
                        'Ошибка выполнения задачи для воронки '
                        f'"{pipeline_name}": {e}',
                    exc_info=True
                )

            finally:
                self._queue.task_done()
                logger.debug('Задача завершена.')

        logger.info('Поток менеджера очереди остановлен')


    def stop_worker(self):
        self._running = False

        # Кладём маркер, чтобы воркер проснулся даже если очередь пустая
        self._queue.put((None, None))

        # Если поток запущен — ждём его корректное завершение
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=3)
            if self._worker_thread.is_alive():
                logger.warning("Менеджер очереди не успел завершиться за timeout")
            else:
                logger.info("Менеджер очереди завершён корректно.")
