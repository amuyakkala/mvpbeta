from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from .base import BaseAgent
import json
import re
from datetime import datetime, timedelta
import logging
from ..models import TraceData, IssueCreate
from ..models.database import SessionLocal, Issue, Trace, User
from ..services.notification import NotificationService
from ..services.audit import AuditService
from api.services.external_notification import ExternalNotificationService
import os

logger = logging.getLogger(__name__)

class RCAAgent(BaseAgent):
    """Root Cause Analysis agent for analyzing traces and detecting issues."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.rules = self._load_rules()
        self.notification_service = NotificationService(SessionLocal())
        self.audit_service = AuditService(SessionLocal())
        self.baselines = {}  # Store performance baselines
        self.external_notification = ExternalNotificationService()
        logger.info("RCA Agent initialized with audit service and external notification service")
    
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
                {"pattern": r"Bad gateway|502", "severity": "high"},
                {"pattern": r"CircuitBreakerOpen|RateLimitExceeded|Throttling", "severity": "high", "category": "resilience"},
                {"pattern": r"Deadlock|RaceCondition|ThreadStarvation", "severity": "critical", "category": "concurrency"},
                {"pattern": r"MemoryLeak|ResourceLeak|HandleLeak", "severity": "critical", "category": "resource"},
                {"pattern": r"SecurityException|AccessDenied|Unauthorized", "severity": "high", "category": "security"},
                {"pattern": r"ValidationError|SchemaError|FormatError", "severity": "medium", "category": "validation"}
            ],
            "performance_thresholds": {
                "response_time": 1000,  # ms
                "error_rate": 0.01,     # 1%
                "throughput": 100,      # req/s
                "cpu_usage": 80,        # %
                "memory_usage": 80,     # %
                "disk_usage": 80,       # %
                "network_latency": 100,  # ms
                "p95_latency": 2000,    # ms
                "p99_latency": 5000,    # ms
                "concurrent_users": 1000,
                "queue_length": 100,
                "retry_rate": 0.1,      # 10%
                "timeout_rate": 0.05    # 5%
            },
            "correlation_rules": {
                "error_chain": {
                    "pattern": r"caused by|at .*\.java:\d+|at .*\.py:\d+",
                    "group_by": "stack_trace"
                },
                "performance_degradation": {
                    "pattern": r"slow|latency|timeout|delay",
                    "group_by": "endpoint"
                },
                "temporal_correlation": {
                    "pattern": r"within \d+ (ms|s|m|h)",
                    "group_by": "time_window"
                },
                "service_dependency": {
                    "pattern": r"calling|invoking|requesting",
                    "group_by": "service_name"
                },
                "resource_correlation": {
                    "pattern": r"CPU|Memory|Disk|Network",
                    "group_by": "resource_type"
                }
            },
            "trend_analysis": {
                "window_size": 3600,  # 1 hour in seconds
                "min_data_points": 10,
                "threshold_change": 0.2  # 20% change threshold
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
            logger.info(f"Starting trace analysis for trace {data.get('id')}")
            # Log start of analysis
            audit_log = await self.audit_service.log_system_action(
                action_type="trace_analysis_start",
                resource_type="trace",
                meta_data={
                    "trace_id": data.get("id"),
                    "file_name": data.get("file_name"),
                    "file_size": data.get("file_size")
                }
            )
            logger.info(f"Audit log created for trace analysis start: {audit_log.id if audit_log else 'None'}")
            
            if not await self.validate(data):
                logger.warning(f"Invalid trace data for trace {data.get('id')}")
                audit_log = await self.audit_service.log_system_action(
                    action_type="trace_analysis_failed",
                    resource_type="trace",
                    meta_data={
                        "trace_id": data.get("id"),
                        "reason": "Invalid trace data"
                    }
                )
                logger.info(f"Audit log created for trace analysis failure: {audit_log.id if audit_log else 'None'}")
                return {"error": "Invalid trace data"}
            
            trace_content = data.get("content", {})
            issues = []
            
            # Extract steps from trace content
            steps = trace_content.get("steps", [])
            logger.info(f"Processing {len(steps)} steps in trace {data.get('id')}")
            
            # Analyze each step
            for step in steps:
                step_type = step.get("step_type", "")
                step_content = json.dumps(step)
                
                # Apply error pattern rules
                step_issues = await self._detect_error_patterns(step_content)
                if step_issues:
                    issues.extend(step_issues)
                    # Log detected issues
                    for issue in step_issues:
                        audit_log = await self.audit_service.log_system_action(
                            action_type="issue_detected",
                            resource_type="trace",
                            meta_data={
                                "trace_id": data.get("id"),
                                "issue_type": issue["type"],
                                "severity": issue["severity"],
                                "pattern": issue.get("pattern", ""),
                                "line_number": issue.get("line_number", 0)
                            }
                        )
                        logger.info(f"Audit log created for issue detection: {audit_log.id if audit_log else 'None'}")
                
                # Check performance metrics if available
                if "duration_ms" in step:
                    metrics = {"response_time": step["duration_ms"]}
                    step_issues = await self._analyze_performance_metrics(metrics)
                    if step_issues:
                        issues.extend(step_issues)
                        # Log performance issues
                        for issue in step_issues:
                            audit_log = await self.audit_service.log_system_action(
                                action_type="performance_issue_detected",
                                resource_type="trace",
                                meta_data={
                                    "trace_id": data.get("id"),
                                    "metric": issue["metric"],
                                    "value": issue["value"],
                                    "threshold": issue["threshold"]
                                }
                            )
                            logger.info(f"Audit log created for performance issue: {audit_log.id if audit_log else 'None'}")
            
            # Apply correlation rules to the entire trace
            trace_content_str = json.dumps(trace_content)
            correlation_issues = await self._apply_correlation_rules(trace_content_str)
            issues.extend(correlation_issues)
            
            # Log correlation findings
            for issue in correlation_issues:
                audit_log = await self.audit_service.log_system_action(
                    action_type="correlation_found",
                    resource_type="trace",
                    meta_data={
                        "trace_id": data.get("id"),
                        "rule": issue["rule"],
                        "group_by": issue["group_by"]
                    }
                )
                logger.info(f"Audit log created for correlation finding: {audit_log.id if audit_log else 'None'}")
            
            # If no issues found with rules, try LLM analysis
            if not issues and self.llm_client:
                logger.info("No issues found with rules, trying LLM analysis")
                llm_analysis = await self._analyze_with_llm(data)
                if llm_analysis:
                    issues.append(llm_analysis)
                    audit_log = await self.audit_service.log_system_action(
                        action_type="llm_analysis_completed",
                        resource_type="trace",
                        meta_data={
                            "trace_id": data.get("id"),
                            "analysis_type": "llm",
                            "findings": llm_analysis
                        }
                    )
                    logger.info(f"Audit log created for LLM analysis: {audit_log.id if audit_log else 'None'}")
            
            # Group and deduplicate issues
            issues = await self._group_issues(issues)
            
            if issues:
                logger.info(f"Found {len(issues)} issues in trace {data.get('id')}")
                result = await self._create_issues(data, issues)
                # Log completion with issues
                audit_log = await self.audit_service.log_system_action(
                    action_type="trace_analysis_completed",
                    resource_type="trace",
                    meta_data={
                        "trace_id": data.get("id"),
                        "issues_found": True,
                        "issue_count": len(issues),
                        "severities": [issue["severity"] for issue in issues]
                    }
                )
                logger.info(f"Audit log created for trace analysis completion: {audit_log.id if audit_log else 'None'}")
                return result
            
            # Log completion without issues
            logger.info(f"No issues found in trace {data.get('id')}")
            audit_log = await self.audit_service.log_system_action(
                action_type="trace_analysis_completed",
                resource_type="trace",
                meta_data={
                    "trace_id": data.get("id"),
                    "issues_found": False
                }
            )
            logger.info(f"Audit log created for trace analysis completion (no issues): {audit_log.id if audit_log else 'None'}")
            
            return {
                "status": "completed",
                "issues_found": False,
                "issues": [],
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing trace: {str(e)}")
            # Log error
            audit_log = await self.audit_service.log_system_action(
                action_type="trace_analysis_failed",
                resource_type="trace",
                meta_data={
                    "trace_id": data.get("id"),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            logger.info(f"Audit log created for trace analysis error: {audit_log.id if audit_log else 'None'}")
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
        """Enhanced performance analysis with trend detection."""
        issues = []
        
        # Check against static thresholds
        for metric, threshold in self.rules["performance_thresholds"].items():
            if metric in metrics:
                value = metrics[metric]
                
                # Check absolute threshold
                if value > threshold:
                    issues.append({
                        "type": "performance_threshold",
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "severity": "medium",
                        "timestamp": datetime.now().isoformat(),
                        "category": "performance"
                    })
                
                # Check trend if we have historical data
                if metric in self.baselines:
                    baseline = self.baselines[metric]
                    trend = self._calculate_trend(value, baseline)
                    
                    if abs(trend) > self.rules["trend_analysis"]["threshold_change"]:
                        issues.append({
                            "type": "performance_trend",
                            "metric": metric,
                            "value": value,
                            "baseline": baseline,
                            "trend": trend,
                            "severity": "medium" if abs(trend) < 0.5 else "high",
                            "timestamp": datetime.now().isoformat(),
                            "category": "performance"
                        })
                
                # Update baseline
                self._update_baseline(metric, value)
        
        return issues
    
    def _calculate_trend(self, current: float, baseline: Dict[str, Any]) -> float:
        """Calculate performance trend."""
        if not baseline.get("values"):
            return 0
        
        avg_baseline = sum(baseline["values"]) / len(baseline["values"])
        return (current - avg_baseline) / avg_baseline if avg_baseline != 0 else 0
    
    def _update_baseline(self, metric: str, value: float):
        """Update performance baseline."""
        if metric not in self.baselines:
            self.baselines[metric] = {
                "values": [],
                "last_update": datetime.now()
            }
        
        baseline = self.baselines[metric]
        baseline["values"].append(value)
        
        # Keep only recent values within window
        window_size = self.rules["trend_analysis"]["window_size"]
        cutoff_time = datetime.now() - timedelta(seconds=window_size)
        
        baseline["values"] = [
            v for v, t in zip(baseline["values"], baseline.get("timestamps", []))
            if t > cutoff_time
        ]
        
        baseline["last_update"] = datetime.now()
    
    async def _apply_correlation_rules(self, content: str) -> List[Dict[str, Any]]:
        """Enhanced correlation analysis."""
        issues = []
        
        # Apply all correlation rules
        for rule_name, rule in self.rules["correlation_rules"].items():
            matches = re.finditer(rule["pattern"], content, re.IGNORECASE)
            
            for match in matches:
                # Extract context
                context = self._get_context(content, match.start(), 5)
                
                # Create correlation issue
                issue = {
                    "type": "correlation",
                    "rule": rule_name,
                    "pattern": rule["pattern"],
                    "group_by": rule["group_by"],
                    "context": context,
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "category": "correlation"
                }
                
                # Add specific metadata based on rule type
                if rule_name == "temporal_correlation":
                    issue["time_window"] = self._extract_time_window(match.group())
                elif rule_name == "service_dependency":
                    issue["service_name"] = self._extract_service_name(match.group())
                elif rule_name == "resource_correlation":
                    issue["resource_type"] = self._extract_resource_type(match.group())
                
                issues.append(issue)
        
        return issues
    
    def _extract_time_window(self, text: str) -> Optional[str]:
        """Extract time window from correlation text."""
        match = re.search(r"within (\d+ (ms|s|m|h))", text)
        return match.group(1) if match else None
    
    def _extract_service_name(self, text: str) -> Optional[str]:
        """Extract service name from correlation text."""
        match = re.search(r"(calling|invoking|requesting) (\w+)", text)
        return match.group(2) if match else None
    
    def _extract_resource_type(self, text: str) -> Optional[str]:
        """Extract resource type from correlation text."""
        match = re.search(r"(CPU|Memory|Disk|Network)", text)
        return match.group(1) if match else None
    
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
                # Create issue in database
                db_issue = Issue(
                    trace_id=trace_data["id"],
                    user_id=trace_data["user_id"],
                    title=f"{issue['type']} - {issue.get('pattern', issue.get('metric', 'Unknown'))}",
                    description=json.dumps(issue),
                    status="open",
                    severity=issue["severity"],
                    category=issue["category"],
                    meta_data=issue
                )
                db.add(db_issue)
                db.commit()
                db.refresh(db_issue)
                created_issues.append(db_issue)
                
                # Log issue creation
                audit_log = await self.audit_service.log_system_action(
                    action_type="issue_created",
                    resource_type="issue",
                    resource_id=db_issue.id,
                    meta_data={
                        "trace_id": trace_data["id"],
                        "issue_type": issue["type"],
                        "severity": issue["severity"],
                        "title": db_issue.title
                    }
                )
                logger.info(f"Audit log created for issue creation: {audit_log.id if audit_log else 'None'}")
                
                # Send notification
                await self._notify_about_issue(db_issue, trace_data, trace_data["user"])
            
            return {
                "status": "completed",
                "issues_found": True,
                "issues": [issue.id for issue in created_issues],
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating issues: {str(e)}")
            # Log error
            audit_log = await self.audit_service.log_system_action(
                action_type="issue_creation_failed",
                resource_type="trace",
                meta_data={
                    "trace_id": trace_data["id"],
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            logger.info(f"Audit log created for issue creation error: {audit_log.id if audit_log else 'None'}")
            raise
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

    async def _notify_about_issue(
        self,
        issue: Issue,
        trace: Trace,
        user: User
    ):
        """Notify about a detected issue through multiple channels."""
        try:
            # Format notification content
            notification_content = self.external_notification.format_issue_notification(
                issue_type=issue.issue_type,
                severity=issue.severity,
                message=issue.description,
                metadata={
                    "trace_id": str(trace.id),
                    "service": trace.service_name,
                    "timestamp": str(trace.timestamp),
                    "root_cause": issue.root_cause,
                    "impact": issue.impact,
                    "recommendation": issue.recommendation
                }
            )
            
            # Send Slack notification
            if os.getenv("SLACK_ALERT_CHANNEL"):
                await self.external_notification.send_slack_notification(
                    channel=os.getenv("SLACK_ALERT_CHANNEL"),
                    message=notification_content["slack"]["text"],
                    blocks=notification_content["slack"]["blocks"]
                )
            
            # Send email notification
            if user.email:
                await self.external_notification.send_email_notification(
                    to_email=user.email,
                    subject=notification_content["email"]["subject"],
                    message=notification_content["email"]["text"],
                    html_message=notification_content["email"]["html"]
                )
            
            # Log the notification
            await self.audit_service.log_action(
                user_id=user.id,
                action_type="issue_notification_sent",
                resource_type="issue",
                resource_id=str(issue.id),
                meta_data={
                    "channels": ["slack", "email"],
                    "recipient": user.email,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to send external notifications: {str(e)}")
            # Log the failure
            await self.audit_service.log_action(
                user_id=user.id,
                action_type="notification_failed",
                resource_type="issue",
                resource_id=str(issue.id),
                meta_data={
                    "error": str(e),
                    "issue_type": issue.issue_type
                }
            ) 