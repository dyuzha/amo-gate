from pathlib import Path
from amocrm.v2 import tokens

from gate.amo.models.booked_lead import BookedLead
from gate.amo.models.mc_lead import MCLead
from gate.amo.pipeline_manager import PipelineManager
from gate.transform.booked_models import Booked
from gate.transform.mc_models import MC

from .amo_client import AmoClient
from .mocker_lead_id import MockerLeadID


def amo_register(
        tokens_path: Path,
        mocked_lead_id: bool,
        *,
        amo_settings,
        fields_settings,
        mock_pipeline_settings,
        ):


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


    # Создаем mocker'ы
    booked_mocker = MockerLeadID(
            pipeline_id = mock_pipeline_settings.booked_id,
            status_id = mock_pipeline_settings.booked_status_id,
            name= 'Booked',
            )
    mc_mocker = MockerLeadID(
            pipeline_id = mock_pipeline_settings.mc_id,
            status_id = mock_pipeline_settings.mc_status_id,
            name= 'MC',
            )


    # Мапим поля
    BookedLead.configure(
            created_at=fields_settings.shared.created_at,
            paid_price=fields_settings.shared.paid_price,
            zdrav_id=fields_settings.shared.zdrav_id,

            status=fields_settings.booked.status,
            check_in=fields_settings.booked.check_in,
            check_out=fields_settings.booked.check_out,
            guests=fields_settings.booked.guests,
            doc_num=fields_settings.booked.doc_num,
            bill_data=fields_settings.booked.bill_data,
            )
    MCLead.configure(
            created_at=fields_settings.shared.created_at,
            paid_price=fields_settings.shared.paid_price,
            zdrav_id=fields_settings.shared.zdrav_id,

            birthday=fields_settings.mc.birthday,
            treatments=fields_settings.mc.treatments,
            labs=fields_settings.mc.labs,
            packets=fields_settings.mc.packets,
            complex=fields_settings.mc.complex,
            )


    booked_pl_manager = PipelineManager(
            mock_lead_id_factory=lambda lead_id: \
                    booked_mocker.get_mock(lead_id),
            lead_factory=lambda lead_id: \
                    BookedLead.objects.get(object_id=lead_id),
            data_model=Booked,
            )


    mc_pl_manager = PipelineManager(
            mock_lead_id_factory=lambda lead_id: \
                    mc_mocker.get_mock(lead_id),
            lead_factory=lambda lead_id: \
                    MCLead.objects.get(object_id=lead_id),
            data_model=MC,
            )


    amo_client = AmoClient(
            token_manager,
            amo_settings.auth_code,
            pipelines_data_map={
                'booked': booked_pl_manager,
                'mc': mc_pl_manager,
                },
            mocked_lead_id=mocked_lead_id,
            )

    return amo_client
