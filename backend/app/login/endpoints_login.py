import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from app.dependencies import get_db_session, get_settings, is_user
from app.login import schemas_login
from app.login.schemas_login import Token
from app.types import standard_responses
from app.users import cruds_users, models_users, schemas_users
from app.users.types_users import AccountType
from app.utils import mail, security
from app.utils.config import Settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
async def login_access_token(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await security.authenticate_user(
        db_session=db_session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires, settings=settings
        )
    )


@router.post("/login/test-token", response_model=schemas_users.User)
def test_token(user: Annotated[models_users.User, is_user]) -> Any:
    """
    Test access token
    """
    return user


@router.post("/password-recovery/{email}")
async def recover_password(
    email: str,
    db_session: Annotated[AsyncSession, get_db_session],
    settings: Annotated[Settings, get_settings],
) -> standard_responses.Message:
    """
    Password Recovery
    """
    user = await cruds_users.get_user_by_email(db_session=db_session, email=email)

    if not user:
        # to prevent knowing which adresses are real
        return standard_responses.Message(message="Password recovery email sent")

    password_reset_token = mail.generate_mail_token(email=email, settings=settings)
    email_data = mail.generate_reset_password_email(
        email_to=user.email,
        email=email,
        token=password_reset_token,
        settings=settings,
    )
    mail.send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
        settings=settings,
    )
    return standard_responses.Message(message="Password recovery email sent")


@router.post("/verify-email/", response_model=standard_responses.Message)
async def verify_email(
    db_session: Annotated[AsyncSession, get_db_session],
    body: schemas_login.AccountActivation,
    settings: Annotated[Settings, get_settings],
):
    """
    Verify the email adress exists
    """
    unconfirmed_user = await cruds_users.get_unconfirmed_user_by_activation_token(
        db_session=db_session, activation_token=body.token
    )
    if not unconfirmed_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )

    if unconfirmed_user.expire_on > datetime.now(UTC):
        raise HTTPException(
            status_code=404,
            detail="Activation code expired",
        )

    existing_user = await cruds_users.get_user_by_email(
        db_session=db_session, email=unconfirmed_user.email
    )
    if existing_user:
        raise HTTPException(
            status_code=404, detail="A user with this email already exists"
        )

    user = models_users.User(
        id=uuid.uuid4(),
        email=unconfirmed_user.email,
        password_hash=unconfirmed_user.password_hash,
        is_active=True,
        account_type=AccountType.user,
        name=unconfirmed_user.name,
        created_on=unconfirmed_user.created_on,
    )
    await cruds_users.create_user(db_session=db_session, user=user)

    await cruds_users.delete_unconfirmed_user_by_email(
        db_session=db_session, email=user.email
    )

    return standard_responses.Message(message="Account successfully activated")


@router.post("/reset-password/")
async def reset_password(
    db_session: Annotated[AsyncSession, get_db_session],
    body: schemas_login.NewPassword,
    settings: Annotated[Settings, get_settings],
) -> standard_responses.Message:
    """
    Reset password
    """
    email = mail.verify_mail_token(token=body.token, settings=settings)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = await cruds_users.get_user_by_email(db_session=db_session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    hashed_password = security.get_password_hash(password=body.new_password)
    await cruds_users.update_user_password_by_id(
        db_session=db_session, user_id=user.id, new_password_hash=hashed_password
    )
    return standard_responses.Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(is_user(AccountType.admin))],
    response_class=HTMLResponse,
)
async def recover_password_html_content(
    email: str,
    db_session: Annotated[AsyncSession, get_db_session],
    settings: Annotated[Settings, get_settings],
) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = await cruds_users.get_user_by_email(db_session=db_session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = mail.generate_mail_token(email=email, settings=settings)
    email_data = mail.generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token, settings=settings
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
