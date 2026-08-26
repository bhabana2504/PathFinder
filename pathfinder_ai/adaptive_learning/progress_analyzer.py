"""Learning progress analysis."""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from pathfinder_ai.models import LearnerProfile


@dataclass
class ProgressMetrics:
    """Learning progress metrics."""
    
    completion_rate: float  # Percentage of resources completed
    skill_improvement: float  # Average improvement across skills
    learning_velocity: float  # Speed of completion
    mastery_percentage: float  # Percentage of skills mastered
    engagement_score: float  # Based on feedback and activity
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "completion_rate": self.completion_rate,
            "skill_improvement": self.skill_improvement,
            "learning_velocity": self.learning_velocity,
            "mastery_percentage": self.mastery_percentage,
            "engagement_score": self.engagement_score,
        }


class ProgressAnalyzer:
    """Analyzes learner progress and provides insights."""
    
    MASTERY_THRESHOLD = 0.85
    IMPROVEMENT_THRESHOLD = 0.10  # 10% improvement
    
    def __init__(self):
        """Initialize the progress analyzer."""
        pass
    
    def analyze_progress(
        self,
        current_profile: LearnerProfile,
        previous_profile: LearnerProfile = None,
        total_available_resources: int = 1  # For context
    ) -> ProgressMetrics:
        """
        Analyze learner progress.
        
        Args:
            current_profile: Current learner profile
            previous_profile: Previous profile state (for comparison)
            total_available_resources: Total resources available (for context)
            
        Returns:
            ProgressMetrics with analysis
        """
        
        # Calculate completion rate
        completion_rate = (
            len(current_profile.completed_resources) / total_available_resources
            if total_available_resources > 0
            else 0.0
        )
        
        # Calculate skill improvement
        skill_improvement = self._calculate_skill_improvement(
            current_profile,
            previous_profile
        )
        
        # Calculate learning velocity
        learning_velocity = self._calculate_learning_velocity(
            current_profile,
            previous_profile
        )
        
        # Calculate mastery percentage
        mastery_percentage = self._calculate_mastery_percentage(
            current_profile
        )
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement_score(
            current_profile,
            previous_profile
        )
        
        return ProgressMetrics(
            completion_rate=completion_rate,
            skill_improvement=skill_improvement,
            learning_velocity=learning_velocity,
            mastery_percentage=mastery_percentage,
            engagement_score=engagement_score
        )
    
    def _calculate_skill_improvement(
        self,
        current: LearnerProfile,
        previous: LearnerProfile = None
    ) -> float:
        """
        Calculate average skill improvement.
        
        Returns 0.0 if no previous profile.
        """
        
        if not previous or not current.skill_proficiency:
            return 0.0
        
        improvements = []
        
        for skill, current_prof in current.skill_proficiency.items():
            previous_prof = previous.skill_proficiency.get(skill, 0.0)
            improvement = current_prof - previous_prof
            improvements.append(improvement)
        
        if not improvements:
            return 0.0
        
        return sum(improvements) / len(improvements)
    
    def _calculate_learning_velocity(
        self,
        current: LearnerProfile,
        previous: LearnerProfile = None
    ) -> float:
        """
        Calculate learning velocity (progress speed).
        
        Based on: resource completion rate + skill improvement.
        Range: 0.0-1.0
        """
        
        if not previous:
            return 0.5  # Neutral if no comparison
        
        # New resources completed
        new_resources = len(set(current.completed_resources) - 
                          set(previous.completed_resources))
        
        # New skills added
        new_skills = len(set(current.current_skills) - 
                        set(previous.current_skills))
        
        # Skill improvements
        improvements = self._calculate_skill_improvement(current, previous)
        
        # Combine metrics
        velocity = (new_resources * 0.3 + 
                   new_skills * 0.3 + 
                   improvements * 100 * 0.4)
        
        return min(1.0, velocity)
    
    def _calculate_mastery_percentage(
        self,
        profile: LearnerProfile
    ) -> float:
        """
        Calculate percentage of skills at mastery level.
        
        Mastery = proficiency >= MASTERY_THRESHOLD (0.85)
        """
        
        if not profile.skill_proficiency:
            return 0.0
        
        mastered = sum(
            1 for prof in profile.skill_proficiency.values()
            if prof >= self.MASTERY_THRESHOLD
        )
        
        return mastered / len(profile.skill_proficiency)
    
    def _calculate_engagement_score(
        self,
        current: LearnerProfile,
        previous: LearnerProfile = None
    ) -> float:
        """
        Calculate engagement score based on activity.
        
        Factors:
        - Feedback provided
        - Resources completed recently
        - Assessment participation
        """
        
        score = 0.0
        
        # Feedback engagement
        if current.feedback:
            score += 0.3 * min(1.0, len(current.feedback) / 5)
        
        # Resource completion
        if current.completed_resources:
            score += 0.3 * min(1.0, len(current.completed_resources) / 5)
        
        # Assessment participation
        if current.assessment_results:
            score += 0.2 * min(1.0, len(current.assessment_results) / 5)
        
        # Continuous engagement (if previous profile exists)
        if previous and len(current.completed_resources) > len(previous.completed_resources):
            score += 0.2
        
        return min(1.0, score)
    
    def identify_strengths(self, profile: LearnerProfile) -> List[str]:
        """
        Identify learner's strongest skills.
        
        Args:
            profile: Learner profile
            
        Returns:
            List of skills with high proficiency
        """
        
        return [
            skill for skill, prof in profile.skill_proficiency.items()
            if prof >= self.MASTERY_THRESHOLD
        ]
    
    def identify_struggles(self, profile: LearnerProfile) -> List[str]:
        """
        Identify skills where learner is struggling.
        
        Args:
            profile: Learner profile
            
        Returns:
            List of skills with low proficiency
        """
        
        return [
            skill for skill, prof in profile.skill_proficiency.items()
            if prof < 0.4
        ]
    
    def generate_progress_report(
        self,
        current_profile: LearnerProfile,
        previous_profile: LearnerProfile = None
    ) -> Dict:
        """
        Generate a comprehensive progress report.
        
        Args:
            current_profile: Current learner profile
            previous_profile: Previous profile for comparison
            
        Returns:
            Dict with progress report
        """
        
        metrics = self.analyze_progress(
            current_profile,
            previous_profile
        )
        
        return {
            "user_id": current_profile.user_id,
            "career_goal": current_profile.career_goal,
            "metrics": metrics.to_dict(),
            "strengths": self.identify_strengths(current_profile),
            "struggles": self.identify_struggles(current_profile),
            "resources_completed": len(current_profile.completed_resources),
            "skills_acquired": len(current_profile.current_skills),
            "mastered_skills": [
                s for s, p in current_profile.skill_proficiency.items()
                if p >= self.MASTERY_THRESHOLD
            ],
            "next_priorities": self._identify_next_priorities(current_profile),
        }
    
    def _identify_next_priorities(
        self,
        profile: LearnerProfile
    ) -> List[str]:
        """
        Suggest next priorities based on progress.
        
        Prioritizes:
        1. Weak skills in progress
        2. New skills in career path
        3. Skills with highest impact
        """
        
        struggles = self.identify_struggles(profile)
        
        if struggles:
            return struggles[:3]
        
        return []
