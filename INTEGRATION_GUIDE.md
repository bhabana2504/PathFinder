# PathFinder AI/ML Integration Guide

This guide shows how to integrate the AI/ML module with Harsh's FastAPI backend.

## Architecture Overview

```
RAG System (Harsh's Module)
    ↓ retrieves resources
    ↓
AI/ML Module (This Module)
    ↓ ranks & explains recommendations
    ↓
FastAPI Backend
    ↓
Frontend (Aditya)
```

## Integration Points

### 1. Install AI/ML Module

```bash
# In your FastAPI project root
git submodule add <pathfinder-ai-repo> pathfinder_ai

# Or copy the module
cp -r pathfinder_ai /your/project/path/

# Install dependencies
cd pathfinder_ai
pip install -r requirements.txt
```

### 2. Create FastAPI Endpoints

```python
# main.py or routes/recommendations.py

from fastapi import FastAPI, HTTPException
from pathfinder_ai import (
    LearnerProfile,
    analyze_skill_gap,
    recommend_resources,
    generate_learning_path,
    update_learner_profile,
)
from pathfinder_ai.adaptive_learning import ProgressAnalyzer

app = FastAPI()

# Assume you have a RAG system instance
rag_system = YourRAGSystem()

# ============================================
# ENDPOINT 1: Analyze Skill Gaps
# ============================================

@app.post("/api/v1/skill-gaps")
async def analyze_skill_gaps(profile: LearnerProfile):
    """
    Analyze skill gaps for a learner.
    
    Returns:
        {
            "user_id": str,
            "career_goal": str,
            "missing_skills": List[str],
            "weak_skills": List[str],
            "mastered_skills": List[str],
            "priority_skills": List[str],
            "skill_scores": Dict[str, float]
        }
    """
    try:
        gap = analyze_skill_gap(profile)
        
        return {
            "user_id": gap.user_id,
            "career_goal": gap.career_goal,
            "required_skills": gap.required_skills,
            "current_skills": gap.current_skills,
            "missing_skills": gap.missing_skills,
            "weak_skills": gap.weak_skills,
            "mastered_skills": gap.mastered_skills,
            "priority_skills": gap.priority_skills,
            "skill_scores": gap.skill_scores,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# ENDPOINT 2: Get Recommendations
# ============================================

@app.post("/api/v1/recommendations")
async def get_recommendations(profile: LearnerProfile, top_n: int = 10):
    """
    Get ranked learning resource recommendations.
    
    Process:
    1. Analyze skill gaps
    2. Retrieve relevant resources from RAG
    3. Rank resources
    4. Return top N with explanations
    
    Returns:
        {
            "user_id": str,
            "career_goal": str,
            "total_recommendations": int,
            "top_priority_count": int,
            "average_score": float,
            "recommendations": [
                {
                    "resource_id": str,
                    "title": str,
                    "resource_type": str,
                    "score": float,
                    "reason": str,
                    "primary_skill": str,
                    "difficulty": str,
                    "priority": str,
                    "estimated_hours": float,
                    "fits_schedule": bool,
                    "career_relevance": float,
                    "prerequisite_status": str,
                    "missing_prerequisites": List[str],
                    "url": str,
                    "score_breakdown": Dict[str, float]
                }
            ]
        }
    """
    try:
        # Step 1: Analyze gaps
        gap = analyze_skill_gap(profile)
        
        # Step 2: Retrieve resources from RAG (your module)
        retrieved = await rag_system.retrieve(
            query=gap.priority_skills,
            limit=50,
            career=profile.career_goal
        )
        
        # Step 3: Rank with AI/ML module (this module)
        result = recommend_resources(
            profile=profile,
            skill_gap=gap,
            resources=retrieved,
            top_n=top_n
        )
        
        # Step 4: Format response
        return {
            "user_id": result.user_id,
            "career_goal": result.career_goal,
            "total_recommendations": result.total_recommendations,
            "top_priority_count": result.top_priority_count,
            "average_score": result.average_score,
            "recommendations": [
                {
                    "resource_id": r.resource_id,
                    "title": r.title,
                    "resource_type": r.resource_type,
                    "score": r.score,
                    "reason": r.reason,
                    "primary_skill": r.primary_skill,
                    "secondary_skills": r.secondary_skills,
                    "difficulty": r.difficulty,
                    "priority": r.priority,
                    "estimated_hours": r.estimated_hours,
                    "fits_schedule": r.fits_schedule,
                    "career_relevance": r.career_relevance,
                    "interest_match": r.interest_match,
                    "prerequisite_status": r.prerequisite_status.value,
                    "missing_prerequisites": r.missing_prerequisites,
                    "url": r.url,
                    "score_breakdown": r.score_breakdown,
                }
                for r in result.recommendations
            ]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Recommendation error")


# ============================================
# ENDPOINT 3: Generate Learning Path
# ============================================

@app.post("/api/v1/learning-path")
async def generate_learning_path_endpoint(profile: LearnerProfile):
    """
    Generate a personalized learning path.
    
    Returns:
        {
            "user_id": str,
            "career_goal": str,
            "total_nodes": int,
            "completion_percentage": float,
            "nodes": [
                {
                    "position": int,
                    "resource_id": str,
                    "title": str,
                    "skill": str,
                    "difficulty": str,
                    "estimated_hours": float,
                    "status": str,  # locked/available/in_progress/completed
                    "score": float,
                    "priority": str
                }
            ]
        }
    """
    try:
        # Analyze gaps
        gap = analyze_skill_gap(profile)
        
        # Get recommendations
        retrieved = await rag_system.retrieve(
            query=gap.priority_skills,
            limit=50
        )
        
        recommendations = recommend_resources(
            profile, gap, retrieved, top_n=20
        ).recommendations
        
        # Generate path
        path = generate_learning_path(
            profile, gap, recommendations
        )
        
        return {
            "user_id": path.user_id,
            "career_goal": path.career_goal,
            "total_nodes": len(path.nodes),
            "completion_percentage": path.get_completion_percentage(),
            "nodes": [
                {
                    "position": n.position,
                    "resource_id": n.recommendation.resource_id,
                    "title": n.recommendation.title,
                    "skill": n.recommendation.primary_skill,
                    "difficulty": n.recommendation.difficulty,
                    "estimated_hours": n.recommendation.estimated_hours,
                    "status": n.status,
                    "score": n.recommendation.score,
                    "priority": n.recommendation.priority,
                }
                for n in path.nodes
            ],
            "current_node": (
                {
                    "position": path.get_current_node().position,
                    "title": path.get_current_node().recommendation.title,
                }
                if path.get_current_node()
                else None
            )
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# ENDPOINT 4: Update Profile
# ============================================

@app.post("/api/v1/profile/update")
async def update_profile(
    user_id: str,
    profile: LearnerProfile,
    updates: dict
):
    """
    Update learner profile with completion data.
    
    Updates can include:
    - completed_resources: List[str]
    - skill_proficiency: Dict[str, float]
    - assessment_results: Dict[str, float]
    - feedback: List[str]
    - interests: List[str]
    
    Example:
        {
            "completed_resources": ["course_123"],
            "skill_proficiency": {"Python": 0.9},
            "assessment_results": {"Python": 0.92}
        }
    """
    try:
        updated = update_learner_profile(profile, **updates)
        
        # Save to database (your responsibility)
        await db.update_profile(user_id, updated.dict())
        
        return {
            "user_id": updated.user_id,
            "updated": True,
            "profile": updated.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# ENDPOINT 5: Mark Resource Completed
# ============================================

@app.post("/api/v1/profile/complete-resource")
async def complete_resource(
    user_id: str,
    resource_id: str,
    rating: float = None
):
    """
    Mark a resource as completed.
    """
    try:
        # Get current profile from database
        profile = await db.get_profile(user_id)
        
        # Update profile
        from pathfinder_ai.adaptive_learning import mark_resource_completed
        updated = mark_resource_completed(profile, resource_id, rating)
        
        # Save updated profile
        await db.update_profile(user_id, updated.dict())
        
        return {
            "resource_id": resource_id,
            "completed": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINT 6: Update Skill from Assessment
# ============================================

@app.post("/api/v1/profile/update-skill")
async def update_skill_assessment(
    user_id: str,
    skill: str,
    assessment_score: float
):
    """
    Update skill proficiency from assessment.
    
    Assessment score: 0.0-1.0
    """
    try:
        if not (0.0 <= assessment_score <= 1.0):
            raise ValueError("Assessment score must be 0.0-1.0")
        
        # Get current profile
        profile = await db.get_profile(user_id)
        
        # Update skill
        from pathfinder_ai.adaptive_learning import update_skill_from_assessment
        updated = update_skill_from_assessment(
            profile,
            skill=skill,
            assessment_score=assessment_score,
            weight=0.6
        )
        
        # Save
        await db.update_profile(user_id, updated.dict())
        
        # Optionally re-generate recommendations
        gap = analyze_skill_gap(updated)
        
        return {
            "user_id": user_id,
            "skill": skill,
            "new_proficiency": updated.get_skill_proficiency(skill),
            "priority_skills_updated": gap.priority_skills[:5]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================
# ENDPOINT 7: Get Progress Report
# ============================================

@app.get("/api/v1/progress/{user_id}")
async def get_progress(user_id: str):
    """
    Get learner progress report.
    """
    try:
        # Get current and previous profiles
        current = await db.get_profile(user_id)
        previous = await db.get_profile_history(user_id, offset=1)
        
        # Analyze progress
        analyzer = ProgressAnalyzer()
        report = analyzer.generate_progress_report(current, previous)
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# OPTIONAL: Batch Recommendations
# ============================================

@app.post("/api/v1/batch-recommendations")
async def batch_recommendations(profiles: List[LearnerProfile]):
    """
    Get recommendations for multiple learners (for caching/batch processing).
    """
    results = []
    
    for profile in profiles:
        try:
            gap = analyze_skill_gap(profile)
            retrieved = await rag_system.retrieve(gap.priority_skills, limit=50)
            recs = recommend_resources(profile, gap, retrieved, top_n=5)
            
            results.append({
                "user_id": profile.user_id,
                "success": True,
                "recommendation_count": len(recs.recommendations)
            })
        except Exception as e:
            results.append({
                "user_id": profile.user_id,
                "success": False,
                "error": str(e)
            })
    
    return {"results": results}
```

## Database Integration

### Store LearnerProfile

```python
# Using SQLAlchemy/PostgreSQL

from sqlalchemy import create_engine, Column, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class LearnerProfileDB(Base):
    __tablename__ = "learner_profiles"
    
    user_id = Column(String, primary_key=True)
    career_goal = Column(String)
    experience_level = Column(String)
    current_skills = Column(JSON)  # List[str]
    skill_proficiency = Column(JSON)  # Dict[str, float]
    interests = Column(JSON)  # List[str]
    learning_hours_per_week = Column(Float)
    completed_resources = Column(JSON)  # List[str]
    assessment_results = Column(JSON)  # Dict[str, float]
    feedback = Column(JSON)  # List[str]
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    def to_pydantic(self) -> LearnerProfile:
        return LearnerProfile(
            user_id=self.user_id,
            career_goal=self.career_goal,
            experience_level=self.experience_level,
            current_skills=self.current_skills,
            skill_proficiency=self.skill_proficiency,
            interests=self.interests,
            learning_hours_per_week=self.learning_hours_per_week,
            completed_resources=self.completed_resources,
            assessment_results=self.assessment_results,
            feedback=self.feedback,
        )


# Usage
engine = create_engine("postgresql://user:password@localhost/pathfinder")
Session = sessionmaker(bind=engine)

# Get profile
session = Session()
db_profile = session.query(LearnerProfileDB).filter_by(user_id="123").first()
profile = db_profile.to_pydantic()

# Update profile
db_profile.skill_proficiency = updated_profile.skill_proficiency
db_profile.updated_at = datetime.utcnow()
session.commit()
```

## Error Handling

```python
from fastapi import HTTPException

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": "Invalid input: " + str(exc)}
    )

@app.exception_handler(KeyError)
async def key_error_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Not found: {exc}"}
    )
```

## Performance Tips

### 1. Cache Career Data

```python
from functools import lru_cache

@lru_cache(maxsize=32)
def get_career_skills_cached(career: str):
    from pathfinder_ai.config import get_career_skills
    return get_career_skills(career)
```

### 2. Batch RAG Queries

```python
# Instead of retrieving resources for each skill individually:
gap = analyze_skill_gap(profile)

# Retrieve all at once
resources = await rag_system.retrieve(
    query=gap.priority_skills,  # All priority skills
    limit=100  # Get more, filter locally
)

# This is more efficient than N separate queries
```

### 3. Async/Await for I/O

```python
# Use async RAG calls
retrieved = await rag_system.retrieve(...)  # Non-blocking

# Not:
retrieved = rag_system.retrieve(...)  # Blocking
```

## Testing Integration

```python
# test_integration.py

from fastapi.testclient import TestClient
from main import app
from pathfinder_ai.sample_data import SAMPLE_LEARNER_BEGINNER

client = TestClient(app)

def test_skill_gap_endpoint():
    response = client.post(
        "/api/v1/skill-gaps",
        json=SAMPLE_LEARNER_BEGINNER.dict()
    )
    assert response.status_code == 200
    assert "priority_skills" in response.json()

def test_recommendations_endpoint():
    response = client.post(
        "/api/v1/recommendations",
        json=SAMPLE_LEARNER_BEGINNER.dict()
    )
    assert response.status_code == 200
    assert "recommendations" in response.json()
```

## Troubleshooting

### Issue: "Unknown career" error

```python
# Check supported careers
from pathfinder_ai.config import get_all_careers
print(get_all_careers())

# Add new career to config/careers.py
```

### Issue: Low recommendation scores

```python
# Check skill gap analysis
gap = analyze_skill_gap(profile)
print(gap.skill_scores)

# Adjust scoring weights
custom_weights = ScoringWeights(
    skill_gap_weight=0.5,  # Increase emphasis on gaps
    ...
)
```

### Issue: Prerequisites not working

```python
# Verify prerequisite chains
from pathfinder_ai.learning_path.prerequisite import PrerequisiteEngine

engine = PrerequisiteEngine()
valid, missing = engine.validate_prerequisites(
    resource=resource,
    learner_current_skills=set(profile.current_skills)
)
print(f"Valid: {valid}, Missing: {missing}")
```

## Contact & Support

For integration questions:
- **Bhabana**: Team Lead, AI/ML Module
- **Harsh**: RAG & Backend Integration
- **GitHub Issues**: Log integration problems
