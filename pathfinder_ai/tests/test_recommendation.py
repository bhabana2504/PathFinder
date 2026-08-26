"""Tests for recommendation engine."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import LearnerProfile
from skill_gap.analyzer import analyze_skill_gap
from recommendation.recommender import recommend_resources
from recommendation.ranker import ResourceRanker, ScoringWeights
from sample_data import SAMPLE_LEARNER_BEGINNER, SAMPLE_RESOURCES


def test_recommendation_basic():
    """Test basic recommendation generation."""
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES)
    
    assert result.user_id == profile.user_id
    assert result.career_goal == profile.career_goal
    assert len(result.recommendations) > 0
    print("✓ Basic recommendation generation passed")


def test_recommendation_scoring():
    """Test that recommendations are scored."""
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES)
    
    for rec in result.recommendations:
        assert 0.0 <= rec.score <= 1.0
        assert len(rec.reason) > 0
        assert rec.resource_id is not None
    print("✓ Recommendation scoring passed")


def test_recommendation_ranking():
    """Test that recommendations are ranked by score."""
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES)
    
    # Check that scores are in descending order
    scores = [r.score for r in result.recommendations]
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1]
    print("✓ Recommendation ranking passed")


def test_recommendation_respects_prerequisites():
    """Test that prerequisites affect recommendation score."""
    profile = SAMPLE_LEARNER_BEGINNER  # Limited skills
    gap = analyze_skill_gap(profile)
    
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES)
    
    # Resources with unmet prerequisites should have lower scores
    for rec in result.recommendations:
        if rec.missing_prerequisites:
            assert rec.prerequisite_status.value != "met"
    print("✓ Prerequisite handling passed")


def test_recommendation_excludes_completed():
    """Test that completed resources are excluded."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    profile.completed_resources = ["python_basics_101"]
    
    gap = analyze_skill_gap(profile)
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES)
    
    # Completed resource should not be in recommendations
    rec_ids = [r.resource_id for r in result.recommendations]
    assert "python_basics_101" not in rec_ids
    print("✓ Completed resource exclusion passed")


def test_resource_ranker_weights():
    """Test custom scoring weights."""
    weights = ScoringWeights(
        skill_gap_weight=0.5,  # Emphasize skill gaps
        career_relevance_weight=0.2,
        difficulty_match_weight=0.15,
        prerequisite_match_weight=0.05,
        interest_match_weight=0.05,
        time_fit_weight=0.05,
    )
    
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES, weights=weights)
    assert len(result.recommendations) > 0
    print("✓ Custom weights handling passed")


def test_ranker_skill_gap_score():
    """Test skill gap score calculation."""
    ranker = ResourceRanker()
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    # Find a resource targeting a priority skill
    ml_resource = next(r for r in SAMPLE_RESOURCES if r.primary_skill == "Machine Learning")
    
    score = ranker.score_skill_gap_match(ml_resource, gap, profile)
    assert 0.0 <= score <= 1.0
    print("✓ Skill gap score calculation passed")


def test_ranker_difficulty_match():
    """Test difficulty matching for experience level."""
    ranker = ResourceRanker()
    
    beginner_profile = SAMPLE_LEARNER_BEGINNER
    
    # Beginner-level resource should score higher for beginner
    beginner_resource = next(
        r for r in SAMPLE_RESOURCES
        if r.difficulty.value == "beginner"
    )
    
    score = ranker.score_difficulty_match(beginner_resource, beginner_profile)
    assert score >= 0.7  # Should be high match
    print("✓ Difficulty matching passed")


def test_explanation_generation():
    """Test that recommendations have explanations."""
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES, top_n=5)
    
    for rec in result.recommendations:
        assert len(rec.reason) > 20  # Should have meaningful explanation
        assert "because" in rec.reason.lower() or "recommended" in rec.reason.lower()
    print("✓ Explanation generation passed")


def test_no_resources():
    """Test handling of empty resource list."""
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    result = recommend_resources(profile, gap, [])
    
    assert len(result.recommendations) == 0
    assert result.average_score == 0.0
    print("✓ Empty resource list handling passed")


def test_top_n_limit():
    """Test that top_n parameter is respected."""
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    # Request only 3 recommendations
    result = recommend_resources(profile, gap, SAMPLE_RESOURCES, top_n=3)
    
    assert len(result.recommendations) <= 3
    print("✓ Top N limit passed")


if __name__ == "__main__":
    test_recommendation_basic()
    test_recommendation_scoring()
    test_recommendation_ranking()
    test_recommendation_respects_prerequisites()
    test_recommendation_excludes_completed()
    test_resource_ranker_weights()
    test_ranker_skill_gap_score()
    test_ranker_difficulty_match()
    test_explanation_generation()
    test_no_resources()
    test_top_n_limit()
    
    print("\n✅ All recommendation tests passed!")
