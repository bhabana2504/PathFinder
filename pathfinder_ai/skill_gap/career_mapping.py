"""Career-to-skill mapping logic."""

from typing import List, Dict, Set
from pathfinder_ai.config import get_career_skills, get_skill_prerequisites, SKILL_DEFINITIONS


class CareerSkillMapper:
    """Maps careers to required skills and validates career requirements."""
    
    def __init__(self):
        """Initialize the career mapper."""
        self.skill_defs = SKILL_DEFINITIONS
    
    def get_required_skills(self, career: str) -> List[str]:
        """
        Get required (non-optional) skills for a career.
        
        Args:
            career: Career name
            
        Returns:
            List of required skill names
            
        Raises:
            ValueError: If career is not found
        """
        skills = get_career_skills(career)
        if not skills:
            raise ValueError(f"Unknown career: {career}")
        
        return skills.get("required", []) + skills.get("core", [])
    
    def get_all_skills_for_career(self, career: str) -> List[str]:
        """
        Get all skills (required + optional) for a career.
        
        Args:
            career: Career name
            
        Returns:
            List of all skill names
            
        Raises:
            ValueError: If career is not found
        """
        skills = get_career_skills(career)
        if not skills:
            raise ValueError(f"Unknown career: {career}")
        
        all_skills = []
        all_skills.extend(skills.get("required", []))
        all_skills.extend(skills.get("core", []))
        all_skills.extend(skills.get("optional", []))
        
        return list(dict.fromkeys(all_skills))  # Remove duplicates
    
    def get_skill_tier(self, career: str, skill: str) -> str:
        """
        Get the tier of a skill for a career (required, core, or optional).
        
        Args:
            career: Career name
            skill: Skill name
            
        Returns:
            Tier: 'required', 'core', 'optional', or 'not_relevant'
        """
        skills = get_career_skills(career)
        if not skills:
            return "not_relevant"
        
        if skill in skills.get("required", []):
            return "required"
        elif skill in skills.get("core", []):
            return "core"
        elif skill in skills.get("optional", []):
            return "optional"
        else:
            return "not_relevant"
    
    def get_skill_importance_for_career(self, career: str, skill: str) -> float:
        """
        Get importance score for a skill in the context of a career.
        
        Combines base skill importance with career-specific weighting.
        
        Args:
            career: Career name
            skill: Skill name
            
        Returns:
            Importance score (0.0 to 1.0)
        """
        tier = self.get_skill_tier(career, skill)
        
        # Base importance from skill definition
        base_importance = 0.5
        if skill in self.skill_defs:
            base_importance = self.skill_defs[skill].get("importance", 0.5)
        
        # Adjust based on tier
        if tier == "required":
            return base_importance * 1.0  # Full importance
        elif tier == "core":
            return base_importance * 0.85  # Slightly reduced
        elif tier == "optional":
            return base_importance * 0.65  # Further reduced
        else:
            return base_importance * 0.4  # Not relevant
    
    def get_skill_prerequisites_full(self, skill: str) -> Set[str]:
        """
        Get all prerequisites for a skill (recursively).
        
        Args:
            skill: Skill name
            
        Returns:
            Set of all prerequisite skills
        """
        direct_prereqs = get_skill_prerequisites(skill)
        all_prereqs = set(direct_prereqs)
        
        # Recursively get prerequisites of prerequisites
        for prereq in direct_prereqs:
            all_prereqs.update(self.get_skill_prerequisites_full(prereq))
        
        return all_prereqs
    
    def validate_skill_order(
        self,
        skills: List[str]
    ) -> Dict[str, List[str]]:
        """
        Validate that skills are in a valid order respecting prerequisites.
        
        Args:
            skills: List of skills in proposed order
            
        Returns:
            Dict with 'valid' bool and 'violations' list
        """
        violations = []
        seen_skills = set()
        
        for i, skill in enumerate(skills):
            prereqs = get_skill_prerequisites(skill)
            missing_prereqs = [p for p in prereqs if p not in seen_skills]
            
            if missing_prereqs:
                violations.append({
                    "skill": skill,
                    "position": i,
                    "missing_prerequisites": missing_prereqs
                })
            
            seen_skills.add(skill)
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
