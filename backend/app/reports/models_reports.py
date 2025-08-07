from datetime import datetime

from app.reports.types_reports import ReportStatus, ReportType
from app.types.sqlalchemy import Base, PrimaryKey
from geoalchemy2 import Geometry, WKBElement
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Mapped, mapped_column

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

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"<Report(id='{self.id}', type='{self.report_type.value}', "
            f"status='{self.status.value}', owner_id='{1}')"
            f"location='{self.get_shapely_location()}'>"
        )

    def get_shapely_location(self):
        """Returns the location as a Shapely Point object."""
        if self.location:
            # When retrieved from DB, self.location will be a WKBElement
            return to_shape(self.location)
        return None
