from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action_type: str
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True 