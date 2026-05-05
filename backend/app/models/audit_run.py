"""Audit Run ORM model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum as SAEnum
from app.database import Base


class AuditRun(Base):
    __tablename__ = "audit_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    counterfactual_config = Column(Text, nullable=True)  # JSON string
    variation_strategy = Column(String, default="systematic")  # systematic, random, exhaustive
    status = Column(
        SAEnum("pending", "running", "completed", "failed", name="audit_status"),
        default="pending",
        nullable=False,
    )
    num_test_cases = Column(Integer, default=0)
    progress = Column(Integer, default=0)  # 0-100 percentage
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
