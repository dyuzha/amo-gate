from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request


logger = logging.getLogger(__name__)


def app_register(
        incoming_booked: str,
        incoming_mc: str
        ) -> FastAPI:

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # startup (если понадобится)
        yield
        # shutdown
        logger.info("FastAPI shutdown: останавливаем task_queue")
        try:
            app.state.task_queue.stop_worker()
        except Exception as e:
            logger.error(f"Ошибка при остановке воркера: {e}")

    app = FastAPI(
        title="Amo Gateway API",
        lifespan=lifespan,
    )

    @app.post(incoming_booked)
    async def booked(request: Request):
        """Принимает webhook booked, кладет в очередь и возвращает 200 OK."""

        raw = await request.body()
        logger.debug(f"Получен webhook: {raw.decode()}")

        payload = await request.json()

        for j in payload:
            task_queue = request.app.state.task_queue
            task_queue.put(j, "update_booked_info")

        return {"status": "ok"}


    @app.post(incoming_mc)
    async def mc(request: Request):
        """Принимает webhook mc, кладет в очередь и возвращает 200 OK."""
        payload = await request.json()
        task_queue = request.app.state.task_queue
        task_queue.put(payload, "send_to_mc")

        logger.info(f'Получен webhook: {payload}')
        return {"status": "ok"}

    logger.info('API успешно запущено.')
    return app
