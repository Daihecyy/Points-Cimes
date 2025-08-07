from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from app.reports.types_reports import ReportType
from geoalchemy2 import WKBElement
from geoalchemy2.types import Geometry
from pydantic import BaseModel


class ReportSimple(BaseModel):
    id: UUID
    title: str
    report_type: ReportType
    location: Dict[str, Any]


class Location(BaseModel):
    text: str


class Report(ReportSimple):
    description: str
    creation_time: datetime
    last_updated_time: datetime | None


class ReportCreation(BaseModel):
    title: str
    report_type: ReportType
    location: Dict[str, Any]
    description: str


class ReportEdit(BaseModel):
    title: str | None
    report_type: ReportType | None
    location: Dict[str, Any] | None
    description: str | None
    last_updated_time: datetime
