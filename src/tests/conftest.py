import logging
from pathlib import Path
import pytest
from amocrm.v2 import tokens
from gate.amo.amo_client import AmoClient
from gate.amo.amo_register import amo_register
from gate.settings.config import register_settings

# Настройка логирования для всех тестов
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Определяем пути
root_path = Path(__file__).parent.parent.parent
tokens_path = root_path / ".tokens"
tokens_path.parent.mkdir(exist_ok=True)

settings = register_settings(root_path)

amo_settings = settings.amo
app_settings = settings.app
mock_pipeline_settings = settings.mock_pipeline
booked_fields=settings.booked_fields
shared_fields=settings.shared_fields


@pytest.fixture(scope="session")
def amo_settings_fixture():
    """Загружает настройки AmoCRM для тестов."""
    return amo_settings


@pytest.fixture(scope="session")
def token_manager():
    """Инициализирует менеджер токенов AmoCRM."""
    tokens.default_token_manager(
        client_id=amo_settings.client_id,
        client_secret=amo_settings.client_secret,
        subdomain=amo_settings.subdomain,
        redirect_url=amo_settings.redirect_url,
        storage=tokens.FileTokensStorage(str(tokens_path)),
    )
    return tokens.default_token_manager


@pytest.fixture(scope="session")
def amo_client(token_manager, amo_settings_fixture):
    """Создаёт AmoClient с реальной авторизацией."""
    # return AmoClient(
    #         token_manager,
    #         amo_settings_fixture.auth_code,
    #         # booked_lead_cls=
    #         )
    return amo_register(
        tokens_path=tokens_path,
        mocked_lead_id=False,
        amo_settings=amo_settings,
        shared_fields=shared_fields,
        booked_fields=booked_fields,
        booked_id=mock_pipeline_settings.booked_id,
        booked_status_id=mock_pipeline_settings.booked_status_id,
        )
