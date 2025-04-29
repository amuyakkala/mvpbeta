from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import status

from api.database.database import get_db
from api.models.database import Issue, User
from api.models.issue import IssueCreate, IssueUpdate, IssueFilter, IssueResponse
from api.auth.router import get_current_user

router = APIRouter(
    prefix="/issues",
    tags=["issues"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=IssueResponse)
async def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new issue."""
    db_issue = Issue(
        trace_id=issue.trace_id,
        user_id=current_user.id,
        title=issue.title,
        description=issue.description,
        severity=issue.severity,
        status=issue.status
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return IssueResponse.from_orm(db_issue)

@router.get("/", response_model=Dict[str, Any])
async def get_issues(
    filter: IssueFilter = Depends(),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a list of issues with filtering and pagination.
    By default, only shows issues for the current user.
    """
    query = db.query(Issue).filter(Issue.user_id == current_user.id)
    
    # Apply filters
    if filter.trace_id:
        query = query.filter(Issue.trace_id == filter.trace_id)
    if filter.status:
        query = query.filter(Issue.status == filter.status)
    if filter.severity:
        query = query.filter(Issue.severity == filter.severity)
    if filter.start_date:
        query = query.filter(Issue.created_at >= filter.start_date)
    if filter.end_date:
        query = query.filter(Issue.created_at <= filter.end_date)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    issues = query.offset(skip).limit(limit).all()
    
    # Convert to response model
    issues_response = [IssueResponse.from_orm(issue) for issue in issues]
    
    return {
        "items": issues_response,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific issue by ID."""
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.user_id == current_user.id
    ).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return IssueResponse.from_orm(issue)

@router.put("/{issue_id}", response_model=IssueResponse)
async def update_issue(
    issue_id: int,
    issue: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an issue."""
    db_issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.user_id == current_user.id
    ).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    update_data = issue.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_issue, key, value)
    
    # Update resolved_at if status is changed to RESOLVED or CLOSED
    if issue.status in ["resolved", "closed"] and db_issue.status not in ["resolved", "closed"]:
        db_issue.resolved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_issue)
    return IssueResponse.from_orm(db_issue)

@router.delete("/{issue_id}")
async def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an issue."""
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.user_id == current_user.id
    ).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db.delete(issue)
    db.commit()
    return {"message": "Issue deleted successfully"} 