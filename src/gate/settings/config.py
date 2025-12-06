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

    class Settings:
        app = AppSettings()
        mock_pipeline = MockPipelineSettings()
        amo = AmoSettings() # type: ignore[call-arg]

    return Settings
