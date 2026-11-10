from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase_auth import User

from app.auth.dependencies import bearer, get_current_user
from app.database.supabase import user_client

router = APIRouter(prefix="/auth", tags=["auth"])


class CurrentUser(BaseModel):
    id: UUID
    email: str | None
    application_user_exists: bool


@router.get("/me")
async def me(
    response: Response,
    user: Annotated[User, Depends(get_current_user)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
) -> CurrentUser:
    async with user_client(credentials.credentials) as client:
        result = await client.table("users").select("id").eq("id", user.id).limit(1).execute()

    response.headers["Cache-Control"] = "no-store"
    return CurrentUser(
        id=UUID(user.id), email=user.email, application_user_exists=bool(result.data),
    )
