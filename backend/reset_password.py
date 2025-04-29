from api.models.database import User, SessionLocal
from api.auth.router import get_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def reset_password():
    db = SessionLocal()
    try:
        # Get the user
        email = "amulyay.work@gmail.com"
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.error(f"User {email} not found")
            return
            
        # Set new password
        new_password = "123456"
        logger.info(f"Resetting password for user: {email}")
        
        # Generate new hash
        new_hash = get_password_hash(new_password)
        logger.info(f"New password hash: {new_hash}")
        
        # Update user
        user.hashed_password = new_hash
        db.commit()
        logger.info("Password updated successfully")
            
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_password() 