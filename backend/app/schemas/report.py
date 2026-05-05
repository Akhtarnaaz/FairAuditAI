"""Report schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReportResponse(BaseModel):
    id: str
    audit_run_id: str
    pdf_url: Optional[str] = None
    csv_url: Optional[str] = None
    generated_at: Optional[datetime] = None
    downloaded_count: int = 0


class ReportListResponse(BaseModel):
    id: str
    audit_run_id: str
    model_name: Optional[str] = None
    overall_score: Optional[float] = None
    generated_at: Optional[datetime] = None
    downloaded_count: int = 0
