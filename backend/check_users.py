import logging
from api.database.database import SessionLocal
from api.models.database import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_users():
    logger.info("Starting database query...")
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        logger.info(f"Found {len(users)} users in database")
        
        if not users:
            logger.warning("No users found in database")
        else:
            for user in users:
                logger.info(f"User: {user.email}, Full Name: {user.full_name}")
        
        # Get first user
        first_user = db.query(User).first()
        logger.info(f"First user query result: {first_user}")
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
    finally:
        logger.info("Closing database session")
        db.close()

if __name__ == "__main__":
    check_users() 