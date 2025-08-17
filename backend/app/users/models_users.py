from datetime import datetime
from uuid import UUID

from app.types.sqlalchemy import Base
from app.users.types_users import AccountType
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool]
    account_type: Mapped[AccountType]
    name: Mapped[str]
    created_on: Mapped[datetime | None]


class UserUnconfirmed(Base):
    __tablename__ = "user_unconfirmed"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str]
    name: Mapped[str]
    password_hash: Mapped[str]
    activation_token: Mapped[str]
    created_on: Mapped[datetime]
    expire_on: Mapped[datetime]


class UserRecoverRequest(Base):
    __tablename__ = "user_recover_request"

    email: Mapped[str]
    user_id: Mapped[UUID]
    reset_token: Mapped[str] = mapped_column(primary_key=True)
    created_on: Mapped[datetime]
    expire_on: Mapped[datetime]
