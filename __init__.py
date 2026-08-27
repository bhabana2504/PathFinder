"""
PathFinder AI/ML Module

A comprehensive AI/ML module for personalized learning path recommendation.

Main Entry Points:
- analyze_skill_gap: Identify skill gaps for a learner
- recommend_resources: Get ranked resource recommendations
- generate_learning_path: Create a prerequisite-respecting learning sequence
- update_learner_profile: Update profile based on completion/assessment

Example Usage:
    from pathfinder_ai.models import LearnerProfile
    from pathfinder_ai.skill_gap import analyze_skill_gap
    from pathfinder_ai.recommendation import recommend_resources
    from pathfinder_ai.learning_path import generate_learning_path
    
    # Create learner profile
    profile = LearnerProfile(
        user_id="123",
        career_goal="AI Engineer",
        experience_level="beginner",
        current_skills=["Python", "SQL"]
    )
    
    # Analyze skill gaps
    gap = analyze_skill_gap(profile)
    
    # Get recommendations (from RAG system)
    recommendations = recommend_resources(profile, gap, retrieved_resources)
    
    # Generate learning path
    path = generate_learning_path(profile, gap, recommendations)
"""

__version__ = "0.1.0"
__author__ = "Bhabana Kalita"
__description__ = "AI/ML module for PathFinder personalized learning platform"

from pathfinder_ai.models import (
    LearnerProfile,
    Skill,
    LearningResource,
    Recommendation,
    SkillGapResult,
)
from pathfinder_ai.skill_gap import analyze_skill_gap
from pathfinder_ai.recommendation import recommend_resources
from pathfinder_ai.learning_path import generate_learning_path
from pathfinder_ai.adaptive_learning import update_learner_profile

__all__ = [
    "LearnerProfile",
    "Skill",
    "LearningResource",
    "Recommendation",
    "SkillGapResult",
    "analyze_skill_gap",
    "recommend_resources",
    "generate_learning_path",
    "update_learner_profile",
]
