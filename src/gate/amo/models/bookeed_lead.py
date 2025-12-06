import logging
from typing import Optional, Self
from amocrm.v2 import custom_field as cf

from gate.transform.booked_models import Booking
from .custom_lead import CustomLead
from amocrm.v2.exceptions import NotFound


logger = logging.getLogger(__name__)


class BookedLead(CustomLead):
    c_status = cf.SelectCustomField('', field_id=1304923)
    c_check_in = cf.DateCustomField('', field_id=1305059)
    c_check_out = cf.DateCustomField('', field_id=1305061)
    c_guests = cf.TextAreaCustomField('', field_id=1304335)
    c_doc_num = cf.NumericCustomField('', field_id=1305107)
    c_bill_data = cf.TextAreaCustomField('', field_id=1304929)


    @classmethod
    def load_model(cls, booking: Booking) -> Optional[Self]:
        lead_id = booking.lead_id
        try:
            lead = cls.objects.get(object_id=lead_id)

        except NotFound as e:
            logger.error(f'Лид с lead_id={lead_id} не найден в AmoCRM! {e}')
            return None

        except Exception as e:
            logger.error(f'Лид с lead_id={lead_id} не найден в AmoCRM!, {e}')
            return None

        try:
            lead.update_fields(booking)
        except Exception as e:
            logging.error(
                'Не удалось изменить параметры в АмоСРМ для лида с '
                f'lead_id: "{booking.lead_id}", ОШИБКА: {e}'
                )
            raise e

        return lead


    def update_fields(self, booking: Booking):
        self.price = booking.money.total
        self.c_created_at = booking.bookedAt
        self.c_paid_price = booking.money.paid
        self.c_zdrav_id = booking.id

        self.c_status = booking.status
        self.c_check_in = booking.checkin
        self.c_check_out = booking.checkout
        self.c_guests = booking.extDataText
        self.c_doc_num = booking.docNum
        self.c_bill_data = booking.billDataText
