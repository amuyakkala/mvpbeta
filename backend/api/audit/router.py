from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import or_

from api.database.database import get_db
from api.models.database import AuditLog, User
from api.models.audit import AuditLogCreate, AuditLogFilter, AuditLogResponse
from api.auth.router import get_current_user

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    response_model=List[AuditLogResponse],
    summary="Get audit logs",
    description="Get audit logs with filtering, sorting, and search capabilities.",
    responses={
        200: {"description": "List of audit logs"},
        401: {"description": "Unauthorized"}
    }
)
async def get_audit_logs(
    filter: AuditLogFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs with filtering, sorting, and pagination.
    """
    query = db.query(AuditLog)
    
    # Apply filters
    if filter.user_id:
        query = query.filter(AuditLog.user_id == filter.user_id)
    if filter.action_type:
        query = query.filter(AuditLog.action_type == filter.action_type)
    if filter.resource_type:
        query = query.filter(AuditLog.resource_type == filter.resource_type)
    if filter.resource_id:
        query = query.filter(AuditLog.resource_id == filter.resource_id)
    if filter.start_date:
        query = query.filter(AuditLog.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(AuditLog.created_at <= filter.end_date)
    if filter.search:
        query = query.filter(AuditLog.meta_data.ilike(f"%{filter.search}%"))
    
    # Apply sorting
    if sort_order.lower() == "desc":
        query = query.order_by(getattr(AuditLog, sort_by).desc())
    else:
        query = query.order_by(getattr(AuditLog, sort_by).asc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

@router.get(
    "/user/{user_id}",
    response_model=List[AuditLogResponse],
    summary="Get user audit logs",
    description="Get audit logs for a specific user.",
    responses={
        200: {"description": "List of user audit logs"},
        404: {"description": "User not found"},
        401: {"description": "Unauthorized"}
    }
)
async def get_user_audit_logs(
    user_id: int,
    filter: AuditLogFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a specific user.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
    
    # Apply filters
    if filter.action_type:
        query = query.filter(AuditLog.action_type == filter.action_type)
    if filter.resource_type:
        query = query.filter(AuditLog.resource_type == filter.resource_type)
    if filter.resource_id:
        query = query.filter(AuditLog.resource_id == filter.resource_id)
    if filter.start_date:
        query = query.filter(AuditLog.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(AuditLog.created_at <= filter.end_date)
    if filter.search:
        query = query.filter(AuditLog.meta_data.ilike(f"%{filter.search}%"))
    
    # Apply sorting
    if sort_order.lower() == "desc":
        query = query.order_by(getattr(AuditLog, sort_by).desc())
    else:
        query = query.order_by(getattr(AuditLog, sort_by).asc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

@router.get(
    "/action/{action_type}",
    response_model=List[AuditLogResponse],
    summary="Get action audit logs",
    description="Get audit logs for a specific action type.",
    responses={
        200: {"description": "List of action audit logs"},
        401: {"description": "Unauthorized"}
    }
)
async def get_action_audit_logs(
    action_type: str,
    filter: AuditLogFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a specific action type.
    """
    query = db.query(AuditLog).filter(AuditLog.action_type == action_type)
    
    # Apply filters
    if filter.user_id:
        query = query.filter(AuditLog.user_id == filter.user_id)
    if filter.resource_type:
        query = query.filter(AuditLog.resource_type == filter.resource_type)
    if filter.resource_id:
        query = query.filter(AuditLog.resource_id == filter.resource_id)
    if filter.start_date:
        query = query.filter(AuditLog.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(AuditLog.created_at <= filter.end_date)
    if filter.search:
        query = query.filter(AuditLog.meta_data.ilike(f"%{filter.search}%"))
    
    # Apply sorting
    if sort_order.lower() == "desc":
        query = query.order_by(getattr(AuditLog, sort_by).desc())
    else:
        query = query.order_by(getattr(AuditLog, sort_by).asc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all() 