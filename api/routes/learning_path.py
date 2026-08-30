from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db, get_current_user
from database.models import User
from services import learning_path_service

router = APIRouter(prefix="/api/learning-path", tags=["learning-path"])

@router.get("")
def get_learning_path(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return learning_path_service.get_learner_path(db, user_id=current_user.id)
