from abc import abstractmethod
from typing import Self
from amocrm.v2 import Lead, custom_field as cf


class CustomLead(Lead):
    c_created_at: cf.DateTimeCustomField
    c_paid_price: cf.NumericCustomField
    c_zdrav_id: cf.NumericCustomField

    @classmethod
    def get_lead(cls, lead_id: int) -> Self:
        return cls.objects.get(object_id=lead_id)

    @abstractmethod
    def update_fields(self, *args, **kwargs):
        return
