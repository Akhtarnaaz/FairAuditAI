"""Bias Explanation ORM model."""
import uuid
from sqlalchemy import Column, String, ForeignKey, Text, Enum as SAEnum
from app.database import Base


class BiasExplanation(Base):
    __tablename__ = "bias_explanations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_run_id = Column(String, ForeignKey("audit_runs.id"), nullable=False, index=True)
    dimension = Column(String, nullable=False)
    explanation_text = Column(Text, nullable=False)
    root_cause = Column(String, nullable=True)
    severity = Column(
        SAEnum("low", "medium", "high", name="severity_level"),
        nullable=False,
    )
    affected_metric = Column(String, nullable=True)
    legal_implications = Column(Text, nullable=True)
