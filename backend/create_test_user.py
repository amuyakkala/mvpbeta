from api.models.database import User, SessionLocal
from api.auth.router import get_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_test_user():
    db = SessionLocal()
    try:
        # Test user data
        test_user = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "Test@123",
            "is_active": True
        }
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == test_user["email"]).first()
        if existing_user:
            logger.info(f"User {test_user['email']} already exists")
            return
            
        # Create new user
        hashed_password = get_password_hash(test_user["password"])
        new_user = User(
            email=test_user["email"],
            full_name=test_user["full_name"],
            hashed_password=hashed_password,
            is_active=test_user["is_active"]
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Test user created successfully:")
        logger.info(f"Email: {new_user.email}")
        logger.info(f"Name: {new_user.full_name}")
        logger.info(f"Active: {new_user.is_active}")
        
    except Exception as e:
        logger.error(f"Error creating test user: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user() 