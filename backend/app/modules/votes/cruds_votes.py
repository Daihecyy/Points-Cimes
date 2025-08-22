from uuid import UUID

from app.modules.votes import models_votes
from app.modules.votes.types_votes import VoteValue
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def create_vote(
    db_session: AsyncSession, vote: models_votes.Vote
) -> models_votes.Vote | None:
    await db_session.add(vote)
    await db_session.commit()


async def get_vote_by_report_and_user_id(
    db_session: AsyncSession, user_id: UUID, report_id: UUID
) -> models_votes.Vote | None:
    result = await db_session.execute(
        select(models_votes.Vote).where(
            models_votes.Vote.user_id == user_id,
            models_votes.Vote.report_id == report_id,
        )
    )
    return result.scalars().first()


async def update_vote_by_report_and_user_id(
    db_session: AsyncSession, user_id: UUID, report_id: UUID, vote_value: VoteValue
) -> models_votes.Vote | None:
    await db_session.execute(
        update(models_votes.Vote)
        .where(
            models_votes.Vote.user_id == user_id,
            models_votes.Vote.report_id == report_id,
        )
        .values({"vote_value": vote_value})
    )
    await db_session.commit()


async def delete_vote_by_report_and_user_id(
    db_session: AsyncSession, user_id: UUID, report_id: UUID
) -> models_votes.Vote | None:
    await db_session.execute(
        delete(models_votes.Vote).where(
            models_votes.Vote.user_id == user_id,
            models_votes.Vote.report_id == report_id,
        )
    )
    await db_session.commit()
