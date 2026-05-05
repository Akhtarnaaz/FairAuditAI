"""Audit-related schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditCreateRequest(BaseModel):
    model_id: str
    dataset_id: str
    dimensions: dict  # {"gender": true, "caste": true, "language": false, "region": true}
    variation_strategy: str = "systematic"  # systematic, random, exhaustive


class AuditStatusResponse(BaseModel):
    id: str
    status: str
    progress: int
    num_test_cases: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class FairnessScoreResponse(BaseModel):
    dimension: str
    fairness_score: float
    disparity_ratio: float
    demographic_parity_diff: Optional[float] = None
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    status: str  # "fair", "review", "biased"


class BiasExplanationResponse(BaseModel):
    dimension: str
    explanation_text: str
    root_cause: Optional[str] = None
    severity: str
    affected_metric: Optional[str] = None
    legal_implications: Optional[str] = None


class MitigationResponse(BaseModel):
    dimension: str
    recommendation_type: str
    recommendation_text: str
    effort_level: str
    impact_level: str
    priority: int


class AuditResultsResponse(BaseModel):
    audit_id: str
    status: str
    model_name: str
    dataset_name: str
    num_test_cases: int
    overall_fairness_score: float
    fairness_scores: list[FairnessScoreResponse]
    explanations: list[BiasExplanationResponse]
    mitigations: list[MitigationResponse]
    completed_at: Optional[datetime] = None


class AuditListResponse(BaseModel):
    id: str
    model_name: Optional[str] = None
    dataset_name: Optional[str] = None
    status: str
    num_test_cases: int
    overall_score: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
