"""Learner profile data model."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LearnerProfile(BaseModel):
    """
    Complete learner profile capturing all relevant learning data.
    
    This is the primary input to the AI/ML recommendation system.
    """
    
    user_id: str = Field(..., description="Unique learner identifier")
    career_goal: str = Field(..., description="Target career (e.g., 'AI Engineer')")
    experience_level: str = Field(
        ..., 
        description="Experience level: beginner, intermediate, advanced",
        pattern="^(beginner|intermediate|advanced)$"
    )
    current_skills: List[str] = Field(
        default_factory=list,
        description="List of skills the learner currently has"
    )
    skill_proficiency: Dict[str, float] = Field(
        default_factory=dict,
        description="Skill name → proficiency score (0.0 to 1.0)"
    )
    interests: List[str] = Field(
        default_factory=list,
        description="Learning interests and preferences"
    )
    learning_hours_per_week: float = Field(
        default=10.0,
        ge=0.0,
        le=168.0,
        description="Available learning hours per week"
    )
    completed_resources: List[str] = Field(
        default_factory=list,
        description="IDs of completed learning resources"
    )
    assessment_results: Dict[str, float] = Field(
        default_factory=dict,
        description="Skill → assessment score mapping (0.0 to 1.0)"
    )
    feedback: List[str] = Field(
        default_factory=list,
        description="User feedback on recommendations and resources"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Profile creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last profile update timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "learner_123",
                "career_goal": "AI Engineer",
                "experience_level": "beginner",
                "current_skills": ["Python", "SQL"],
                "skill_proficiency": {
                    "Python": 0.85,
                    "SQL": 0.70
                },
                "interests": ["Machine Learning", "NLP"],
                "learning_hours_per_week": 10.0,
                "completed_resources": ["python_basics_101"],
                "assessment_results": {
                    "Python": 0.82
                },
                "feedback": []
            }
        }

    def copy(self, *, include=None, exclude=None, update=None, deep=True):
        """Return a copy of the model, defaulting to deep copy to avoid shared nested dictionary state."""
        if hasattr(self, "model_copy"):
            return self.model_copy(update=update, deep=deep)
        return super().copy(include=include, exclude=exclude, update=update, deep=deep)

    def get_skill_proficiency(self, skill: str) -> float:
        """
        Get proficiency for a skill, defaulting to 0.0 if not found.
        
        Args:
            skill: Skill name
            
        Returns:
            Proficiency score between 0.0 and 1.0
        """
        return self.skill_proficiency.get(skill, 0.0)

    def has_completed_resource(self, resource_id: str) -> bool:
        """Check if a resource has been completed."""
        return resource_id in self.completed_resources

    def is_beginner(self) -> bool:
        """Check if learner is a beginner."""
        return self.experience_level == "beginner"

    def is_intermediate(self) -> bool:
        """Check if learner is intermediate."""
        return self.experience_level == "intermediate"

    def is_advanced(self) -> bool:
        """Check if learner is advanced."""
        return self.experience_level == "advanced"
