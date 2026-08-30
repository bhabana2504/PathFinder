"""Explanation generator for recommendations."""

from typing import Dict, List
from models import (
    LearnerProfile,
    LearningResource,
    SkillGapResult,
    PrerequisiteStatus,
)
from skill_gap.scorer import SkillPriorityScorer


class ExplanationGenerator:
    """
    Generates human-readable explanations for why resources are recommended.
    """
    
    def __init__(self):
        """Initialize the explanation generator."""
        self.scorer = SkillPriorityScorer()
    
    def generate_explanation(
        self,
        resource: LearningResource,
        profile: LearnerProfile,
        skill_gap: SkillGapResult,
        score_breakdown: Dict[str, float],
        prerequisite_status: PrerequisiteStatus,
        missing_prerequisites: List[str]
    ) -> str:
        """
        Generate a detailed explanation for a recommendation.
        
        Args:
            resource: The learning resource
            profile: Learner profile
            skill_gap: Skill gap analysis result
            score_breakdown: Component scores
            prerequisite_status: Status of prerequisites
            missing_prerequisites: Any missing prerequisites
            
        Returns:
            Human-readable explanation string
        """
        reasons = []
        
        # Reason 1: Skill importance
        if resource.primary_skill in skill_gap.priority_skills:
            priority_index = skill_gap.priority_skills.index(
                resource.primary_skill
            )
            
            if priority_index == 0:
                reasons.append(
                    f"{resource.primary_skill} is your highest priority skill "
                    f"for becoming an {profile.career_goal}"
                )
            else:
                reasons.append(
                    f"{resource.primary_skill} is a high-priority skill "
                    f"needed for your {profile.career_goal} goal"
                )
        
        # Reason 2: Skill gap
        current_prof = profile.get_skill_proficiency(resource.primary_skill)
        if current_prof < 0.3:
            reasons.append(
                f"your {resource.primary_skill} proficiency is currently low ({current_prof:.0%}), "
                f"and this resource covers the fundamentals"
            )
        elif current_prof < 0.6:
            reasons.append(
                f"you have basic {resource.primary_skill} knowledge but need strengthening"
            )
        
        # Reason 3: Difficulty match
        difficulty = resource.difficulty.value
        exp_level = profile.experience_level
        
        if difficulty == exp_level:
            reasons.append(
                f"the resource difficulty ({difficulty}) matches your experience level"
            )
        elif difficulty == "beginner" and exp_level != "beginner":
            reasons.append(
                f"it covers fundamentals to fill foundational gaps"
            )
        
        # Reason 4: Prerequisites
        if prerequisite_status == PrerequisiteStatus.MET:
            completed_prereqs = [p for p in resource.prerequisites
                               if p in profile.current_skills]
            if completed_prereqs:
                reasons.append(
                    f"you've already completed the required prerequisites "
                    f"({', '.join(completed_prereqs[:2])})"
                )
        elif prerequisite_status == PrerequisiteStatus.PARTIALLY_MET:
            met_count = len(resource.prerequisites) - len(missing_prerequisites)
            reasons.append(
                f"you've met {met_count}/{len(resource.prerequisites)} prerequisites; "
                f"this can still be valuable with review"
            )
        elif missing_prerequisites:
            reasons.append(
                f"note: this resource requires {', '.join(missing_prerequisites)}, "
                f"which you should complete first for best results"
            )
        
        # Reason 5: Career relevance
        career_score = score_breakdown.get("career_relevance", 0)
        if career_score >= 0.85:
            reasons.append(
                f"it is directly relevant to {profile.career_goal} roles"
            )
        elif career_score >= 0.7:
            reasons.append(
                f"it is important for {profile.career_goal} careers"
            )
        
        # Reason 6: Interest match
        interest_score = score_breakdown.get("interest_match", 0)
        if interest_score > 0.6 and profile.interests:
            # Find which interest matched
            for interest in profile.interests:
                if interest.lower() in resource.primary_skill.lower():
                    reasons.append(
                        f"it aligns with your interest in {interest}"
                    )
                    break
                elif any(interest.lower() in tag.lower() 
                        for tag in resource.tags):
                    reasons.append(
                        f"it aligns with your interest in {interest}"
                    )
                    break
        
        # Reason 7: Time fit
        time_score = score_breakdown.get("time_fit", 0)
        hours = resource.estimated_hours
        weeks = hours / max(1, profile.learning_hours_per_week)
        
        if time_score >= 0.85:
            if weeks <= 4:
                weeks_val = round(weeks)
                weeks_str = f"{weeks_val} week" if weeks_val == 1 else f"{weeks_val} weeks"
                learning_hours = profile.learning_hours_per_week
                hours_str = f"{int(learning_hours)} hours/week" if learning_hours.is_integer() else f"{learning_hours} hours/week"
                reasons.append(
                    f"it is achievable in about {weeks_str} based on your "
                    f"{hours_str} availability"
                )
        elif time_score < 0.5:
            reasons.append(
                f"it requires a longer commitment ({hours:.0f} hours); "
                f"consider breaking it into parts"
            )
        
        # Combine reasons into coherent explanation
        if len(reasons) == 0:
            return (
                f"This {resource.resource_type.value} on {resource.primary_skill} "
                f"is recommended because it is relevant to your learning goals."
            )
        
        def adjust_first_reason(text: str) -> str:
            if not text:
                return text
            words = text.split(" ")
            first_word = words[0]
            # If the first word matches the primary skill name, keep capitalization
            if first_word.lower() == resource.primary_skill.split(" ")[0].lower():
                return text
            # Otherwise lowercase the first letter
            return text[0].lower() + text[1:]
            
        def capitalize_sentence(text: str) -> str:
            if not text:
                return text
            return text[0].upper() + text[1:]

        main_reason = "This resource is recommended because " + adjust_first_reason(reasons[0])
        supporting_reasons = reasons[1:]
        
        if supporting_reasons:
            supporting_text = " ".join([
                f"{capitalize_sentence(reason)}."
                for reason in supporting_reasons
            ])
            return f"{main_reason}. {supporting_text}"
        else:
            return f"{main_reason}."
    
    def generate_brief_reason(
        self,
        resource: LearningResource,
        skill_gap: SkillGapResult,
        score_breakdown: Dict[str, float]
    ) -> str:
        """
        Generate a brief one-sentence explanation.
        
        Args:
            resource: The learning resource
            skill_gap: Skill gap analysis result
            score_breakdown: Component scores
            
        Returns:
            Brief explanation string
        """
        # Find the strongest component score
        components = [
            ("skill_gap", "addresses a key skill gap"),
            ("career_relevance", "is relevant to your career goal"),
            ("difficulty_match", "matches your skill level"),
            ("interest_match", "aligns with your interests"),
            ("prerequisite_match", "builds on your current skills"),
        ]
        
        best_component = max(
            [(name, reason) for name, reason in components],
            key=lambda x: score_breakdown.get(x[0], 0)
        )
        
        return (
            f"Recommended because this resource "
            f"{best_component[1]}"
        )
    
    def prioritize_reason(
        self,
        resource: LearningResource,
        profile: LearnerProfile,
        skill_gap: SkillGapResult,
        score_breakdown: Dict[str, float]
    ) -> str:
        """
        Generate explanation focused on priority/urgency.
        
        Args:
            resource: The learning resource
            profile: Learner profile
            skill_gap: Skill gap analysis result
            score_breakdown: Component scores
            
        Returns:
            Priority-focused explanation
        """
        if resource.primary_skill in skill_gap.priority_skills[:3]:
            position = skill_gap.priority_skills.index(
                resource.primary_skill
            ) + 1
            
            return (
                f"This resource is recommended because it teaches {resource.primary_skill}, "
                f"your #{position} priority skill. "
                f"Completing this will significantly improve your path to {profile.career_goal}."
            )
        else:
            return (
                f"This resource is recommended because it covers {resource.primary_skill}, "
                f"which will strengthen your foundation after addressing "
                f"your immediate priorities."
            )
