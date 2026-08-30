from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import RecommendationResult
from database import crud
from skill_gap.analyzer import analyze_skill_gap
from services.rag_service import query_candidate_resources
from recommendation.recommender import recommend_resources

def get_learner_recommendations(db: Session, user_id: str) -> RecommendationResult:
    # 1. Fetch learner profile
    profile = crud.get_learner_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
        
    # 2. Analyze skill gaps
    gap_result = analyze_skill_gap(profile)
    
    # 3. Retrieve relevant resources from DB (RAG fallback)
    candidates = query_candidate_resources(
        db,
        query_skills=gap_result.priority_skills,
        career_goal=profile.career_goal,
        experience_level=profile.experience_level
    )
    
    # 4. Generate recommendations using engine
    rec_result = recommend_resources(profile, gap_result, candidates)
    
    # 5. Save generated recommendations in database
    crud.save_recommendations(db, learner_id=user_id, recommendations=rec_result.recommendations)
    
    return rec_result
