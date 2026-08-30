from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import crud
from api.dependencies import get_db, get_current_user
from database.models import User
from models.learner import LearnerProfile
from services import learner_service
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/learners", tags=["learners"])

class ProfileCreateUpdate(BaseModel):
    career_goal: str = Field(..., description="Target career path")
    experience_level: str = Field(..., description="Experience level (beginner, intermediate, advanced)")
    learning_hours_per_week: float = Field(10.0, ge=1.0, le=168.0, description="Available study hours per week")
    interests: List[str] = Field(default_factory=list, description="List of learning interests")
    current_skills: List[str] = Field(default_factory=list, description="List of current skills")

@router.get("/profile", response_model=LearnerProfile)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = learner_service.get_learner_profile(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found. Please complete onboarding."
        )
    return profile

@router.post("/profile", response_model=LearnerProfile)
def save_profile(
    profile_data: ProfileCreateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = learner_service.get_learner_profile(db, user_id=current_user.id)
    if profile:
        # Update existing profile
        profile.career_goal = profile_data.career_goal
        profile.experience_level = profile_data.experience_level
        profile.learning_hours_per_week = profile_data.learning_hours_per_week
        profile.interests = profile_data.interests
        # Merge new current skills (default initial proficiency to 0.2 if not exists)
        for s in profile_data.current_skills:
            if s not in profile.current_skills:
                profile.current_skills.append(s)
                profile.skill_proficiency[s] = 0.2
        updated_profile = learner_service.update_learner_profile(db, profile)
        return updated_profile
    else:
        # Create new profile
        new_profile = learner_service.create_learner_profile(
            db,
            user_id=current_user.id,
            career_goal=profile_data.career_goal,
            experience_level=profile_data.experience_level,
            learning_hours_per_week=profile_data.learning_hours_per_week,
            interests=profile_data.interests,
            current_skills=profile_data.current_skills
        )
        return new_profile
