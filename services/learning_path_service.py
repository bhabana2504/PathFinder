from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database import crud
from skill_gap.analyzer import analyze_skill_gap
from services.rag_service import query_candidate_resources
from services.recommendation_service import get_learner_recommendations
from learning_path.generator import generate_learning_path_with_resources

def get_learner_path(db: Session, user_id: str) -> dict:
    profile = crud.get_learner_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
        
    gap_result = analyze_skill_gap(profile)
    
    # Get recommendations
    rec_result = get_learner_recommendations(db, user_id=user_id)
    
    # Retrieve full resource data for candidates
    candidates = query_candidate_resources(
        db,
        query_skills=gap_result.priority_skills,
        career_goal=profile.career_goal,
        experience_level=profile.experience_level
    )
    
    # Generate path
    path = generate_learning_path_with_resources(
        profile,
        gap_result,
        rec_result.recommendations,
        candidates
    )
    
    # Serialize and save to database
    nodes_data = []
    for node in path.nodes:
        nodes_data.append({
            "resource_id": node.resource.resource_id,
            "position": node.position,
            "status": node.status,
            "percentage_complete": node.percentage_complete
        })
        
    crud.save_learning_path(
        db,
        learner_id=user_id,
        career_goal=profile.career_goal,
        completion_percentage=path.get_completion_percentage(),
        nodes=nodes_data
    )
    
    return path.to_dict()
