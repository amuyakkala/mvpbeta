from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from api.database.database import get_db
from api.models.notification import Notification, NotificationCreate, NotificationUpdate, NotificationFilter
from api.models.user import User
from api.auth.router import get_current_user
from api.services.notification import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new notification.
    """
    notification_service = NotificationService(db)
    return await notification_service.send_notification(notification)

@router.get("/", response_model=List[Notification])
async def get_notifications(
    filter: NotificationFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications with filtering, sorting, and pagination.
    """
    notification_service = NotificationService(db)
    return await notification_service.get_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_read=filter.is_read
    )

@router.get("/{notification_id}", response_model=Notification)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific notification by ID.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification

@router.put("/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: int,
    notification: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a notification.
    """
    notification_service = NotificationService(db)
    return await notification_service.update_notification(notification_id, notification)

@router.post("/{notification_id}/read", response_model=Notification)
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read.
    """
    notification_service = NotificationService(db)
    return await notification_service.mark_as_read(notification_id)

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a notification.
    """
    notification_service = NotificationService(db)
    await notification_service.delete_notification(notification_id)
    return {"message": "Notification deleted successfully"}

@router.delete("/")
async def clear_notifications(
    notification_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear notifications for the current user.
    """
    notification_service = NotificationService(db)
    success = await notification_service.clear_notifications(current_user.id, notification_ids)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear notifications")
    return {"message": "Notifications cleared successfully"} 