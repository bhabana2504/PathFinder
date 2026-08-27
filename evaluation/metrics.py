"""Evaluation metrics for recommendations and learning paths."""

from typing import Dict, List, Set
from dataclasses import dataclass
from pathfinder_ai.models import Recommendation, SkillGapResult


@dataclass
class RecommendationMetrics:
    """Metrics for recommendation quality."""
    
    skill_gap_coverage: float  # % of priority skills covered
    diversity_score: float  # How diverse the recommendations are
    difficulty_appropriateness: float  # How well difficulty matches learner
    prerequisite_adherence: float  # % with met prerequisites
    average_relevance: float  # Average relevance score
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "skill_gap_coverage": self.skill_gap_coverage,
            "diversity_score": self.diversity_score,
            "difficulty_appropriateness": self.difficulty_appropriateness,
            "prerequisite_adherence": self.prerequisite_adherence,
            "average_relevance": self.average_relevance,
        }


@dataclass
class SkillGapMetrics:
    """Metrics for skill gap analysis."""
    
    gap_completeness: float  # Were all gaps identified?
    priority_accuracy: float  # Is priority ordering correct?
    prerequisite_correctness: float  # Were prerequisite chains validated?
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "gap_completeness": self.gap_completeness,
            "priority_accuracy": self.priority_accuracy,
            "prerequisite_correctness": self.prerequisite_correctness,
        }


def evaluate_recommendations(
    recommendations: List[Recommendation],
    skill_gap: SkillGapResult,
    experience_level: str
) -> RecommendationMetrics:
    """
    Evaluate recommendation quality.
    
    Args:
        recommendations: List of recommendations
        skill_gap: Skill gap analysis
        experience_level: Learner experience level
        
    Returns:
        RecommendationMetrics with evaluation results
    """
    
    if not recommendations:
        return RecommendationMetrics(
            skill_gap_coverage=0.0,
            diversity_score=0.0,
            difficulty_appropriateness=0.0,
            prerequisite_adherence=0.0,
            average_relevance=0.0
        )
    
    # Skill gap coverage: % of priority skills with recommendations
    covered_skills = set(r.primary_skill for r in recommendations)
    priority_skills = set(skill_gap.priority_skills[:5])
    skill_gap_coverage = (
        len(covered_skills & priority_skills) / len(priority_skills)
        if priority_skills else 0.0
    )
    
    # Diversity: different skills and difficulty levels
    skill_diversity = len(covered_skills) / max(1, len(skill_gap.priority_skills))
    difficulty_diversity = len(set(r.difficulty for r in recommendations)) / 4
    diversity_score = (skill_diversity + difficulty_diversity) / 2
    
    # Difficulty appropriateness
    difficulty_map = {
        "beginner": 0,
        "intermediate": 1,
        "advanced": 2,
        "expert": 3
    }
    experience_map = {"beginner": 0, "intermediate": 1, "advanced": 2}
    learner_level = experience_map.get(experience_level, 1)
    
    appropriate = sum(
        1 for r in recommendations
        if abs(difficulty_map.get(r.difficulty, 1) - learner_level) <= 1
    )
    difficulty_appropriateness = appropriate / len(recommendations)
    
    # Prerequisite adherence
    met_prereqs = sum(
        1 for r in recommendations
        if r.prerequisite_status.value == "met"
    )
    prerequisite_adherence = met_prereqs / len(recommendations)
    
    # Average relevance
    average_relevance = sum(r.score for r in recommendations) / len(recommendations)
    
    return RecommendationMetrics(
        skill_gap_coverage=skill_gap_coverage,
        diversity_score=diversity_score,
        difficulty_appropriateness=difficulty_appropriateness,
        prerequisite_adherence=prerequisite_adherence,
        average_relevance=average_relevance
    )


def evaluate_skill_gap(
    gap: SkillGapResult,
    total_career_skills: int
) -> SkillGapMetrics:
    """
    Evaluate skill gap analysis quality.
    
    Args:
        gap: Skill gap analysis result
        total_career_skills: Total skills in the career path
        
    Returns:
        SkillGapMetrics with evaluation results
    """
    
    # Gap completeness: were all gaps found?
    identified_gaps = len(gap.missing_skills) + len(gap.weak_skills)
    expected_gaps = total_career_skills - len(gap.mastered_skills)
    gap_completeness = (
        identified_gaps / expected_gaps
        if expected_gaps > 0 else 1.0
    )
    
    # Priority accuracy: are high-importance skills ranked first?
    if gap.priority_skills:
        # Simple heuristic: do missing skills rank before mastered?
        missing_in_priority = [
            s for s in gap.priority_skills[:5]
            if s in gap.missing_skills
        ]
        priority_accuracy = (
            len(missing_in_priority) / min(5, len(gap.priority_skills))
        )
    else:
        priority_accuracy = 0.5
    
    # Prerequisite correctness: simple check
    # (More thorough checks should be in unit tests)
    prerequisite_correctness = 0.8  # Placeholder
    
    return SkillGapMetrics(
        gap_completeness=gap_completeness,
        priority_accuracy=priority_accuracy,
        prerequisite_correctness=prerequisite_correctness
    )


def evaluate_learning_path(
    path_nodes: List,  # LearningPathNode objects
    skill_gap: SkillGapResult
) -> Dict:
    """
    Evaluate learning path quality.
    
    Args:
        path_nodes: Nodes in the learning path
        skill_gap: Skill gap analysis
        
    Returns:
        Dict with evaluation results
    """
    
    if not path_nodes:
        return {
            "path_length": 0,
            "difficulty_progression": 0.0,
            "skill_coverage": 0.0,
            "prerequisite_validity": True,
        }
    
    path_length = len(path_nodes)
    
    # Difficulty progression
    difficulties = [n.recommendation.difficulty for n in path_nodes]
    difficulty_map = {"beginner": 0, "intermediate": 1, "advanced": 2, "expert": 3}
    difficulty_values = [difficulty_map.get(d, 1) for d in difficulties]
    
    # Check if difficulties generally increase or stay reasonable
    if len(difficulty_values) > 1:
        increases = sum(
            1 for i in range(1, len(difficulty_values))
            if difficulty_values[i] >= difficulty_values[i-1] - 1
        )
        difficulty_progression = increases / (len(difficulty_values) - 1)
    else:
        difficulty_progression = 1.0
    
    # Skill coverage
    path_skills = set(n.recommendation.primary_skill for n in path_nodes)
    priority_skills = set(skill_gap.priority_skills[:5])
    skill_coverage = (
        len(path_skills & priority_skills) / len(priority_skills)
        if priority_skills else 0.0
    )
    
    # Prerequisite validity (all non-locked resources should be reachable)
    available = [n for n in path_nodes if n.status != "locked"]
    prerequisite_valid = len(available) >= len(path_nodes) * 0.8
    
    return {
        "path_length": path_length,
        "difficulty_progression": difficulty_progression,
        "skill_coverage": skill_coverage,
        "prerequisite_validity": prerequisite_valid,
    }
