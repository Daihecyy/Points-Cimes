from enum import Enum


class ReportType(str, Enum):
    HIGHLIGHT = "highlight"
    DANGER = "danger"
    PROBLEM = "problem"


class ReportStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    RESOLVED = "resolved"
    ARCHIVED = "archived"
    REJECTED = "rejected"
