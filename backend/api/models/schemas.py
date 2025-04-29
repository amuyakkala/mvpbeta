from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .database import IssueStatus, IssueSeverity

class UserBase(BaseModel):
    email: str
    full_name: str
    is_active: bool

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TraceData(BaseModel):
    content: Dict[str, Any]
    file_name: str
    file_size: int
    user_id: int
    analysis_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TraceBase(BaseModel):
    content: Dict[str, Any]
    file_name: Optional[str] = None
    file_size: Optional[int] = None

class TraceCreate(TraceBase):
    pass

class Trace(TraceBase):
    id: int
    user_id: int
    analysis_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IssueBase(BaseModel):
    title: str
    description: str
    severity: IssueSeverity = IssueSeverity.MEDIUM
    assigned_to: Optional[int] = None
    resolution: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class IssueCreate(IssueBase):
    trace_id: int

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    severity: Optional[IssueSeverity] = None
    assigned_to: Optional[int] = None
    resolution: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class Issue(IssueBase):
    id: int
    trace_id: int
    user_id: int
    status: IssueStatus
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class IssueFilter(BaseModel):
    status: Optional[IssueStatus] = None
    severity: Optional[IssueSeverity] = None
    assigned_to: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None

class AuditLogBase(BaseModel):
    action_type: str
    resource_type: str
    resource_id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True 