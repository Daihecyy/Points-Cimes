import json
from collections.abc import Sequence
from uuid import UUID

from app.reports import models_reports, schemas_reports, types_reports
from geoalchemy2 import WKTElement
from sqlalchemy import RowMapping, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

# ========================================
# REPORTS
# ========================================


async def create_report(db_session: AsyncSession, new_report: models_reports.Report):
    """Create a full report in db"""
    db_session.add(new_report)
    await db_session.commit()


async def get_report_by_id(
    report_id: UUID, db_session: AsyncSession
) -> models_reports.Report | None:
    """Get a report by its id"""
    result = await db_session.execute(
        select(models_reports.Report).where(models_reports.Report.id == report_id)
    )
    return result.scalars().first()


async def get_reports_in_location(
    db_session: AsyncSession, location: WKTElement
) -> Sequence[RowMapping]:
    """Get reports in a geometry"""
    result = await db_session.execute(
        select(
            models_reports.Report,
            models_reports.Report.location.ST_AsGeoJSON().label("location_geojson"),
        ).filter(models_reports.Report.location.ST_Intersects(location))
    )
    return result.mappings().all()


async def update_report_by_id(
    report_id: UUID,
    db_session: AsyncSession,
    report_edit: schemas_reports.ReportEdit,
):
    """Update a report in db"""
    await db_session.execute(
        update(models_reports.Report)
        .where(models_reports.Report.id == report_id)
        .values(**report_edit.model_dump(exclude_none=True)),
    )


async def update_report_status_by_id(
    report_id: UUID,
    db_session: AsyncSession,
    new_report_status: types_reports.ReportStatus,
):
    """Update the status of a report in db"""
    await db_session.execute(
        update(models_reports.Report)
        .where(models_reports.Report.id == report_id)
        .values(status=new_report_status),
    )


async def delete_report_by_id(report_id: UUID, db_session: AsyncSession):
    """Delete a report in db"""
    await db_session.execute(
        delete(models_reports.Report).where(models_reports.Report.id == report_id),
    )
