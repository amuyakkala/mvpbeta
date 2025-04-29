from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from ..services.notification import NotificationService
from ..models.user import User
from ..models.audit_log import AuditLog
from ..auth import get_current_user
from ..config.database import get_db
from datetime import datetime
from sqlalchemy import inspect

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    response_model=List[Notification],
    summary="Get user notifications",
    description="Retrieve notifications for the current user with pagination and sorting. Optionally filter for unread notifications only.",
    responses={
        200: {"description": "List of notifications"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_notifications(
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notifications for the current user with pagination and sorting.
    
    Args:
        unread_only: If True, returns only unread notifications
        skip: Number of records to skip
        limit: Maximum number of records to return
        sort_by: Field to sort by (created_at, title, type)
        sort_order: Sort order (asc, desc)
        
    Returns:
        List of notifications
    """
    notification_service = NotificationService(db)
    notifications = await notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Log the action
    db_audit = AuditLog(
        user_id=current_user.id,
        action_type="get_notifications",
        metadata={"unread_only": unread_only, "skip": skip, "limit": limit, "sort_by": sort_by, "sort_order": sort_order}
    )
    db.add(db_audit)
    db.commit()
    
    return notifications

@router.post(
    "/read",
    summary="Mark notifications as read",
    description="Mark specified notifications as read for the current user.",
    responses={
        200: {"description": "Notifications marked as read"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def mark_notifications_as_read(
    notification_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark notifications as read.
    
    - **notification_ids**: List of notification IDs to mark as read
    - **current_user**: Current authenticated user
    """
    notification_service = NotificationService(db)
    success = await notification_service.mark_as_read(
        current_user.id,
        notification_ids
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to mark notifications as read")
    
    # Log the action
    db_audit = AuditLog(
        user_id=current_user.id,
        action_type="mark_notifications_read",
        metadata={"notification_ids": notification_ids}
    )
    db.add(db_audit)
    db.commit()
    
    return {"message": "Notifications marked as read"}

@router.delete(
    "/",
    summary="Clear notifications",
    description="Clear notifications for the current user. Optionally clear specific notifications by ID.",
    responses={
        200: {"description": "Notifications cleared"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def clear_notifications(
    notification_ids: Optional[List[int]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Clear notifications.
    
    - **notification_ids**: Optional list of notification IDs to clear. If not provided, clears all notifications.
    - **current_user**: Current authenticated user
    """
    notification_service = NotificationService(db)
    success = await notification_service.clear_notifications(
        current_user.id,
        notification_ids
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear notifications")
    
    # Log the action
    db_audit = AuditLog(
        user_id=current_user.id,
        action_type="clear_notifications",
        metadata={"notification_ids": notification_ids}
    )
    db.add(db_audit)
    db.commit()
    
    return {"message": "Notifications cleared"}

@router.get(
    "/health",
    summary="Notification service health check",
    description="Check the health of the notification service and database connection.",
    responses={
        200: {"description": "Service is healthy"},
        500: {"description": "Service is unhealthy"}
    }
)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for notification service.
    Performs comprehensive checks of:
    - Database connection
    - Notification service functionality
    - Database schema
    - Recent notification processing
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Check database schema
        inspector = inspect(db.get_bind())
        required_tables = ['notifications', 'users', 'audit_logs']
        missing_tables = [table for table in required_tables if table not in inspector.get_table_names()]
        if missing_tables:
            raise Exception(f"Missing required tables: {', '.join(missing_tables)}")
        
        # Test notification service
        notification_service = NotificationService(db)
        test_notification = await notification_service.send_notification(
            NotificationCreate(
                user_id=1,  # System user
                title="Health Check",
                message="Notification service is healthy",
                type="info"
            )
        )
        
        # Check recent notification processing
        recent_notifications = await notification_service.get_user_notifications(1, limit=5)
        notification_count = len(recent_notifications)
        
        return {
            "status": "healthy",
            "database": "connected",
            "notification_service": "operational",
            "schema": "valid",
            "recent_notifications": notification_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        ) 