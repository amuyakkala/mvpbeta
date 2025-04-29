from api.models.database import User, SessionLocal
from api.auth.router import verify_password
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def verify_user_password():
    db = SessionLocal()
    try:
        # Get the user
        email = "amulyay.work@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.error(f"User {email} not found")
            return
            
        logger.info(f"Found user: {email}")
        logger.info(f"Current password hash: {user.hashed_password}")
        
        # Test password verification
        test_password = "123456"
        logger.info(f"Testing password: {test_password}")
        
        # Verify the password
        is_valid = verify_password(test_password, user.hashed_password)
        logger.info(f"Password verification result: {is_valid}")
        
        if is_valid:
            logger.info("Password verification successful! You can now log in with this password.")
        else:
            logger.error("Password verification failed. Please try resetting the password again.")
            
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_user_password() 