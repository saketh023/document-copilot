from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth import User
from supabase_auth.errors import AuthApiError

from app.database.supabase import user_client

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    """Verify the bearer token with Supabase Auth and return its user."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or not credentials.credentials.strip():
        raise unauthorized

    async with user_client(credentials.credentials) as client:
        try:
            response = await client.auth.get_user(credentials.credentials)
        except AuthApiError as exc:
            # Service failures must not masquerade as invalid credentials.
            if exc.status not in (400, 401, 403):
                raise
            raise unauthorized from exc

    if response is None:
        raise unauthorized
    return response.user
