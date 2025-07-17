import logging
import alembic.command as alembic_command
import alembic.config as alembic_config
import alembic.migration as alembic_migration
from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.engine import Connection

from app.types.sqlalchemy import Base
from app.utils.config import Settings


def get_sync_db_engine(settings: Settings) -> Engine:
    """
    Create a synchronous database engine
    """
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"

    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=settings.DATABASE_DEBUG)
    return engine


def drop_db_sync(conn: Connection):
    """
    Drop all tables in the database
    """
    # All tables should be dropped, including the alembic_version table
    # or Points Cimes will think that the database is up to date and will not initialize it
    # when running tests a second time.
    # To let SQLAlchemy drop the alembic_version table, we created a AlembicVersion model.

    # `Base.metadata.drop_all(conn)` is only able to drop tables that are defined in models
    # This means that if a model is deleted, its table will never be dropped by `Base.metadata.drop_all(conn)`

    # Thus we construct a metadata object that reflects the database instead of only using models
    my_metadata: MetaData = MetaData(schema=Base.metadata.schema)
    my_metadata.reflect(bind=conn, resolve_fks=False)
    my_metadata.drop_all(bind=conn)


def get_alembic_config(connection: Connection) -> alembic_config.Config:
    """
    Return the alembic configuration object in a synchronous way
    """
    alembic_cfg = alembic_config.Config("alembic.ini")
    alembic_cfg.attributes["connection"] = connection

    return alembic_cfg


def get_alembic_current_revision(connection: Connection) -> str | None:
    """
    Return the current revision of the database in a synchronous way

    NOTE: SQLAlchemy does not support `Inspection on an AsyncConnection`. If you have an AsyncConnection, the call to this method must be wrapped in a `run_sync` call to obtain a Connection.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.
        Exemple usage:
        ```python
        async with engine.connect() as conn:
            await conn.run_sync(run_alembic_upgrade)
        ```
    """

    context = alembic_migration.MigrationContext.configure(connection)
    return context.get_current_revision()


def stamp_alembic_head(connection: Connection) -> None:
    """
    Stamp the database with the latest revision in a synchronous way

    NOTE: SQLAlchemy does not support `Inspection on an AsyncConnection`. If you have an AsyncConnection, the call to this method must be wrapped in a `run_sync` call to obtain a Connection.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.
        Exemple usage:
        ```python
        async with engine.connect() as conn:
            await conn.run_sync(run_alembic_upgrade)
        ```
    """
    alembic_cfg = get_alembic_config(connection)
    alembic_command.stamp(alembic_cfg, "head")


def run_alembic_upgrade(connection: Connection) -> None:
    """
    Run the alembic upgrade command to upgrade the database to the latest version (`head`) in a synchronous way

    WARNING: SQLAlchemy does not support `Inspection on an AsyncConnection`. The call to Alembic must be wrapped in a `run_sync` call.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.

    NOTE: SQLAlchemy does not support `Inspection on an AsyncConnection`. If you have an AsyncConnection, the call to this method must be wrapped in a `run_sync` call to obtain a Connection.
    See https://alembic.sqlalchemy.org/en/latest/cookbook.html#programmatic-api-use-connection-sharing-with-asyncio for more information.
        Exemple usage:
        ```python
        async with engine.connect() as conn:
            await conn.run_sync(run_alembic_upgrade)
        ```
    """

    alembic_cfg = get_alembic_config(connection)

    alembic_command.upgrade(alembic_cfg, "head")


def update_db_tables(
    sync_engine: Engine,
    points_cimes_error_logger: logging.Logger,
    drop_db: bool = False,
) -> None:
    """
    If the database is not initialized, create the tables and stamp the database with the latest revision.
    Otherwise, run the alembic upgrade command to upgrade the database to the latest version (`head`).

    if drop_db is True, we will drop all tables before creating them again

    This method requires a synchronous engine
    """

    try:
        # We have an Engine, we want to acquire a Connection
        with sync_engine.begin() as conn:
            if drop_db:
                drop_db_sync(conn)

            alembic_current_revision = get_alembic_current_revision(conn)

            if alembic_current_revision is None:
                # We generate the database using SQLAlchemy
                # in order not to have to run all migrations one by one
                # See https://alembic.sqlalchemy.org/en/latest/cookbook.html#building-an-up-to-date-database-from-scratch
                points_cimes_error_logger.info(
                    "Startup: Database tables not created yet, creating them",
                )

                # Create all tables
                Base.metadata.create_all(conn)
                # We stamp the database with the latest revision so that
                # alembic knows that the database is up to date
                stamp_alembic_head(conn)
            else:
                points_cimes_error_logger.info(
                    f"Startup: Database tables already created (current revision: {alembic_current_revision}), running migrations",
                )
                run_alembic_upgrade(conn)

            points_cimes_error_logger.info("Startup: Database tables updated")
    except Exception as error:
        points_cimes_error_logger.fatal(
            f"Startup: Could not create tables in the database: {error}",
        )
        raise
