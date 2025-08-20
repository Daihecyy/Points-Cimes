import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from app.dependencies import get_db_session
from app.modules.reports import (
    cruds_reports,
    models_reports,
    schemas_reports,
    types_reports,
)
from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import WKBElement, WKTElement
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/reports", tags=["reports"])

points_cimes_error_logger = logging.getLogger("points-cimes.error")


@router.get("/types")
async def get_report_types():
    return [*types_reports.ReportType]


@router.get("/statuses")
async def get_report_statuses():
    return [*types_reports.ReportStatus]


@router.patch("/{report_id}/status", status_code=204)
async def change_report_status(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    report_id: UUID,
    new_status: types_reports.ReportStatus,
):
    report = await cruds_reports.get_report_by_id(
        db_session=db_session, report_id=report_id
    )
    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    await cruds_reports.update_report_status_by_id(
        db_session=db_session,
        report_id=report_id,
        new_report_status=new_status,
    )


@router.patch("/{report_id}", status_code=204)
async def edit_report(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    report_id: UUID,
    report_edit: schemas_reports.ReportEdit,
):
    report = await cruds_reports.get_report_by_id(
        db_session=db_session, report_id=report_id
    )
    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    await cruds_reports.update_report_by_id(
        db_session=db_session, report_id=report_id, report_edit=report_edit
    )


@router.delete("/{report_id}", status_code=204)
async def delete_report(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    report_id: UUID,
):
    report = await cruds_reports.get_report_by_id(
        db_session=db_session, report_id=report_id
    )
    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )

    await cruds_reports.delete_report_by_id(
        db_session=db_session,
        report_id=report_id,
    )


@router.get("/")
async def get_reports_in_location(
    db_session: Annotated[AsyncSession, Depends(get_db_session)], location_text: str
):
    location = WKTElement(location_text, srid=models_reports.SRID)
    data = await cruds_reports.get_reports_in_location(
        db_session=db_session, location=location
    )
    data = [
        schemas_reports.ReportSimple(
            id=item["Report"].id,
            title=item["Report"].title,
            report_type=item["Report"].report_type,
            location=json.loads(item["location_geojson"]),
        )
        for item in data
    ]

    return data


@router.post("/")
async def create_report(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    report_creation: schemas_reports.ReportCreation,
):
    report_id = uuid.uuid4()
    creation_time = datetime.now(UTC)
    report = models_reports.Report(
        id=report_id,
        title=report_creation.title,
        location=WKBElement(report_creation.location, srid=models_reports.SRID),
        report_type=report_creation.report_type,
        description=report_creation.description,
        creation_time=creation_time,
        status=types_reports.ReportStatus.ACTIVE,
    )
    await cruds_reports.create_report(db_session=db_session, new_report=report)
    report = await cruds_reports.get_report_by_id(
        db_session=db_session, report_id=report_id
    )
    return report


@router.get("/{report_id}", response_model=schemas_reports.Report)
async def get_report_by_id(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    report_id: UUID,
):
    report_row = await cruds_reports.get_report_by_id(
        db_session=db_session, report_id=report_id
    )
    if report_row is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found",
        )
    return {
        **report_row["Report"].__dict__,  # Unpack the attributes from the Report object
        "latitude": report_row["latitude"],
        "longitude": report_row["longitude"],
    }
