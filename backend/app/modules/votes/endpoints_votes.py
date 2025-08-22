import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Sequence

from app.dependencies import get_db_session, get_settings, is_user
from app.modules.users import models_users
from app.modules.users.types_users import AccountType
from app.modules.votes import cruds_votes, models_votes, schemas_votes, types_votes
from app.types import standard_responses
from app.utils import mail
from app.utils.config import Settings
from app.utils.security import get_password_hash, verify_password
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

points_cimes_access_logger = logging.getLogger("points-cimes.access")

router = APIRouter(prefix="/votes", tags=["votes"])


@router.get(
    "/specific_vote",
    dependencies=[Depends(is_user(AccountType.admin))],
    response_model=schemas_votes.Vote,
)
async def get_specific_vote(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    specific_vote: schemas_votes.SpecificVote,
):
    vote = await cruds_votes.get_vote_by_report_and_user_id(
        db_session=db_session,
        user_id=specific_vote.user_id,
        report_id=specific_vote.report_id,
    )
    return vote


@router.get(
    "/{report_id}",
    response_model=schemas_votes.Vote,
)
async def get_my_vote(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[models_users.User, Depends(is_user())],
    report_id: uuid.UUID,
):
    vote = await cruds_votes.get_vote_by_report_and_user_id(
        db_session=db_session,
        user_id=user.id,
        report_id=report_id,
    )
    return vote


@router.put("/{report_id}", status_code=204)
async def upsert_my_vote(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[models_users.User, Depends(is_user())],
    report_id: uuid.UUID,
    vote_value: types_votes.VoteValue | None,
):
    existing_vote = await cruds_votes.get_vote_by_report_and_user_id(
        db_session=db_session, user_id=user.id, report_id=report_id
    )
    if not existing_vote:
        if vote_value:
            vote = models_votes.Vote(
                id=uuid.uuid4(),
                user_id=user.id,
                report_id=report_id,
                vote_value=vote_value,
            )
            await cruds_votes.create_vote(db_session=db_session, vote=vote)
            return
        else:
            return

    if existing_vote.vote_value == vote_value:
        return

    if not vote_value:
        await cruds_votes.delete_vote_by_report_and_user_id(
            db_session=db_session, user_id=user.id, report_id=report_id
        )
    else:
        await cruds_votes.update_vote_by_report_and_user_id(
            db_session=db_session,
            user_id=user.id,
            report_id=report_id,
            vote_value=vote_value,
        )
