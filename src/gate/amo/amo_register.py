from typing import Optional
from pathlib import Path
from amocrm.v2 import tokens

from gate.amo.models.bookeed_lead import booked_lead_factory

from .amo_client import AmoClient
from .mocker_lead_id import MockerLeadID


def amo_register(
        tokens_path: Path,
        mocked_lead_id: bool,
        amo_settings,
        shared_fields,
        booked_fields,
        booked_id: Optional[int] = None,
        booked_status_id: Optional[int] = None,
        ):
    booked_mocker = None

    # Настраиваем токен менеджер
    tokens_path.mkdir(exist_ok=True)
    tokens.default_token_manager(
        client_id=amo_settings.client_id,
        client_secret=amo_settings.client_secret,
        subdomain=amo_settings.subdomain,
        redirect_url=amo_settings.redirect_url,
        storage=tokens.FileTokensStorage(str(tokens_path)),
    )
    token_manager = tokens.default_token_manager

    if mocked_lead_id:
        # Создаем mocker
        booked_mocker = MockerLeadID(
                pipeline_id = booked_id,
                status_id = booked_status_id,
                name_mocker= 'Booked',
                )

    # Мапим поля в BookedLead
    booked_lead_cls = booked_lead_factory(
            created_at=shared_fields.created_at,
            paid_price=shared_fields.paid_price,
            zdrav_id=shared_fields.zdrav_id,

            status=booked_fields.status,
            check_in=booked_fields.check_in,
            check_out=booked_fields.check_out,
            guests=booked_fields.guests,
            doc_num=booked_fields.doc_num,
            bill_data=booked_fields.bill_data,
            )

    amo_client = AmoClient(
            token_manager,
            amo_settings.auth_code,
            booked_lead_cls=booked_lead_cls,
            mocked_lead_id=mocked_lead_id,
            mocker=booked_mocker,
            )

    return amo_client
