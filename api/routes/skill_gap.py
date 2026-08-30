from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user
from database.models import User
from models.recommendations import SkillGapResult
from services import skill_gap_service

router = APIRouter(prefix="/api/skill-gap", tags=["skill-gap"])

@router.get("", response_model=SkillGapResult)
def get_skill_gap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return skill_gap_service.analyze_learner_gap(db, user_id=current_user.id)
