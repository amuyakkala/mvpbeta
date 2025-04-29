from sqlalchemy import inspect
from api.database.database import engine
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_schema():
    inspector = inspect(engine)
    
    # Get all tables
    tables = inspector.get_table_names()
    logger.info(f"Found tables: {tables}")
    
    # Check users table
    if 'users' in tables:
        logger.info("\nUsers table columns:")
        columns = inspector.get_columns('users')
        for column in columns:
            logger.info(f"Column: {column['name']}, Type: {column['type']}")
            
        # Check for indexes
        indexes = inspector.get_indexes('users')
        logger.info("\nUsers table indexes:")
        for index in indexes:
            logger.info(f"Index: {index['name']}, Columns: {index['column_names']}")
            
    # Check for foreign keys
    if 'users' in tables:
        logger.info("\nUsers table foreign keys:")
        fks = inspector.get_foreign_keys('users')
        for fk in fks:
            logger.info(f"Foreign Key: {fk['name']}, Referenced Table: {fk['referred_table']}")

if __name__ == "__main__":
    check_schema() 