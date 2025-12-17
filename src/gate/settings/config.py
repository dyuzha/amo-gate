import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


def register_settings(root_path: Path):
    env_path = os.getenv('ENV_FILE') or root_path / ".env"
    certs_path = root_path / ".certs"

    class ConfigBase(BaseSettings):
        """Базовый класс конфигурации"""
        model_config = SettingsConfigDict(
            env_file=env_path,
            env_file_encoding="utf-8",
            extra="ignore",
        )


    class AmoSettings(ConfigBase):
        model_config = SettingsConfigDict(env_prefix='AMO_')

        client_id: str
        client_secret: str
        subdomain: str
        redirect_url: str
        auth_code: str
        # auth_code: Optional[str] = None


    class MockPipelineSettings(ConfigBase):
        model_config = SettingsConfigDict(env_prefix='MOCK_PIPELINE_')

        booked_id: Optional[int] = None
        mc_id: Optional[int] = None
        booked_status_id: Optional[int] = None
        mc_status_id: Optional[int] = None


    class AppSettings(ConfigBase):
        model_config = SettingsConfigDict(env_prefix='APP_')

        incoming_mc: str = 'mc'
        incoming_booked: str = 'booked'
        ssl_key: Path = certs_path / "cert.key"
        ssl_cert: Path = certs_path / "fullchain.cer"
        log_dir: Path = root_path / 'logs'
        ssl_enabled: bool = False
        port: int = 5000
        host: str = "0.0.0.0"


    class SharedFieldMapping(ConfigBase):
        model_config = SettingsConfigDict(env_prefix='FIELD_SHARED_')

        created_at: int = 1287599
        paid_price: int = 1305167
        zdrav_id: int = 1305111


    class BookedFieldMapping(ConfigBase):
        model_config = SettingsConfigDict(env_prefix='FIELD_BOOKED_')

        status: int = 1304923
        check_in: int = 1305059
        check_out: int = 1305061
        guests: int = 1304335
        doc_num: int = 1305107
        bill_data: int = 1304929


    class Settings:
        app = AppSettings()
        mock_pipeline = MockPipelineSettings()
        amo = AmoSettings() # type: ignore[call-arg]
        booked_fields = BookedFieldMapping()
        shared_fields = SharedFieldMapping()

    return Settings
