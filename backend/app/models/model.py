"""AI Model upload ORM model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from app.database import Base


class MLModel(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    model_name = Column(String, nullable=False)
    model_type = Column(
        SAEnum("classification", "regression", "generation", "multiclass", name="model_type"),
        nullable=False,
    )
    model_filepath = Column(String, nullable=True)  # None for API endpoint models
    api_endpoint = Column(String, nullable=True)  # URL for API-based models
    model_version = Column(String, default="1.0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
