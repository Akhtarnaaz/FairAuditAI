"""Reports router — generate and download audit reports."""
import csv
import io
import json
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import REPORTS_DIR
from app.models.user import User
from app.models.audit_run import AuditRun
from app.models.model import MLModel
from app.models.dataset import Dataset
from app.models.fairness_score import FairnessScore
from app.models.bias_explanation import BiasExplanation
from app.models.mitigation import MitigationRecommendation
from app.models.audit_report import AuditReport
from app.schemas.report import ReportResponse, ReportListResponse
from app.middleware.auth_middleware import get_current_user, require_admin

router = APIRouter()


def _generate_csv_report(audit_id: str, db: Session) -> str:
    """Generate a CSV report file and return its path."""
    scores = db.query(FairnessScore).filter(FairnessScore.audit_run_id == audit_id).all()
    explanations = db.query(BiasExplanation).filter(BiasExplanation.audit_run_id == audit_id).all()
    mitigations = db.query(MitigationRecommendation).filter(
        MitigationRecommendation.audit_run_id == audit_id
    ).order_by(MitigationRecommendation.priority).all()

    filename = f"audit_{audit_id[:8]}_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = REPORTS_DIR / filename

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(["=== FAIRNESS SCORES ==="])
        writer.writerow(["Dimension", "Fairness Score", "Disparity Ratio", "Status"])
        for s in scores:
            status = "Fair" if s.fairness_score >= 0.8 else "Review" if s.fairness_score >= 0.5 else "Biased"
            writer.writerow([s.dimension, s.fairness_score, s.disparity_ratio, status])

        writer.writerow([])
        writer.writerow(["=== BIAS EXPLANATIONS ==="])
        writer.writerow(["Dimension", "Severity", "Explanation", "Root Cause"])
        for e in explanations:
            writer.writerow([e.dimension, e.severity, e.explanation_text, e.root_cause])

        writer.writerow([])
        writer.writerow(["=== MITIGATION RECOMMENDATIONS ==="])
        writer.writerow(["Priority", "Dimension", "Type", "Recommendation", "Effort", "Impact"])
        for m in mitigations:
            writer.writerow([
                m.priority, m.dimension, m.recommendation_type,
                m.recommendation_text, m.effort_level, m.impact_level,
            ])

    return str(filepath)


def _generate_pdf_report(audit_id: str, db: Session) -> str:
    """Generate a PDF report file. Falls back to text if reportlab unavailable."""
    audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
    model = db.query(MLModel).filter(MLModel.id == audit.model_id).first() if audit else None
    scores = db.query(FairnessScore).filter(FairnessScore.audit_run_id == audit_id).all()
    explanations = db.query(BiasExplanation).filter(BiasExplanation.audit_run_id == audit_id).all()
    mitigations = db.query(MitigationRecommendation).filter(
        MitigationRecommendation.audit_run_id == audit_id
    ).order_by(MitigationRecommendation.priority).all()

    filename = f"audit_{audit_id[:8]}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = REPORTS_DIR / filename

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=18, spaceAfter=20)
        story.append(Paragraph("AI Bias & Fairness Audit Report", title_style))
        story.append(Spacer(1, 12))

        # Model info
        if model:
            story.append(Paragraph(f"<b>Model:</b> {model.model_name} (v{model.model_version})", styles['Normal']))
        if audit:
            story.append(Paragraph(f"<b>Date:</b> {audit.created_at}", styles['Normal']))
            story.append(Paragraph(f"<b>Test Cases:</b> {audit.num_test_cases}", styles['Normal']))
        story.append(Spacer(1, 20))

        # Overall score
        overall = sum(s.fairness_score for s in scores) / len(scores) if scores else 0
        status_text = "FAIR" if overall >= 0.8 else "REVIEW REQUIRED" if overall >= 0.5 else "BIASED - ACTION REQUIRED"
        story.append(Paragraph(f"<b>Overall Fairness Score: {overall:.2f} — {status_text}</b>", styles['Heading2']))
        story.append(Spacer(1, 12))

        # Scores table
        score_data = [["Dimension", "Score", "DI Ratio", "Status"]]
        for s in scores:
            st = "✓ Fair" if s.fairness_score >= 0.8 else "⚠ Review" if s.fairness_score >= 0.5 else "✗ Biased"
            score_data.append([s.dimension.title(), f"{s.fairness_score:.2f}", f"{s.disparity_ratio:.2f}", st])

        t = Table(score_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Explanations
        story.append(Paragraph("Bias Analysis", styles['Heading2']))
        for e in explanations:
            story.append(Paragraph(f"<b>{e.dimension.title()} (Severity: {e.severity.upper()})</b>", styles['Heading3']))
            story.append(Paragraph(e.explanation_text, styles['Normal']))
            story.append(Paragraph(f"<i>Root Cause: {e.root_cause}</i>", styles['Normal']))
            story.append(Spacer(1, 10))

        # Recommendations
        story.append(Paragraph("Mitigation Recommendations", styles['Heading2']))
        for m in mitigations[:10]:
            story.append(Paragraph(
                f"<b>#{m.priority} [{m.recommendation_type}]</b> {m.recommendation_text} "
                f"(Effort: {m.effort_level}, Impact: {m.impact_level})",
                styles['Normal'],
            ))
            story.append(Spacer(1, 6))

        doc.build(story)

    except ImportError:
        # Fallback: plain text file with .pdf extension
        with open(filepath, "w") as f:
            f.write("AI BIAS & FAIRNESS AUDIT REPORT\n")
            f.write("=" * 50 + "\n\n")
            if model:
                f.write(f"Model: {model.model_name}\n")
            for s in scores:
                f.write(f"{s.dimension}: {s.fairness_score:.2f}\n")
            f.write("\n")
            for e in explanations:
                f.write(f"[{e.severity.upper()}] {e.dimension}: {e.explanation_text}\n\n")

    return str(filepath)


@router.post("/{audit_id}/generate", response_model=ReportResponse)
def generate_report(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Generate PDF and CSV reports for an audit."""
    audit = db.query(AuditRun).filter(AuditRun.id == audit_id).first()
    if not audit:
        raise HTTPException(404, "Audit not found")
    if audit.status != "completed":
        raise HTTPException(400, "Audit must be completed before generating report")

    pdf_path = _generate_pdf_report(audit_id, db)
    csv_path = _generate_csv_report(audit_id, db)

    report = AuditReport(
        audit_run_id=audit_id,
        pdf_filepath=pdf_path,
        csv_filepath=csv_path,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return ReportResponse(
        id=report.id,
        audit_run_id=report.audit_run_id,
        pdf_url=f"/api/reports/{report.id}/download/pdf",
        csv_url=f"/api/reports/{report.id}/download/csv",
        generated_at=report.generated_at,
        downloaded_count=report.downloaded_count,
    )


@router.get("/{report_id}/download/pdf")
def download_pdf(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download PDF report."""
    report = db.query(AuditReport).filter(AuditReport.id == report_id).first()
    if not report or not report.pdf_filepath:
        raise HTTPException(404, "Report not found")

    report.downloaded_count += 1
    db.commit()

    return FileResponse(report.pdf_filepath, media_type="application/pdf", filename=Path(report.pdf_filepath).name)


@router.get("/{report_id}/download/csv")
def download_csv(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download CSV report."""
    report = db.query(AuditReport).filter(AuditReport.id == report_id).first()
    if not report or not report.csv_filepath:
        raise HTTPException(404, "Report not found")

    report.downloaded_count += 1
    db.commit()

    return FileResponse(report.csv_filepath, media_type="text/csv", filename=Path(report.csv_filepath).name)


@router.get("/", response_model=list[ReportListResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all generated reports."""
    reports = db.query(AuditReport).order_by(AuditReport.generated_at.desc()).all()
    results = []
    for r in reports:
        audit = db.query(AuditRun).filter(AuditRun.id == r.audit_run_id).first()
        model = db.query(MLModel).filter(MLModel.id == audit.model_id).first() if audit else None
        scores = db.query(FairnessScore).filter(FairnessScore.audit_run_id == r.audit_run_id).all()
        overall = sum(s.fairness_score for s in scores) / len(scores) if scores else None

        results.append(ReportListResponse(
            id=r.id,
            audit_run_id=r.audit_run_id,
            model_name=model.model_name if model else None,
            overall_score=round(overall, 4) if overall else None,
            generated_at=r.generated_at,
            downloaded_count=r.downloaded_count,
        ))
    return results
