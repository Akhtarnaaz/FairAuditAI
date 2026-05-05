"""Models router — upload and manage AI models."""
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import MODELS_DIR, MAX_MODEL_SIZE_MB, ALLOWED_MODEL_EXTENSIONS
from app.models.model import MLModel
from app.models.user import User
from app.schemas.model import ModelUploadResponse, ModelListResponse
from app.middleware.auth_middleware import require_admin, get_current_user

router = APIRouter()


@router.post("/upload", response_model=ModelUploadResponse)
async def upload_model(
    model_name: str = Form(...),
    model_type: str = Form(...),
    model_version: str = Form("1.0"),
    api_endpoint: str = Form(None),
    file: UploadFile = File(None),
    demo_model_key: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Upload an AI model file or register an API endpoint/demo model."""
    filepath = None

    if demo_model_key:
        # Handle demo model selection
        demo_map = {
            "bias_logistic": "loan_bias_logistic.joblib",
            "bias_rf": "loan_bias_random_forest.joblib",
            "neutral": "loan_neutral.joblib"
        }
        if demo_model_key not in demo_map:
            raise HTTPException(400, "Invalid demo model key")
        
        demo_filename = demo_map[demo_model_key]
        demo_source = Path(__file__).resolve().parent.parent.parent.parent / "demo_downloads" / demo_filename
        
        if not demo_source.exists():
            # Fallback to demo/ folder just in case
            demo_source = Path(__file__).resolve().parent.parent.parent.parent / "demo" / demo_filename
            if not demo_source.exists():
                 raise HTTPException(404, f"Demo model file not found at {demo_source}")

        
        # Copy to uploads/models
        filepath = MODELS_DIR / f"{current_user.id}_{demo_filename}"
        shutil.copy(demo_source, filepath)

    elif file:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_MODEL_EXTENSIONS:
            raise HTTPException(400, f"Invalid file type. Allowed: {ALLOWED_MODEL_EXTENSIONS}")

        # Save file
        filepath = MODELS_DIR / f"{current_user.id}_{file.filename}"
        with open(filepath, "wb") as f:
            content = await file.read()
            if len(content) > MAX_MODEL_SIZE_MB * 1024 * 1024:
                raise HTTPException(400, f"File exceeds {MAX_MODEL_SIZE_MB}MB limit")
            f.write(content)

    elif not api_endpoint:
        raise HTTPException(400, "Provide either a model file, API endpoint URL, or demo model key")


    model = MLModel(
        created_by_user_id=current_user.id,
        model_name=model_name,
        model_type=model_type,
        model_filepath=str(filepath) if filepath else None,
        api_endpoint=api_endpoint,
        model_version=model_version,
    )
    db.add(model)
    db.commit()
    db.refresh(model)

    return ModelUploadResponse.model_validate(model)


@router.get("/", response_model=list[ModelListResponse])
def list_models(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all models. Admins see all, users see their own."""
    query = db.query(MLModel)
    if current_user.role != "admin":
        query = query.filter(MLModel.created_by_user_id == current_user.id)
    
    models = query.order_by(MLModel.created_at.desc()).all()
    return [ModelListResponse.model_validate(m) for m in models]


@router.get("/{model_id}", response_model=ModelListResponse)
def get_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get model details."""
    model = db.query(MLModel).filter(MLModel.id == model_id).first()
    if not model:
        raise HTTPException(404, "Model not found")
    return ModelListResponse.model_validate(model)


@router.delete("/{model_id}")
def delete_model(
    model_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a model."""
    model = db.query(MLModel).filter(
        MLModel.id == model_id,
        MLModel.created_by_user_id == current_user.id,
    ).first()
    if not model:
        raise HTTPException(404, "Model not found")

    if model.model_filepath:
        p = Path(model.model_filepath)
        if p.exists():
            p.unlink()

    db.delete(model)
    db.commit()
    return {"detail": "Model deleted"}
