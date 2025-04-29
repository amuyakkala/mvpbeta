from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from ...config.database import get_db
from ..models import AuditLog, User
from .handlers import SlackHandler, JiraHandler
from ..auth.router import get_current_user

router = APIRouter()
slack_handler = SlackHandler()
jira_handler = JiraHandler()

@router.post("/slack/configure")
async def configure_slack(
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Configure Slack integration.
    """
    try:
        slack_handler.webhook_url = config.get("webhook_url")
        if not slack_handler.validate_config():
            raise HTTPException(status_code=400, detail="Invalid Slack configuration")
        
        # Log the configuration
        db_audit = AuditLog(
            user_id=current_user.id,
            action_type="slack_configure",
            metadata={"status": "success"}
        )
        db.add(db_audit)
        db.commit()
        
        return {"status": "success", "message": "Slack configured successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jira/configure")
async def configure_jira(
    config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Configure Jira integration.
    """
    try:
        jira_handler.api_url = config.get("api_url")
        jira_handler.api_key = config.get("api_key")
        if not jira_handler.validate_config():
            raise HTTPException(status_code=400, detail="Invalid Jira configuration")
        
        # Log the configuration
        db_audit = AuditLog(
            user_id=current_user.id,
            action_type="jira_configure",
            metadata={"status": "success"}
        )
        db.add(db_audit)
        db.commit()
        
        return {"status": "success", "message": "Jira configured successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/slack/notify")
async def notify_slack(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send notification through Slack.
    """
    try:
        success = await slack_handler.send_notification(data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send Slack notification")
        
        # Log the notification
        db_audit = AuditLog(
            user_id=current_user.id,
            action_type="slack_notify",
            metadata={"status": "success"}
        )
        db.add(db_audit)
        db.commit()
        
        return {"status": "success", "message": "Notification sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jira/create")
async def create_jira_issue(
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Jira issue.
    """
    try:
        success = await jira_handler.send_notification(data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to create Jira issue")
        
        # Log the issue creation
        db_audit = AuditLog(
            user_id=current_user.id,
            action_type="jira_create",
            metadata={"status": "success"}
        )
        db.add(db_audit)
        db.commit()
        
        return {"status": "success", "message": "Jira issue created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 