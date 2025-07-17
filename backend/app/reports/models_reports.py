from datetime import datetime
from uuid import UUID

from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.types.sqlalchemy import Base, PrimaryKey
from app.reports.types_reports import ReportStatus, ReportType, VoteValue


SRID = 4326


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[PrimaryKey]
    title: Mapped[str] = mapped_column(nullable=False)
    creation_time: Mapped[datetime]
    location: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=SRID), nullable=False
    )
    report_type: Mapped[ReportType]
    status: Mapped[ReportStatus]
    description: Mapped[str]
    votes: Mapped[list["ReportVote"]] = relationship(
        "ReportVote",
        lazy="selectin",
        default_factory=list,
    )
    vote_score: Mapped[int]
    tags: Mapped[list["ReportTag"]] = relationship(
        "ReportTag",
        lazy="selectin",
        default_factory=list,
    )

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Report(id='{self.id}', type='{self.report_type.value}', "
            f"status='{self.status.value}', owner_id='{1}')>"
            f"Vote score: {self.vote_score}"
        )

    def get_shapely_location(self):
        """Returns the location as a Shapely Point object."""
        if self.location:
            # When retrieved from DB, self.location will be a WKBElement
            return to_shape(self.location)
        return None


class ReportTag(Base):
    __tablename__ = "reports_tags"

    id: Mapped[PrimaryKey]
    report_type: Mapped[ReportType]
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str]
    active: Mapped[bool]


class ReportVote(Base):
    __tablename__ = "reports_votes"

    id = Mapped[PrimaryKey]
    report_id: Mapped[UUID] = mapped_column(ForeignKey("report.id"))
    vote_value: Mapped[VoteValue]
