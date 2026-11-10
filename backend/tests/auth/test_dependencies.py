import httpx
import pytest
from fastapi.testclient import TestClient

from app.database import supabase
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize("authorization", [None, "Basic abc", "Bearer", "Bearer   "])
def test_missing_bearer_token_is_rejected(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, authorization: str | None,
) -> None:
    def unexpected_client(token: str) -> None:
        pytest.fail("Missing credentials must not reach Supabase")

    monkeypatch.setattr("app.auth.dependencies.user_client", unexpected_client)
    headers = {"Authorization": authorization} if authorization is not None else {}

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    ("token", "auth_status", "payload", "expected_status"),
    [
        (
            "valid-token", 200,
            {
                "id": "cc988569-8a9b-4eda-9402-c2307d640382",
                "email": "analyst@example.com",
                "aud": "authenticated",
                "app_metadata": {},
                "user_metadata": {},
                "created_at": "2026-11-08T00:00:00Z",
            },
            200,
        ),
        ("invalid-token", 401, {"code": "bad_jwt", "msg": "Invalid JWT"}, 401),
        ("expired-token", 403, {"code": "bad_jwt", "msg": "JWT expired"}, 401),
        ("malformed-token", 400, {"code": "bad_jwt", "msg": "Malformed JWT"}, 401),
        ("valid-token", 503, {"msg": "Service unavailable"}, 500),
    ],
)
@pytest.mark.parametrize("user_exists", [True, False])
def test_token_is_verified_with_supabase(
    client: TestClient, monkeypatch: pytest.MonkeyPatch,
    token: str, auth_status: int, payload: dict, expected_status: int,
    user_exists: bool,
) -> None:
    requests: list[httpx.Request] = []
    connections: list[httpx.AsyncClient] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/rest/v1/users":
            assert request.url.params["id"] == f"eq.{payload['id']}"
            return httpx.Response(200, json=[{"id": payload["id"]}] if user_exists else [])
        return httpx.Response(auth_status, json=payload)

    def http_client() -> httpx.AsyncClient:
        connection = httpx.AsyncClient(transport=httpx.MockTransport(respond))
        connections.append(connection)
        return connection

    monkeypatch.setattr(supabase, "AsyncHttpClient", http_client)
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == expected_status
    assert requests[0].method == "GET"
    assert requests[0].url.path == "/auth/v1/user"
    assert requests[0].headers["authorization"] == f"Bearer {token}"
    assert all(connection.is_closed for connection in connections)
    if expected_status == 200:
        assert response.json() == {
            "id": payload["id"], "email": payload["email"],
            "application_user_exists": user_exists,
        }
        assert response.headers["cache-control"] == "no-store"
        assert len(requests) == 2
        assert requests[1].headers["authorization"] == f"Bearer {token}"
    elif expected_status == 401:
        assert response.headers["www-authenticate"] == "Bearer"
        assert token not in response.text
        assert len(requests) == 1
