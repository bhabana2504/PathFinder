from sqlalchemy.orm import Session
from typing import List, Optional
from models import LearnerProfile
from database import crud

def get_learner_profile(db: Session, user_id: str) -> Optional[LearnerProfile]:
    return crud.get_learner_profile(db, user_id=user_id)

def create_learner_profile(
    db: Session,
    user_id: str,
    career_goal: str,
    experience_level: str,
    learning_hours_per_week: float,
    interests: List[str],
    current_skills: List[str]
) -> LearnerProfile:
    # Initialize proficiency map (default to 0.1 for onboarding skills, or 0.0 if not specified)
    proficiency = {}
    for skill in current_skills:
        proficiency[skill] = 0.5 if experience_level == "intermediate" else (0.8 if experience_level == "advanced" else 0.2)
        
    profile = LearnerProfile(
        user_id=user_id,
        career_goal=career_goal,
        experience_level=experience_level,
        current_skills=current_skills,
        skill_proficiency=proficiency,
        interests=interests,
        learning_hours_per_week=learning_hours_per_week,
        completed_resources=[],
        assessment_results={},
        feedback=[]
    )
    crud.save_learner_profile(db, profile)
    return profile

def update_learner_profile(db: Session, profile: LearnerProfile) -> LearnerProfile:
    crud.save_learner_profile(db, profile)
    return profile
