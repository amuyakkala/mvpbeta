import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.notification import NotificationDB, Base
from ..services.notification import NotificationService

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def notification_service(db_session):
    return NotificationService(db_session)

@pytest.mark.asyncio
async def test_send_notification(notification_service, db_session):
    notification_data = {
        "user_id": 1,
        "title": "Test Notification",
        "message": "This is a test",
        "type": "info"
    }
    
    notification = await notification_service.send_notification(notification_data)
    
    assert notification.id is not None
    assert notification.user_id == 1
    assert notification.title == "Test Notification"
    assert notification.message == "This is a test"
    assert notification.type == "info"
    assert notification.is_read is False
    
    # Verify database entry
    db_notification = db_session.query(NotificationDB).first()
    assert db_notification is not None
    assert db_notification.title == "Test Notification"

@pytest.mark.asyncio
async def test_get_user_notifications(notification_service, db_session):
    # Create test notifications
    for i in range(3):
        notification = NotificationDB(
            user_id=1,
            title=f"Test {i}",
            message=f"Message {i}",
            type="info",
            is_read=(i % 2 == 0)
        )
        db_session.add(notification)
    db_session.commit()
    
    # Test getting all notifications
    notifications = await notification_service.get_user_notifications(1)
    assert len(notifications) == 3
    
    # Test getting only unread notifications
    unread_notifications = await notification_service.get_user_notifications(1, unread_only=True)
    assert len(unread_notifications) == 1

@pytest.mark.asyncio
async def test_mark_as_read(notification_service, db_session):
    # Create test notification
    notification = NotificationDB(
        user_id=1,
        title="Test",
        message="Message",
        type="info",
        is_read=False
    )
    db_session.add(notification)
    db_session.commit()
    
    # Mark as read
    success = await notification_service.mark_as_read(1, [notification.id])
    assert success is True
    
    # Verify
    db_notification = db_session.query(NotificationDB).first()
    assert db_notification.is_read is True

@pytest.mark.asyncio
async def test_clear_notifications(notification_service, db_session):
    # Create test notifications
    for i in range(3):
        notification = NotificationDB(
            user_id=1,
            title=f"Test {i}",
            message=f"Message {i}",
            type="info"
        )
        db_session.add(notification)
    db_session.commit()
    
    # Clear all notifications
    success = await notification_service.clear_notifications(1)
    assert success is True
    
    # Verify
    notifications = db_session.query(NotificationDB).filter(NotificationDB.user_id == 1).all()
    assert len(notifications) == 0 