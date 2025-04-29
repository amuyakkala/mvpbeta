from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum

class MetricType(str, Enum):
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    RCA_QUALITY = "rca_quality"
    ISSUE_DETECTION = "issue_detection"
    SEVERITY_ACCURACY = "severity_accuracy"
    CUSTOM = "custom"

@dataclass
class Metric:
    name: str
    type: MetricType
    description: str
    threshold: float
    weight: float = 1.0
    metadata: Dict[str, Any] = None

class MetricsRegistry:
    """Registry for evaluation metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, Metric] = {
            "accuracy": Metric(
                name="Accuracy",
                type=MetricType.ACCURACY,
                description="Overall correctness of predictions",
                threshold=0.9
            ),
            "precision": Metric(
                name="Precision",
                type=MetricType.PRECISION,
                description="Ratio of true positives to all positives",
                threshold=0.85
            ),
            "recall": Metric(
                name="Recall",
                type=MetricType.RECALL,
                description="Ratio of true positives to all actual positives",
                threshold=0.85
            ),
            "f1_score": Metric(
                name="F1 Score",
                type=MetricType.F1_SCORE,
                description="Harmonic mean of precision and recall",
                threshold=0.85
            ),
            "rca_quality": Metric(
                name="RCA Quality",
                type=MetricType.RCA_QUALITY,
                description="Overall quality of root cause analysis",
                threshold=0.8,
                metadata={
                    "components": ["issue_detection", "severity_accuracy", "recommendation_quality"]
                }
            ),
            "issue_detection": Metric(
                name="Issue Detection",
                type=MetricType.ISSUE_DETECTION,
                description="Accuracy of issue detection in traces",
                threshold=0.85,
                metadata={
                    "error_types": ["error", "warning", "performance", "security"]
                }
            ),
            "severity_accuracy": Metric(
                name="Severity Accuracy",
                type=MetricType.SEVERITY_ACCURACY,
                description="Accuracy of severity level assignment",
                threshold=0.8,
                metadata={
                    "severity_levels": ["high", "medium", "low"]
                }
            )
        }
    
    def get_metric(self, name: str) -> Metric:
        """
        Get a metric by name.
        
        Args:
            name: Name of the metric
            
        Returns:
            Metric object
        """
        return self.metrics.get(name.lower())
    
    def register_metric(self, metric: Metric) -> None:
        """
        Register a new metric.
        
        Args:
            metric: Metric to register
        """
        self.metrics[metric.name.lower()] = metric
    
    def get_all_metrics(self) -> List[Metric]:
        """
        Get all registered metrics.
        
        Returns:
            List of all metrics
        """
        return list(self.metrics.values())
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[Metric]:
        """
        Get metrics by type.
        
        Args:
            metric_type: Type of metrics to retrieve
            
        Returns:
            List of metrics of the specified type
        """
        return [m for m in self.metrics.values() if m.type == metric_type]
    
    def get_rca_metrics(self) -> List[Metric]:
        """
        Get metrics specifically for RCA evaluation.
        
        Returns:
            List of RCA-specific metrics
        """
        return [
            self.metrics["rca_quality"],
            self.metrics["issue_detection"],
            self.metrics["severity_accuracy"]
        ] 