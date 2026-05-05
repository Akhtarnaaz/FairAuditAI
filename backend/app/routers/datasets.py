"""Datasets router — upload, preview, and manage test datasets."""
import json
from pathlib import Path
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import DATASETS_DIR, MAX_DATASET_SIZE_MB, ALLOWED_DATASET_EXTENSIONS
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.dataset import DatasetUploadResponse, DatasetListResponse
from app.middleware.auth_middleware import require_admin, get_current_user

router = APIRouter()


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    dataset_name: str = Form(None),
    file: UploadFile = File(None),
    demo_dataset_key: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Upload a test dataset or select a demo dataset."""
    import shutil

    if demo_dataset_key:
        demo_map = {
            "loan": "loan_dataset.csv",
            "loan_extreme": "loan_extreme_dataset.csv",
            "hiring": "hiring_dataset.csv",
            "hiring_extreme": "hiring_extreme_dataset.csv",
            "healthcare": "healthcare_dataset.csv",
            "healthcare_extreme": "healthcare_extreme_dataset.csv",
            "insurance": "insurance_dataset.csv",
            "education": "education_dataset.csv"
        }
        if demo_dataset_key not in demo_map:
            raise HTTPException(400, "Invalid demo dataset key")
        
        demo_filename = demo_map[demo_dataset_key]
        demo_source = Path(__file__).resolve().parent.parent.parent.parent / "demo_test_suite" / demo_filename
        
        if not demo_source.exists():
            raise HTTPException(404, f"Demo dataset file not found at {demo_source}")
            
        filepath = DATASETS_DIR / f"{current_user.id}_{demo_filename}"
        shutil.copy(demo_source, filepath)
        ext = ".csv"
        actual_name = dataset_name or demo_filename.replace('.csv', '')
    elif file:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_DATASET_EXTENSIONS:
            raise HTTPException(400, f"Invalid file type. Allowed: {ALLOWED_DATASET_EXTENSIONS}")

        filepath = DATASETS_DIR / f"{current_user.id}_{file.filename}"
        content = await file.read()

        if len(content) > MAX_DATASET_SIZE_MB * 1024 * 1024:
            raise HTTPException(400, f"File exceeds {MAX_DATASET_SIZE_MB}MB limit")

        with open(filepath, "wb") as f:
            f.write(content)
        actual_name = dataset_name or file.filename.replace(ext, '')
    else:
        raise HTTPException(400, "Provide either a file or a demo dataset key")

    # Parse and validate
    try:
        if ext == ".csv":
            df = pd.read_csv(filepath)
        else:
            df = pd.read_json(filepath)
    except Exception as e:
        filepath.unlink(missing_ok=True)
        raise HTTPException(400, f"Failed to parse file: {str(e)}")

    if len(df) < 10:
        filepath.unlink(missing_ok=True)
        raise HTTPException(400, "Dataset must have at least 10 rows")

    schema_info = {col: str(dtype) for col, dtype in df.dtypes.items()}
    preview = df.head(5).fillna("").to_dict(orient="records")

    dataset = Dataset(
        uploaded_by_user_id=current_user.id,
        dataset_name=actual_name,
        filepath=str(filepath),
        num_rows=len(df),
        num_columns=len(df.columns),
        schema_json=json.dumps(schema_info),
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return DatasetUploadResponse(
        id=dataset.id,
        dataset_name=dataset.dataset_name,
        num_rows=dataset.num_rows,
        num_columns=dataset.num_columns,
        schema_info=schema_info,
        preview=preview,
        created_at=dataset.created_at,
    )


@router.get("/", response_model=list[DatasetListResponse])
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all datasets. Admins see all, users see their own."""
    query = db.query(Dataset)
    if current_user.role != "admin":
        query = query.filter(Dataset.uploaded_by_user_id == current_user.id)
    
    datasets = query.order_by(Dataset.created_at.desc()).all()
    return [DatasetListResponse.model_validate(d) for d in datasets]


@router.get("/{dataset_id}")
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get dataset details with schema and preview."""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    schema_info = json.loads(dataset.schema_json) if dataset.schema_json else {}
    preview = []
    if dataset.filepath and Path(dataset.filepath).exists():
        df = pd.read_csv(dataset.filepath)
        preview = df.head(5).fillna("").to_dict(orient="records")

    return {
        "id": dataset.id,
        "dataset_name": dataset.dataset_name,
        "num_rows": dataset.num_rows,
        "num_columns": dataset.num_columns,
        "schema_info": schema_info,
        "preview": preview,
    }


@router.delete("/{dataset_id}")
def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a dataset."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.uploaded_by_user_id == current_user.id,
    ).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found")

    if dataset.filepath:
        Path(dataset.filepath).unlink(missing_ok=True)

    db.delete(dataset)
    db.commit()
    return {"detail": "Dataset deleted"}
