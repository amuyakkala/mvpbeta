from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from config.settings import settings
from pydantic import ConfigDict
import logging
from enum import Enum as PyEnum

logger = logging.getLogger(__name__)

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True  # Enable SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

class User(Base):
    """SQLAlchemy model for users table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    traces = relationship("Trace", back_populates="user")
    issues = relationship("Issue", back_populates="user", foreign_keys="[Issue.user_id]")
    assigned_issues = relationship("Issue", back_populates="assigned_to_user", foreign_keys="[Issue.assigned_to]")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

    model_config = ConfigDict(from_attributes=True)

class Trace(Base):
    """SQLAlchemy model for traces table."""
    __tablename__ = "traces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(JSON)
    file_name = Column(String)
    file_size = Column(Integer)
    analysis_results = Column(JSON)
    status = Column(String, default="pending")  # pending, analyzing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="traces")
    issues = relationship("Issue", back_populates="trace")

    model_config = ConfigDict(from_attributes=True)

class IssueStatus(str, PyEnum):
    """Enum for issue statuses."""
    OPEN = "open"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IssueSeverity(str, PyEnum):
    """Enum for issue severities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class Issue(Base):
    """SQLAlchemy model for issues table."""
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(Integer, ForeignKey("traces.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    description = Column(Text)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN)
    severity = Column(Enum(IssueSeverity), default=IssueSeverity.MEDIUM)
    category = Column(String, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="issues", foreign_keys=[user_id])
    assigned_to_user = relationship("User", back_populates="assigned_issues", foreign_keys=[assigned_to])
    trace = relationship("Trace", back_populates="issues")

    model_config = ConfigDict(from_attributes=True)

class AuditLog(Base):
    """SQLAlchemy model for audit_logs table."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action_type = Column(String)
    resource_type = Column(String)
    resource_id = Column(Integer, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    model_config = ConfigDict(from_attributes=True)

class Notification(Base):
    """SQLAlchemy model for notifications table."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(String)
    type = Column(String)  # alert, warning, info, error
    status = Column(String)  # pending, sent, failed, read
    recipient = Column(String)
    notification_metadata = Column(JSON)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")

    model_config = ConfigDict(from_attributes=True)

def get_db():
    """Dependency for getting DB session"""
    db = SessionLocal()
    try:
        logger.debug("Creating new database session")
        yield db
    finally:
        logger.debug("Closing database session")
        db.close() 