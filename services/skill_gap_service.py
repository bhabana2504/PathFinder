from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import SkillGapResult
from database import crud
from skill_gap.analyzer import analyze_skill_gap

def analyze_learner_gap(db: Session, user_id: str) -> SkillGapResult:
    profile = crud.get_learner_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found. Please onboarding first."
        )
    return analyze_skill_gap(profile)
