import logging
from typing import Any, Optional
from amocrm.v2 import Lead
from gate.amo.services import create_lead
from gate.utils.prefix_logger_adapter import PrefixAdapter


base_logger = logging.getLogger(__name__)


class LeadIDError(KeyError):
    pass


class MockerLeadID:
    def __init__(
            self,
            pipeline_id: Optional[int] = None,
            status_id: Optional[int] = None,
            lead_name_prefix: str = 'ID_',
            name: str = 'Mocker'
            ):
        self.pipeline_id = pipeline_id
        self.status_id = status_id
        self.prefix = lead_name_prefix
        self.logger = PrefixAdapter(base_logger, name)
        self.logger.info('Мокер успешно инициализирован.')


    def find_mock(self, mock_name) -> Optional[int]:
        try:
            lead = Lead.objects.get(query=mock_name)
            lead_id = lead.id
            self.logger.debug(
                    f'Найден "Мок лид" <name: {mock_name},'
                    f'lead_id: {lead_id}>'
                    )
            return lead_id

        except StopIteration:
            self.logger.debug(
                    f'"Мок лид" с name: {mock_name} не найден.'
                    )
            return None


    def get_mock(self, id) ->int:
        mock_name = f'{self.prefix}{id}'

        try:
            self.logger.debug('Ищем существующий мок...')
            lead_id = self.find_mock(mock_name)
            if lead_id is not None:
                self.logger.info(f'Мок {mock_name} успешно найден.')
                return lead_id

            self.logger.debug('Существующий мок не найден. Созадем мок...')
            lead = create_lead(self.pipeline_id, self.status_id, mock_name)
            lead_id = lead.id
            self.logger.info(f'Мок с {lead_id=} успешно создан')

        except Exception as e:
            raise e

        return lead_id

