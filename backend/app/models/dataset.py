"""Dataset ORM model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    uploaded_by_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    dataset_name = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    num_rows = Column(Integer, nullable=True)
    num_columns = Column(Integer, nullable=True)
    schema_json = Column(Text, nullable=True)  # JSON string: {col: dtype, ...}
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
