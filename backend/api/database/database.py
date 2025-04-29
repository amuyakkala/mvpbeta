from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # Enable SQL query logging
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=settings.DB_AUTOCOMMIT,
    autoflush=settings.DB_AUTOFLUSH,
    bind=engine
)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        logger.debug("Creating new database session")
        yield db
        # Commit the session if no exceptions occurred
        db.commit()
        logger.debug("Database session committed successfully")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        logger.debug("Closing database session")
        db.close() 