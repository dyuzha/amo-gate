import logging
from typing import Optional, Self
from amocrm.v2 import custom_field as cf

from gate.transform.booked_models import Booking
from .custom_lead import CustomLead
from amocrm.v2.exceptions import NotFound


logger = logging.getLogger(__name__)

def booked_lead_factory(
        created_at: int,
        paid_price: int,
        zdrav_id: int,
        status: int,
        check_in: int,
        check_out: int,
        guests: int,
        doc_num: int,
        bill_data: int,
        ):
    """Возвращает класс BookedLead с зарегестрированными полями"""

    class BookedLead(CustomLead):
        c_created_at = cf.DateTimeCustomField('', field_id=created_at)
        c_paid_price = cf.NumericCustomField('', field_id=paid_price)
        c_zdrav_id = cf.NumericCustomField('', field_id=zdrav_id)

        c_status = cf.TextCustomField('', field_id=status)
        c_check_in = cf.DateCustomField('', field_id=check_in)
        c_check_out = cf.DateCustomField('', field_id=check_out)
        c_guests = cf.TextAreaCustomField('', field_id=guests)
        c_doc_num = cf.NumericCustomField('', field_id=doc_num)
        c_bill_data = cf.TextAreaCustomField('', field_id=bill_data)


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

    return BookedLead
