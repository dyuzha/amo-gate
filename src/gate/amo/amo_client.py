import logging
from typing import Optional
from amocrm.v2.tokens import TokenManager
from amocrm.v2.exceptions import NoToken
from gate.amo.pipeline_manager import LeadNotFound, MockLeadException, PipelineManager, LeadIdKeyError


logger = logging.getLogger(__name__)


class AmoClient:
    def __init__(
            self,
            manager: TokenManager,
            auth_code: Optional[str],
            *,
            pipelines_data_map: dict[str, PipelineManager],
            mocked_lead_id: bool = False,
            ):
        self._ensure_initialized(manager, auth_code)
        self.pl_data_map = pipelines_data_map
        self.mocked_lead_id = mocked_lead_id
        if mocked_lead_id:
            logger.info('AmoClient запущен в режиме подмены lead_id')


    def load_pipeline_lead_data(self, data: dict, pipeline_name: str):
        """Загружает данные в воронку"""
        pl = self.pl_data_map.get(pipeline_name)
        if pl is None:
            logger.error(
                    f'Воронка {pipeline_name=} не найдена в {self.pl_data_map}'
                    )
            return False

        # Получаем lead_id
        lead_id = data.get('lead_id', None)
        if lead_id is None:
            logger.error(f'Поле lead_id не найдено в данных: {data}')
            return False

        # Обновляем данные
        try:
            pl.update_info(lead_id, data, self.mocked_lead_id)

        except MockLeadException as e:
            logger.error(str(e))
            return False

        except LeadNotFound as e:
            logger.warning(str(e))
            return False

        except Exception as e:
            logger.warning(
                    f'Не удалось обновить параметры лида с lead_id: {lead_id}',
                    str(e)
                    )
            raise e

        logger.info(f'Данные c {lead_id=} успешно загружены.')
        return True


    def _ensure_initialized(
            self, manager: TokenManager, auth_code: str | None = None
            ):
        try:
            manager.get_access_token()
        except NoToken as e:
            if auth_code:
                try:
                    logger.info('Инициализация токенов...')
                    manager.init(code=auth_code, skip_error=False)
                    logger.info('Токены успешно инициализирован!')
                except Exception as e:
                    logger.error(
                            'Ошибка инициализации токенов. '
                            f'Добавьте AUTH_CODE в .env: {e}'
                            )
                    raise e
            else:
                raise RuntimeError(
                        f"Токены отсутствуют. Добавьте AUTH_CODE в .env: {e}"
                    )
