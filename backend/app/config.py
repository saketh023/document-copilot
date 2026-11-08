from typing import Annotated

from pydantic import AnyHttpUrl, Field, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    supabase_url: AnyHttpUrl
    supabase_anon_key: SecretStr
    supabase_service_role_key: SecretStr

    database_url: PostgresDsn

    openai_api_key: SecretStr
    openai_embedding_model: str = "text-embedding-3-small"
    openai_embedding_dimensions: int = Field(default=1536, gt=0)

    allowed_origins: Annotated[list[AnyHttpUrl], NoDecode]

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        return [origin.strip() for origin in value.split(",") if origin.strip()]

    @field_validator("allowed_origins")
    @classmethod
    def require_allowed_origin(cls, value: list[AnyHttpUrl]) -> list[AnyHttpUrl]:
        if not value:
            raise ValueError("at least one allowed origin is required")
        return value

    @field_validator(
        "supabase_anon_key",
        "supabase_service_role_key",
        "openai_api_key",
    )
    @classmethod
    def require_nonempty_secret(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("secret cannot be empty")
        return value

    @field_validator("openai_embedding_model")
    @classmethod
    def require_nonempty_model(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("embedding model cannot be empty")
        return value

settings = Settings()
