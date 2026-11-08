from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from httpx import AsyncClient as AsyncHttpClient
from supabase import AsyncClient, AsyncClientOptions, acreate_client

from app.config import settings


@asynccontextmanager
async def user_client(access_token: str) -> AsyncIterator[AsyncClient]:
    """Use a verified user's raw access token for RLS-scoped operations."""
    if not access_token.strip():
        raise ValueError("A user access token is required")

    async with AsyncHttpClient() as http_client:
        client = await acreate_client(
            str(settings.supabase_url),
            settings.supabase_anon_key.get_secret_value(),
            options=AsyncClientOptions(
                headers={"Authorization": f"Bearer {access_token}"},
                auto_refresh_token=False,
                persist_session=False,
                httpx_client=http_client,
            ),
        )
        yield client


@asynccontextmanager
async def service_role_client() -> AsyncIterator[AsyncClient]:
    """Use privileged backend access; callers must enforce authorization."""
    async with AsyncHttpClient() as http_client:
        client = await acreate_client(
            str(settings.supabase_url),
            settings.supabase_service_role_key.get_secret_value(),
            options=AsyncClientOptions(
                auto_refresh_token=False,
                persist_session=False,
                httpx_client=http_client,
            ),
        )
        yield client
