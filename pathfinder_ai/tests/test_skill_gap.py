"""Tests for skill gap analysis module."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import LearnerProfile
from skill_gap.analyzer import analyze_skill_gap
from skill_gap.scorer import SkillPriorityScorer
from skill_gap.career_mapping import CareerSkillMapper
from sample_data import SAMPLE_LEARNER_BEGINNER, SAMPLE_LEARNER_INTERMEDIATE


def test_skill_gap_analysis_basic():
    """Test basic skill gap analysis."""
    profile = SAMPLE_LEARNER_BEGINNER
    result = analyze_skill_gap(profile)
    
    assert result.user_id == profile.user_id
    assert result.career_goal == profile.career_goal
    assert len(result.required_skills) > 0
    assert len(result.priority_skills) > 0
    print("✓ Basic skill gap analysis passed")


def test_skill_gap_missing_skills():
    """Test that missing skills are correctly identified."""
    profile = SAMPLE_LEARNER_BEGINNER
    result = analyze_skill_gap(profile)
    
    # For AI Engineer role, several skills should be missing
    assert "Machine Learning" in result.missing_skills
    assert "Deep Learning" in result.missing_skills
    assert "Statistics" in result.missing_skills
    print("✓ Missing skills detection passed")


def test_skill_gap_mastered_skills():
    """Test that mastered skills are correctly identified."""
    profile = SAMPLE_LEARNER_INTERMEDIATE
    result = analyze_skill_gap(profile)
    
    # Python should be mastered or strong
    assert "Python" in result.mastered_skills or "Python" not in result.missing_skills
    print("✓ Mastered skills detection passed")


def test_skill_gap_priority_ordering():
    """Test that skills are prioritized correctly."""
    profile = SAMPLE_LEARNER_BEGINNER
    result = analyze_skill_gap(profile)
    
    # Priority skills should be ordered by score
    scores = [result.skill_scores.get(s, 0) for s in result.priority_skills]
    
    # Scores should be in descending order
    for i in range(len(scores) - 1):
        assert scores[i] >= scores[i + 1]
    print("✓ Priority ordering passed")


def test_skill_priority_scorer():
    """Test skill priority scoring algorithm."""
    scorer = SkillPriorityScorer()
    profile = SAMPLE_LEARNER_BEGINNER
    
    # Score Python (should be high because it's required and low proficiency gap)
    score, breakdown = scorer.score_skill_priority(
        skill="Statistics",
        career="AI Engineer",
        current_proficiency=0.0,
        current_skills=profile.skill_proficiency,
        interests=profile.interests,
        experience_level=profile.experience_level
    )
    
    assert 0.0 <= score <= 1.0
    assert breakdown.skill == "Statistics"
    print("✓ Skill priority scorer passed")


def test_career_skill_mapper():
    """Test career-to-skill mapping."""
    mapper = CareerSkillMapper()
    
    # Get required skills for AI Engineer
    ai_skills = mapper.get_required_skills("AI Engineer")
    assert len(ai_skills) > 0
    assert "Python" in ai_skills or "Machine Learning" in ai_skills
    
    # Check skill importance
    importance = mapper.get_skill_importance_for_career("AI Engineer", "Python")
    assert 0.0 <= importance <= 1.0
    print("✓ Career skill mapper passed")


def test_career_skill_mapper_tiers():
    """Test skill tier classification."""
    mapper = CareerSkillMapper()
    
    # Python should be required for AI Engineer
    tier = mapper.get_skill_tier("AI Engineer", "Python")
    assert tier in ["required", "core"]
    
    # Optional skill should be classified as optional
    tier = mapper.get_skill_tier("AI Engineer", "Computer Vision")
    assert tier == "optional"
    print("✓ Skill tier classification passed")


def test_invalid_career():
    """Test handling of invalid career."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    profile.career_goal = "Unknown Career"
    
    try:
        result = analyze_skill_gap(profile)
        assert False, "Should raise ValueError for unknown career"
    except ValueError:
        print("✓ Invalid career handling passed")


def test_empty_profile():
    """Test analysis with minimal profile."""
    profile = LearnerProfile(
        user_id="test_empty",
        career_goal="AI Engineer",
        experience_level="beginner"
    )
    
    result = analyze_skill_gap(profile)
    
    assert len(result.missing_skills) > 0
    assert len(result.required_skills) > 0
    print("✓ Empty profile analysis passed")


def test_all_skills_mastered():
    """Test analysis when all skills are mastered."""
    profile = LearnerProfile(
        user_id="test_mastered",
        career_goal="AI Engineer",
        experience_level="advanced",
        current_skills=["Python", "Statistics", "Machine Learning", "Deep Learning"],
        skill_proficiency={
            "Python": 0.95,
            "Statistics": 0.9,
            "Machine Learning": 0.92,
            "Deep Learning": 0.88,
        }
    )
    
    result = analyze_skill_gap(profile)
    
    # Should have fewer missing skills
    assert len(result.missing_skills) < 5
    print("✓ All skills mastered analysis passed")


if __name__ == "__main__":
    test_skill_gap_analysis_basic()
    test_skill_gap_missing_skills()
    test_skill_gap_mastered_skills()
    test_skill_gap_priority_ordering()
    test_skill_priority_scorer()
    test_career_skill_mapper()
    test_career_skill_mapper_tiers()
    test_invalid_career()
    test_empty_profile()
    test_all_skills_mastered()
    
    print("\n✅ All skill gap tests passed!")
