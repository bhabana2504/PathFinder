"""Main skill gap analyzer."""

from typing import Dict
from models import LearnerProfile, SkillGapResult
from skill_gap.career_mapping import CareerSkillMapper
from skill_gap.scorer import SkillPriorityScorer


def analyze_skill_gap(profile: LearnerProfile) -> SkillGapResult:
    """
    Analyze skill gaps for a learner against their career goal.
    
    This is the main entry point for skill gap analysis.
    
    Process:
    1. Load career requirements
    2. Compare with current skills
    3. Identify missing and weak skills
    4. Score priority for each skill
    5. Return comprehensive analysis
    
    Args:
        profile: Learner profile with goals and current skills
        
    Returns:
        SkillGapResult with detailed analysis
        
    Raises:
        ValueError: If career goal is not found
    """
    
    mapper = CareerSkillMapper()
    scorer = SkillPriorityScorer()
    
    # Validate career
    required_skills = mapper.get_required_skills(profile.career_goal)
    if not required_skills:
        raise ValueError(f"Unknown career: {profile.career_goal}")
    
    # Get all skills for the career
    all_required_skills = mapper.get_all_skills_for_career(profile.career_goal)
    
    # Classify learner's current skills
    missing_skills = []
    weak_skills = []
    mastered_skills = []
    current_skills_set = set(profile.current_skills)
    
    for skill in all_required_skills:
        proficiency = profile.get_skill_proficiency(skill)
        is_known = (skill in current_skills_set) or (proficiency > 0.0)
        tier = mapper.get_skill_tier(profile.career_goal, skill)
        
        if proficiency >= scorer.PROFICIENCY_THRESHOLD_MASTERED:
            mastered_skills.append(skill)
        elif tier == "required":
            if is_known and proficiency >= 0.2:
                weak_skills.append(skill)
            else:
                missing_skills.append(skill)
        elif tier == "core":
            if is_known:
                weak_skills.append(skill)
        elif tier == "optional":
            if is_known:
                weak_skills.append(skill)
    
    # Calculate priority scores for all missing and weak skills
    skill_scores = {}
    gap_analysis = {}
    
    for skill in missing_skills + weak_skills:
        score, breakdown = scorer.score_skill_priority(
            skill=skill,
            career=profile.career_goal,
            current_proficiency=profile.get_skill_proficiency(skill),
            current_skills=profile.skill_proficiency,
            interests=profile.interests,
            experience_level=profile.experience_level
        )
        
        skill_scores[skill] = score
        
        current_prof = profile.get_skill_proficiency(skill)
        target_prof = 0.8
        gap_val = max(0.0, target_prof - current_prof)
        
        if score >= 0.5:
            priority_val = "critical"
        elif score >= 0.3:
            priority_val = "high"
        elif score >= 0.1:
            priority_val = "medium"
        else:
            priority_val = "low"
            
        analysis_dict = breakdown.to_dict()
        analysis_dict.update({
            "current": current_prof,
            "required": target_prof,
            "gap": gap_val,
            "priority": priority_val
        })
        gap_analysis[skill] = analysis_dict
    
    # Rank skills by priority
    priority_skills = sorted(
        skill_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    priority_skills_list = [skill for skill, _ in priority_skills]
    
    # Create result
    result = SkillGapResult(
        user_id=profile.user_id,
        career_goal=profile.career_goal,
        required_skills=all_required_skills,
        current_skills=list(current_skills_set),
        missing_skills=missing_skills,
        weak_skills=weak_skills,
        mastered_skills=mastered_skills,
        skill_scores=skill_scores,
        priority_skills=priority_skills_list,
        gap_analysis=gap_analysis
    )
    
    return result
