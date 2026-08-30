"""Skill data model."""

from typing import List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class SkillCategory(str, Enum):
    """Skill categories."""
    
    PROGRAMMING = "programming"
    MATHEMATICS = "mathematics"
    MACHINE_LEARNING = "machine_learning"
    DATA_SCIENCE = "data_science"
    FRONTEND = "frontend"
    BACKEND = "backend"
    CLOUD = "cloud"
    DEVOPS = "devops"
    SECURITY = "security"
    SOFT_SKILLS = "soft_skills"
    OTHER = "other"


class Skill(BaseModel):
    """
    Represents a learnable skill with its relationships and metadata.
    """
    
    name: str = Field(..., description="Skill name (e.g., 'Python')")
    category: SkillCategory = Field(..., description="Skill category")
    description: str = Field(
        default="",
        description="Detailed description of the skill"
    )
    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Base importance score (0.0 to 1.0)"
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="List of prerequisite skill names"
    )
    related_skills: List[str] = Field(
        default_factory=list,
        description="List of related skill names"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Python",
                "category": "programming",
                "description": "Python programming language",
                "importance": 1.0,
                "prerequisites": [],
                "related_skills": ["JavaScript", "C++"]
            }
        }
    )

    def has_prerequisites(self) -> bool:
        """Check if skill has prerequisites."""
        return len(self.prerequisites) > 0

    def __hash__(self) -> int:
        """Make Skill hashable for use in sets/dicts."""
        return hash(self.name)

    def __eq__(self, other) -> bool:
        """Compare skills by name."""
        if isinstance(other, Skill):
            return self.name == other.name
        return False
