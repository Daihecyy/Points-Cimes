from collections.abc import Sequence
from uuid import UUID

from app.users import models_users, schemas_users
from app.users.types_users import AccountType
from sqlalchemy import and_, delete, not_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def count_users(db_session: AsyncSession) -> int:
    """Return the number of users in the database"""

    result = await db_session.execute(select(models_users.User))
    return len(result.scalars().all())


async def get_users(
    db_session: AsyncSession, limit: int, skip: int
) -> Sequence[models_users.User]:
    result = await db_session.execute(
        select(models_users.User)
        .limit(limit)
        .offset(skip)
        .order_by(models_users.User.name)
    )
    return result.scalars().all()


async def get_users_by_account(
    db_session: AsyncSession,
    included_account_types: list[AccountType] | None = None,
    excluded_account_types: list[AccountType] | None = None,
) -> Sequence[models_users.User]:
    """
    Return all users from database.

    Parameters `excluded_account_types` and `excluded_groups` can be used to filter results.
    """
    included_account_types = included_account_types or None
    excluded_account_types = excluded_account_types or []

    included_account_type_condition = (
        or_(
            False,
            *[
                models_users.User.account_type == account_type
                for account_type in included_account_types
            ],
        )
        if included_account_types
        else and_(True)
    )
    excluded_account_type_condition = [
        not_(
            models_users.User.account_type == account_type,
        )
        for account_type in excluded_account_types
    ]

    result = await db_session.execute(
        select(models_users.User).where(
            and_(
                True,
                included_account_type_condition,
                *excluded_account_type_condition,
            ),
        ),
    )
    return result.scalars().all()


async def get_user_by_id(
    db_session: AsyncSession,
    user_id: UUID,
) -> models_users.User | None:
    """Return user with id from database as a dictionary"""

    result = await db_session.execute(
        select(models_users.User).where(models_users.User.id == user_id),
    )
    return result.scalars().first()


async def get_user_by_email(
    db_session: AsyncSession,
    email: str,
) -> models_users.User | None:
    """Return user with id from database as a dictionary"""

    result = await db_session.execute(
        select(models_users.User).where(models_users.User.email == email),
    )
    return result.scalars().first()


async def update_user(
    db_session: AsyncSession,
    user_id: UUID,
    user_update: schemas_users.UserUpdateAdmin | schemas_users.UserUpdate,
):
    await db_session.execute(
        update(models_users.User)
        .where(models_users.User.id == user_id)
        .values(**user_update.model_dump(exclude_none=True)),
    )


async def create_unconfirmed_user(
    db_session: AsyncSession,
    user_unconfirmed: models_users.UserUnconfirmed,
):
    """
    Create a new user in the unconfirmed database
    """

    db_session.add(user_unconfirmed)
    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise


async def get_unconfirmed_user_by_activation_token(
    db_session: AsyncSession,
    activation_token: str,
) -> models_users.UserUnconfirmed | None:
    result = await db_session.execute(
        select(models_users.UserUnconfirmed).where(
            models_users.UserUnconfirmed.activation_token == activation_token,
        ),
    )
    return result.scalars().first()


async def delete_unconfirmed_user_by_email(db_session: AsyncSession, email: str):
    """Delete a user from database by id"""

    await db_session.execute(
        delete(models_users.UserUnconfirmed).where(
            models_users.UserUnconfirmed.email == email,
        ),
    )
    await db_session.commit()


async def create_user(
    db_session: AsyncSession,
    user: models_users.User,
) -> models_users.User:
    db_session.add(user)
    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise
    else:
        return user


async def delete_user_by_id(db_session: AsyncSession, user_id: UUID):
    """Delete a user from database by id"""

    await db_session.execute(
        delete(models_users.User).where(models_users.User.id == user_id),
    )
    await db_session.commit()


async def create_user_recover_request(
    db_session: AsyncSession,
    recover_request: models_users.UserRecoverRequest,
) -> models_users.UserRecoverRequest:
    db_session.add(recover_request)
    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise
    else:
        return recover_request


async def get_recover_request_by_reset_token(
    db_session: AsyncSession,
    reset_token: str,
) -> models_users.UserRecoverRequest | None:
    result = await db_session.execute(
        select(models_users.UserRecoverRequest).where(
            models_users.UserRecoverRequest.reset_token == reset_token,
        ),
    )
    return result.scalars().first()


async def create_email_migration_code(
    migration_object: models_users.UserEmailMigrationCode,
    db_session: AsyncSession,
) -> models_users.UserEmailMigrationCode:
    db_session.add(migration_object)
    try:
        await db_session.commit()
    except IntegrityError:
        await db_session.rollback()
        raise
    else:
        return migration_object


async def delete_recover_request_by_email(db_session: AsyncSession, email: str):
    """Delete a user from database by id"""

    await db_session.execute(
        delete(models_users.UserRecoverRequest).where(
            models_users.UserRecoverRequest.email == email,
        ),
    )
    await db_session.commit()


async def update_user_password_by_id(
    db_session: AsyncSession,
    user_id: UUID,
    new_password_hash: str,
):
    await db_session.execute(
        update(models_users.User)
        .where(models_users.User.id == user_id)
        .values(password_hash=new_password_hash),
    )
    await db_session.commit()
