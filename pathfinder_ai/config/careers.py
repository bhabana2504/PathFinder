"""
Career-to-skill mapping configuration.

Defines required, core, and optional skills for each career path with importance weights.
This is the knowledge base that drives skill gap analysis.
"""

from typing import Dict, List, Optional


# Skill definitions with importance and prerequisites
SKILL_DEFINITIONS: Dict[str, Dict] = {
    # Programming
    "Python": {
        "category": "programming",
        "importance": 1.0,
        "prerequisites": [],
        "description": "Python programming language"
    },
    "JavaScript": {
        "category": "programming",
        "importance": 0.95,
        "prerequisites": [],
        "description": "JavaScript/TypeScript programming"
    },
    "C++": {
        "category": "programming",
        "importance": 0.85,
        "prerequisites": [],
        "description": "C++ programming language"
    },
    "Java": {
        "category": "programming",
        "importance": 0.85,
        "prerequisites": [],
        "description": "Java programming language"
    },
    "SQL": {
        "category": "programming",
        "importance": 0.9,
        "prerequisites": [],
        "description": "SQL and database querying"
    },
    "Go": {
        "category": "programming",
        "importance": 0.7,
        "prerequisites": [],
        "description": "Go programming language"
    },
    "Rust": {
        "category": "programming",
        "importance": 0.7,
        "prerequisites": [],
        "description": "Rust programming language"
    },
    
    # Mathematics & Statistics
    "Statistics": {
        "category": "mathematics",
        "importance": 1.0,
        "prerequisites": [],
        "description": "Statistical methods and probability"
    },
    "Linear Algebra": {
        "category": "mathematics",
        "importance": 1.0,
        "prerequisites": [],
        "description": "Linear algebra and matrices"
    },
    "Calculus": {
        "category": "mathematics",
        "importance": 0.8,
        "prerequisites": [],
        "description": "Calculus fundamentals"
    },
    "Probability": {
        "category": "mathematics",
        "importance": 0.9,
        "prerequisites": [],
        "description": "Probability theory"
    },
    
    # Machine Learning & AI
    "Machine Learning": {
        "category": "machine_learning",
        "importance": 1.0,
        "prerequisites": ["Python", "Statistics", "Linear Algebra"],
        "description": "ML algorithms and techniques"
    },
    "Deep Learning": {
        "category": "machine_learning",
        "importance": 0.95,
        "prerequisites": ["Machine Learning", "Linear Algebra"],
        "description": "Neural networks and deep learning"
    },
    "NLP": {
        "category": "machine_learning",
        "importance": 0.85,
        "prerequisites": ["Machine Learning", "Python"],
        "description": "Natural Language Processing"
    },
    "Computer Vision": {
        "category": "machine_learning",
        "importance": 0.85,
        "prerequisites": ["Deep Learning", "Python"],
        "description": "Computer Vision and image processing"
    },
    "Generative AI": {
        "category": "machine_learning",
        "importance": 0.9,
        "prerequisites": ["Deep Learning", "NLP"],
        "description": "Generative models and LLMs"
    },
    "Reinforcement Learning": {
        "category": "machine_learning",
        "importance": 0.75,
        "prerequisites": ["Machine Learning", "Probability"],
        "description": "Reinforcement learning fundamentals"
    },
    "MLOps": {
        "category": "machine_learning",
        "importance": 0.8,
        "prerequisites": ["Machine Learning", "Python"],
        "description": "ML operations and deployment"
    },
    
    # Data Science
    "Data Analysis": {
        "category": "data_science",
        "importance": 0.95,
        "prerequisites": ["Python", "Statistics"],
        "description": "Data analysis and visualization"
    },
    "Data Engineering": {
        "category": "data_science",
        "importance": 0.85,
        "prerequisites": ["SQL", "Python"],
        "description": "Data pipelines and ETL"
    },
    "Database Design": {
        "category": "data_science",
        "importance": 0.8,
        "prerequisites": ["SQL"],
        "description": "Database design and optimization"
    },
    
    # Web Development
    "React": {
        "category": "frontend",
        "importance": 0.95,
        "prerequisites": ["JavaScript"],
        "description": "React.js frontend framework"
    },
    "Vue.js": {
        "category": "frontend",
        "importance": 0.85,
        "prerequisites": ["JavaScript"],
        "description": "Vue.js frontend framework"
    },
    "CSS": {
        "category": "frontend",
        "importance": 0.9,
        "prerequisites": [],
        "description": "CSS and styling"
    },
    "HTML": {
        "category": "frontend",
        "importance": 0.9,
        "prerequisites": [],
        "description": "HTML markup"
    },
    "Node.js": {
        "category": "backend",
        "importance": 0.9,
        "prerequisites": ["JavaScript"],
        "description": "Node.js backend runtime"
    },
    "Express.js": {
        "category": "backend",
        "importance": 0.85,
        "prerequisites": ["Node.js"],
        "description": "Express.js web framework"
    },
    "FastAPI": {
        "category": "backend",
        "importance": 0.9,
        "prerequisites": ["Python"],
        "description": "FastAPI Python web framework"
    },
    "Django": {
        "category": "backend",
        "importance": 0.85,
        "prerequisites": ["Python"],
        "description": "Django web framework"
    },
    
    # Cloud & DevOps
    "AWS": {
        "category": "cloud",
        "importance": 0.9,
        "prerequisites": [],
        "description": "Amazon Web Services"
    },
    "GCP": {
        "category": "cloud",
        "importance": 0.85,
        "prerequisites": [],
        "description": "Google Cloud Platform"
    },
    "Azure": {
        "category": "cloud",
        "importance": 0.85,
        "prerequisites": [],
        "description": "Microsoft Azure"
    },
    "Docker": {
        "category": "devops",
        "importance": 0.9,
        "prerequisites": [],
        "description": "Docker containerization"
    },
    "Kubernetes": {
        "category": "devops",
        "importance": 0.85,
        "prerequisites": ["Docker"],
        "description": "Kubernetes orchestration"
    },
    "CI/CD": {
        "category": "devops",
        "importance": 0.8,
        "prerequisites": [],
        "description": "Continuous Integration/Deployment"
    },
    
    # Security
    "Cybersecurity": {
        "category": "security",
        "importance": 0.85,
        "prerequisites": [],
        "description": "Cybersecurity fundamentals"
    },
    "Network Security": {
        "category": "security",
        "importance": 0.8,
        "prerequisites": [],
        "description": "Network security principles"
    },
    "Cryptography": {
        "category": "security",
        "importance": 0.75,
        "prerequisites": [],
        "description": "Cryptography and encryption"
    },
    
    # Soft Skills
    "Communication": {
        "category": "soft_skills",
        "importance": 0.8,
        "prerequisites": [],
        "description": "Technical communication"
    },
    "Problem Solving": {
        "category": "soft_skills",
        "importance": 0.85,
        "prerequisites": [],
        "description": "Problem solving and critical thinking"
    },
    "Leadership": {
        "category": "soft_skills",
        "importance": 0.75,
        "prerequisites": [],
        "description": "Team leadership and management"
    },
}


# Career paths with required, core, and optional skills
CAREER_SKILLS: Dict[str, Dict[str, List[str]]] = {
    "AI Engineer": {
        "required": [
            "Python",
            "Statistics",
            "Linear Algebra",
            "Machine Learning",
            "Deep Learning",
        ],
        "core": [
            "NLP",
            "Generative AI",
            "MLOps",
            "Data Analysis",
            "Problem Solving",
        ],
        "optional": [
            "Computer Vision",
            "Reinforcement Learning",
            "AWS",
            "FastAPI",
        ],
    },
    "Machine Learning Engineer": {
        "required": [
            "Python",
            "Statistics",
            "Linear Algebra",
            "Machine Learning",
        ],
        "core": [
            "Deep Learning",
            "MLOps",
            "Data Engineering",
            "Problem Solving",
            "FastAPI",
        ],
        "optional": [
            "Computer Vision",
            "NLP",
            "AWS",
            "Docker",
        ],
    },
    "Data Scientist": {
        "required": [
            "Python",
            "SQL",
            "Statistics",
            "Data Analysis",
        ],
        "core": [
            "Linear Algebra",
            "Machine Learning",
            "Data Engineering",
            "Problem Solving",
        ],
        "optional": [
            "Deep Learning",
            "Probability",
            "Communication",
        ],
    },
    "Full Stack Developer": {
        "required": [
            "Python",
            "JavaScript",
            "HTML",
            "CSS",
            "SQL",
        ],
        "core": [
            "React",
            "Node.js",
            "FastAPI",
            "Database Design",
            "Problem Solving",
        ],
        "optional": [
            "TypeScript",
            "Docker",
            "AWS",
            "Communication",
        ],
    },
    "Frontend Developer": {
        "required": [
            "JavaScript",
            "HTML",
            "CSS",
            "React",
        ],
        "core": [
            "Problem Solving",
            "Communication",
            "Vue.js",
            "TypeScript",
        ],
        "optional": [
            "Animation",
            "Accessibility",
            "Performance Optimization",
        ],
    },
    "Backend Developer": {
        "required": [
            "Python",
            "SQL",
            "FastAPI",
        ],
        "core": [
            "Database Design",
            "Data Engineering",
            "Problem Solving",
            "Node.js",
        ],
        "optional": [
            "AWS",
            "Docker",
            "Kubernetes",
            "Caching",
        ],
    },
    "Cloud Engineer": {
        "required": [
            "AWS",
            "Python",
        ],
        "core": [
            "Docker",
            "Kubernetes",
            "CI/CD",
            "GCP",
            "Problem Solving",
        ],
        "optional": [
            "Terraform",
            "Azure",
            "Networking",
        ],
    },
    "DevOps Engineer": {
        "required": [
            "Docker",
            "CI/CD",
            "Python",
        ],
        "core": [
            "Kubernetes",
            "AWS",
            "Linux",
            "Problem Solving",
        ],
        "optional": [
            "Terraform",
            "Monitoring",
            "GCP",
        ],
    },
    "Cybersecurity Engineer": {
        "required": [
            "Cybersecurity",
            "Network Security",
        ],
        "core": [
            "Linux",
            "Python",
            "Cryptography",
            "Problem Solving",
        ],
        "optional": [
            "Penetration Testing",
            "Cloud Security",
        ],
    },
}


def get_career_skills(career: str) -> Optional[Dict[str, List[str]]]:
    """
    Get skill requirements for a career.
    
    Args:
        career: Career name
        
    Returns:
        Dict with 'required', 'core', and 'optional' skill lists, or None if not found
    """
    return CAREER_SKILLS.get(career)


def get_all_career_skills(career: str) -> List[str]:
    """
    Get all skills (required + core + optional) for a career.
    
    Args:
        career: Career name
        
    Returns:
        Flattened list of all skills for the career
    """
    skills_dict = get_career_skills(career)
    if not skills_dict:
        return []
    
    all_skills = []
    all_skills.extend(skills_dict.get("required", []))
    all_skills.extend(skills_dict.get("core", []))
    all_skills.extend(skills_dict.get("optional", []))
    
    return list(dict.fromkeys(all_skills))  # Remove duplicates while preserving order


def get_skill_info(skill: str) -> Optional[Dict]:
    """
    Get information about a skill.
    
    Args:
        skill: Skill name
        
    Returns:
        Skill definition dict or None if not found
    """
    return SKILL_DEFINITIONS.get(skill)


def get_skill_importance(skill: str) -> float:
    """
    Get importance weight for a skill.
    
    Args:
        skill: Skill name
        
    Returns:
        Importance score (0.0 to 1.0), defaults to 0.5 if not found
    """
    skill_info = get_skill_info(skill)
    return skill_info.get("importance", 0.5) if skill_info else 0.5


def get_skill_prerequisites(skill: str) -> List[str]:
    """
    Get prerequisites for a skill.
    
    Args:
        skill: Skill name
        
    Returns:
        List of prerequisite skill names
    """
    skill_info = get_skill_info(skill)
    return skill_info.get("prerequisites", []) if skill_info else []


def is_valid_career(career: str) -> bool:
    """Check if career exists in the knowledge base."""
    return career in CAREER_SKILLS


def get_all_careers() -> List[str]:
    """Get all supported careers."""
    return list(CAREER_SKILLS.keys())
