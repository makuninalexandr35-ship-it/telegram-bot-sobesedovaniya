from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: SecretStr
    openai_api_key: SecretStr
    openai_model: str = "gpt-4o-mini"
    database_url: str
    redis_url: str
    admin_telegram_ids: frozenset[int] = Field(default_factory=frozenset)
    log_level: str = "INFO"
    free_interviews_per_month: int = 3
    max_upload_bytes: int = 5 * 1024 * 1024
    max_resume_chars: int = 30_000
    max_vacancy_chars: int = 20_000
    ai_timeout_seconds: float = 45
    ai_retries: int = 1
    model_input_price_per_million: float = 0
    model_output_price_per_million: float = 0

    @field_validator("admin_telegram_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: object) -> object:
        if isinstance(value, str):
            return frozenset(int(item.strip()) for item in value.split(",") if item.strip())
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

