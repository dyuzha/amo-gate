import pytest
from amocrm.v2 import Lead

from gate.amo.services import create_lead


pipline_id = 10156066 # Забронированно
status_id = 80453106 # Принимают решение


@pytest.mark.parametrize(
    "pipeline_id,status_id",
    [
        (pipline_id, None),
        (None, status_id),
        (None, None),
    ],
)
@pytest.mark.integration
def test_create_lead(pipeline_id, status_id, amo_client):
    """
    Интеграционный тест: создаём лид с pipeline_id, status_id и name.
    Проверяем, что объект реально создан в AmoCRM.
    """

    name = "Test Lead Integration"

    lead = create_lead(
        pipeline_id=pipeline_id,
        status_id=status_id,
        name=name
    )

    # Проверяем, что лид создался и имеет ID
    assert isinstance(lead, Lead)
    assert lead.id is not None
    print(f'{lead.id=}')
    print("Lead:", {k: lead._data.get(k) for k in lead._data})
    assert isinstance(lead.id, int)
