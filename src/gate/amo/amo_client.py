import logging
from typing import Optional
from amocrm.v2.tokens import TokenManager
from amocrm.v2.exceptions import NoToken, NotFound
from gate.amo.mocker_lead_id import MockerLeadID
from gate.transform.booked_models import Booking


logger = logging.getLogger(__name__)

class AmoClient:

    def __init__(
            self,
            manager: TokenManager,
            auth_code: Optional[str],
            *,
            booked_lead_cls,
            mocked_lead_id: bool = False,
            mocker: Optional[MockerLeadID] = None,
            ):
        self._ensure_initialized(manager, auth_code)
        self.mocker = mocker
        self.mocked_lead_id = mocked_lead_id
        self.BookedLead = booked_lead_cls

        if mocked_lead_id:
            logger.info('Амо клиент запущен в режиме подмены lead_id.')
            if mocker is None:
                raise RuntimeError(
                        "Mocker не передан! Режим подмены lead_id недоступен!"
                        )


    def update_booked_info(self, data: dict) -> bool:
        # Получаем lead_id
        lead_id = data.get('lead_id', None)

        if lead_id is None:
            logger.warning(f'Данные не содержат lead_id! Данные: {data}')
            return False

        # Подменяем lead_id если включен режим подмены
        if self.mocked_lead_id:
            if self.mocker:
                try:
                    mock_lead_id = self.mocker.get_mock(lead_id)
                    lead_id = mock_lead_id
                except Exception as e:
                    logger.warning(
                        'При попытки получить mock лид для данных с '
                        f'lead_id: "{lead_id}" произошла непредвиденная ошибка :{e}'
                        )
                    raise e

        # Получаем lead_id
        try:
            lead = self.BookedLead.objects.get(object_id=lead_id)
        except NotFound:
            logger.warning(f'Лид с lead_id: {lead_id} не найден.')
            return False

        # Обновляем поля
        try:
            booking = Booking(**data)
            lead.update_fields(booking)
            lead.save()
            logger.info(f'Данные для лида {lead.id=} успешно обновлены.')
            return True
        except Exception as e:
            logger.warning(
                    f'Не удалось обновить параметры лида с lead_id: {lead_id}'
                    )
            raise e

    def update_mc_info(self, data):
        # transformer.transform('mc', data)
        pass

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
