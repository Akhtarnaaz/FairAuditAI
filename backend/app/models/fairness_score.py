"""Fairness Score ORM model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from app.database import Base


class FairnessScore(Base):
    __tablename__ = "fairness_scores"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_run_id = Column(String, ForeignKey("audit_runs.id"), nullable=False, index=True)
    dimension = Column(String, nullable=False)  # gender, caste, language, region
    fairness_score = Column(Float, nullable=False)  # 0.0 to 1.0
    disparity_ratio = Column(Float, nullable=False)  # actual DIRatio
    demographic_parity_diff = Column(Float, nullable=True)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    sample_size = Column(Float, nullable=True)
    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
