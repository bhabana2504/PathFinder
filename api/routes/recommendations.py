from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user
from database.models import User
from models.recommendations import RecommendationResult
from services import recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.get("", response_model=RecommendationResult)
def get_recommendations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return recommendation_service.get_learner_recommendations(db, user_id=current_user.id)
