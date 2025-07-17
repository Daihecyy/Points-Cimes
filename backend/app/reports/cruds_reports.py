from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.reports import models_reports


async def get_report_by_id(
    report_id: UUID, db_session: AsyncSession
) -> models_reports.Report | None:
    """Get a report by its id"""
    result = await db_session.execute(
        select(models_reports.Report).where(models_reports.Report.id == report_id)
    )
    return result.scalars().first()

async def get_reports_in_location()