"""
Various FastAPI [dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)

They are used in endpoints function signatures. For example:
```python
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
```
"""

import logging
from collections.abc import AsyncGenerator, Callable
from functools import lru_cache
from typing import Annotated, cast
from uuid import UUID

import jwt
from app.modules.login.schemas_login import TokenPayload
from app.modules.users import cruds_users, models_users
from app.modules.users.types_users import AccountType
from app.utils import security
from app.utils.config import Settings, construct_prod_settings
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

points_cimes_access_logger = logging.getLogger("points-cimes.access")
points_cimes_error_logger = logging.getLogger("points-cimes.error")

engine: AsyncEngine | None = (
    None  # Create a global variable for the database engine, so that it can be instancied in the startup event
)
SessionLocal: Callable[[], AsyncSession] | None = (
    None  # Create a global variable for the database session, so that it can be instancied in the startup event
)


async def get_request_id(request: Request) -> str:
    """
    The request identifier is a unique UUID which is used to associate logs saved during the same request
    """
    # `request_id` is a string injected in the state by our middleware
    # We force Mypy to consider it as a str instead of Any
    request_id = cast(str, request.state.request_id)

    return request_id


def init_and_get_db_engine(settings: Settings) -> AsyncEngine:
    """
    Return the (asynchronous) database engine, if the engine doesn't exit yet it will create one based on the settings
    """
    global engine
    global SessionLocal
    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

    if engine is None:
        engine = create_async_engine(
            SQLALCHEMY_DATABASE_URL,
            echo=settings.DATABASE_DEBUG,
        )
        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Return a database session
    """
    if SessionLocal is None:
        points_cimes_error_logger.error("Database engine is not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database engine is not initialized",
        )
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


@lru_cache
def get_settings() -> Settings:
    """
    Return a settings object, based on `.env` dotenv
    """
    # `lru_cache()` decorator is here to prevent the class to be instantiated multiple times.
    # See https://fastapi.tiangolo.com/advanced/settings/#lru_cache-technical-details
    return construct_prod_settings()


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")


async def get_current_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    token: Annotated[str, Depends(reusable_oauth2)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> models_users.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await cruds_users.get_user_by_id(
        db_session=db_session, user_id=UUID(token_data.sub)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


def is_user(
    account_type: AccountType | None = None,
) -> Callable[[models_users.User], models_users.User]:
    """
    A dependency that will:
        * check if the request header contains a valid API JWT token (a token that can be used to call endpoints from the API)
        * make sure the user making the request exists
        * verify the user has at least the right account type
    """
    account_type = account_type or AccountType.user

    def is_user(
        user: models_users.User = Depends(get_current_user),
    ) -> models_users.User:
        if user.account_type == AccountType.admin:
            return user
        if account_type == AccountType.admin:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized, user does not have admin permissions",
            )

        if user.account_type == AccountType.moderator:
            return user
        if account_type == AccountType.moderator:
            raise HTTPException(
                status_code=403,
                detail="Unauthorized, user does not have moderator permissions",
            )

        # else : user exists
        return user

    return is_user
