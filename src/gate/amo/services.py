import logging
from typing import Any, Optional

from amocrm.v2 import Lead
from amocrm.v2.exceptions import NotFound


logger = logging.getLogger(__name__)


def create_lead(
        pipeline_id: Optional[int] = None,
        status_id: Optional[int] = None,
        name: Optional[str] = None,
        ):
    args: dict[str, Any] = {}

    logger.debug(
            'Создание лида с параметрами: '
            f'ID воронки={pipeline_id if pipeline_id else "Не задано"}, '
            f'ID этапа={status_id if status_id else "Не задано"}, '
            f'Имя={name}.'
            )

    if pipeline_id is not None:
        args.update(pipeline_id=pipeline_id)

    if name is not None:
        args.update(name=name)

    if status_id is not None:
        args.update(status_id=status_id)

    lead = Lead.objects.create(**args)

    return lead


def check_lead(id) -> bool:
    try:
        Lead.objects.get(object_id=id)
        return True
    except NotFound:
        return False
