"""Dataset schemas."""
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DatasetUploadResponse(BaseModel):
    id: str
    dataset_name: str
    num_rows: Optional[int] = None
    num_columns: Optional[int] = None
    schema_info: Optional[dict] = None
    preview: Optional[list[dict]] = None
    created_at: Optional[datetime] = None


class DatasetListResponse(BaseModel):
    id: str
    dataset_name: str
    num_rows: Optional[int] = None
    num_columns: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
