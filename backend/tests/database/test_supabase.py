import asyncio

import httpx
import pytest

from app.config import Settings
from app.database import supabase


def test_clients_send_isolated_credentials_and_close_connections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        supabase,
        "settings",
        Settings(
            _env_file=None,
            supabase_url="https://example.supabase.co",
            supabase_anon_key="test-anon",
            supabase_service_role_key="test-service",
        ),
    )
    requests: list[httpx.Request] = []
    connections: list[httpx.AsyncClient] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=[])

    def http_client() -> httpx.AsyncClient:
        client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        connections.append(client)
        return client

    monkeypatch.setattr(supabase, "AsyncHttpClient", http_client)

    async def run() -> None:
        async with (
            supabase.user_client("user-one") as first,
            supabase.user_client("user-two") as second,
            supabase.service_role_client() as service,
        ):
            await first.table("chat_threads").select("id").execute()
            await second.table("chat_threads").select("id").execute()
            await service.table("source_documents").select("id").execute()
            await first.table("chat_threads").select("id").execute()

    asyncio.run(run())

    assert [request.headers["authorization"] for request in requests] == [
        "Bearer user-one",
        "Bearer user-two",
        "Bearer test-service",
        "Bearer user-one",
    ]
    assert [request.headers["apikey"] for request in requests] == [
        "test-anon", "test-anon", "test-service", "test-anon"
    ]
    assert all(connection.is_closed for connection in connections)


def test_user_client_requires_a_token() -> None:
    async def run() -> None:
        with pytest.raises(ValueError, match="access token"):
            async with supabase.user_client(" "):
                pytest.fail("An empty token must not create a client")

    asyncio.run(run())


def test_user_client_closes_connections_on_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    connection = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=[])
    ))
    monkeypatch.setattr(supabase, "AsyncHttpClient", lambda: connection)

    async def run() -> None:
        with pytest.raises(RuntimeError, match="operation failed"):
            async with supabase.user_client("user-token"):
                raise RuntimeError("operation failed")

    asyncio.run(run())
    assert connection.is_closed
