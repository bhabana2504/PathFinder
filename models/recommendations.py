"""Recommendation and analysis result models."""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class PrerequisiteStatus(str, Enum):
    """Status of prerequisites for a resource or skill."""
    
    MET = "met"
    PARTIALLY_MET = "partially_met"
    NOT_MET = "not_met"


class SkillGapResult(BaseModel):
    """
    Result of skill gap analysis for a learner.
    """
    
    user_id: str = Field(..., description="Learner ID")
    career_goal: str = Field(..., description="Target career")
    
    required_skills: List[str] = Field(
        ...,
        description="All skills required for the career goal"
    )
    current_skills: List[str] = Field(
        ...,
        description="Skills the learner currently has"
    )
    missing_skills: List[str] = Field(
        ...,
        description="Skills completely missing"
    )
    weak_skills: List[str] = Field(
        ...,
        description="Skills present but below threshold"
    )
    mastered_skills: List[str] = Field(
        ...,
        description="Skills above mastery threshold"
    )
    
    skill_scores: Dict[str, float] = Field(
        ...,
        description="Skill → normalized priority score (0.0 to 1.0)"
    )
    priority_skills: List[str] = Field(
        ...,
        description="Skills ranked by priority (highest first)"
    )
    
    gap_analysis: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Detailed analysis for each skill"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "learner_123",
                "career_goal": "AI Engineer",
                "required_skills": ["Python", "Statistics", "ML", "Deep Learning"],
                "current_skills": ["Python"],
                "missing_skills": ["Statistics", "ML", "Deep Learning"],
                "weak_skills": [],
                "mastered_skills": [],
                "skill_scores": {
                    "Statistics": 0.92,
                    "Machine Learning": 0.88,
                    "Deep Learning": 0.75
                },
                "priority_skills": ["Statistics", "Machine Learning", "Deep Learning"],
                "gap_analysis": {}
            }
        }


class Recommendation(BaseModel):
    """
    A single ranked resource recommendation.
    """
    
    resource_id: str = Field(..., description="Resource ID from RAG system")
    title: str = Field(..., description="Resource title")
    resource_type: str = Field(..., description="Type of resource")
    
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall recommendation score (0.0 to 1.0)"
    )
    
    reason: str = Field(
        ...,
        description="Explainable reason for recommendation"
    )
    
    primary_skill: str = Field(..., description="Main skill addressed")
    secondary_skills: List[str] = Field(
        default_factory=list,
        description="Additional skills covered"
    )
    
    difficulty: str = Field(..., description="Resource difficulty level")
    priority: str = Field(
        ...,
        description="Priority level: critical, high, medium, low"
    )
    
    prerequisite_status: PrerequisiteStatus = Field(
        ...,
        description="Status of prerequisites"
    )
    missing_prerequisites: List[str] = Field(
        default_factory=list,
        description="Prerequisites not yet completed"
    )
    
    estimated_hours: float = Field(..., description="Hours to complete")
    fits_schedule: bool = Field(
        ...,
        description="Whether it fits learner's available time"
    )
    
    career_relevance: float = Field(
        ge=0.0,
        le=1.0,
        description="Relevance to career goal (0.0 to 1.0)"
    )
    
    interest_match: float = Field(
        ge=0.0,
        le=1.0,
        description="Match with learner interests (0.0 to 1.0)"
    )
    
    url: Optional[str] = Field(
        default=None,
        description="Resource URL"
    )
    
    # Detailed scoring breakdown for transparency
    score_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Component scores contributing to final score"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "resource_id": "ml101",
                "title": "Machine Learning Fundamentals",
                "resource_type": "course",
                "score": 0.91,
                "reason": "This resource is recommended because Machine Learning is a high-priority skill for your AI Engineer goal, your current proficiency is low (0.1), and you have already completed the required Python prerequisite.",
                "primary_skill": "Machine Learning",
                "secondary_skills": ["Python", "Statistics"],
                "difficulty": "intermediate",
                "priority": "critical",
                "prerequisite_status": "met",
                "missing_prerequisites": [],
                "estimated_hours": 20.0,
                "fits_schedule": True,
                "career_relevance": 0.95,
                "interest_match": 0.85,
                "url": "https://example.com/ml101",
                "score_breakdown": {
                    "skill_gap": 0.90,
                    "career_relevance": 0.95,
                    "difficulty_match": 0.80,
                    "prerequisite_match": 1.0,
                    "interest_match": 0.85,
                    "time_fit": 0.95
                }
            }
        }


class RecommendationResult(BaseModel):
    """
    Complete recommendation result for a learner.
    """
    
    user_id: str = Field(..., description="Learner ID")
    career_goal: str = Field(..., description="Target career")
    
    recommendations: List[Recommendation] = Field(
        ...,
        description="Ranked list of recommendations"
    )
    
    total_recommendations: int = Field(
        ...,
        description="Total number of recommendations"
    )
    
    top_priority_count: int = Field(
        ...,
        description="Number of critical priority recommendations"
    )
    
    average_score: float = Field(
        ...,
        description="Average recommendation score"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "learner_123",
                "career_goal": "AI Engineer",
                "recommendations": [],
                "total_recommendations": 3,
                "top_priority_count": 1,
                "average_score": 0.87
            }
        }
