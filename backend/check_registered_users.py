from api.models.database import User, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_registered_users():
    db = SessionLocal()
    try:
        # Get all users
        users = db.query(User).all()
        total_users = len(users)
        
        logger.info(f"Total registered users: {total_users}")
        
        if total_users > 0:
            logger.info("\nUser Details:")
            for user in users:
                logger.info(f"""
                User ID: {user.id}
                Email: {user.email}
                Full Name: {user.full_name}
                Is Active: {user.is_active}
                Created At: {user.created_at}
                """)
        else:
            logger.warning("No users found in the database")
            
    except Exception as e:
        logger.error(f"Error checking users: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_registered_users() 