from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class IssueStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IssueBase(BaseModel):
    title: str
    description: str
    severity: IssueSeverity = IssueSeverity.MEDIUM
    status: IssueStatus = IssueStatus.OPEN

class IssueCreate(IssueBase):
    trace_id: int
    user_id: int

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IssueSeverity] = None
    status: Optional[IssueStatus] = None
    assigned_to: Optional[int] = None
    resolution: Optional[str] = None

class IssueFilter(BaseModel):
    trace_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[IssueStatus] = None
    severity: Optional[IssueSeverity] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class IssueResponse(IssueBase):
    id: int
    trace_id: int
    user_id: int
    assigned_to: Optional[int] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True) 