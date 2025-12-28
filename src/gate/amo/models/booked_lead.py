from typing import Self
from amocrm.v2 import custom_field as cf

from gate.transform.booked_models import Booked
from .custom_lead import CustomLead


class BookedLead(CustomLead):
    _configured: bool = False

    c_status: cf.TextCustomField
    c_check_in: cf.DateCustomField
    c_check_out: cf.DateCustomField
    c_guests: cf.TextAreaCustomField
    c_doc_num: cf.NumericCustomField
    c_bill_data: cf.TextAreaCustomField

    @classmethod
    def configure(
        cls,
        *,
        created_at: int,
        paid_price: int,
        zdrav_id: int,

        status: int,
        check_in: int,
        check_out: int,
        guests: int,
        doc_num: int,
        bill_data: int,
        ) -> type[Self]:

        if cls._configured:
            raise RuntimeError('BookedLead уже скофигурирован.')


        cls.c_created_at = cf.DateTimeCustomField('', field_id=created_at)
        cls.c_paid_price = cf.NumericCustomField('', field_id=paid_price)
        cls.c_zdrav_id = cf.TextCustomField('', field_id=zdrav_id)

        cls.c_status = cf.TextCustomField('', field_id=status)
        cls.c_check_in = cf.DateCustomField('', field_id=check_in)
        cls.c_check_out = cf.DateCustomField('', field_id=check_out)
        cls.c_guests = cf.TextAreaCustomField('', field_id=guests)
        cls.c_doc_num = cf.NumericCustomField('', field_id=doc_num)
        cls.c_bill_data = cf.TextAreaCustomField('', field_id=bill_data)

        return cls


    def update_fields(self, data: Booked):
        self.price = data.money.total
        self.c_created_at = data.bookedAt
        self.c_paid_price = data.money.paid
        self.c_zdrav_id = str(data.id)

        self.c_status = data.status
        self.c_check_in = data.checkin
        self.c_check_out = data.checkout
        self.c_guests = data.extDataText
        self.c_doc_num = data.docNum
        self.c_bill_data = data.billDataText
