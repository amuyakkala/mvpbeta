from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class TraceBase(BaseModel):
    content: Dict[str, Any]
    file_name: str
    file_size: int

class TraceCreate(TraceBase):
    user_id: int

class TraceUpdate(BaseModel):
    content: Optional[Dict[str, Any]] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    analysis_results: Optional[Dict[str, Any]] = None

class TraceFilter(BaseModel):
    user_id: Optional[int] = None
    file_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TraceResponse(TraceBase):
    id: int
    user_id: int
    analysis_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TraceAnalysisRequest(BaseModel):
    trace_id: int
    analysis_type: str
    parameters: Optional[Dict[str, Any]] = None

class TraceAnalysisResponse(BaseModel):
    trace_id: int
    analysis_type: str
    results: Dict[str, Any]
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) 