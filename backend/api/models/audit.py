from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AuditLogBase(BaseModel):
    action_type: str
    resource_type: str
    resource_id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None

class AuditLogCreate(AuditLogBase):
    user_id: int

class AuditLogResponse(AuditLogBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogFilter(BaseModel):
    user_id: Optional[int] = None
    action_type: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None 