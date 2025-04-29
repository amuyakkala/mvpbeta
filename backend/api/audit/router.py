from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import or_
import os
import logging
from slack_sdk.errors import SlackApiError

from api.database.database import get_db
from api.models.database import AuditLog, User
from api.models.audit import AuditLogCreate, AuditLogFilter, AuditLogResponse
from api.auth.router import get_current_user
from api.services.audit import AuditService
from api.services.external_notification import ExternalNotificationService

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.get(
    "/",
    response_model=List[AuditLogResponse],
    summary="Get audit logs",
    description="Get audit logs with filtering, sorting, and search capabilities.",
    responses={
        200: {"description": "List of audit logs"},
        401: {"description": "Unauthorized"}
    }
)
async def get_audit_logs(
    filter: AuditLogFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs with filtering, sorting, and pagination.
    Only shows logs for the current user.
    """
    query = db.query(AuditLog).filter(AuditLog.user_id == current_user.id)
    
    # Apply filters
    if filter.action_type:
        query = query.filter(AuditLog.action_type == filter.action_type)
    if filter.resource_type:
        query = query.filter(AuditLog.resource_type == filter.resource_type)
    if filter.resource_id:
        query = query.filter(AuditLog.resource_id == filter.resource_id)
    if filter.start_date:
        query = query.filter(AuditLog.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(AuditLog.created_at <= filter.end_date)
    if filter.search:
        query = query.filter(AuditLog.meta_data.ilike(f"%{filter.search}%"))
    
    # Apply sorting
    if sort_order.lower() == "desc":
        query = query.order_by(getattr(AuditLog, sort_by).desc())
    else:
        query = query.order_by(getattr(AuditLog, sort_by).asc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

@router.get(
    "/user/{user_id}",
    response_model=List[AuditLogResponse],
    summary="Get user audit logs",
    description="Get audit logs for a specific user.",
    responses={
        200: {"description": "List of user audit logs"},
        404: {"description": "User not found"},
        401: {"description": "Unauthorized"}
    }
)
async def get_user_audit_logs(
    user_id: int,
    filter: AuditLogFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a specific user.
    Only allows users to view their own logs.
    """
    # Verify user exists and is the current user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to view other users' audit logs"
        )
    
    query = db.query(AuditLog).filter(AuditLog.user_id == current_user.id)
    
    # Apply filters
    if filter.action_type:
        query = query.filter(AuditLog.action_type == filter.action_type)
    if filter.resource_type:
        query = query.filter(AuditLog.resource_type == filter.resource_type)
    if filter.resource_id:
        query = query.filter(AuditLog.resource_id == filter.resource_id)
    if filter.start_date:
        query = query.filter(AuditLog.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(AuditLog.created_at <= filter.end_date)
    if filter.search:
        query = query.filter(AuditLog.meta_data.ilike(f"%{filter.search}%"))
    
    # Apply sorting
    if sort_order.lower() == "desc":
        query = query.order_by(getattr(AuditLog, sort_by).desc())
    else:
        query = query.order_by(getattr(AuditLog, sort_by).asc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

@router.get(
    "/action/{action_type}",
    response_model=List[AuditLogResponse],
    summary="Get action audit logs",
    description="Get audit logs for a specific action type.",
    responses={
        200: {"description": "List of action audit logs"},
        401: {"description": "Unauthorized"}
    }
)
async def get_action_audit_logs(
    action_type: str,
    filter: AuditLogFilter = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for a specific action type.
    Only shows logs for the current user.
    """
    query = db.query(AuditLog).filter(
        AuditLog.action_type == action_type,
        AuditLog.user_id == current_user.id
    )
    
    # Apply filters
    if filter.resource_type:
        query = query.filter(AuditLog.resource_type == filter.resource_type)
    if filter.resource_id:
        query = query.filter(AuditLog.resource_id == filter.resource_id)
    if filter.start_date:
        query = query.filter(AuditLog.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(AuditLog.created_at <= filter.end_date)
    if filter.search:
        query = query.filter(AuditLog.meta_data.ilike(f"%{filter.search}%"))
    
    # Apply sorting
    if sort_order.lower() == "desc":
        query = query.order_by(getattr(AuditLog, sort_by).desc())
    else:
        query = query.order_by(getattr(AuditLog, sort_by).asc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

@router.post("/test")
async def test_audit_logging(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test endpoint to verify audit logging is working."""
    try:
        audit_service = AuditService(db)
        
        # Test system action
        system_log = await audit_service.log_system_action(
            action_type="test_action",
            resource_type="test",
            meta_data={"test": "data"}
        )
        
        # Test user action
        user_log = await audit_service.log_user_action(
            user_id=current_user.id,
            action_type="test_user_action",
            meta_data={"test": "user_data"}
        )
        
        return {
            "system_log_id": system_log.id if system_log else None,
            "user_log_id": user_log.id if user_log else None,
            "message": "Test audit logs created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-notification")
async def test_notification(
    current_user: User = Depends(get_current_user)
):
    """Test the notification system by sending a test notification."""
    try:
        notification_service = ExternalNotificationService()
        
        # Test Slack notification
        slack_success = await notification_service.send_slack_notification(
            channel=os.getenv("SLACK_ALERT_CHANNEL"),
            message="Test notification from Trace Analysis System",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Test Notification*\nThis is a test message from the Trace Analysis System."
                    }
                }
            ]
        )
        
        # Test email notification
        email_success = await notification_service.send_email_notification(
            to_email=current_user.email,
            subject="Test Notification from Trace Analysis System",
            message="This is a test message from the Trace Analysis System.",
            html_message="""
            <html>
                <body>
                    <h2>Test Notification</h2>
                    <p>This is a test message from the Trace Analysis System.</p>
                </body>
            </html>
            """
        )
        
        return {
            "status": "success",
            "slack_sent": slack_success,
            "email_sent": email_success,
            "message": "Test notifications sent successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to send test notifications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test notifications: {str(e)}"
        )

@router.get("/test-slack-permissions")
async def test_slack_permissions(
    current_user: User = Depends(get_current_user)
):
    """Test Slack bot permissions and channel access."""
    try:
        logger.info("Initializing notification service")
        notification_service = ExternalNotificationService()
        
        if not notification_service.slack_client:
            logger.error("Slack client not initialized")
            return {
                "status": "error",
                "message": "Slack client not initialized. Check SLACK_BOT_TOKEN in environment variables."
            }
        
        logger.info("Attempting to list Slack channels")
        # Test listing channels
        try:
            response = notification_service.slack_client.conversations_list(
                types="public_channel,private_channel"
            )
            logger.info(f"Slack API response: {response}")
        except SlackApiError as e:
            logger.error(f"Slack API error: {str(e)}")
            logger.error(f"Error response: {e.response}")
            raise
        
        channels = response.get("channels", [])
        channel_names = [channel["name"] for channel in channels]
        
        # Check if our alert channel exists
        alert_channel = os.getenv("SLACK_ALERT_CHANNEL", "").lstrip("#")
        channel_exists = any(channel["name"] == alert_channel for channel in channels)
        
        logger.info(f"Available channels: {channel_names}")
        logger.info(f"Looking for alert channel: {alert_channel}")
        logger.info(f"Channel exists: {channel_exists}")
        
        return {
            "status": "success",
            "bot_initialized": True,
            "available_channels": channel_names,
            "alert_channel": alert_channel,
            "channel_exists": channel_exists,
            "channel_access": "Yes" if channel_exists else "No"
        }
        
    except SlackApiError as e:
        logger.error(f"Slack API error: {str(e)}")
        return {
            "status": "error",
            "message": f"Slack API error: {str(e)}",
            "error_details": e.response
        }
    except Exception as e:
        logger.error(f"Error testing Slack permissions: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error testing Slack permissions: {str(e)}",
            "error_type": type(e).__name__
        }

@router.get("/test-slack-token")
async def test_slack_token(
    current_user: User = Depends(get_current_user)
):
    """Test if the Slack bot token is valid."""
    try:
        notification_service = ExternalNotificationService()
        
        if not notification_service.slack_client:
            return {
                "status": "error",
                "message": "Slack client not initialized"
            }
        
        # Test the token by getting bot info
        response = notification_service.slack_client.auth_test()
        
        return {
            "status": "success",
            "bot_info": {
                "user_id": response.get("user_id"),
                "user": response.get("user"),
                "team": response.get("team"),
                "team_id": response.get("team_id"),
                "bot_id": response.get("bot_id")
            }
        }
        
    except SlackApiError as e:
        return {
            "status": "error",
            "message": f"Slack API error: {str(e)}",
            "error_details": e.response
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing Slack token: {str(e)}"
        }

@router.post("/test-slack-message")
async def test_slack_message(
    current_user: User = Depends(get_current_user)
):
    """Test sending a message to the Slack alerts channel."""
    try:
        logger.info("Initializing notification service")
        notification_service = ExternalNotificationService()
        
        if not notification_service.slack_client:
            return {
                "status": "error",
                "message": "Slack client not initialized"
            }
        
        # Get channel name from environment variable, default to "alerts" without #
        channel = os.getenv("SLACK_ALERT_CHANNEL", "alerts").lstrip("#")
        message = "Test message from Trace Analysis System"
        
        logger.info(f"Attempting to send message to channel: {channel}")
        
        # Use the notification service's send_slack_notification method
        success = await notification_service.send_slack_notification(
            channel=channel,
            message=message,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Test Message*\nThis is a test message from the Trace Analysis System."
                    }
                }
            ]
        )
        
        if success:
            return {
                "status": "success",
                "message": "Test message sent successfully",
                "channel": channel
            }
        else:
            return {
                "status": "error",
                "message": "Failed to send test message",
                "channel": channel
            }
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error sending Slack message: {str(e)}",
            "error_type": type(e).__name__
        }

@router.get("/test-slack-scopes")
async def test_slack_scopes(
    current_user: User = Depends(get_current_user)
):
    """Test if the Slack bot has the necessary permissions."""
    try:
        logger.info("Initializing notification service")
        notification_service = ExternalNotificationService()
        
        if not notification_service.slack_client:
            logger.error("Slack client not initialized")
            return {
                "status": "error",
                "message": "Slack client not initialized"
            }
        
        try:
            # Get bot info to check scopes
            logger.info("Getting auth test info")
            auth_test = notification_service.slack_client.auth_test()
            logger.info(f"Auth test response: {auth_test}")
            
            logger.info("Getting bot info")
            bot_info = notification_service.slack_client.bots_info(bot=auth_test["bot_id"])
            logger.info(f"Bot info response: {bot_info}")
            
            required_scopes = [
                "channels:read",
                "channels:join",
                "chat:write",
                "chat:write.public"
            ]
            
            # Get the bot's scopes
            scopes = auth_test.get("scopes", [])
            missing_scopes = [scope for scope in required_scopes if scope not in scopes]
            
            logger.info(f"Current scopes: {scopes}")
            logger.info(f"Missing scopes: {missing_scopes}")
            
            return {
                "status": "success",
                "bot_info": {
                    "user_id": auth_test.get("user_id"),
                    "bot_id": auth_test.get("bot_id"),
                    "team": auth_test.get("team"),
                    "scopes": scopes,
                    "missing_scopes": missing_scopes
                }
            }
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {str(e)}")
            logger.error(f"Error response: {e.response}")
            return {
                "status": "error",
                "message": f"Slack API error: {str(e)}",
                "error_details": e.response,
                "error_type": "SlackApiError"
            }
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": f"Error checking Slack scopes: {str(e)}",
            "error_type": type(e).__name__
        } 