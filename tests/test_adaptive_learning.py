"""Tests for adaptive learning module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import LearnerProfile
from adaptive_learning.updater import (
    update_learner_profile,
    update_skill_from_assessment,
    mark_resource_completed,
)
from adaptive_learning.progress_analyzer import ProgressAnalyzer
from sample_data import SAMPLE_LEARNER_BEGINNER, SAMPLE_LEARNER_INTERMEDIATE


def test_update_skill_from_assessment():
    """Test skill proficiency updates from assessment."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    initial_prof = profile.get_skill_proficiency("Python")
    
    # Update based on assessment
    updated = update_skill_from_assessment(
        profile,
        skill="Python",
        assessment_score=0.9,
        weight=0.6
    )
    
    new_prof = updated.get_skill_proficiency("Python")
    
    # New proficiency should be between old and assessment score
    assert initial_prof < new_prof < 1.0
    assert updated.assessment_results["Python"] == 0.9
    print("✓ Assessment-based skill update passed")


def test_update_skill_new_skill():
    """Test adding a new skill via assessment."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    
    updated = update_skill_from_assessment(
        profile,
        skill="Machine Learning",
        assessment_score=0.75,
        weight=0.6
    )
    
    # New skill should be added
    assert "Machine Learning" in updated.current_skills
    assert updated.get_skill_proficiency("Machine Learning") > 0
    print("✓ New skill addition passed")


def test_update_profile_resources():
    """Test marking resources as completed."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    
    updated = update_learner_profile(
        profile,
        completed_resources=["course_123", "course_456"]
    )
    
    assert "course_123" in updated.completed_resources
    assert "course_456" in updated.completed_resources
    print("✓ Resource completion update passed")


def test_update_profile_skills():
    """Test batch skill proficiency updates."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    
    updates = {
        "Python": 0.9,
        "SQL": 0.75,
        "Statistics": 0.6,
    }
    
    updated = update_learner_profile(profile, skill_proficiency=updates)
    
    assert updated.get_skill_proficiency("Python") == 0.9
    assert updated.get_skill_proficiency("SQL") == 0.75
    assert updated.get_skill_proficiency("Statistics") == 0.6
    print("✓ Batch skill update passed")


def test_mark_resource_completed():
    """Test marking resource as completed."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    
    updated = mark_resource_completed(profile, "course_789", rating=4.5)
    
    assert "course_789" in updated.completed_resources
    assert any("course_789" in f for f in updated.feedback)
    print("✓ Resource completion marking passed")


def test_progress_analysis_basic():
    """Test basic progress analysis."""
    analyzer = ProgressAnalyzer()
    profile = SAMPLE_LEARNER_INTERMEDIATE
    
    metrics = analyzer.analyze_progress(profile, total_available_resources=20)
    
    assert 0.0 <= metrics.completion_rate <= 1.0
    assert 0.0 <= metrics.mastery_percentage <= 1.0
    assert 0.0 <= metrics.engagement_score <= 1.0
    print("✓ Basic progress analysis passed")


def test_identify_strengths():
    """Test identification of strong skills."""
    analyzer = ProgressAnalyzer()
    profile = SAMPLE_LEARNER_INTERMEDIATE
    
    strengths = analyzer.identify_strengths(profile)
    
    # Should identify high-proficiency skills
    assert len(strengths) > 0
    for skill in strengths:
        assert profile.get_skill_proficiency(skill) >= 0.85
    print("✓ Strength identification passed")


def test_identify_struggles():
    """Test identification of struggling skills."""
    analyzer = ProgressAnalyzer()
    profile = SAMPLE_LEARNER_INTERMEDIATE
    
    struggles = analyzer.identify_struggles(profile)
    
    # All identified struggles should have low proficiency
    for skill in struggles:
        assert profile.get_skill_proficiency(skill) < 0.4
    print("✓ Struggle identification passed")


def test_progress_report():
    """Test comprehensive progress report generation."""
    analyzer = ProgressAnalyzer()
    profile = SAMPLE_LEARNER_INTERMEDIATE
    
    report = analyzer.generate_progress_report(profile)
    
    assert "metrics" in report
    assert "strengths" in report
    assert "struggles" in report
    assert "resources_completed" in report
    assert report["user_id"] == profile.user_id
    print("✓ Progress report generation passed")


def test_progress_improvement_tracking():
    """Test tracking of skill improvements."""
    analyzer = ProgressAnalyzer()
    
    # Create before and after profiles
    before = SAMPLE_LEARNER_BEGINNER.copy()
    after = SAMPLE_LEARNER_BEGINNER.copy()
    after.skill_proficiency["Python"] = 0.85
    after.skill_proficiency["SQL"] = 0.75
    
    metrics = analyzer.analyze_progress(after, before)
    
    # Should detect improvement
    assert metrics.skill_improvement > 0
    print("✓ Progress improvement tracking passed")


def test_mastery_percentage():
    """Test mastery percentage calculation."""
    analyzer = ProgressAnalyzer()
    
    # Profile with some mastered skills
    profile = LearnerProfile(
        user_id="test_mastery",
        career_goal="AI Engineer",
        experience_level="intermediate",
        skill_proficiency={
            "Python": 0.95,
            "Statistics": 0.82,
            "SQL": 0.7,
        }
    )
    
    metrics = analyzer.analyze_progress(profile)
    
    # Python is mastered (0.95 >= 0.85), others are not
    # So mastery percentage should be around 1/3
    assert 0 < metrics.mastery_percentage < 1
    print("✓ Mastery percentage calculation passed")


def test_invalid_assessment_score():
    """Test validation of assessment scores."""
    profile = SAMPLE_LEARNER_BEGINNER.copy()
    
    try:
        update_skill_from_assessment(profile, "Python", 1.5)
        assert False, "Should reject score > 1.0"
    except ValueError:
        print("✓ Invalid assessment score rejection passed")


if __name__ == "__main__":
    test_update_skill_from_assessment()
    test_update_skill_new_skill()
    test_update_profile_resources()
    test_update_profile_skills()
    test_mark_resource_completed()
    test_progress_analysis_basic()
    test_identify_strengths()
    test_identify_struggles()
    test_progress_report()
    test_progress_improvement_tracking()
    test_mastery_percentage()
    test_invalid_assessment_score()
    
    print("\n✅ All adaptive learning tests passed!")
