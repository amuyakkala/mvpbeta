from fastapi import APIRouter
from api.auth.router import router as auth_router
from api.logs.router import router as logs_router
from api.issues.router import router as issues_router
from api.audit.router import router as audit_router
from api.dashboard.router import router as dashboard_router
from api.notifications.router import router as notifications_router
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create the main API router
api_router = APIRouter()

# Include essential routers for MVP
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(logs_router, tags=["logs"])
api_router.include_router(issues_router, tags=["issues"])
api_router.include_router(audit_router, tags=["audit"])
api_router.include_router(dashboard_router, tags=["dashboard"])
api_router.include_router(notifications_router, tags=["notifications"]) 