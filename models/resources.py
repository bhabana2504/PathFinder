"""Learning resource data model."""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum


class ResourceType(str, Enum):
    """Types of learning resources."""
    
    COURSE = "course"
    TUTORIAL = "tutorial"
    ARTICLE = "article"
    VIDEO = "video"
    BOOK = "book"
    PROJECT = "project"
    CHALLENGE = "challenge"
    DOCUMENTATION = "documentation"
    PODCAST = "podcast"
    WORKSHOP = "workshop"


class DifficultyLevel(str, Enum):
    """Resource difficulty levels."""
    
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningResource(BaseModel):
    """
    Represents a learning resource retrieved from RAG system.
    
    This model comes from Harsh's RAG module and is consumed
    by the recommendation engine.
    """
    
    resource_id: str = Field(..., description="Unique resource identifier")
    title: str = Field(..., description="Resource title")
    description: str = Field(..., description="Detailed description")
    resource_type: ResourceType = Field(..., description="Type of resource")
    primary_skill: str = Field(..., description="Main skill this resource teaches")
    secondary_skills: List[str] = Field(
        default_factory=list,
        description="Additional skills covered"
    )
    difficulty: DifficultyLevel = Field(..., description="Resource difficulty level")
    prerequisites: List[str] = Field(
        default_factory=list,
        description="Required prerequisite skills"
    )
    estimated_hours: float = Field(
        default=5.0,
        ge=0.5,
        le=500.0,
        description="Estimated hours to complete"
    )
    url: Optional[str] = Field(
        default=None,
        description="URL to the resource"
    )
    target_careers: List[str] = Field(
        default_factory=list,
        description="Careers this resource is relevant for"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags and categories"
    )
    ratings: float = Field(
        default=4.0,
        ge=0.0,
        le=5.0,
        description="Average rating (0-5 stars)"
    )
    completion_rate: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Estimated completion rate"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "resource_id": "ml101",
                "title": "Machine Learning Fundamentals",
                "description": "Learn the basics of machine learning",
                "resource_type": "course",
                "primary_skill": "Machine Learning",
                "secondary_skills": ["Python", "Statistics"],
                "difficulty": "intermediate",
                "prerequisites": ["Python", "Statistics"],
                "estimated_hours": 20.0,
                "url": "https://example.com/ml101",
                "target_careers": ["AI Engineer", "ML Engineer", "Data Scientist"],
                "tags": ["ml", "ai", "supervised-learning"],
                "ratings": 4.5,
                "completion_rate": 0.75
            }
        }

    def has_prerequisites(self) -> bool:
        """Check if resource has prerequisites."""
        return len(self.prerequisites) > 0

    def is_beginner_friendly(self) -> bool:
        """Check if suitable for beginners."""
        return self.difficulty == DifficultyLevel.BEGINNER

    def is_advanced(self) -> bool:
        """Check if advanced level."""
        return self.difficulty in [DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]

    def all_skills(self) -> List[str]:
        """Get all skills covered by this resource."""
        return [self.primary_skill] + self.secondary_skills

    def is_relevant_to_career(self, career: str) -> bool:
        """Check if resource targets the given career."""
        return career in self.target_careers
