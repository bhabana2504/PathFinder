"""Skill priority scoring algorithm."""

from typing import Dict, Tuple
from dataclasses import dataclass
from pathfinder_ai.skill_gap.career_mapping import CareerSkillMapper


@dataclass
class SkillGapScoreBreakdown:
    """Detailed breakdown of skill gap score calculation."""
    
    skill: str
    career_importance: float
    skill_gap_score: float  # How much improvement is needed
    prerequisite_factor: float
    learning_relevance: float
    final_score: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "career_importance": self.career_importance,
            "skill_gap_score": self.skill_gap_score,
            "prerequisite_factor": self.prerequisite_factor,
            "learning_relevance": self.learning_relevance,
            "final_score": self.final_score,
        }


class SkillPriorityScorer:
    """
    Calculates priority scores for skills using a transparent algorithm.
    
    The priority score reflects:
    1. How important the skill is for the career goal
    2. How much the learner needs to improve (skill gap)
    3. Whether prerequisites are met
    4. Relevance to the learner's interests and goals
    
    Formula:
    priority_score = career_importance × skill_gap × prerequisite_factor × learning_relevance
    
    All components are normalized to 0.0-1.0.
    """
    
    # Configuration - make these adjustable
    PROFICIENCY_THRESHOLD_WEAK = 0.6  # Below this is "weak"
    PROFICIENCY_THRESHOLD_MASTERED = 0.85  # Above this is "mastered"
    
    def __init__(self):
        """Initialize the scorer."""
        self.mapper = CareerSkillMapper()
    
    def calculate_skill_gap_score(
        self,
        current_proficiency: float,
        target_proficiency: float = 0.8
    ) -> float:
        """
        Calculate how much improvement is needed.
        
        Args:
            current_proficiency: Current skill level (0.0-1.0)
            target_proficiency: Target skill level (default 0.8)
            
        Returns:
            Gap score (0.0-1.0), where 1.0 means complete gap
        """
        gap = max(0.0, target_proficiency - current_proficiency)
        # Normalize to 0.0-1.0
        return min(1.0, gap / target_proficiency)
    
    def calculate_prerequisite_factor(
        self,
        skill: str,
        current_skills: Dict[str, float]
    ) -> float:
        """
        Calculate factor based on prerequisite fulfillment.
        
        If all prerequisites are met, factor is 1.0.
        Each missing prerequisite reduces the factor.
        
        Args:
            skill: Skill name
            current_skills: Dict of skill → proficiency
            
        Returns:
            Factor (0.0-1.0)
        """
        prereqs = self.mapper.get_skill_prerequisites_full(skill)
        
        if not prereqs:
            return 1.0
        
        # Count how many prerequisites are met
        met_prereqs = sum(
            1 for p in prereqs
            if current_skills.get(p, 0.0) >= self.PROFICIENCY_THRESHOLD_WEAK
        )
        
        # Factor decreases with missing prerequisites
        return 0.5 + (0.5 * (met_prereqs / len(prereqs)))
    
    def calculate_learning_relevance(
        self,
        skill: str,
        career: str,
        interests: list,
        experience_level: str
    ) -> float:
        """
        Calculate relevance based on career goal and interests.
        
        Args:
            skill: Skill name
            career: Career goal
            interests: List of interests
            experience_level: 'beginner', 'intermediate', or 'advanced'
            
        Returns:
            Relevance score (0.0-1.0)
        """
        relevance = 0.0
        
        # Career tier weight: required > core > optional
        tier = self.mapper.get_skill_tier(career, skill)
        tier_weights = {
            "required": 0.6,
            "core": 0.4,
            "optional": 0.2,
            "not_relevant": 0.1
        }
        relevance += tier_weights.get(tier, 0.1)
        
        # Interest match: boost if in interests
        for interest in interests:
            if interest.lower() in skill.lower() or skill.lower() in interest.lower():
                relevance += 0.3
                break
        
        # Experience level adjustment
        experience_boost = {
            "beginner": 0.1,   # Beginners should focus on fundamentals
            "intermediate": 0.2,
            "advanced": 0.15
        }
        relevance += experience_boost.get(experience_level, 0.1)
        
        return min(1.0, relevance)
    
    def score_skill_priority(
        self,
        skill: str,
        career: str,
        current_proficiency: float,
        current_skills: Dict[str, float],
        interests: list,
        experience_level: str
    ) -> Tuple[float, SkillGapScoreBreakdown]:
        """
        Calculate priority score for a skill.
        
        Args:
            skill: Skill name
            career: Career goal
            current_proficiency: Current proficiency (0.0-1.0)
            current_skills: All current skills and proficiencies
            interests: List of interests
            experience_level: Experience level
            
        Returns:
            Tuple of (score, breakdown_details)
        """
        # Component 1: Career importance
        career_importance = self.mapper.get_skill_importance_for_career(
            career, skill
        )
        
        # Component 2: Skill gap
        skill_gap = self.calculate_skill_gap_score(current_proficiency)
        
        # Component 3: Prerequisite fulfillment
        prerequisite_factor = self.calculate_prerequisite_factor(
            skill, current_skills
        )
        
        # Component 4: Learning relevance
        learning_relevance = self.calculate_learning_relevance(
            skill, career, interests, experience_level
        )
        
        # Final score: multiply all components
        final_score = (
            career_importance * 
            skill_gap * 
            prerequisite_factor * 
            learning_relevance
        )
        
        # Normalize final score to 0.0-1.0
        final_score = min(1.0, final_score)
        
        breakdown = SkillGapScoreBreakdown(
            skill=skill,
            career_importance=career_importance,
            skill_gap_score=skill_gap,
            prerequisite_factor=prerequisite_factor,
            learning_relevance=learning_relevance,
            final_score=final_score
        )
        
        return final_score, breakdown
    
    def classify_proficiency(self, proficiency: float) -> str:
        """
        Classify proficiency level.
        
        Args:
            proficiency: Proficiency score (0.0-1.0)
            
        Returns:
            Classification: 'none', 'weak', 'moderate', 'strong', or 'mastered'
        """
        if proficiency < 0.2:
            return "none"
        elif proficiency < self.PROFICIENCY_THRESHOLD_WEAK:
            return "weak"
        elif proficiency < 0.75:
            return "moderate"
        elif proficiency < self.PROFICIENCY_THRESHOLD_MASTERED:
            return "strong"
        else:
            return "mastered"
