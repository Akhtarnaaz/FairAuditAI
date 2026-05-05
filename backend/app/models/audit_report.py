"""Audit Report ORM model."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.database import Base


class AuditReport(Base):
    __tablename__ = "audit_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    audit_run_id = Column(String, ForeignKey("audit_runs.id"), nullable=False, index=True)
    pdf_filepath = Column(String, nullable=True)
    csv_filepath = Column(String, nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    downloaded_count = Column(Integer, default=0)
