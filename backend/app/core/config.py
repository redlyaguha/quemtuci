"""Конфигурация приложения (pydantic-settings).

В production-режиме приложение не должно стартовать без TOKEN_ENCRYPTION_KEY.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/campus"
    elasticsearch_url: str = "http://localhost:9200"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change_me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    token_encryption_key: str | None = None

    mtuci_tech_base_url: str = "https://tech.mtuci.ru"
    mtuci_mock: bool = True

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def validate_production(self) -> None:
        """Падаем в production без ключа шифрования токена."""
        if self.app_env == "production" and not self.token_encryption_key:
            raise RuntimeError("TOKEN_ENCRYPTION_KEY обязателен в production-режиме")


settings = Settings()
settings.validate_production()
