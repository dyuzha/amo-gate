from typing import Optional
from pathlib import Path
from amocrm.v2 import tokens

from .amo_client import AmoClient
from .mocker_lead_id import MockerLeadID


def amo_register(
        tokens_path: Path,
        mocked_lead_id: bool,
        amo_settings,
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

    amo_client = AmoClient(
            token_manager,
            amo_settings.auth_code,
            mocked_lead_id=mocked_lead_id,
            mocker=booked_mocker,
            )

    return amo_client
