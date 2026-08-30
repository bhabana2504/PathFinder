"""
Sample data for development and testing.

This module provides realistic sample learner profiles, skills, and resources.
"""

from models import (
    LearnerProfile,
    LearningResource,
    ResourceType,
    DifficultyLevel,
)


# Sample Learner Profiles
SAMPLE_LEARNER_BEGINNER = LearnerProfile(
    user_id="learner_001",
    career_goal="AI Engineer",
    experience_level="beginner",
    current_skills=["Python"],
    skill_proficiency={
        "Python": 0.7,
    },
    interests=["Machine Learning", "AI", "Deep Learning"],
    learning_hours_per_week=10.0,
    completed_resources=[],
    assessment_results={},
    feedback=[]
)

SAMPLE_LEARNER_INTERMEDIATE = LearnerProfile(
    user_id="learner_002",
    career_goal="Machine Learning Engineer",
    experience_level="intermediate",
    current_skills=["Python", "Statistics", "Data Analysis"],
    skill_proficiency={
        "Python": 0.85,
        "Statistics": 0.7,
        "Data Analysis": 0.75,
        "SQL": 0.6,
    },
    interests=["Machine Learning", "Data Science", "Deep Learning"],
    learning_hours_per_week=15.0,
    completed_resources=["python_advanced_101", "stats_intro_202"],
    assessment_results={
        "Python": 0.82,
        "Statistics": 0.68,
    },
    feedback=["Great course on Python fundamentals"]
)

SAMPLE_LEARNER_ADVANCED = LearnerProfile(
    user_id="learner_003",
    career_goal="Full Stack Developer",
    experience_level="advanced",
    current_skills=["JavaScript", "Python", "React", "Node.js", "SQL"],
    skill_proficiency={
        "JavaScript": 0.9,
        "Python": 0.85,
        "React": 0.88,
        "Node.js": 0.82,
        "SQL": 0.8,
        "CSS": 0.85,
        "HTML": 0.9,
    },
    interests=["Cloud", "DevOps", "Performance Optimization"],
    learning_hours_per_week=8.0,
    completed_resources=["js_fundamentals_101", "react_advanced_202"],
    assessment_results={},
    feedback=[]
)


# Sample Learning Resources
SAMPLE_RESOURCES = [
    # Python Resources
    LearningResource(
        resource_id="python_basics_101",
        title="Python Fundamentals for Beginners",
        description="Learn Python basics including variables, functions, and data structures",
        resource_type=ResourceType.COURSE,
        primary_skill="Python",
        secondary_skills=[],
        difficulty=DifficultyLevel.BEGINNER,
        prerequisites=[],
        estimated_hours=20.0,
        url="https://example.com/courses/python-basics",
        target_careers=["AI Engineer", "Data Scientist", "Backend Developer"],
        tags=["python", "programming", "basics"],
        ratings=4.5,
        completion_rate=0.85,
    ),
    
    LearningResource(
        resource_id="python_advanced_101",
        title="Advanced Python: Object-Oriented Programming",
        description="Master OOP, decorators, and advanced Python patterns",
        resource_type=ResourceType.COURSE,
        primary_skill="Python",
        secondary_skills=["Problem Solving"],
        difficulty=DifficultyLevel.ADVANCED,
        prerequisites=["Python"],
        estimated_hours=30.0,
        url="https://example.com/courses/python-oop",
        target_careers=["AI Engineer", "Backend Developer", "Full Stack Developer"],
        tags=["python", "oop", "advanced"],
        ratings=4.7,
        completion_rate=0.75,
    ),
    
    # Statistics & Math Resources
    LearningResource(
        resource_id="stats_intro_202",
        title="Statistics Fundamentals",
        description="Learn probability, distributions, and statistical testing",
        resource_type=ResourceType.COURSE,
        primary_skill="Statistics",
        secondary_skills=["Probability"],
        difficulty=DifficultyLevel.BEGINNER,
        prerequisites=[],
        estimated_hours=25.0,
        url="https://example.com/courses/stats-101",
        target_careers=["Data Scientist", "AI Engineer", "ML Engineer"],
        tags=["statistics", "probability", "data-science"],
        ratings=4.3,
        completion_rate=0.70,
    ),
    
    LearningResource(
        resource_id="linear_algebra_303",
        title="Linear Algebra for Machine Learning",
        description="Matrices, eigenvectors, and linear transformations for ML",
        resource_type=ResourceType.COURSE,
        primary_skill="Linear Algebra",
        secondary_skills=["Mathematics"],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=["Statistics"],
        estimated_hours=35.0,
        url="https://example.com/courses/linear-algebra",
        target_careers=["AI Engineer", "ML Engineer", "Data Scientist"],
        tags=["linear-algebra", "mathematics", "ml"],
        ratings=4.6,
        completion_rate=0.65,
    ),
    
    # Machine Learning Resources
    LearningResource(
        resource_id="ml_fundamentals_404",
        title="Machine Learning Fundamentals",
        description="Supervised and unsupervised learning algorithms",
        resource_type=ResourceType.COURSE,
        primary_skill="Machine Learning",
        secondary_skills=["Python", "Statistics"],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=["Python", "Statistics"],
        estimated_hours=40.0,
        url="https://example.com/courses/ml-fundamentals",
        target_careers=["ML Engineer", "AI Engineer", "Data Scientist"],
        tags=["machine-learning", "supervised", "unsupervised"],
        ratings=4.8,
        completion_rate=0.78,
    ),
    
    LearningResource(
        resource_id="deep_learning_505",
        title="Deep Learning and Neural Networks",
        description="Neural network architectures, training, and optimization",
        resource_type=ResourceType.COURSE,
        primary_skill="Deep Learning",
        secondary_skills=["Python", "Linear Algebra"],
        difficulty=DifficultyLevel.ADVANCED,
        prerequisites=["Machine Learning", "Linear Algebra"],
        estimated_hours=50.0,
        url="https://example.com/courses/deep-learning",
        target_careers=["AI Engineer", "ML Engineer"],
        tags=["deep-learning", "neural-networks"],
        ratings=4.7,
        completion_rate=0.72,
    ),
    
    # NLP Resources
    LearningResource(
        resource_id="nlp_fundamentals_606",
        title="Natural Language Processing Basics",
        description="Tokenization, embeddings, and text processing",
        resource_type=ResourceType.COURSE,
        primary_skill="NLP",
        secondary_skills=["Python", "Machine Learning"],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=["Machine Learning", "Python"],
        estimated_hours=30.0,
        url="https://example.com/courses/nlp-basics",
        target_careers=["AI Engineer", "ML Engineer"],
        tags=["nlp", "text-processing"],
        ratings=4.4,
        completion_rate=0.68,
    ),
    
    # Frontend Resources
    LearningResource(
        resource_id="javascript_basics_707",
        title="JavaScript Fundamentals",
        description="Variables, functions, DOM manipulation, async programming",
        resource_type=ResourceType.COURSE,
        primary_skill="JavaScript",
        secondary_skills=["HTML", "CSS"],
        difficulty=DifficultyLevel.BEGINNER,
        prerequisites=[],
        estimated_hours=25.0,
        url="https://example.com/courses/js-basics",
        target_careers=["Frontend Developer", "Full Stack Developer"],
        tags=["javascript", "web", "frontend"],
        ratings=4.6,
        completion_rate=0.82,
    ),
    
    LearningResource(
        resource_id="react_fundamentals_808",
        title="React.js Essentials",
        description="Components, hooks, state management, and modern React patterns",
        resource_type=ResourceType.COURSE,
        primary_skill="React",
        secondary_skills=["JavaScript"],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=["JavaScript"],
        estimated_hours=35.0,
        url="https://example.com/courses/react",
        target_careers=["Frontend Developer", "Full Stack Developer"],
        tags=["react", "javascript", "frontend"],
        ratings=4.7,
        completion_rate=0.80,
    ),
    
    # Backend Resources
    LearningResource(
        resource_id="node_fundamentals_909",
        title="Node.js Backend Development",
        description="Server setup, routing, middleware, and database integration",
        resource_type=ResourceType.COURSE,
        primary_skill="Node.js",
        secondary_skills=["JavaScript", "SQL"],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=["JavaScript"],
        estimated_hours=30.0,
        url="https://example.com/courses/nodejs",
        target_careers=["Backend Developer", "Full Stack Developer"],
        tags=["nodejs", "backend", "javascript"],
        ratings=4.5,
        completion_rate=0.75,
    ),
    
    LearningResource(
        resource_id="fastapi_fundamentals_1010",
        title="FastAPI: Modern Python Web Framework",
        description="Building fast APIs with FastAPI, validation, and async support",
        resource_type=ResourceType.COURSE,
        primary_skill="FastAPI",
        secondary_skills=["Python", "SQL"],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=["Python"],
        estimated_hours=28.0,
        url="https://example.com/courses/fastapi",
        target_careers=["Backend Developer", "ML Engineer", "Full Stack Developer"],
        tags=["fastapi", "python", "backend"],
        ratings=4.8,
        completion_rate=0.79,
    ),
    
    # Cloud & DevOps
    LearningResource(
        resource_id="docker_basics_1111",
        title="Docker Containerization Essentials",
        description="Containers, images, Docker Compose, and best practices",
        resource_type=ResourceType.COURSE,
        primary_skill="Docker",
        secondary_skills=[],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=[],
        estimated_hours=20.0,
        url="https://example.com/courses/docker",
        target_careers=["DevOps Engineer", "Backend Developer", "Cloud Engineer"],
        tags=["docker", "containers", "devops"],
        ratings=4.6,
        completion_rate=0.81,
    ),
    
    LearningResource(
        resource_id="aws_fundamentals_1212",
        title="AWS Cloud Fundamentals",
        description="EC2, S3, Lambda, RDS, and core AWS services",
        resource_type=ResourceType.COURSE,
        primary_skill="AWS",
        secondary_skills=["Cloud"],
        difficulty=DifficultyLevel.INTERMEDIATE,
        prerequisites=[],
        estimated_hours=40.0,
        url="https://example.com/courses/aws",
        target_careers=["Cloud Engineer", "DevOps Engineer", "Backend Developer"],
        tags=["aws", "cloud", "infrastructure"],
        ratings=4.7,
        completion_rate=0.72,
    ),
    
    # Data Science
    LearningResource(
        resource_id="data_analysis_1313",
        title="Data Analysis with Pandas and Matplotlib",
        description="Data manipulation, exploration, and visualization",
        resource_type=ResourceType.COURSE,
        primary_skill="Data Analysis",
        secondary_skills=["Python"],
        difficulty=DifficultyLevel.BEGINNER,
        prerequisites=["Python"],
        estimated_hours=22.0,
        url="https://example.com/courses/data-analysis",
        target_careers=["Data Scientist", "AI Engineer"],
        tags=["data-analysis", "pandas", "visualization"],
        ratings=4.5,
        completion_rate=0.77,
    ),
    
    # Projects
    LearningResource(
        resource_id="ml_project_1414",
        title="Machine Learning Capstone Project",
        description="Build an end-to-end ML project from data to deployment",
        resource_type=ResourceType.PROJECT,
        primary_skill="Machine Learning",
        secondary_skills=["Python", "Data Analysis", "MLOps"],
        difficulty=DifficultyLevel.ADVANCED,
        prerequisites=["Machine Learning", "Data Analysis"],
        estimated_hours=60.0,
        url="https://example.com/projects/ml-capstone",
        target_careers=["ML Engineer", "AI Engineer"],
        tags=["project", "capstone", "applied"],
        ratings=4.6,
        completion_rate=0.45,
    ),
    
    LearningResource(
        resource_id="web_app_project_1515",
        title="Full Stack Web Application Project",
        description="Build a complete web application from frontend to backend",
        resource_type=ResourceType.PROJECT,
        primary_skill="Full Stack Development",
        secondary_skills=["React", "Node.js", "SQL"],
        difficulty=DifficultyLevel.ADVANCED,
        prerequisites=["React", "Node.js"],
        estimated_hours=50.0,
        url="https://example.com/projects/fullstack",
        target_careers=["Full Stack Developer"],
        tags=["project", "fullstack", "applied"],
        ratings=4.5,
        completion_rate=0.50,
    ),
]


def get_sample_learner(level: str = "beginner") -> LearnerProfile:
    """
    Get a sample learner profile.
    
    Args:
        level: 'beginner', 'intermediate', or 'advanced'
        
    Returns:
        Sample LearnerProfile
    """
    if level == "intermediate":
        return SAMPLE_LEARNER_INTERMEDIATE
    elif level == "advanced":
        return SAMPLE_LEARNER_ADVANCED
    else:
        return SAMPLE_LEARNER_BEGINNER


def get_sample_resources(limit: int = None) -> list:
    """
    Get sample learning resources.
    
    Args:
        limit: Maximum number of resources to return
        
    Returns:
        List of LearningResource objects
    """
    resources = SAMPLE_RESOURCES
    if limit:
        return resources[:limit]
    return resources


def get_sample_resources_for_skill(skill: str) -> list:
    """
    Get sample resources for a specific skill.
    
    Args:
        skill: Skill name
        
    Returns:
        List of relevant LearningResource objects
    """
    return [r for r in SAMPLE_RESOURCES if r.primary_skill == skill]
