from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.user_query import UserQuery
from app.middleware.auth_middleware import get_current_user
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

class AskRequest(BaseModel):
    query: str

class CheckFairnessRequest(BaseModel):
    query: str
    response: str

class TestProfileRequest(BaseModel):
    query: str
    original_response: str
    modified_identity: dict # {gender: 'Male', region: 'Urban', ...}

@router.post("/ask")
def ask_ai(data: AskRequest, current_user: User = Depends(get_current_user)):
    query = data.query.lower()
    
    # Heuristic responses to simulate bias in different domains
    if "loan" in query or "credit" in query:
        response = "Your creditworthiness has been assessed based on regional and financial history. We recommend a limit of $4,500."
    elif "job" in query or "candidate" in query or "hiring" in query:
        response = "The candidate shows potential. However, their profile suggests they might prefer a roles with less travel requirements."
    elif "health" in query or "treatment" in query:
        response = "Priority for advanced cardiac screening is currently assigned to high-risk demographic groups."
    else:
        response = "I have analyzed your request. Based on standard parameters, the outcome is positive."
    
    return {"response": response}

@router.post("/check-fairness")
def check_fairness(data: CheckFairnessRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = data.query.lower()
    response = data.response.lower()
    
    status = "fair"
    explanation = "The response appears neutral and does not reference sensitive protected groups directly."
    
    # Simulated bias detection logic
    if any(word in response for word in ["travel", "priority", "regional", "demographic"]):
        status = "slight_bias"
        explanation = "The AI used proxy variables (like travel preference or regional history) which are often correlated with protected identity groups."
    
    if any(word in query for word in ["gender", "caste", "religion", "village"]):
        status = "biased"
        explanation = "The query explicitly included identity markers, and the AI response may have subconsciously weighed these factors in its output."

    # Save to history
    query_record = UserQuery(
        user_id=current_user.id,
        query_text=data.query,
        response_text=data.response,
        fairness_status=status,
        fairness_explanation=explanation
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)
    
    return {
        "status": status,
        "explanation": explanation,
        "query_id": query_record.id
    }

@router.post("/test-profile")
def test_profile(data: TestProfileRequest, current_user: User = Depends(get_current_user)):
    orig = data.original_response
    mod = orig
    
    # Simulate bias by changing the response based on identity markers
    gender = data.modified_identity.get("gender")
    region = data.modified_identity.get("region")
    
    if gender == "Male" and "travel" in orig:
        mod = orig.replace("prefer a roles with less travel requirements", "be an excellent fit for this high-intensity role")
    elif region == "Urban" and "$4,500" in orig:
        mod = orig.replace("$4,500", "$7,200")
    elif "Priority" in orig:
        mod = "Priority for advanced cardiac screening is approved for your profile."

    return {
        "original_response": orig,
        "modified_response": mod,
        "is_different": orig != mod
    }

@router.get("/history")
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    queries = db.query(UserQuery).filter(UserQuery.user_id == current_user.id).order_by(UserQuery.created_at.desc()).all()
    return queries

@router.delete("/history")
def clear_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(UserQuery).filter(UserQuery.user_id == current_user.id).delete()
    db.commit()
    return {"status": "success"}
