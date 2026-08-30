from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import crud, models
from models import LearnerProfile
from adaptive_learning.updater import update_skill_from_assessment
from adaptive_learning.progress_analyzer import ProgressAnalyzer
from services.learning_path_service import get_learner_path

def track_resource_completion(
    db: Session,
    user_id: str,
    resource_id: str,
    rating: Optional[float] = None
) -> dict:
    profile = crud.get_learner_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
        
    # Check if resource is already completed
    if resource_id not in profile.completed_resources:
        profile.completed_resources.append(resource_id)
        
    crud.save_learner_profile(db, profile)
    
    # Save resource completion rating if provided
    if rating is not None:
        db_comp = db.query(models.CompletedResource).filter(
            models.CompletedResource.learner_id == user_id,
            models.CompletedResource.resource_id == resource_id
        ).first()
        if db_comp:
            db_comp.rating = rating
            db.commit()
            
    # Trigger roadmap status updates by recalculating learning path
    updated_path = get_learner_path(db, user_id=user_id)
    return {
        "status": "success",
        "message": f"Resource {resource_id} marked as completed",
        "learning_path": updated_path
    }

def submit_learner_assessment(
    db: Session,
    user_id: str,
    skill_name: str,
    score: float
) -> dict:
    profile = crud.get_learner_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
        
    # Run adaptive learning updater logic
    updated_profile = update_skill_from_assessment(profile, skill_name, score)
    crud.save_learner_profile(db, updated_profile)
    
    # Recalculate recommendations and roadmap with new skill proficiencies
    updated_path = get_learner_path(db, user_id=user_id)
    return {
        "status": "success",
        "new_proficiency": updated_profile.skill_proficiency.get(skill_name, 0.0),
        "learning_path": updated_path
    }

def get_learner_progress_report(db: Session, user_id: str) -> dict:
    profile = crud.get_learner_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
        
    total_resources = db.query(models.LearningResource).count()
    
    analyzer = ProgressAnalyzer()
    report = analyzer.generate_progress_report(profile, previous_profile=None)
    
    # Dynamically update the completion rate using actual DB counts
    if total_resources > 0:
        real_completion_rate = len(profile.completed_resources) / total_resources
        report["metrics"]["completion_rate"] = real_completion_rate
        
    return report
