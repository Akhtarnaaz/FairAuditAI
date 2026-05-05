"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

UPLOAD_DIR = BASE_DIR / "uploads"
MODELS_DIR = UPLOAD_DIR / "models"
DATASETS_DIR = UPLOAD_DIR / "datasets"
REPORTS_DIR = BASE_DIR / "reports"

# Create directories
for d in [MODELS_DIR, DATASETS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Database ───────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'bias_auditor.db'}")

# ── Auth / JWT ─────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production-abc123xyz")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ── CORS ───────────────────────────────────────────────────────────────
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

# ── Upload Limits ──────────────────────────────────────────────────────
MAX_MODEL_SIZE_MB = 100
MAX_DATASET_SIZE_MB = 100
ALLOWED_MODEL_EXTENSIONS = {".pkl", ".h5", ".pickle", ".joblib"}

ALLOWED_DATASET_EXTENSIONS = {".csv", ".json"}
