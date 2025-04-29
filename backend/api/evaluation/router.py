from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...config.database import get_db
from ..models import AuditLog, User
from .deepeval import DeepEvalIntegration
from .metrics import MetricsRegistry
from ..auth.router import get_current_user

router = APIRouter()
deepeval = DeepEvalIntegration()
metrics_registry = MetricsRegistry()

@router.post("/evaluate")
async def evaluate_model(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluate model outputs using DeepEval.
    """
    try:
        result = await deepeval.evaluate(data)
        
        # Log the evaluation
        db_audit = AuditLog(
            user_id=current_user.id,
            action_type="model_evaluation",
            metadata={
                "metrics": result.get("metrics", {}),
                "status": result.get("status")
            }
        )
        db.add(db_audit)
        db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """
    Get all available evaluation metrics.
    """
    return metrics_registry.get_all_metrics()

@router.post("/metrics")
async def register_metric(metric: dict):
    """
    Register a new evaluation metric.
    """
    try:
        metrics_registry.register_metric(metric)
        return {"status": "success", "message": "Metric registered successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 