from enum import Enum


class ReportType(str, Enum):
    HIGHLIGHT = "highlight"
    PROBLEM = "problem"


class ReportStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"
    REJECTED = "rejected"


class VoteValue(int, Enum):
    UP = 1
    DOWN = -1
