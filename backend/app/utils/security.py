from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from app.users import cruds_users, models_users
from app.utils.config import Settings
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any, expires_delta: timedelta, settings: Settings
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def authenticate_user(
    db_session: AsyncSession,
    email: str,
    password: str,
) -> models_users.User | None:
    """
    Try to authenticate the user.
    If the user is unknown or the password is invalid return `None`. Else return the user's *User* representation.
    """
    user = await cruds_users.get_user_by_email(db_session=db_session, email=email)
    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
