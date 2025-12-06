from amocrm.v2 import custom_field

# сохраняем оригинальный __init__
_original_init = custom_field.BaseCustomField.__init__

# новая версия с name=None по умолчанию
def _patched_init(
        self,
        name=None,
        code=None,
        auto_create=False,
        field_id=None,
        **kwargs
        ):
    return _original_init(
            self,
            name,
            code=code,
            auto_create=auto_create,
            field_id=field_id,
            **kwargs
            )

def _get_raw_field(self, data):
    if data is None:
        return None
    for field in data:
        if self._field_id and field.get("field_id") == self._field_id:
            return field
        if self._name and field.get("field_name") == self._name:
            return field
        if self._code and field.get("field_code") == self._code:
            return field
    return None

def _create_raw_field(self):
    _data = {"field_id": self._field_id, "values": []}
    if self._code:
        _data["field_code"] = self._code
    if self._name:  # только если имя задано
        _data["field_name"] = self._name
    return _data


# применяем патч
custom_field.BaseCustomField.__init__ = _patched_init
custom_field.BaseCustomField._get_raw_field = _get_raw_field
custom_field.BaseCustomField._create_raw_field = _create_raw_field
