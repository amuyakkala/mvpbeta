from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from api.models.database import AuditLog, User
import logging

logger = logging.getLogger(__name__)

class AuditService:
    """Service for handling audit logging across the system."""
    
    def __init__(self, db: Session):
        logger.info("Initializing AuditService")
        self.db = db
        logger.info("AuditService initialized with database session")
        self._last_action = {}  # Track last action to prevent duplicates
    
    async def log_action(
        self,
        user_id: int,
        action_type: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log an action in the system with comprehensive metadata.
        
        Args:
            user_id: ID of the user performing the action
            action_type: Type of action (e.g., 'create', 'update', 'delete', 'login', 'logout')
            resource_type: Type of resource being acted upon (e.g., 'trace', 'issue', 'user')
            resource_id: ID of the resource (if applicable)
            meta_data: Additional metadata about the action
            additional_context: Any additional context about the action
            
        Returns:
            The created audit log entry
        """
        try:
            # Check for duplicate action
            action_key = f"{user_id}_{action_type}_{resource_type}_{resource_id}"
            current_time = datetime.utcnow()
            
            if action_key in self._last_action:
                last_time = self._last_action[action_key]
                # If same action within 1 second, skip
                if (current_time - last_time).total_seconds() < 1:
                    logger.debug(f"Skipping duplicate action: {action_key}")
                    return None
            
            self._last_action[action_key] = current_time
            
            logger.info(f"Attempting to log action: {action_type} on {resource_type} by user {user_id}")
            
            # Get user details
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found for audit logging")
                return None

            # Prepare comprehensive metadata
            full_meta_data = {
                "user_email": user.email,
                "user_name": user.full_name,
                "action_timestamp": current_time.isoformat(),
                "action_details": meta_data or {},
                "system_context": additional_context or {},
                "ip_address": additional_context.get("ip_address") if additional_context else None,
                "user_agent": additional_context.get("user_agent") if additional_context else None,
                "session_id": additional_context.get("session_id") if additional_context else None
            }

            logger.info(f"Creating audit log with metadata: {full_meta_data}")

            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                action_type=action_type,
                resource_type=resource_type,
                resource_id=resource_id,
                meta_data=full_meta_data,
                created_at=current_time
            )
            
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)
            
            logger.info(f"Successfully created audit log with ID: {audit_log.id}")
            return audit_log
            
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            self.db.rollback()
            return None

    async def log_trace_action(
        self,
        user_id: int,
        action_type: str,
        trace_id: int,
        meta_data: Optional[Dict[str, Any]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log an action related to traces."""
        logger.info(f"Logging trace action: {action_type} for trace {trace_id}")
        return await self.log_action(
            user_id=user_id,
            action_type=action_type,
            resource_type="trace",
            resource_id=trace_id,
            meta_data=meta_data,
            additional_context=additional_context
        )

    async def log_issue_action(
        self,
        user_id: int,
        action_type: str,
        issue_id: int,
        meta_data: Optional[Dict[str, Any]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log an action related to issues."""
        logger.info(f"Logging issue action: {action_type} for issue {issue_id}")
        return await self.log_action(
            user_id=user_id,
            action_type=action_type,
            resource_type="issue",
            resource_id=issue_id,
            meta_data=meta_data,
            additional_context=additional_context
        )

    async def log_user_action(
        self,
        user_id: int,
        action_type: str,
        meta_data: Optional[Dict[str, Any]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log an action related to users."""
        logger.info(f"Logging user action: {action_type} for user {user_id}")
        return await self.log_action(
            user_id=user_id,
            action_type=action_type,
            resource_type="user",
            meta_data=meta_data,
            additional_context=additional_context
        )

    async def log_system_action(
        self,
        action_type: str,
        resource_type: str,
        meta_data: Optional[Dict[str, Any]] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Log a system-level action (no specific user)."""
        logger.info(f"Logging system action: {action_type} on {resource_type}")
        return await self.log_action(
            user_id=1,  # System user ID
            action_type=action_type,
            resource_type=resource_type,
            meta_data=meta_data,
            additional_context=additional_context
        ) 