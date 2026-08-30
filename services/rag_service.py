from sqlalchemy.orm import Session
from typing import List, Set
from models.resources import LearningResource, ResourceType, DifficultyLevel
from database import models

def to_pydantic_resource(db_res: models.LearningResource) -> LearningResource:
    return LearningResource(
        resource_id=db_res.resource_id,
        title=db_res.title,
        description=db_res.description,
        resource_type=ResourceType(db_res.resource_type) if hasattr(ResourceType, 'value') else db_res.resource_type,
        primary_skill=db_res.primary_skill,
        secondary_skills=[s.skill_name for s in db_res.secondary_skills],
        difficulty=DifficultyLevel(db_res.difficulty) if hasattr(DifficultyLevel, 'value') else db_res.difficulty,
        prerequisites=[p.skill_name for p in db_res.prerequisites],
        estimated_hours=db_res.estimated_hours,
        url=db_res.url,
        target_careers=[c.career_name for c in db_res.target_careers],
        tags=[t.tag for t in db_res.tags],
        ratings=db_res.ratings,
        completion_rate=db_res.completion_rate
    )

def query_candidate_resources(
    db: Session,
    query_skills: List[str],
    career_goal: str,
    experience_level: str
) -> List[LearningResource]:
    """
    Deterministic database retrieval fallback to fetch learning resources matching
    skills gap, career goals, and experience levels.
    """
    db_resources = db.query(models.LearningResource).all()
    candidates = []
    
    query_skills_set = set(query_skills)
    
    for db_res in db_resources:
        score = 0.0
        
        # 1. Skill Match
        if db_res.primary_skill in query_skills_set:
            score += 3.0
            
        sec_skills = {s.skill_name for s in db_res.secondary_skills}
        matching_sec = sec_skills.intersection(query_skills_set)
        score += len(matching_sec) * 1.0
        
        # 2. Career Match
        target_careers = {c.career_name for c in db_res.target_careers}
        if career_goal in target_careers:
            score += 2.0
            
        # 3. Difficulty Level Alignment
        # Align difficulty strings
        diff = db_res.difficulty.lower()
        exp = experience_level.lower()
        if diff == exp:
            score += 1.5
        elif (exp == "beginner" and diff == "intermediate") or (exp == "intermediate" and diff == "advanced"):
            score += 0.5
            
        if score > 0.0:
            candidates.append((score, db_res))
            
    # Sort candidates by match score descending, then by resource rating descending
    candidates.sort(key=lambda x: (x[0], x[1].ratings), reverse=True)
    
    return [to_pydantic_resource(item[1]) for item in candidates]
