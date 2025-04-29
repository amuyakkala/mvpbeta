from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from ..models.trace import TraceData
from ..models.issue import IssueCreate
from ..models.notification import NotificationCreate
from ..agents.rca_agent import RCAAgent
from ..services.notification import NotificationService
from ..models.audit_log import AuditLog

logger = logging.getLogger(__name__)

class Orchestrator:
    """Orchestrator for managing the end-to-end flow of trace analysis and issue creation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.rca_agent = RCAAgent()
        self.notification_service = NotificationService(db)
    
    async def process_trace(
        self,
        trace_data: Dict[str, Any],
        user_id: int,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a trace file through the entire pipeline.
        
        Args:
            trace_data: Trace data to process
            user_id: ID of the user uploading the trace
            file_name: Optional name of the uploaded file
            
        Returns:
            Dict containing processing results
        """
        try:
            # Create trace record
            db_trace = TraceData(
                user_id=user_id,
                content=trace_data,
                created_at=datetime.utcnow()
            )
            self.db.add(db_trace)
            self.db.commit()
            self.db.refresh(db_trace)
            
            # Run RCA analysis
            analysis_result = await self.rca_agent.process(trace_data)
            
            # Create issues if problems found
            issues_created = []
            if analysis_result.get("issues_found", False):
                for issue_data in analysis_result.get("issues", []):
                    issue = IssueCreate(
                        trace_id=db_trace.id,
                        title=f"Detected {issue_data['type']}",
                        description=self._format_issue_description(issue_data),
                        severity=self._get_severity_level(issue_data.get("severity", "low")),
                        status="open",
                        created_by=user_id
                    )
                    self.db.add(issue)
                    issues_created.append(issue)
            
            self.db.commit()
            
            # Send notifications
            if issues_created:
                await self.notification_service.send_notification(
                    NotificationCreate(
                        user_id=user_id,
                        title="New Issues Detected",
                        message=f"RCA analysis found {len(issues_created)} issues in your trace",
                        type="warning",
                        metadata={
                            "trace_id": db_trace.id,
                            "issue_ids": [issue.id for issue in issues_created]
                        }
                    )
                )
            
            # Log the action
            self._log_audit(
                user_id=user_id,
                action_type="trace_processed",
                metadata={
                    "trace_id": db_trace.id,
                    "file_name": file_name,
                    "issues_created": len(issues_created),
                    "analysis_result": analysis_result
                }
            )
            
            return {
                "status": "success",
                "trace_id": db_trace.id,
                "issues_created": len(issues_created),
                "analysis_result": analysis_result
            }
            
        except Exception as e:
            logger.error(f"Error processing trace: {str(e)}")
            self._log_audit(
                user_id=user_id,
                action_type="trace_processing_failed",
                metadata={
                    "error": str(e),
                    "file_name": file_name
                }
            )
            raise
    
    def _format_issue_description(self, issue_data: Dict[str, Any]) -> str:
        """Format issue description from analysis data."""
        description = f"Type: {issue_data['type']}\n"
        description += f"Severity: {issue_data.get('severity', 'unknown')}\n"
        
        if "line_number" in issue_data:
            description += f"Line: {issue_data['line_number']}\n"
        
        if "context" in issue_data:
            description += "\nContext:\n"
            description += "\n".join(issue_data["context"])
        
        if "recommendations" in issue_data:
            description += "\nRecommendations:\n"
            description += issue_data["recommendations"]
        
        return description
    
    def _get_severity_level(self, severity: str) -> int:
        """Convert severity string to numeric level."""
        severity_map = {
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return severity_map.get(severity.lower(), 1)
    
    def _log_audit(self, user_id: int, action_type: str, metadata: Dict[str, Any]) -> None:
        """Log an audit entry."""
        audit_log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        self.db.add(audit_log)
        self.db.commit()
    
    async def validate_trace(self, trace_data: Dict[str, Any]) -> bool:
        """
        Validate trace data.
        
        Args:
            trace_data: Trace data to validate
            
        Returns:
            bool indicating if data is valid
        """
        return await self.rca_agent.validate(trace_data)
    
    async def get_workflow_status(self, trace_id: int, db: Session) -> Dict[str, Any]:
        """
        Get status of workflow for a trace.
        
        Args:
            trace_id: ID of the trace
            db: Database session
            
        Returns:
            Dict containing workflow status
        """
        trace = db.query(TraceData).filter(TraceData.id == trace_id).first()
        if not trace:
            return {"error": "Trace not found"}
        
        issues = db.query(IssueCreate).filter(IssueCreate.trace_id == trace_id).all()
        
        return {
            "trace_id": trace_id,
            "status": "processed" if issues else "pending",
            "issues_count": len(issues),
            "last_updated": trace.updated_at.isoformat() if trace.updated_at else None
        } 