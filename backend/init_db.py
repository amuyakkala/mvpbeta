import sys
import os
import logging

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.database.database import engine
from api.models.database import Base
from config.settings import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        # Print the database URL and current directory
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        logger.info(f"Database file path: {os.path.abspath(settings.DATABASE_URL.replace('sqlite:///', ''))}")
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Check if the database file exists
        db_path = os.path.abspath(settings.DATABASE_URL.replace('sqlite:///', ''))
        if os.path.exists(db_path):
            logger.info(f"Database file created at: {db_path}")
        else:
            logger.error(f"Database file not found at: {db_path}")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 