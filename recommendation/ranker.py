"""Resource ranking and scoring."""

from typing import Dict, List, Tuple
from dataclasses import dataclass

from models import (
    LearnerProfile,
    LearningResource,
    SkillGapResult,
    PrerequisiteStatus,
)

from skill_gap.career_mapping import CareerSkillMapper


@dataclass
class ScoringWeights:
    """Configurable weights for recommendation scoring."""

    skill_gap_weight: float = 0.30
    career_relevance_weight: float = 0.25
    difficulty_match_weight: float = 0.15
    prerequisite_match_weight: float = 0.10
    interest_match_weight: float = 0.10
    time_fit_weight: float = 0.10

    def validate(self) -> None:
        """Validate that weights sum to 1.0."""

        total = sum([
            self.skill_gap_weight,
            self.career_relevance_weight,
            self.difficulty_match_weight,
            self.prerequisite_match_weight,
            self.interest_match_weight,
            self.time_fit_weight,
        ])

        # Allow small floating point variations
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0, got {total}"
            )


class ResourceRanker:
    """
    Ranks learning resources based on learner profile and skill gaps.
    """

    def __init__(self, weights: ScoringWeights = None):
        """
        Initialize ranker with optional custom weights.

        Args:
            weights: ScoringWeights configuration.
                     Uses defaults if None.
        """

        self.weights = weights or ScoringWeights()
        self.weights.validate()
        self.mapper = CareerSkillMapper()

    def score_skill_gap_match(
        self,
        resource: LearningResource,
        skill_gap: SkillGapResult,
        profile: LearnerProfile,
    ) -> float:
        """
        Score how well resource addresses skill gaps.

        Higher score if resource teaches high-priority missing skills.

        Args:
            resource: Learning resource
            skill_gap: Skill gap analysis result
            profile: Learner profile

        Returns:
            Score 0.0-1.0
        """

        score = 0.0

        # Check if resource teaches a priority skill
        if resource.primary_skill in skill_gap.priority_skills:
            # Find priority ranking
            priority_index = skill_gap.priority_skills.index(
                resource.primary_skill
            )

            # Top priority skills score higher
            score += 0.6 * (
                1.0 -
                (priority_index / len(skill_gap.priority_skills))
            )

        # Secondary skills also count
        for secondary_skill in resource.secondary_skills:
            if secondary_skill in skill_gap.priority_skills:
                score += 0.15

        # Prefer resources for skills in missing/weak list
        if resource.primary_skill in (
            skill_gap.missing_skills +
            skill_gap.weak_skills
        ):
            score += 0.25

        return min(1.0, score)

    def score_career_relevance(
        self,
        resource: LearningResource,
        career: str,
    ) -> float:
        """
        Score how relevant resource is to the career goal.

        Args:
            resource: Learning resource
            career: Career goal

        Returns:
            Score 0.0-1.0
        """

        # Direct career match
        if resource.is_relevant_to_career(career):
            return 1.0

        # Check if resource teaches career-relevant skills
        score = 0.0

        # Primary skill relevance
        tier = self.mapper.get_skill_tier(
            career,
            resource.primary_skill,
        )

        tier_scores = {
            "required": 0.9,
            "core": 0.7,
            "optional": 0.4,
            "not_relevant": 0.1,
        }

        score += tier_scores.get(tier, 0.1)

        # Secondary skills also matter
        for skill in resource.secondary_skills:
            tier = self.mapper.get_skill_tier(
                career,
                skill,
            )
            score += tier_scores.get(tier, 0.1) * 0.3

        return min(1.0, score)

    def score_difficulty_match(
        self,
        resource: LearningResource,
        profile: LearnerProfile,
    ) -> float:
        """
        Score how well difficulty matches learner level.

        Beginner → prefer beginner resources
        Intermediate → prefer intermediate resources
        Advanced → can handle advanced resources

        Args:
            resource: Learning resource
            profile: Learner profile

        Returns:
            Score 0.0-1.0
        """

        difficulty_map = {
            "beginner": 0,
            "intermediate": 1,
            "advanced": 2,
            "expert": 3,
        }

        experience_map = {
            "beginner": 0,
            "intermediate": 1,
            "advanced": 2,
        }

        resource_diff = difficulty_map.get(
            resource.difficulty.value,
            1,
        )

        learner_exp = experience_map.get(
            profile.experience_level,
            1,
        )

        # Perfect match scores highest
        diff = abs(resource_diff - learner_exp)

        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.7
        else:
            return 0.4

    def score_prerequisite_match(
        self,
        resource: LearningResource,
        profile: LearnerProfile,
    ) -> Tuple[float, PrerequisiteStatus, List[str]]:
        """
        Score and validate prerequisites.

        Args:
            resource: Learning resource
            profile: Learner profile

        Returns:
            Tuple of (score, status, missing_prerequisites)
        """

        if not resource.has_prerequisites():
            return 1.0, PrerequisiteStatus.MET, []

        # Check which prerequisites are met
        met = 0
        missing = []

        for prereq in resource.prerequisites:
            if profile.get_skill_proficiency(prereq) >= 0.6:
                met += 1
            else:
                missing.append(prereq)

        # Determine status
        if not missing:
            status = PrerequisiteStatus.MET
            score = 1.0

        elif met > 0:
            status = PrerequisiteStatus.PARTIALLY_MET
            score = 0.5 * (
                met / len(resource.prerequisites)
            )

        else:
            status = PrerequisiteStatus.NOT_MET
            score = 0.0

        return score, status, missing

    def score_interest_match(
        self,
        resource: LearningResource,
        profile: LearnerProfile,
    ) -> float:
        """
        Score how well resource matches learner interests.

        Args:
            resource: Learning resource
            profile: Learner profile

        Returns:
            Score 0.0-1.0
        """

        if not profile.interests:
            return 0.5

        score = 0.0
        matched_interests = 0

        for interest in profile.interests:
            interest_lower = interest.lower()

            # Check resource tags
            if any(
                interest_lower in tag.lower()
                for tag in resource.tags
            ):
                matched_interests += 1
                score += 0.5

            # Check resource primary skill
            if interest_lower in resource.primary_skill.lower():
                matched_interests += 1
                score += 0.7

            # Check secondary skills
            for skill in resource.secondary_skills:
                if interest_lower in skill.lower():
                    matched_interests += 1
                    score += 0.3

        return min(1.0, score)

    def score_time_fit(
        self,
        resource: LearningResource,
        profile: LearnerProfile,
    ) -> Tuple[float, bool, float]:
        """
        Score whether resource fits available time.

        Args:
            resource: Learning resource
            profile: Learner profile

        Returns:
            Tuple of:
            - score: 0.0-1.0
            - fits_schedule: whether resource fits schedule
            - weeks_needed: estimated completion time
        """

        if profile.learning_hours_per_week <= 0:
            return 0.5, False, float("inf")

        # Estimate weeks needed
        weeks_needed = (
            resource.estimated_hours /
            profile.learning_hours_per_week
        )

        if weeks_needed <= 4:
            return 1.0, True, weeks_needed

        elif weeks_needed <= 8:
            return 0.85, True, weeks_needed

        elif weeks_needed <= 16:
            return 0.65, True, weeks_needed

        else:
            return 0.4, False, weeks_needed

    def rank_resources(
        self,
        resources: List[LearningResource],
        profile: LearnerProfile,
        skill_gap: SkillGapResult,
    ) -> List[Tuple[LearningResource, Dict[str, float], float]]:
        """
        Rank resources by overall recommendation score.

        Args:
            resources: List of resources from RAG system
            profile: Learner profile
            skill_gap: Skill gap analysis

        Returns:
            List of tuples:
            (resource, score_breakdown, final_score)

            Sorted by final_score descending.
        """

        ranked = []

        for resource in resources:

            # Skip completed resources
            if profile.has_completed_resource(
                resource.resource_id
            ):
                continue

            # Calculate component scores
            skill_gap_score = self.score_skill_gap_match(
                resource,
                skill_gap,
                profile,
            )

            career_score = self.score_career_relevance(
                resource,
                profile.career_goal,
            )

            difficulty_score = self.score_difficulty_match(
                resource,
                profile,
            )

            prereq_score, _, _ = self.score_prerequisite_match(
                resource,
                profile,
            )

            interest_score = self.score_interest_match(
                resource,
                profile,
            )

            time_score, fits_schedule, _ = self.score_time_fit(
                resource,
                profile,
            )

            # Calculate final weighted score
            final_score = (
                self.weights.skill_gap_weight *
                skill_gap_score

                + self.weights.career_relevance_weight *
                career_score

                + self.weights.difficulty_match_weight *
                difficulty_score

                + self.weights.prerequisite_match_weight *
                prereq_score

                + self.weights.interest_match_weight *
                interest_score

                + self.weights.time_fit_weight *
                time_score
            )

            breakdown = {
                "skill_gap": skill_gap_score,
                "career_relevance": career_score,
                "difficulty_match": difficulty_score,
                "prerequisite_match": prereq_score,
                "interest_match": interest_score,
                "time_fit": time_score,
            }

            ranked.append(
                (
                    resource,
                    breakdown,
                    final_score,
                )
            )

        # Sort by final score descending
        ranked.sort(
            key=lambda x: x[2],
            reverse=True,
        )

        return ranked