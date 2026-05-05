"""Model upload schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ModelUploadResponse(BaseModel):
    id: str
    model_name: str
    model_type: str
    model_version: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ModelListResponse(BaseModel):
    id: str
    model_name: str
    model_type: str
    model_version: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
