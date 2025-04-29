from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from api.database.database import get_db
from api.auth.router import get_current_user
from api.models.database import User as UserModel, Trace, Issue
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={404: {"description": "Not found"}},
)

@router.get("/stats", response_model=Dict)
async def get_dashboard_stats(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Log current user info
        logger.info(f"Fetching stats for user: {current_user.id} - {current_user.email}")
        
        # Get total traces count for current user
        total_traces = db.query(Trace).filter(Trace.user_id == current_user.id).count()
        logger.info(f"Found {total_traces} traces for user {current_user.id}")
        
        # Get active issues count for current user
        active_issues = db.query(Issue).filter(
            Issue.user_id == current_user.id,
            Issue.status == "open"
        ).count()
        logger.info(f"Found {active_issues} active issues for user {current_user.id}")
        
        # Get system health (mock data for now)
        system_health = 95  # This would be calculated based on actual system metrics
        
        # Get average response time (mock data for now)
        avg_response_time = 150  # This would be calculated from actual response times
        
        return {
            "totalTraces": total_traces,
            "activeIssues": active_issues,
            "systemHealth": system_health,
            "responseTime": avg_response_time
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching dashboard statistics")

@router.get("/activities", response_model=List[Dict])
async def get_recent_activities(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get recent activities (mock data for now)
        activities = [
            {
                "type": "success",
                "message": "System scan completed successfully",
                "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat() + "Z"
            },
            {
                "type": "warning",
                "message": "High CPU usage detected",
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
            },
            {
                "type": "info",
                "message": "New user registered",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
            }
        ]
        return activities
    except Exception as e:
        logger.error(f"Error fetching recent activities: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching recent activities")

@router.get("/health", response_model=List[Dict])
async def get_system_health(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get system health metrics (mock data for now)
        health_data = [
            {
                "name": "CPU Usage",
                "value": 75
            },
            {
                "name": "Memory Usage",
                "value": 60
            },
            {
                "name": "Disk Space",
                "value": 85
            },
            {
                "name": "Network Latency",
                "value": 90
            }
        ]
        return health_data
    except Exception as e:
        logger.error(f"Error fetching system health: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching system health metrics") 