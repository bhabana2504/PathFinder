"""Main recommendation engine."""

from typing import List
from pathfinder_ai.models import (
    LearnerProfile,
    LearningResource,
    SkillGapResult,
    Recommendation,
    RecommendationResult,
)
from pathfinder_ai.recommendation.ranker import ResourceRanker, ScoringWeights
from pathfinder_ai.recommendation.explain import ExplanationGenerator


def recommend_resources(
    profile: LearnerProfile,
    skill_gap: SkillGapResult,
    resources: List[LearningResource],
    top_n: int = 10,
    weights: ScoringWeights = None
) -> RecommendationResult:
    """
    Generate ranked recommendations for a learner.
    
    This is the main entry point for the recommendation engine.
    
    Process:
    1. Rank resources based on learner profile and skill gaps
    2. Generate explanations for each recommendation
    3. Determine priority levels
    4. Return ranked list with explanations
    
    Important:
    - Resources come from Harsh's RAG system
    - This module does NOT do vector search
    - We receive pre-retrieved resources and rank them
    
    Args:
        profile: Learner profile
        skill_gap: Skill gap analysis from analyze_skill_gap()
        resources: List of LearningResources from RAG system
        top_n: Maximum number of recommendations to return (default 10)
        weights: Custom scoring weights. Uses defaults if None.
        
    Returns:
        RecommendationResult with ranked recommendations and metadata
        
    Raises:
        ValueError: If inputs are invalid
    """
    
    if not resources:
        return RecommendationResult(
            user_id=profile.user_id,
            career_goal=profile.career_goal,
            recommendations=[],
            total_recommendations=0,
            top_priority_count=0,
            average_score=0.0
        )
    
    # Rank resources
    ranker = ResourceRanker(weights)
    ranked = ranker.rank_resources(resources, profile, skill_gap)
    
    # Generate explanations
    explainer = ExplanationGenerator()
    recommendations = []
    
    for resource, breakdown, score in ranked[:top_n]:
        # Validate prerequisites
        prereq_score, prereq_status, missing_prereqs = ranker.score_prerequisite_match(
            resource, profile
        )
        
        # Determine priority
        priority = _determine_priority(score, skill_gap, resource)
        
        # Generate explanation
        explanation = explainer.generate_explanation(
            resource=resource,
            profile=profile,
            skill_gap=skill_gap,
            score_breakdown=breakdown,
            prerequisite_status=prereq_status,
            missing_prerequisites=missing_prereqs
        )
        
        # Create recommendation
        recommendation = Recommendation(
            resource_id=resource.resource_id,
            title=resource.title,
            resource_type=resource.resource_type.value,
            score=score,
            reason=explanation,
            primary_skill=resource.primary_skill,
            secondary_skills=resource.secondary_skills,
            difficulty=resource.difficulty.value,
            priority=priority,
            prerequisite_status=prereq_status,
            missing_prerequisites=missing_prereqs,
            estimated_hours=resource.estimated_hours,
            fits_schedule=(breakdown.get("time_fit", 0) >= 0.7),
            career_relevance=breakdown.get("career_relevance", 0),
            interest_match=breakdown.get("interest_match", 0),
            url=resource.url,
            score_breakdown=breakdown
        )
        
        recommendations.append(recommendation)
    
    # Calculate metadata
    top_priority_count = sum(
        1 for r in recommendations if r.priority == "critical"
    )
    
    average_score = (
        sum(r.score for r in recommendations) / len(recommendations)
        if recommendations else 0.0
    )
    
    # Create result
    result = RecommendationResult(
        user_id=profile.user_id,
        career_goal=profile.career_goal,
        recommendations=recommendations,
        total_recommendations=len(recommendations),
        top_priority_count=top_priority_count,
        average_score=average_score
    )
    
    return result


def _determine_priority(
    score: float,
    skill_gap: SkillGapResult,
    resource: LearningResource
) -> str:
    """
    Determine priority level for a recommendation.
    
    Args:
        score: Overall recommendation score (0.0-1.0)
        skill_gap: Skill gap analysis
        resource: Learning resource
        
    Returns:
        Priority: 'critical', 'high', 'medium', or 'low'
    """
    
    # Critical: top priority skills with high scores
    if (resource.primary_skill in skill_gap.priority_skills[:2] and
        score >= 0.85):
        return "critical"
    
    # High: important skills or high scores
    if resource.primary_skill in skill_gap.priority_skills[:5] or score >= 0.80:
        return "high"
    
    # Medium: moderate priority
    if score >= 0.65:
        return "medium"
    
    # Low: lower priority
    return "low"
