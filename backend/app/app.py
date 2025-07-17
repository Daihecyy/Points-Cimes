"""File defining the Metadata. And the basic functions creating the database tables and calling the router"""

import logging
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.utils.config import Settings
from app.utils.log import LogConfig
from app.dependencies import (
    init_and_get_db_engine,
)
from app.types.exceptions import ContentHTTPException
from app.utils import database


# NOTE: We can not get loggers at the top of this file like we do in other files
# as the loggers are not yet initialized


def init_db(
    settings: Settings,
    points_cimes_error_logger: logging.Logger,
    drop_db: bool = False,
) -> None:
    """
    Init the database by creating the tables and adding the necessary groups

    The method will use a synchronous engine to create the tables and add the groups
    """
    # Initialize the sync engine
    sync_engine = database.get_sync_db_engine(settings=settings)

    # Update database tables
    database.update_db_tables(
        sync_engine=sync_engine,
        points_cimes_error_logger=points_cimes_error_logger,
        drop_db=drop_db,
    )


# We wrap the application in a function to be able to pass the settings and drop_db parameters
# The drop_db parameter is used to drop the database tables before creating them again
def get_application(settings: Settings, drop_db: bool = False) -> FastAPI:
    # Initialize loggers
    LogConfig().initialize_loggers(settings=settings)

    points_cimes_access_logger = logging.getLogger("points-cimes.access")
    points_cimes_security_logger = logging.getLogger("points-cimes.security")
    points_cimes_error_logger = logging.getLogger("points-cimes.error")

    # Create folder for calendars if they don't already exists
    Path("data/ics/").mkdir(parents=True, exist_ok=True)
    Path("data/core/").mkdir(parents=True, exist_ok=True)

    # Creating a lifespan which will be called when the application starts then shuts down
    # https://fastapi.tiangolo.com/advanced/events/
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        yield
        points_cimes_error_logger.info("Shutting down")

    # Initialize app
    app = FastAPI(
        title="Points Cimes",
        version=settings.POINTS_CIMES_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.INIT_DB:
        init_db(
            settings=settings,
            points_cimes_error_logger=points_cimes_error_logger,
            drop_db=drop_db,
        )
    else:
        points_cimes_error_logger.info("Database initialization skipped")

    # We need to init the database engine to be able to use it in dependencies
    init_and_get_db_engine(settings)

    @app.middleware("http")
    async def logging_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        This middleware is called around each request.
        It logs the request and inject a unique identifier in the request that should be used to associate logs saved during the request.
        """
        # We use a middleware to log every request
        # See https://fastapi.tiangolo.com/tutorial/middleware/

        # We generate a unique identifier for the request and save it as a state.
        # This identifier will allow combining logs associated with the same request
        # https://www.starlette.io/requests/#other-state
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # This should never happen, but we log it just in case
        if request.client is None:
            points_cimes_security_logger.warning(
                f"Client information not available for {request.url.path}",
            )
            raise HTTPException(status_code=400, detail="No client information")

        ip_address = request.client.host
        port = request.client.port
        client_address = f"{ip_address}:{port}"

        process = True
        if process:
            response = await call_next(request)

            points_cimes_access_logger.info(
                f'{client_address} - "{request.method} {request.url.path}" {response.status_code} ({request_id})',
            )
        else:
            response = Response(status_code=429, content="Too Many Requests")
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        # We use a Debug logger to log the error as personal data may be present in the request
        points_cimes_error_logger.debug(
            f"Validation error: {exc.errors()} ({request.state.request_id})",
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    @app.exception_handler(ContentHTTPException)
    async def auth_exception_handler(
        request: Request,
        exc: ContentHTTPException,
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.content),
            headers=exc.headers,
        )

    return app
