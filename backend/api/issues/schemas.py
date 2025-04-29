from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models import IssueSeverity, IssueStatus

class IssueBase(BaseModel):
    title: str
    description: str
    severity: IssueSeverity

class IssueCreate(IssueBase):
    trace_id: int

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IssueSeverity] = None
    status: Optional[IssueStatus] = None
    assigned_to_user_id: Optional[int] = None

class IssueResponse(IssueBase):
    id: int
    trace_id: int
    status: IssueStatus
    assigned_to_user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True 