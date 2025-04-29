import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..models.notification import NotificationDB
from ..models.user import User
from ..auth import create_access_token

client = TestClient(app)

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_token(test_user):
    return create_access_token({"sub": test_user.email})

def test_get_notifications(test_token, db_session):
    # Create test notification
    notification = NotificationDB(
        user_id=1,
        title="Test",
        message="Message",
        type="info"
    )
    db_session.add(notification)
    db_session.commit()
    
    response = client.get(
        "/notifications",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_mark_notifications_as_read(test_token, db_session):
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
    
    response = client.post(
        "/notifications/read",
        headers={"Authorization": f"Bearer {test_token}"},
        json={"notification_ids": [notification.id]}
    )
    assert response.status_code == 200
    
    # Verify notification is marked as read
    db_notification = db_session.query(NotificationDB).first()
    assert db_notification.is_read is True

def test_clear_notifications(test_token, db_session):
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
    
    response = client.delete(
        "/notifications",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    
    # Verify notifications are cleared
    notifications = db_session.query(NotificationDB).filter(NotificationDB.user_id == 1).all()
    assert len(notifications) == 0

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy" 