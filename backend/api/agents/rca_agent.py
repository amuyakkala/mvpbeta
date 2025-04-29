from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from .base import BaseAgent
import json
import re
from datetime import datetime
import logging
from ..models import TraceData, IssueCreate
from ..models.database import SessionLocal, Issue
from ..services.notification import NotificationService

logger = logging.getLogger(__name__)

class RCAAgent(BaseAgent):
    """Root Cause Analysis agent for analyzing traces and detecting issues."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.rules = self._load_rules()
        self.notification_service = NotificationService(SessionLocal())
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load predefined rules for RCA."""
        return {
            "error_patterns": [
                {"pattern": r"ERROR|Exception|Failed|Timeout|Warning", "severity": "high"},
                {"pattern": r"Connection refused|Connection reset|Connection timeout", "severity": "high"},
                {"pattern": r"Out of memory|Stack overflow|Buffer overflow", "severity": "critical"},
                {"pattern": r"Deadlock|Race condition|Thread starvation", "severity": "high"},
                {"pattern": r"Invalid input|Validation failed|Format error", "severity": "medium"},
                {"pattern": r"Resource not found|File not found|404", "severity": "medium"},
                {"pattern": r"Permission denied|Access denied|403", "severity": "high"},
                {"pattern": r"Rate limit exceeded|Throttling|429", "severity": "medium"},
                {"pattern": r"Service unavailable|503", "severity": "high"},
                {"pattern": r"Bad gateway|502", "severity": "high"}
            ],
            "performance_thresholds": {
                "response_time": 1000,  # ms
                "error_rate": 0.01,     # 1%
                "throughput": 100,      # req/s
                "cpu_usage": 80,        # %
                "memory_usage": 80,     # %
                "disk_usage": 80,       # %
                "network_latency": 100  # ms
            },
            "correlation_rules": {
                "error_chain": {
                    "pattern": r"caused by|at .*\.java:\d+|at .*\.py:\d+",
                    "group_by": "stack_trace"
                },
                "performance_degradation": {
                    "pattern": r"slow|latency|timeout|delay",
                    "group_by": "endpoint"
                }
            }
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process trace data and perform root cause analysis.
        
        Args:
            data: Trace data to analyze
            
        Returns:
            Dict containing analysis results and detected issues
        """
        try:
            if not await self.validate(data):
                return {"error": "Invalid trace data"}
            
            trace_content = data.get("content", {})
            issues = []
            
            # Extract steps from trace content
            steps = trace_content.get("steps", [])
            
            # Analyze each step
            for step in steps:
                step_type = step.get("step_type", "")
                step_content = json.dumps(step)
                
                # Apply error pattern rules
                step_issues = await self._detect_error_patterns(step_content)
                if step_issues:
                    issues.extend(step_issues)
                
                # Check performance metrics if available
                if "duration_ms" in step:
                    metrics = {"response_time": step["duration_ms"]}
                    step_issues = await self._analyze_performance_metrics(metrics)
                    if step_issues:
                        issues.extend(step_issues)
            
            # Apply correlation rules to the entire trace
            trace_content_str = json.dumps(trace_content)
            issues.extend(await self._apply_correlation_rules(trace_content_str))
            
            # If no issues found with rules, try LLM analysis
            if not issues and self.llm_client:
                llm_analysis = await self._analyze_with_llm(data)
                if llm_analysis:
                    issues.append(llm_analysis)
            
            # Group and deduplicate issues
            issues = await self._group_issues(issues)
            
            if issues:
                return await self._create_issues(data, issues)
            
            return {
                "status": "completed",
                "issues_found": False,
                "issues": [],
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing trace: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "issues_found": False,
                "issues": [],
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    async def _detect_error_patterns(self, content: str) -> List[Dict[str, Any]]:
        """Detect issues using error patterns."""
        issues = []
        for rule in self.rules["error_patterns"]:
            matches = re.finditer(rule["pattern"], content, re.IGNORECASE)
            for match in matches:
                line_number = content[:match.start()].count('\n') + 1
                context = self._get_context(content, match.start(), 3)
                
                issues.append({
                    "type": "error_pattern",
                    "pattern": rule["pattern"],
                    "severity": rule["severity"],
                    "line_number": line_number,
                    "context": context,
                    "timestamp": datetime.now().isoformat(),
                    "category": "error"
                })
        return issues
    
    async def _analyze_performance_metrics(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance metrics against thresholds."""
        issues = []
        for metric, threshold in self.rules["performance_thresholds"].items():
            if metric in metrics and metrics[metric] > threshold:
                issues.append({
                    "type": "performance",
                    "metric": metric,
                    "value": metrics[metric],
                    "threshold": threshold,
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "category": "performance"
                })
        return issues
    
    async def _apply_correlation_rules(self, content: str) -> List[Dict[str, Any]]:
        """Apply correlation rules to group related issues."""
        issues = []
        for rule_name, rule in self.rules["correlation_rules"].items():
            matches = re.finditer(rule["pattern"], content, re.IGNORECASE)
            for match in matches:
                issues.append({
                    "type": "correlation",
                    "rule": rule_name,
                    "pattern": rule["pattern"],
                    "group_by": rule["group_by"],
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "category": "correlation"
                })
        return issues
    
    async def _group_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group and deduplicate issues."""
        grouped_issues = {}
        for issue in issues:
            key = f"{issue['type']}:{issue.get('pattern', '')}:{issue.get('metric', '')}"
            if key not in grouped_issues:
                grouped_issues[key] = issue
            else:
                # Merge similar issues
                existing = grouped_issues[key]
                existing["count"] = existing.get("count", 1) + 1
                if issue["severity"] > existing["severity"]:
                    existing["severity"] = issue["severity"]
        return list(grouped_issues.values())
    
    async def _create_issues(self, trace_data: Dict[str, Any], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create issues in the database and return the result."""
        db = SessionLocal()
        try:
            created_issues = []
            for issue in issues:
                # Ensure user_id is present in trace_data
                if "user_id" not in trace_data:
                    logger.error("Missing user_id in trace_data")
                    raise ValueError("Missing user_id in trace_data")
                
                # Create issue in database
                db_issue = Issue(
                    trace_id=trace_data["id"],
                    user_id=trace_data["user_id"],
                    title=f"RCA: {issue['type']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    description=json.dumps(issue),
                    severity=issue["severity"],
                    status="open",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                db.add(db_issue)
                db.commit()
                db.refresh(db_issue)
                created_issues.append(db_issue)
                
                # Send notification
                notification_data = {
                    "user_id": trace_data["user_id"],
                    "title": f"New Issue Detected: {issue['type']}",
                    "message": f"RCA analysis found a {issue['severity']} severity issue",
                    "notification_metadata": {
                        "trace_id": trace_data["id"],
                        "issue_id": db_issue.id,
                        "issue_type": issue["type"],
                        "severity": issue["severity"]
                    }
                }
                await self.notification_service.send_notification(notification_data)
            
            return {
                "status": "completed",
                "issues_found": True,
                "issues": issues,
                "issue_ids": [issue.id for issue in created_issues],
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to create issues: {str(e)}")
            db.rollback()
            return {
                "status": "error",
                "error": str(e),
                "issues": issues
            }
        finally:
            db.close()
    
    async def validate(self, data: Dict[str, Any]) -> bool:
        """Validate trace data."""
        required_fields = ["content", "timestamp", "id"]
        return all(field in data for field in required_fields)
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get agent metadata."""
        return {
            "name": "RCA Agent",
            "version": "1.0.0",
            "capabilities": [
                "error_detection",
                "performance_analysis",
                "llm_analysis",
                "correlation_analysis",
                "issue_grouping"
            ]
        }
    
    def _get_context(self, content: str, position: int, lines: int) -> List[str]:
        """Get context around a position in the content."""
        lines_before = content[:position].split('\n')[-lines:]
        lines_after = content[position:].split('\n')[:lines]
        return lines_before + lines_after
    
    async def _analyze_with_llm(self, trace_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze trace data using LLM."""
        if not self.llm_client:
            return None
            
        try:
            prompt = f"""
            Analyze this trace data for potential issues:
            {trace_data['content']}
            
            Consider the following aspects:
            1. Error patterns and exceptions
            2. Performance bottlenecks
            3. Resource utilization
            4. Security concerns
            5. Integration issues
            
            Provide a detailed analysis with:
            - Issue type
            - Severity
            - Root cause
            - Impact
            - Recommended actions
            """
            
            response = await self.llm_client.analyze(prompt)
            
            if response and "issues" in response:
                return {
                    "type": "llm_analysis",
                    "analysis": response["issues"],
                    "confidence": response.get("confidence", 0.8),
                    "timestamp": datetime.now().isoformat(),
                    "severity": "medium"
                }
        except Exception as e:
            logger.error(f"LLM analysis failed: {str(e)}")
        
        return None 