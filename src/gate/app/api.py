from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request


logger = logging.getLogger(__name__)


def app_register(
        incoming_booked: str,
        incoming_mc: str,
        amo_client,
        ) -> FastAPI:


    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.task_queue.start_worker(amo_client)
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
        logger.debug(f"Получен booking webhook: {raw.decode()}")

        payload = await request.json()

        for j in payload:
            task_queue = request.app.state.task_queue
            task_queue.put(j, "booked")

        return {"status": "ok"}


    @app.post(incoming_mc)
    async def mc(request: Request):
        """Принимает webhook mc, кладет в очередь и возвращает 200 OK."""

        raw = await request.body()
        logger.debug(f"Получен mc webhook: {raw.decode()}")

        payload = await request.json()

        for j in payload:
            task_queue = request.app.state.task_queue
            task_queue.put(j, "mc")

        return {"status": "ok"}

    logger.info('API успешно запущено.')
    return app
