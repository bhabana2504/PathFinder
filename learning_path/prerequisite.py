"""Prerequisite validation and ordering engine."""

from typing import Dict, List, Set, Tuple
from collections import defaultdict, deque
from pathfinder_ai.models import LearningResource
from pathfinder_ai.config import get_skill_prerequisites


class PrerequisiteEngine:
    """
    Validates and orders resources based on prerequisites.
    
    Uses topological sort to ensure prerequisites are always
    presented before dependent resources.
    """
    
    def __init__(self):
        """Initialize the prerequisite engine."""
        pass
    
    def build_resource_graph(
        self,
        resources: List[LearningResource]
    ) -> Dict[str, List[str]]:
        """
        Build a dependency graph of resources.
        
        Args:
            resources: List of learning resources
            
        Returns:
            Dict mapping resource_id → list of resource_ids that depend on it
        """
        graph = defaultdict(list)
        resource_skills = {}
        
        # Map resources to the skills they teach
        for resource in resources:
            resource_skills[resource.resource_id] = resource.primary_skill
        
        # Build dependency edges
        for resource in resources:
            for prereq_skill in resource.prerequisites:
                # Find which resources teach this prerequisite skill
                for other_resource in resources:
                    if other_resource.primary_skill == prereq_skill:
                        graph[other_resource.resource_id].append(
                            resource.resource_id
                        )
        
        return dict(graph)
    
    def topological_sort(
        self,
        resources: List[LearningResource],
        learner_current_skills: Set[str]
    ) -> Tuple[List[LearningResource], List[str]]:
        """
        Order resources using topological sort, respecting prerequisites.
        
        Args:
            resources: List of learning resources
            learner_current_skills: Set of skills already mastered
            
        Returns:
            Tuple of (ordered_resources, warnings)
        """
        # Build graph
        graph = self.build_resource_graph(resources)
        
        # Calculate in-degree for each resource
        in_degree = defaultdict(int)
        resource_map = {r.resource_id: r for r in resources}
        
        for resource_id in resource_map:
            # Count how many prerequisites are NOT met
            resource = resource_map[resource_id]
            unmet_prereqs = sum(
                1 for prereq in resource.prerequisites
                if prereq not in learner_current_skills
            )
            in_degree[resource_id] = unmet_prereqs
        
        # Topological sort using Kahn's algorithm
        queue = deque([
            rid for rid in resource_map
            if in_degree[rid] == 0
        ])
        
        sorted_ids = []
        warnings = []
        
        while queue:
            resource_id = queue.popleft()
            sorted_ids.append(resource_id)
            
            # Process dependents
            for dependent_id in graph.get(resource_id, []):
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    queue.append(dependent_id)
        
        # Check for cycles or unmet prerequisites
        if len(sorted_ids) < len(resources):
            missing = set(resource_map.keys()) - set(sorted_ids)
            for resource_id in missing:
                resource = resource_map[resource_id]
                missing_prereqs = [
                    p for p in resource.prerequisites
                    if p not in learner_current_skills
                ]
                warnings.append(
                    f"Resource '{resource.title}' has unmet prerequisites: "
                    f"{', '.join(missing_prereqs)}"
                )
                # Still include it but mark the warning
                sorted_ids.append(resource_id)
        
        # Convert back to resources maintaining order
        ordered = [resource_map[rid] for rid in sorted_ids if rid in resource_map]
        
        return ordered, warnings
    
    def validate_prerequisites(
        self,
        resource: LearningResource,
        learner_current_skills: Set[str]
    ) -> Tuple[bool, List[str]]:
        """
        Check if all prerequisites are met for a resource.
        
        Args:
            resource: Learning resource to validate
            learner_current_skills: Set of current skills
            
        Returns:
            Tuple of (is_valid, missing_prerequisites)
        """
        missing = [
            prereq for prereq in resource.prerequisites
            if prereq not in learner_current_skills
        ]
        
        return len(missing) == 0, missing
    
    def find_prerequisite_path(
        self,
        target_skill: str,
        resources: List[LearningResource],
        learner_current_skills: Set[str]
    ) -> List[LearningResource]:
        """
        Find the shortest path of resources to learn a target skill,
        including all necessary prerequisites.
        
        Args:
            target_skill: The skill to learn
            resources: Available learning resources
            learner_current_skills: Current skills
            
        Returns:
            List of resources in order to reach target skill
        """
        # Build skill → resources mapping
        skill_to_resources = defaultdict(list)
        for resource in resources:
            skill_to_resources[resource.primary_skill].append(resource)
        
        # BFS to find prerequisites
        needed_skills = deque([target_skill])
        all_needed = set()
        path_order = []
        
        while needed_skills:
            skill = needed_skills.popleft()
            
            if skill in all_needed or skill in learner_current_skills:
                continue
            
            all_needed.add(skill)
            
            # Find resource for this skill
            if skill in skill_to_resources:
                resource = skill_to_resources[skill][0]  # Pick first
                path_order.append(resource)
                
                # Add prerequisites
                for prereq in resource.prerequisites:
                    if prereq not in all_needed and prereq not in learner_current_skills:
                        needed_skills.append(prereq)
        
        # Topologically sort the path
        path_resources = list({r.resource_id: r for r in path_order}.values())
        ordered, _ = self.topological_sort(path_resources, learner_current_skills)
        
        return ordered
