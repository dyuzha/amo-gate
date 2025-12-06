from datetime import datetime, timedelta, timezone
from amocrm.v2 import custom_field


def on_set(self, value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone(timedelta(hours=3)))
        value = value.isoformat()
    return [{"value": value}]

custom_field.DateCustomField.on_set = on_set
