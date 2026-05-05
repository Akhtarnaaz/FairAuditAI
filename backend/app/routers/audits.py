"""Audits router — create, configure, run, and view bias audit results."""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import joblib
import pickle


# Add parent to path for bias_engine imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.model import MLModel
from app.models.dataset import Dataset
from app.models.audit_run import AuditRun
from app.models.fairness_score import FairnessScore
from app.models.bias_explanation import BiasExplanation
from app.models.mitigation import MitigationRecommendation
from app.schemas.audit import (
    AuditCreateRequest, AuditStatusResponse, AuditResultsResponse,
    FairnessScoreResponse, BiasExplanationResponse, MitigationResponse,
    AuditListResponse,
)
from app.middleware.auth_middleware import require_admin, get_current_user
from bias_engine.counterfactual import preview_counterfactuals
from bias_engine.detector import run_bias_detection
from bias_engine.scorer import calculate_fairness_scores, calculate_overall_score
from bias_engine.explainer import generate_explanations
from bias_engine.recommender import generate_recommendations

router = APIRouter()


def _run_audit_pipeline(audit_id: str):
    """Background task: run the full bias detection pipeline."""
    # Ensure pickled models can find their classes even if saved as __main__
    import bias_engine.model_utils
    sys.modules['__main__'].NeutralWrapper = bias_engine.model_utils.NeutralWrapper
    sys.modules['__main__'].BiasPreprocessor = bias_engine.model_utils.BiasPreprocessor

    db = SessionLocal()
    try:
        audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
        if not audit:
            return

        audit.status = "running"
        audit.started_at = datetime.now(timezone.utc)
        audit.progress = 10
        db.commit()

        # Load dataset
        dataset = db.query(Dataset).filter(Dataset.id == audit.dataset_id).first()
        if not dataset or not Path(dataset.filepath).exists():
            audit.status = "failed"
            audit.error_message = "Dataset file not found"
            db.commit()
            return

        df = pd.read_csv(dataset.filepath)
        config = json.loads(audit.counterfactual_config) if audit.counterfactual_config else {}
        dims = config.get("dimensions", {"gender": True, "caste": True, "language": True, "region": True})

        audit.progress = 25
        db.commit()

        # Load model if available
        ml_model = db.query(MLModel).filter(MLModel.id == audit.model_id).first()
        loaded_model = None
        if ml_model and ml_model.model_filepath:
            model_path = Path(ml_model.model_filepath)
            if model_path.exists():
                try:
                    if model_path.suffix == ".joblib":
                        loaded_model = joblib.load(model_path)
                    else:
                        with open(model_path, "rb") as f:
                            loaded_model = pickle.load(f)
                except Exception as model_err:
                    print(f"Error loading model {model_path}: {model_err}")
                    # Fallback to MockModel if loading fails? Or fail the audit?
                    # For now, let's fail it to be explicit.
                    audit.status = "failed"
                    audit.error_message = f"Failed to load model file: {model_err}"
                    db.commit()
                    return

        # Run bias detection
        results = run_bias_detection(df, dims, audit.variation_strategy, model=loaded_model)
        audit.num_test_cases = results["num_test_cases"]
        audit.progress = 60
        db.commit()

        # Calculate fairness scores
        scores = calculate_fairness_scores(results["dimension_stats"])
        audit.progress = 75
        db.commit()

        # Store fairness scores
        for dim, score_data in scores.items():
            fs = FairnessScore(
                audit_run_id=audit.id,
                dimension=dim,
                fairness_score=score_data["fairness_score"],
                disparity_ratio=score_data["disparity_ratio"],
                demographic_parity_diff=score_data["demographic_parity_diff"],
                confidence_lower=score_data["confidence_lower"],
                confidence_upper=score_data["confidence_upper"],
                sample_size=score_data["sample_size"],
            )
            db.add(fs)

        # Generate and store explanations
        explanations = generate_explanations(scores, results["dimension_stats"])
        for expl in explanations:
            be = BiasExplanation(
                audit_run_id=audit.id,
                dimension=expl["dimension"],
                explanation_text=expl["explanation_text"],
                root_cause=expl["root_cause"],
                severity=expl["severity"],
                affected_metric=expl["affected_metric"],
                legal_implications=expl["legal_implications"],
            )
            db.add(be)

        audit.progress = 90
        db.commit()

        # Generate and store recommendations
        recs = generate_recommendations(scores)
        for rec in recs:
            mr = MitigationRecommendation(
                audit_run_id=audit.id,
                dimension=rec["dimension"],
                recommendation_type=rec["recommendation_type"],
                recommendation_text=rec["recommendation_text"],
                effort_level=rec["effort_level"],
                impact_level=rec["impact_level"],
                priority=rec["priority"],
            )
            db.add(mr)

        audit.status = "completed"
        audit.progress = 100
        audit.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
        if audit:
            audit.status = "failed"
            audit.error_message = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/", response_model=AuditStatusResponse)
def create_audit(
    data: AuditCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new audit run."""
    model = db.query(MLModel).filter(MLModel.id == data.model_id).first()
    if not model:
        raise HTTPException(404, "Model not found")

    dataset = db.query(Dataset).filter(Dataset.id == data.dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    audit = AuditRun(
        admin_user_id=current_user.id,
        model_id=data.model_id,
        dataset_id=data.dataset_id,
        counterfactual_config=json.dumps({"dimensions": data.dimensions}),
        variation_strategy=data.variation_strategy,
        status="pending",
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    return AuditStatusResponse.model_validate(audit)


@router.post("/{audit_id}/run", response_model=AuditStatusResponse)
def run_audit(
    audit_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Start running a bias detection audit (async)."""
    audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
    if not audit:
        raise HTTPException(404, "Audit not found")
    if audit.status == "running":
        raise HTTPException(400, "Audit is already running")

    audit.status = "running"
    audit.progress = 0
    db.commit()

    background_tasks.add_task(_run_audit_pipeline, audit_id)

    return AuditStatusResponse.model_validate(audit)


@router.get("/{audit_id}/status", response_model=AuditStatusResponse)
def get_audit_status(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Poll audit execution status."""
    audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
    if not audit:
        raise HTTPException(404, "Audit not found")
    return AuditStatusResponse.model_validate(audit)


@router.get("/{audit_id}/results", response_model=AuditResultsResponse)
def get_audit_results(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full audit results including scores, explanations, mitigations."""
    audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
    if not audit:
        raise HTTPException(404, "Audit not found")

    model = db.query(MLModel).filter(MLModel.id == audit.model_id).first()
    dataset = db.query(Dataset).filter(Dataset.id == audit.dataset_id).first()

    scores = db.query(FairnessScore).filter(FairnessScore.audit_run_id == audit_id).all()
    explanations = db.query(BiasExplanation).filter(BiasExplanation.audit_run_id == audit_id).all()
    mitigations = db.query(MitigationRecommendation).filter(
        MitigationRecommendation.audit_run_id == audit_id
    ).order_by(MitigationRecommendation.priority).all()

    score_responses = []
    for s in scores:
        status = "fair" if s.fairness_score >= 0.8 else "review" if s.fairness_score >= 0.5 else "biased"
        score_responses.append(FairnessScoreResponse(
            dimension=s.dimension,
            fairness_score=s.fairness_score,
            disparity_ratio=s.disparity_ratio,
            demographic_parity_diff=s.demographic_parity_diff,
            confidence_lower=s.confidence_lower,
            confidence_upper=s.confidence_upper,
            status=status,
        ))

    overall = sum(s.fairness_score for s in scores) / len(scores) if scores else 0

    return AuditResultsResponse(
        audit_id=audit.id,
        status=audit.status,
        model_name=model.model_name if model else "Unknown",
        dataset_name=dataset.dataset_name if dataset else "Unknown",
        num_test_cases=audit.num_test_cases,
        overall_fairness_score=round(overall, 4),
        fairness_scores=score_responses,
        explanations=[BiasExplanationResponse(
            dimension=e.dimension,
            explanation_text=e.explanation_text,
            root_cause=e.root_cause,
            severity=e.severity,
            affected_metric=e.affected_metric,
            legal_implications=e.legal_implications,
        ) for e in explanations],
        mitigations=[MitigationResponse(
            dimension=m.dimension,
            recommendation_type=m.recommendation_type,
            recommendation_text=m.recommendation_text,
            effort_level=m.effort_level,
            impact_level=m.impact_level,
            priority=m.priority,
        ) for m in mitigations],
        completed_at=audit.completed_at,
    )


@router.get("/", response_model=list[AuditListResponse])
def list_audits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all audit runs."""
    if current_user.role == "admin":
        audits = db.query(AuditRun).order_by(AuditRun.created_at.desc()).all()
    else:
        audits = db.query(AuditRun).filter(
            AuditRun.status == "completed"
        ).order_by(AuditRun.created_at.desc()).all()

    results = []
    for a in audits:
        model = db.query(MLModel).filter(MLModel.id == a.model_id).first()
        dataset = db.query(Dataset).filter(Dataset.id == a.dataset_id).first()
        scores = db.query(FairnessScore).filter(FairnessScore.audit_run_id == a.id).all()
        overall = sum(s.fairness_score for s in scores) / len(scores) if scores else None

        results.append(AuditListResponse(
            id=a.id,
            model_name=model.model_name if model else None,
            dataset_name=dataset.dataset_name if dataset else None,
            status=a.status,
            num_test_cases=a.num_test_cases,
            overall_score=round(overall, 4) if overall else None,
            created_at=a.created_at,
        ))

    return results


@router.post("/{audit_id}/preview")
def preview_counterfactual_pairs(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Preview counterfactual pairs before running audit."""
    audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
    if not audit:
        raise HTTPException(404, "Audit not found")

    dataset = db.query(Dataset).filter(Dataset.id == audit.dataset_id).first()
    if not dataset or not Path(dataset.filepath).exists():
        raise HTTPException(404, "Dataset not found")

    df = pd.read_csv(dataset.filepath)
    config = json.loads(audit.counterfactual_config) if audit.counterfactual_config else {}
    dims = config.get("dimensions", {"gender": True})

    previews = preview_counterfactuals(df, dims, audit.variation_strategy)
    return {"previews": previews, "estimated_pairs": len(df) * sum(1 for v in dims.values() if v)}


@router.delete("/all/clear")
def clear_all_audits(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete all audit runs and associated data."""
    db.query(FairnessScore).delete()
    db.query(BiasExplanation).delete()
    db.query(MitigationRecommendation).delete()
    db.query(AuditRun).delete()
    db.commit()
    return {"detail": "All audits cleared successfully"}


@router.delete("/{audit_id}")
def delete_audit(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete an audit run and its associated scores, explanations, and mitigations."""
    audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
    if not audit:
        raise HTTPException(404, "Audit not found")

    # Cascade delete is usually handled by DB, but we can do it explicitly if needed.
    # Since we defined relationships (or just let the DB handle it if cascading is setup).
    # Let's delete explicitly to be safe.
    db.query(FairnessScore).filter(FairnessScore.audit_run_id == audit_id).delete()
    db.query(BiasExplanation).filter(BiasExplanation.audit_run_id == audit_id).delete()
    db.query(MitigationRecommendation).filter(MitigationRecommendation.audit_run_id == audit_id).delete()
    
    db.delete(audit)
    db.commit()
    return {"detail": "Audit deleted successfully"}

