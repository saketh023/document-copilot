import pytest
from pydantic import ValidationError

from app.config import Settings

VALID_SETTINGS = {
    "supabase_url": "https://example.supabase.co",
    "supabase_anon_key": "anon-key",
    "supabase_service_role_key": "service-role-key",
    "database_url": "postgresql://postgres:password@db.example.supabase.co/postgres",
    "openai_api_key": "openai-key",
    "allowed_origins": "http://localhost:5173, https://app.example.com",
}

REQUIRED_ENV_NAMES = (
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "ALLOWED_ORIGINS",
)


def test_settings_parse_allowed_origins() -> None:
    settings = Settings(**VALID_SETTINGS)

    assert [str(origin) for origin in settings.allowed_origins] == [
        "http://localhost:5173/",
        "https://app.example.com/",
    ]


def test_settings_fail_when_required_values_are_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in REQUIRED_ENV_NAMES:
        monkeypatch.delenv(name)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_empty_allowed_origins() -> None:
    with pytest.raises(ValidationError, match="at least one allowed origin"):
        Settings(**(VALID_SETTINGS | {"allowed_origins": " , "}))
