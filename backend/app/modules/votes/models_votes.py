from datetime import datetime
from uuid import UUID

from app.modules.votes.types_votes import VoteValue
from app.types.sqlalchemy import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Vote(Base):
    __tablename__ = "vote"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    report_id: Mapped[UUID] = mapped_column(ForeignKey("report.id"))
    vote_value: VoteValue
