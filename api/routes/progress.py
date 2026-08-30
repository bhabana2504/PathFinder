from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, Field

from api.dependencies import get_db, get_current_user
from database.models import User
from services import progress_service

router = APIRouter(prefix="/api/progress", tags=["progress"])

class ResourceCompleteRequest(BaseModel):
    resource_id: str = Field(..., description="ID of the completed resource")
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Optional rating (1 to 5)")

class AssessmentSubmitRequest(BaseModel):
    skill_name: str = Field(..., description="Name of the skill assessed")
    score: float = Field(..., ge=0.0, le=1.0, description="Assessment score (0.0 to 1.0)")

@router.post("/complete")
def complete_resource(
    payload: ResourceCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return progress_service.track_resource_completion(
        db,
        user_id=current_user.id,
        resource_id=payload.resource_id,
        rating=payload.rating
    )

@router.post("/assessment")
def submit_assessment(
    payload: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return progress_service.submit_learner_assessment(
        db,
        user_id=current_user.id,
        skill_name=payload.skill_name,
        score=payload.score
    )

@router.get("/report")
def get_progress_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return progress_service.get_learner_progress_report(db, user_id=current_user.id)
