"""Adaptive learning profile updates."""

from typing import Dict, Optional
from pathfinder_ai.models import LearnerProfile


def update_skill_from_assessment(
    profile: LearnerProfile,
    skill: str,
    assessment_score: float,
    weight: float = 0.6
) -> LearnerProfile:
    """
    Update skill proficiency based on assessment results.
    
    Uses a weighted average to combine:
    - Existing proficiency
    - New assessment score
    
    Args:
        profile: Current learner profile
        skill: Skill name
        assessment_score: Assessment score (0.0-1.0)
        weight: Weight for new assessment (0.0-1.0), default 0.6
        
    Returns:
        Updated learner profile
        
    Raises:
        ValueError: If score is outside 0.0-1.0
    """
    
    if not (0.0 <= assessment_score <= 1.0):
        raise ValueError(
            f"Assessment score must be between 0.0 and 1.0, got {assessment_score}"
        )
    
    if not (0.0 <= weight <= 1.0):
        raise ValueError(
            f"Weight must be between 0.0 and 1.0, got {weight}"
        )
    
    # Get current proficiency
    current_proficiency = profile.get_skill_proficiency(skill)
    
    # Calculate new proficiency using weighted average
    new_proficiency = (
        (current_proficiency * (1 - weight)) +
        (assessment_score * weight)
    )
    
    # Add skill if not present
    if skill not in profile.current_skills:
        profile.current_skills.append(skill)
    
    # Update proficiency
    profile.skill_proficiency[skill] = new_proficiency
    
    # Record assessment result
    profile.assessment_results[skill] = assessment_score
    
    return profile


def update_learner_profile(
    profile: LearnerProfile,
    **updates
) -> LearnerProfile:
    """
    Update learner profile with new information.
    
    Supported updates:
    - completed_resources: Add completed resource IDs
    - skill_proficiency: Update skill levels
    - assessment_results: Add assessment scores
    - feedback: Add user feedback
    - interests: Update interests
    
    Args:
        profile: Current learner profile
        **updates: Keyword arguments for fields to update
        
    Returns:
        Updated learner profile
        
    Example:
        >>> updated = update_learner_profile(
        ...     profile,
        ...     completed_resources=["course_123"],
        ...     skill_proficiency={"Python": 0.9}
        ... )
    """
    
    # Handle completed resources
    if "completed_resources" in updates:
        new_resources = updates["completed_resources"]
        if isinstance(new_resources, list):
            profile.completed_resources.extend(new_resources)
        else:
            profile.completed_resources.append(new_resources)
        profile.completed_resources = list(dict.fromkeys(profile.completed_resources))
    
    # Handle skill proficiency updates
    if "skill_proficiency" in updates:
        updates_dict = updates["skill_proficiency"]
        for skill, proficiency in updates_dict.items():
            if not (0.0 <= proficiency <= 1.0):
                raise ValueError(
                    f"Skill proficiency must be 0.0-1.0, got {proficiency}"
                )
            profile.skill_proficiency[skill] = proficiency
            
            # Add to current_skills if not present
            if skill not in profile.current_skills:
                profile.current_skills.append(skill)
    
    # Handle assessment results
    if "assessment_results" in updates:
        profile.assessment_results.update(updates["assessment_results"])
    
    # Handle feedback
    if "feedback" in updates:
        feedback = updates["feedback"]
        if isinstance(feedback, list):
            profile.feedback.extend(feedback)
        else:
            profile.feedback.append(feedback)
    
    # Handle interests
    if "interests" in updates:
        interests = updates["interests"]
        if isinstance(interests, list):
            profile.interests = interests
        else:
            profile.interests = [interests]
    
    # Handle other simple updates
    for field in ["career_goal", "experience_level", "learning_hours_per_week"]:
        if field in updates:
            setattr(profile, field, updates[field])
    
    return profile


def mark_resource_completed(
    profile: LearnerProfile,
    resource_id: str,
    rating: Optional[float] = None
) -> LearnerProfile:
    """
    Mark a resource as completed.
    
    Args:
        profile: Current learner profile
        resource_id: Resource ID to mark complete
        rating: Optional rating (0.0-5.0)
        
    Returns:
        Updated learner profile
    """
    
    if resource_id not in profile.completed_resources:
        profile.completed_resources.append(resource_id)
    
    if rating is not None:
        if not (0.0 <= rating <= 5.0):
            raise ValueError(f"Rating must be 0.0-5.0, got {rating}")
        
        # Add to feedback for tracking
        profile.feedback.append(f"Resource {resource_id}: {rating}/5.0 stars")
    
    return profile


def reset_skill_proficiency(
    profile: LearnerProfile,
    skill: str
) -> LearnerProfile:
    """
    Reset a skill proficiency to 0.0.
    
    Useful for correcting mistaken proficiency assessments.
    
    Args:
        profile: Current learner profile
        skill: Skill to reset
        
    Returns:
        Updated learner profile
    """
    
    if skill in profile.skill_proficiency:
        profile.skill_proficiency[skill] = 0.0
    
    return profile
