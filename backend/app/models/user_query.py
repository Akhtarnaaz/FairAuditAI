from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

class UserQuery(Base):
    __tablename__ = "user_queries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    query_text = Column(String)
    response_text = Column(String)
    fairness_status = Column(String)  # fair, slight_bias, biased
    fairness_explanation = Column(String)
    counterfactual_comparison = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
