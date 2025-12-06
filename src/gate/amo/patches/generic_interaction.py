from amocrm.v2.interaction import GenericInteraction

# оригинальный метод
_original_update = GenericInteraction.update

def _clean_cf(data: dict):
    cfs = data.get("custom_fields_values", [])
    for cf in cfs:
        cf.pop("is_computed", None)
    return data

def patched_update(self, object_id, data=None, **kwargs):
    if data:
        data = _clean_cf(data)
    return _original_update(self, object_id, data, **kwargs)


GenericInteraction.update = patched_update
