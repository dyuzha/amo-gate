from typing import Self
from amocrm.v2 import custom_field as cf

from gate.transform.mc_models import MC
from .custom_lead import CustomLead


class MCLead(CustomLead):
    _configured: bool = False

    c_birthday: cf.DateCustomField
    c_treatments: cf.TextAreaCustomField
    c_labs: cf.TextAreaCustomField
    c_packets: cf.TextAreaCustomField
    c_complex: cf.TextAreaCustomField

    @classmethod
    def configure(
        cls,
        *,
        created_at: int,
        paid_price: int,
        zdrav_id: int,

        birthday: int,
        treatments: int,
        labs: int,
        packets: int,
        complex: int,
        ) -> type[Self]:

        if cls._configured:
            raise RuntimeError('BookedLead уже скофигурирован.')

        cls.c_created_at = cf.DateTimeCustomField('', field_id=created_at)
        cls.c_paid_price = cf.NumericCustomField('', field_id=paid_price)
        cls.c_zdrav_id = cf.TextCustomField('', field_id=zdrav_id)

        cls.c_birthday = cf.DateCustomField('', field_id=birthday)
        cls.c_treatments = cf.TextAreaCustomField('', field_id=treatments)
        cls.c_labs = cf.TextAreaCustomField('', field_id=labs)
        cls.c_packets = cf.TextAreaCustomField('', field_id=packets)
        cls.c_complex = cf.TextAreaCustomField('', field_id=complex)

        return cls


    def update_fields(self, data: MC):
        self.price = data.total_price
        self.c_paid_price = data.paid_price
        self.c_zdrav_id = str(data.id)
        self.c_created_at = data.created_at

        # self.c_birthday = data.birthday
        self.c_treatments = data.tretments_text
        self.c_labs = data.labs_text
        self.c_packets = data.packets_text
        self.c_complex = data.complex_text
