from api.models.database import User, SessionLocal
from api.auth.router import verify_password
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_database():
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        logger.info(f"Found {len(users)} users in database")
        
        # Print user details
        for user in users:
            logger.info(f"""
            User Details:
            ID: {user.id}
            Email: {user.email}
            First Name: {user.first_name}
            Last Name: {user.last_name}
            Is Active: {user.is_active}
            Created At: {user.created_at}
            Updated At: {user.updated_at}
            """)
            
        # Check specific user
        test_email = "amulyay.work@gmail.com"
        user = db.query(User).filter(User.email == test_email).first()
        if user:
            logger.info(f"User {test_email} exists in database")
            logger.info(f"User is active: {user.is_active}")
        else:
            logger.warning(f"User {test_email} not found in database")
            
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database() 