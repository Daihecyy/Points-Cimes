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
from typing import cast

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.utils.config import Settings, construct_prod_settings

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
