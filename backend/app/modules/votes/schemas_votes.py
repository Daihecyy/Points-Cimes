from uuid import UUID

from pydantic import BaseModel


class Vote(BaseModel):
    id: UUID
    user_id: UUID
    report_id: UUID


class SpecificVote(BaseModel):
    user_id: UUID
    report_id: UUID
