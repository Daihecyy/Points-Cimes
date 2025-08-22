import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Sequence

from app.dependencies import get_db_session, get_settings, is_user
from app.modules.users import cruds_users, models_users, schemas_users
from app.modules.users.types_users import AccountType
from app.types import standard_responses
from app.utils import mail
from app.utils.config import Settings
from app.utils.security import get_password_hash, verify_password
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

points_cimes_access_logger = logging.getLogger("points-cimes.access")

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(is_user(AccountType.admin))],
    response_model=Sequence[schemas_users.User],
)
async def read_users(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve users.
    """
    users = await cruds_users.get_users(db_session=db_session, skip=skip, limit=limit)
    return users


@router.post(
    "/",
    dependencies=[Depends(is_user(AccountType.admin))],
    response_model=schemas_users.User,
)
async def create_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user_in: schemas_users.UserCreateAdmin,
    settings: Annotated[Settings, Depends(get_settings)],
):
    """
    Create new user.
    """
    existing_user = await cruds_users.get_user_by_email(
        db_session=db_session, email=user_in.email
    )
    if existing_user:
        raise HTTPException(
            status_code=409, detail="User with this email already exists"
        )

    user = models_users.User(
        id=uuid.uuid4(),
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        account_type=user_in.account_type,
        name=user_in.name,
        created_on=datetime.now(UTC),
    )

    await cruds_users.create_user(db_session=db_session, user=user)

    if settings.emails_enabled and user_in.email:
        email_data = mail.generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
            settings=settings,
        )
        mail.send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            settings=settings,
        )
    return user


@router.patch("/me", status_code=204)
async def update_user_me(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user_update: schemas_users.UserUpdate,
    user: Annotated[models_users.User, Depends(is_user())],
):
    """
    Update own user.
    """

    # Allow email migrations without verification
    if user_update.email:
        existing_user = await cruds_users.get_user_by_email(
            db_session=db_session, email=user_update.email
        )
        if existing_user and existing_user.id != user.id:
            return

    await cruds_users.update_user(
        db_session=db_session,
        user_id=user.id,
        user_update=user_update,
    )


@router.post(
    "/me/make-admin",
    status_code=200,
)
async def make_admin(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[models_users.User, Depends(is_user())],
):
    """
    This endpoint is only usable if the database contains exactly one user.
    It will add this user to the `admin` group.
    """
    users_count = await cruds_users.count_users(db_session=db_session)

    if users_count != 1:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only usable if there is exactly one user in the database",
        )

    account_type_update = schemas_users.UserUpdateAdmin(account_type=AccountType.admin)
    await cruds_users.update_user(
        db_session=db_session, user_id=user.id, user_update=account_type_update
    )


@router.patch("/me/password", response_model=standard_responses.Message)
async def update_password_me(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    password_update: schemas_users.PasswordUpdate,
    user: Annotated[models_users.User, Depends(is_user())],
):
    """
    Update own password.
    """
    if not verify_password(password_update.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect password")

    if password_update.current_password == password_update.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )

    hashed_password = get_password_hash(password_update.new_password)
    await cruds_users.update_user_password_by_id(
        db_session=db_session, user_id=user.id, new_password_hash=hashed_password
    )
    return standard_responses.Message(message="Password updated successfully")


@router.get("/me", response_model=schemas_users.User)
def read_user_me(user: Annotated[models_users.User, Depends(is_user())]):
    """
    Get current user.
    """
    return user


@router.delete("/me", response_model=standard_responses.Message)
async def delete_user_me(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[models_users.User, Depends(is_user())],
):
    """
    Delete own user.
    """
    if user.account_type == AccountType.admin:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    await cruds_users.delete_user_by_id(db_session=db_session, user_id=user.id)
    return standard_responses.Message(message="User deleted successfully")


@router.post("/signup")
async def register_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user_create: schemas_users.UserCreateRequest,
    settings: Annotated[Settings, Depends(get_settings)],
):
    """
    Create new user without the need to be logged in.
    """
    user = await cruds_users.get_user_by_email(
        db_session=db_session, email=user_create.email
    )
    if user:
        return standard_responses.Message(message="Email was sent to the address")

    creation_time = datetime.now(UTC)
    activation_token = mail.generate_mail_token(
        email=user_create.email, settings=settings
    )
    points_cimes_access_logger.info(
        f"Activation token {activation_token} for {user_create.email}"
    )
    user_unconfirmed = models_users.UserUnconfirmed(
        id=uuid.uuid4(),
        name=user_create.name,
        email=user_create.email,
        password_hash=get_password_hash(user_create.password),
        activation_token=activation_token,
        created_on=creation_time,
        expire_on=creation_time + timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS),
    )
    await cruds_users.create_unconfirmed_user(
        db_session=db_session, user_unconfirmed=user_unconfirmed
    )
    if settings.emails_enabled:
        email_data = mail.generate_account_activation_email(
            email_to=user_create.email,
            username=user_create.name,
            token=activation_token,
            settings=settings,
        )
        mail.send_email(
            email_to=user_create.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
            settings=settings,
        )


@router.get(
    "/{user_id}",
    dependencies=[Depends(is_user(AccountType.admin))],
    response_model=schemas_users.User,
)
async def read_user_by_id(
    user_id: uuid.UUID,
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    """
    Get a specific user base by id.
    """
    user = await cruds_users.get_user_by_id(db_session=db_session, user_id=user_id)
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(is_user(AccountType.admin))],
    response_model=schemas_users.User,
)
async def update_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: uuid.UUID,
    user_update: schemas_users.UserUpdateAdmin,
):
    """
    Update a user.
    """

    user = await cruds_users.get_user_by_id(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    if user.id == user_id:
        raise HTTPException(
            status_code=409, detail="Admins must modify themselves as normal users"
        )

    if user_update.email:
        existing_user = await cruds_users.get_user_by_email(
            db_session=db_session, email=user_update.email
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_session_user = await cruds_users.update_user(
        db_session=db_session, user_id=user_id, user_update=user_update
    )
    return db_session_user


@router.delete("/{user_id}", dependencies=[])
async def delete_user(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: uuid.UUID,
    user: Annotated[models_users.User, Depends(is_user(AccountType.admin))],
) -> standard_responses.Message:
    """
    Delete a user.
    """
    db_user = await cruds_users.get_user_by_id(db_session=db_session, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == db_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )

    await cruds_users.delete_user_by_id(db_session=db_session, user_id=user_id)

    return standard_responses.Message(message="User deleted successfully")
