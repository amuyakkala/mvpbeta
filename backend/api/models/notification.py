from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    ALERT = "alert"
    WARNING = "warning"
    INFO = "info"
    ERROR = "error"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    READ = "read"

class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    status: NotificationStatus = NotificationStatus.PENDING
    recipient: str
    notification_metadata: Optional[dict] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[NotificationType] = None
    status: Optional[NotificationStatus] = None
    recipient: Optional[str] = None
    notification_metadata: Optional[dict] = None

class NotificationFilter(BaseModel):
    type: Optional[NotificationType] = None
    status: Optional[NotificationStatus] = None
    recipient: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 