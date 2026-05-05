"""FastAPI application entry point."""
import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, REPORTS_DIR
from app.database import engine, Base

# Import all models so Base.metadata knows about them
from app.models import user, model, dataset, audit_run, fairness_score, bias_explanation, mitigation, audit_report  # noqa: F401

app = FastAPI(
    title="AI Bias & Fairness Auditor",
    description="Detect, measure, and explain bias in AI model outputs using counterfactual testing.",
    version="1.0.0",
)

# ── CORS ───────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files for report downloads ──────────────────────────────────
app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")


# ── Startup ────────────────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)


# ── Health check ───────────────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "AI Bias & Fairness Auditor"}


# ── Register routers (imported after app creation) ─────────────────────
from app.routers import auth, models, datasets, audits, reports, user_explore  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(models.router, prefix="/api/models", tags=["Models"])
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(audits.router, prefix="/api/audits", tags=["Audits"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(user_explore.router, prefix="/api/user-explore", tags=["User Explore"])

