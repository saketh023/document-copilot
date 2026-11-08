from sqlalchemy import Column, MetaData, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase

auth_users = Table(
    "users",
    MetaData(schema="auth"),
    Column("id", UUID(as_uuid=True), primary_key=True),
)


class Base(DeclarativeBase):
    """Base class for application database models."""
