from typing import List, Optional, Callable, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.notification import Notification, NotificationCreate, NotificationUpdate
from api.models.database import Notification as NotificationModel
from api.database.database import get_db

class NotificationService:
    """Service for handling notifications."""
    
    def __init__(self, db: Session):
        self.db = db
        self.subscribers: List[Callable] = []
    
    async def send_notification(self, notification: NotificationCreate) -> Notification:
        """
        Send a notification to a user.
        """
        db_notification = NotificationModel(
            user_id=notification.user_id,
            title=notification.title,
            message=notification.message,
            notification_metadata=notification.notification_metadata,
            is_read=False,
            created_at=datetime.utcnow()
        )
        self.db.add(db_notification)
        self.db.commit()
        self.db.refresh(db_notification)
        return Notification.from_orm(db_notification)
    
    def subscribe(self, callback: Callable[[Notification], Any]) -> None:
        """
        Subscribe to notifications.
        """
        self.subscribers.append(callback)
    
    async def get_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        is_read: Optional[bool] = None
    ) -> List[Notification]:
        """
        Get notifications for a user with pagination and read status filter.
        """
        query = self.db.query(NotificationModel).filter(NotificationModel.user_id == user_id)
        if is_read is not None:
            query = query.filter(NotificationModel.is_read == is_read)
        notifications = query.order_by(NotificationModel.created_at.desc()).offset(skip).limit(limit).all()
        return [Notification.from_orm(n) for n in notifications]
    
    async def mark_as_read(self, notification_id: int) -> Notification:
        """
        Mark a notification as read.
        """
        notification = self.db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return Notification.from_orm(notification)
    
    async def update_notification(
        self,
        notification_id: int,
        notification: NotificationUpdate
    ) -> Notification:
        """
        Update a notification.
        """
        db_notification = self.db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
        if not db_notification:
            raise ValueError("Notification not found")
        
        update_data = notification.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_notification, key, value)
        
        self.db.commit()
        self.db.refresh(db_notification)
        return Notification.from_orm(db_notification)
    
    async def delete_notification(self, notification_id: int) -> None:
        """
        Delete a notification.
        """
        notification = self.db.query(NotificationModel).filter(NotificationModel.id == notification_id).first()
        if not notification:
            raise ValueError("Notification not found")
        
        self.db.delete(notification)
        self.db.commit()
    
    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[Notification]:
        """
        Get notifications for a user with advanced filtering and sorting.
        """
        query = self.db.query(NotificationModel).filter(NotificationModel.user_id == user_id)
        
        if unread_only:
            query = query.filter(NotificationModel.is_read == False)
        
        # Add sorting
        if sort_order.lower() == "desc":
            query = query.order_by(getattr(NotificationModel, sort_by).desc())
        else:
            query = query.order_by(getattr(NotificationModel, sort_by))
        
        notifications = query.offset(skip).limit(limit).all()
        return [Notification.from_orm(n) for n in notifications]
    
    async def clear_notifications(
        self,
        user_id: int,
        notification_ids: Optional[List[int]] = None
    ) -> bool:
        """
        Clear notifications for a user.
        If notification_ids is provided, only clear those specific notifications.
        """
        try:
            if notification_ids:
                self.db.query(NotificationModel).filter(
                    NotificationModel.user_id == user_id,
                    NotificationModel.id.in_(notification_ids)
                ).delete()
            else:
                self.db.query(NotificationModel).filter(
                    NotificationModel.user_id == user_id
                ).delete()
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e 