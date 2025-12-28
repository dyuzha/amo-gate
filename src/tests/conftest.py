import logging
from pathlib import Path
import pytest
from amocrm.v2 import tokens
from gate.amo.amo_register import amo_register
from gate.settings.config import register_settings


# Настройка логирования для всех тестов
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def root_path() -> Path:
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def test_data_path(root_path) -> Path:
    return root_path / "src" / "tests" / "data"


@pytest.fixture(scope="session")
def settings(root_path: Path):
    """Загружает настройки AmoCRM"""
    return register_settings(root_path)


@pytest.fixture(scope="session")
def token_manager(settings, root_path: Path):
    """Инициализирует менеджер токенов AmoCRM"""
    amo_settings = settings.amo_settings
    tokens.default_token_manager(
        client_id=amo_settings.client_id,
        client_secret=amo_settings.client_secret,
        subdomain=amo_settings.subdomain,
        redirect_url=amo_settings.redirect_url,
        storage=tokens.FileTokensStorage(str(root_path / ".tokens")),
    )
    return tokens.default_token_manager


@pytest.fixture(scope="session")
def amo_client(root_path: Path, settings):
    """Создаёт AmoClient с реальной авторизацией."""
    return amo_register(
        tokens_path=root_path / ".tokens",
        mocked_lead_id=True,
        amo_settings=settings.amo,
        fields_settings=settings.fields,
        mock_pipeline_settings=settings.mock_pipeline,
        )
