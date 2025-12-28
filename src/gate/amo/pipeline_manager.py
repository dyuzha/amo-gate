from typing import Callable

from amocrm.v2.exceptions import NotFound
from pydantic import BaseModel

from gate.amo.models.custom_lead import CustomLead


class LeadIdKeyError(KeyError):
    """Данные не содержат lead_id"""
    pass


class MockLeadException(Exception):
    pass


class LeadNotFound(Exception):
    pass


class PipelineManager:
    def __init__(
            self,
            mock_lead_id_factory: Callable[[int], int],
            lead_factory: Callable[[int], CustomLead] ,
            data_model: type[BaseModel],
            ) :
        self.get_mock_lead_id = mock_lead_id_factory
        self.lead_factory = lead_factory
        self.data_model_cls = data_model

    def update_info(
            self, lead_id: int, data: dict, mocked_lead_id: bool = False
            ):

        # Подменяем lead_id если включен режим подмены
        if mocked_lead_id:
            try:
                mock_lead_id = self.get_mock_lead_id(lead_id)
                lead_id = mock_lead_id
            except Exception as e:
                raise MockLeadException (
                    'При попытки получить mock лид для данных с '
                    f'lead_id: "{lead_id}" произошла непредвиденная ошибка :{e}'
                    )

        # Получаем lead
        try:
            lead = self.lead_factory(lead_id)
        except NotFound:
            raise LeadNotFound(f'Лид с lead_id: {lead_id} не найден.')

        # Обновляем поля
        data_model = self.data_model_cls(**data)
        lead.update_fields(data_model)
        lead.save()
