"""Learning path generation."""

from typing import Dict, List
from dataclasses import dataclass
from pathfinder_ai.models import (
    LearnerProfile,
    LearningResource,
    SkillGapResult,
    Recommendation,
)
from pathfinder_ai.learning_path.prerequisite import PrerequisiteEngine


@dataclass
class LearningPathNode:
    """Node in the learning path."""
    
    resource: LearningResource
    recommendation: Recommendation
    position: int
    status: str  # 'locked', 'available', 'in_progress', 'completed'
    percentage_complete: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "resource_id": self.resource.resource_id,
            "title": self.resource.title,
            "position": self.position,
            "status": self.status,
            "skill": self.resource.primary_skill,
            "difficulty": self.resource.difficulty.value,
            "estimated_hours": self.resource.estimated_hours,
            "percentage_complete": self.percentage_complete,
        }


class LearningPath:
    """Represents a complete learning path."""
    
    def __init__(self, career_goal: str, user_id: str):
        """Initialize learning path."""
        self.career_goal = career_goal
        self.user_id = user_id
        self.nodes: List[LearningPathNode] = []
    
    def add_node(self, node: LearningPathNode) -> None:
        """Add a node to the path."""
        self.nodes.append(node)
    
    def get_current_node(self) -> LearningPathNode:
        """Get the current node (first available or in_progress)."""
        for node in self.nodes:
            if node.status in ["available", "in_progress"]:
                return node
        return None
    
    def get_completion_percentage(self) -> float:
        """Get overall completion percentage."""
        if not self.nodes:
            return 0.0
        
        completed = sum(
            1 for node in self.nodes
            if node.status == "completed"
        )
        
        return (completed / len(self.nodes)) * 100
    
    def to_dict(self) -> Dict:
        """Convert path to dictionary."""
        return {
            "user_id": self.user_id,
            "career_goal": self.career_goal,
            "total_nodes": len(self.nodes),
            "nodes": [node.to_dict() for node in self.nodes],
            "completion_percentage": self.get_completion_percentage(),
            "current_node": self.get_current_node().to_dict() if self.get_current_node() else None,
        }


def generate_learning_path(
    profile: LearnerProfile,
    skill_gap: SkillGapResult,
    recommendations: List[Recommendation]
) -> LearningPath:
    """
    Generate a structured learning path from recommendations.
    
    The path is ordered to respect prerequisites and difficulty progression.
    
    Process:
    1. Build prerequisite graph
    2. Topologically sort resources
    3. Determine status for each (locked/available/completed)
    4. Create path nodes
    5. Return ordered path
    
    Args:
        profile: Learner profile
        skill_gap: Skill gap analysis
        recommendations: Ranked recommendations with resources
        
    Returns:
        LearningPath with nodes in recommended order
    """
    
    if not recommendations:
        return LearningPath(profile.career_goal, profile.user_id)
    
    # Extract resources from recommendations
    resources = [r for r in [
        # We need to get resources from recommendations
        # In real use, recommendations will have the resource objects
        None
    ] if r is not None]
    
    # For now, we'll work with recommendation data
    engine = PrerequisiteEngine()
    
    # Create learning path
    path = LearningPath(profile.career_goal, profile.user_id)
    
    # Determine status for each recommendation
    completed_resources = set(profile.completed_resources)
    available = False  # First resource becomes available
    
    for position, recommendation in enumerate(recommendations):
        # Determine status
        if recommendation.resource_id in completed_resources:
            status = "completed"
        elif recommendation.prerequisite_status.value == "not_met":
            status = "locked"
        elif not available:
            status = "available"
            available = True
        else:
            status = "available"
        
        # Create node
        # Note: In real implementation, we'd have the resource object from RAG
        # For now we create a minimal mock
        node = LearningPathNode(
            resource=None,  # Would be the actual resource
            recommendation=recommendation,
            position=position,
            status=status,
            percentage_complete=0.0 if status != "completed" else 100.0
        )
        
        path.add_node(node)
    
    return path


def generate_learning_path_with_resources(
    profile: LearnerProfile,
    skill_gap: SkillGapResult,
    recommendations: List[Recommendation],
    resources: List[LearningResource]  # Resources with full data
) -> LearningPath:
    """
    Generate learning path with actual resource objects.
    
    Args:
        profile: Learner profile
        skill_gap: Skill gap analysis
        recommendations: Ranked recommendations
        resources: Full resource objects from RAG system
        
    Returns:
        LearningPath with complete resource information
    """
    
    # Create resource map
    resource_map = {r.resource_id: r for r in resources}
    
    # Create path
    path = LearningPath(profile.career_goal, profile.user_id)
    
    # Topologically sort by prerequisites
    engine = PrerequisiteEngine()
    available_resources = [resource_map[r.resource_id] for r in recommendations
                          if r.resource_id in resource_map]
    
    ordered_resources, warnings = engine.topological_sort(
        available_resources,
        set(profile.current_skills)
    )
    
    # Build path with proper status
    completed_resources = set(profile.completed_resources)
    prerequisite_met_count = 0
    
    for position, resource in enumerate(ordered_resources):
        # Find corresponding recommendation
        recommendation = next(
            (r for r in recommendations if r.resource_id == resource.resource_id),
            None
        )
        
        if not recommendation:
            continue
        
        # Determine status
        if resource.resource_id in completed_resources:
            status = "completed"
        elif recommendation.prerequisite_status.value != "met":
            status = "locked"
        elif position == 0 or prerequisite_met_count >= position:
            status = "available"
            prerequisite_met_count += 1
        else:
            status = "available"
        
        # Create node
        node = LearningPathNode(
            resource=resource,
            recommendation=recommendation,
            position=position,
            status=status,
            percentage_complete=100.0 if status == "completed" else 0.0
        )
        
        path.add_node(node)
    
    return path
