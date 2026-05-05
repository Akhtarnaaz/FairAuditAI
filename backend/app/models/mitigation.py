"""Mitigation Recommendation ORM model."""
import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum as SAEnum
from app.database import Base


class MitigationRecommendation(Base):
    __tablename__ = "mitigation_recommendations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_run_id = Column(String, ForeignKey("audit_runs.id"), nullable=False, index=True)
    dimension = Column(String, nullable=False)
    recommendation_type = Column(
        SAEnum("data_level", "feature_level", "output_level", "model_level", "best_practice", name="rec_type"),
        nullable=False,
    )
    recommendation_text = Column(Text, nullable=False)
    effort_level = Column(
        SAEnum("low", "medium", "high", name="effort_level"),
        nullable=False,
    )
    impact_level = Column(
        SAEnum("low", "medium", "high", "very_high", name="impact_level"),
        nullable=False,
    )
    priority = Column(Integer, nullable=False)  # 1 = highest
