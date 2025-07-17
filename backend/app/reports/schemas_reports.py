from datetime import datetime
from uuid import UUID

from geoalchemy2 import WKBElement
from pydantic import BaseModel

from app.reports.types_reports import ReportType


class ReportSimple(BaseModel):
    id: UUID
    title: str
    report_type: ReportType
    tags: list[str]
    vote_score: int
    location: WKBElement


class Report(ReportSimple):
    description: str
    creation_time: datetime


class Tags(BaseModel):
    id: UUID
    report_type: ReportType
    title: str
    description: str
    active: bool
