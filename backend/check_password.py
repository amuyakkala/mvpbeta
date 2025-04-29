from api.models.database import User, SessionLocal
from api.auth.router import verify_password, get_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_password():
    db = SessionLocal()
    try:
        # Get the user
        email = "amulyay.work@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.error(f"User {email} not found")
            return
            
        logger.info(f"Found user: {email}")
        logger.info(f"Stored password hash: {user.hashed_password}")
        
        # Test password verification
        test_password = "123456"
        logger.info(f"Testing password: {test_password}")
        
        # Verify the password
        is_valid = verify_password(test_password, user.hashed_password)
        logger.info(f"Password verification result: {is_valid}")
        
        if not is_valid:
            # Try creating a new hash with the same password
            new_hash = get_password_hash(test_password)
            logger.info(f"New hash for same password: {new_hash}")
            logger.info(f"Original hash: {user.hashed_password}")
            logger.info(f"Are they the same? {new_hash == user.hashed_password}")
            
    except Exception as e:
        logger.error(f"Error checking password: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_password() 