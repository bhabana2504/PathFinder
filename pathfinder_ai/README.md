# PathFinder AI/ML Module

A production-quality AI/ML module for **personalized learning path recommendation** in the PathFinder platform.

## Purpose

The PathFinder AI/ML module analyzes learner profiles, identifies skill gaps, ranks learning resources, and generates adaptive learning paths that respect prerequisites and difficulty progression.

**Key Responsibility**: Transform learner data into intelligent recommendations without duplicating RAG functionality.

## Architecture

```
ai/
├── config/              # Career-to-skill knowledge base
├── models/              # Pydantic data models
├── skill_gap/           # Skill gap analysis
├── recommendation/      # Resource ranking & explanations
├── learning_path/       # Path generation & prerequisites
├── adaptive_learning/   # Profile updates & progress tracking
├── evaluation/          # Metrics and evaluation
├── services/            # AI service abstraction (for LLM integration)
├── tests/               # Comprehensive unit tests
└── sample_data.py       # Realistic sample data
```

## Installation

### Requirements
- Python 3.11+
- Pydantic 2.0+

### Setup

```bash
# Clone the repository
git clone <pathfinder-repo>
cd pathfinder_ai

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
python -m pytest tests/ -v
```

## Quick Start

### 1. Create a Learner Profile

```python
from pathfinder_ai import LearnerProfile

profile = LearnerProfile(
    user_id="learner_123",
    career_goal="AI Engineer",
    experience_level="beginner",
    current_skills=["Python", "SQL"],
    skill_proficiency={
        "Python": 0.85,
        "SQL": 0.70
    },
    interests=["Machine Learning", "NLP"],
    learning_hours_per_week=10.0
)
```

### 2. Analyze Skill Gaps

```python
from pathfinder_ai import analyze_skill_gap

gap = analyze_skill_gap(profile)

print(f"Missing skills: {gap.missing_skills}")
print(f"Priority skills: {gap.priority_skills}")
print(f"Skill scores: {gap.skill_scores}")
```

### 3. Get Recommendations from RAG

The RAG system (Harsh's module) provides relevant learning resources:

```python
# This comes from Harsh's RAG system
retrieved_resources = rag_system.retrieve(
    query=gap.priority_skills,
    limit=50
)
```

### 4. Rank Resources

```python
from pathfinder_ai import recommend_resources

recommendations = recommend_resources(
    profile=profile,
    skill_gap=gap,
    resources=retrieved_resources,  # From RAG system
    top_n=10
)

for rec in recommendations.recommendations[:3]:
    print(f"\n{rec.title}")
    print(f"Score: {rec.score:.2f}")
    print(f"Reason: {rec.reason}")
```

### 5. Generate Learning Path

```python
from pathfinder_ai import generate_learning_path

learning_path = generate_learning_path(
    profile=profile,
    skill_gap=gap,
    recommendations=recommendations.recommendations
)

for node in learning_path.nodes:
    print(f"{node.position+1}. {node.recommendation.title}")
    print(f"   Status: {node.status}")
    print(f"   Skill: {node.recommendation.primary_skill}")
```

## Core Components

### 1. Skill Gap Analysis

**File**: `skill_gap/analyzer.py`

Identifies missing and weak skills relative to career goals.

```python
from pathfinder_ai.skill_gap import analyze_skill_gap

gap = analyze_skill_gap(profile)

# Returns SkillGapResult with:
# - required_skills: All skills for the career
# - missing_skills: Skills at proficiency < 0.1
# - weak_skills: Skills at 0.1-0.6 proficiency
# - mastered_skills: Skills at proficiency >= 0.85
# - priority_skills: Skills ranked by priority
```

**Algorithm**:
1. Load career requirements from knowledge base
2. Compare against current skills
3. Calculate priority scores:
   ```
   priority = career_importance × skill_gap × prerequisite_factor × learning_relevance
   ```
4. Rank skills by priority

### 2. Recommendation Engine

**File**: `recommendation/recommender.py`

Ranks learning resources based on learner profile and skill gaps.

```python
from pathfinder_ai.recommendation import recommend_resources

recommendations = recommend_resources(
    profile,
    gap,
    resources,  # From RAG system
    top_n=10,
    weights=None  # Optional custom weights
)
```

**Scoring Factors** (configurable weights):
- **Skill Gap** (30%): Addresses priority skills
- **Career Relevance** (25%): Importance for career goal
- **Difficulty Match** (15%): Appropriate difficulty level
- **Prerequisites** (10%): Prerequisites met
- **Interests** (10%): Matches learner interests
- **Time Fit** (10%): Fits available learning hours

**Explanation Generation**:
Each recommendation includes a human-readable explanation:
```
"This resource is recommended because Machine Learning is your highest 
priority skill for your AI Engineer goal, your current proficiency is low 
(10%), and you have already completed the required Python prerequisite."
```

### 3. Learning Path Generation

**File**: `learning_path/generator.py`

Creates an ordered learning sequence respecting prerequisites.

```python
from pathfinder_ai.learning_path import generate_learning_path

path = generate_learning_path(profile, gap, recommendations)

# Path nodes have statuses:
# - locked: Prerequisites not met
# - available: Ready to start
# - in_progress: Currently working on
# - completed: Finished
```

**Ordering Algorithm**:
1. Build prerequisite graph
2. Topological sort to respect dependencies
3. Assign status based on prerequisites and completion
4. Return ordered path

### 4. Adaptive Learning

**File**: `adaptive_learning/updater.py`

Updates learner profile based on completion and assessments.

```python
from pathfinder_ai.adaptive_learning import (
    update_learner_profile,
    update_skill_from_assessment
)

# Update from assessment
profile = update_skill_from_assessment(
    profile,
    skill="Python",
    assessment_score=0.92,
    weight=0.6  # 60% weight for new assessment
)

# Mark resource as completed
from pathfinder_ai.adaptive_learning import mark_resource_completed
profile = mark_resource_completed(profile, "course_123", rating=4.5)
```

**Features**:
- Weighted average skill updates: `new = current × (1-weight) + assessment × weight`
- Track completed resources
- Record assessment results
- Maintain skill proficiency history

### 5. Progress Analysis

**File**: `adaptive_learning/progress_analyzer.py`

Analyzes learner progress and generates insights.

```python
from pathfinder_ai.adaptive_learning import ProgressAnalyzer

analyzer = ProgressAnalyzer()
metrics = analyzer.analyze_progress(profile)

# Returns metrics for:
# - completion_rate: % of resources completed
# - skill_improvement: Average improvement across skills
# - learning_velocity: Speed of progress
# - mastery_percentage: % of skills mastered
# - engagement_score: Activity-based engagement

# Generate comprehensive report
report = analyzer.generate_progress_report(profile)
```

## Career Knowledge Base

**File**: `config/careers.py`

Defines career paths with required, core, and optional skills.

### Supported Careers

- AI Engineer
- Machine Learning Engineer
- Data Scientist
- Full Stack Developer
- Frontend Developer
- Backend Developer
- Cloud Engineer
- DevOps Engineer
- Cybersecurity Engineer

### Adding New Careers

```python
# In config/careers.py

CAREER_SKILLS["Data Engineer"] = {
    "required": [
        "Python",
        "SQL",
        "Data Engineering",
    ],
    "core": [
        "Apache Spark",
        "Data Pipeline",
        "Problem Solving",
    ],
    "optional": [
        "AWS",
        "Kubernetes",
    ],
}
```

## Data Models

### LearnerProfile

```python
LearnerProfile(
    user_id: str                              # Unique identifier
    career_goal: str                          # Target career
    experience_level: str                     # beginner/intermediate/advanced
    current_skills: List[str]                 # Skills learner has
    skill_proficiency: Dict[str, float]       # Skill → 0.0-1.0 score
    interests: List[str]                      # Learning interests
    learning_hours_per_week: float            # Available time
    completed_resources: List[str]            # Resource IDs completed
    assessment_results: Dict[str, float]      # Skill → assessment score
    feedback: List[str]                       # User feedback
)
```

### LearningResource

```python
LearningResource(
    resource_id: str                          # From RAG system
    title: str                                # Resource title
    description: str                          # Full description
    resource_type: ResourceType               # course/tutorial/project/etc
    primary_skill: str                        # Main skill taught
    secondary_skills: List[str]               # Other skills covered
    difficulty: DifficultyLevel               # beginner/intermediate/advanced/expert
    prerequisites: List[str]                  # Required skills
    estimated_hours: float                    # Time to complete
    url: str                                  # Resource URL
    target_careers: List[str]                 # Relevant careers
    tags: List[str]                           # Search tags
    ratings: float                            # 0.0-5.0 user rating
    completion_rate: float                    # Estimated % completion
)
```

### Recommendation

```python
Recommendation(
    resource_id: str                          # Resource ID
    title: str                                # Resource title
    score: float                              # 0.0-1.0 recommendation score
    reason: str                               # Explanation
    primary_skill: str                        # Main skill
    secondary_skills: List[str]               # Other skills
    difficulty: str                           # Difficulty level
    priority: str                             # critical/high/medium/low
    prerequisite_status: PrerequisiteStatus   # met/partially_met/not_met
    missing_prerequisites: List[str]          # Any missing prerequisites
    estimated_hours: float                    # Time estimate
    fits_schedule: bool                       # Fits available time?
    career_relevance: float                   # 0.0-1.0 relevance
    interest_match: float                     # 0.0-1.0 interest match
    score_breakdown: Dict[str, float]         # Component scores
)
```

## RAG Integration

The AI/ML module integrates with Harsh's RAG system through clean interfaces:

### Input from RAG
```python
# Harsh's RAG system provides:
retrieved_resources: List[LearningResource] = rag_system.retrieve(
    query=skill_gap.priority_skills,
    limit=50
)
```

### Output to FastAPI Backend
```python
# The AI/ML module outputs rankings:
recommendations_result = recommend_resources(
    profile, gap, retrieved_resources
)

# FastAPI endpoint wraps this:
@app.post("/recommendations")
def get_recommendations(profile: LearnerProfile):
    gap = analyze_skill_gap(profile)
    resources = rag_system.retrieve(gap.priority_skills)
    return recommend_resources(profile, gap, resources)
```

## Testing

Run comprehensive unit tests:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_skill_gap.py -v

# Run with coverage
python -m pytest tests/ --cov=pathfinder_ai

# Run individual test
python -m pytest tests/test_skill_gap.py::test_skill_gap_analysis_basic -v
```

### Test Coverage

- **Skill Gap Analysis**: 9 tests
  - Basic analysis, missing skills, mastered skills
  - Priority ordering, scorer, career mapping
  - Invalid careers, empty profiles, all mastered

- **Recommendations**: 11 tests
  - Basic generation, scoring, ranking
  - Prerequisites, completed resources
  - Custom weights, explanation generation

- **Adaptive Learning**: 12 tests
  - Assessment updates, new skills
  - Resource completion, profile updates
  - Progress analysis, mastery tracking

- **Learning Paths**: 9 tests
  - Prerequisite validation, topological sort
  - Path generation, status assignment
  - Completion handling, prerequisite ordering

## Sample Data

For development and testing:

```python
from pathfinder_ai.sample_data import (
    SAMPLE_LEARNER_BEGINNER,
    SAMPLE_LEARNER_INTERMEDIATE,
    SAMPLE_LEARNER_ADVANCED,
    SAMPLE_RESOURCES,
    get_sample_learner,
    get_sample_resources,
)

# Use sample learners
profile = get_sample_learner("beginner")

# Use sample resources
resources = get_sample_resources(limit=20)

# Get resources for specific skill
python_resources = get_sample_resources_for_skill("Python")
```

## API Integration Example

### FastAPI Backend Integration

```python
from fastapi import FastAPI
from pathfinder_ai import (
    LearnerProfile,
    analyze_skill_gap,
    recommend_resources,
    generate_learning_path,
    update_learner_profile,
)

app = FastAPI()

@app.post("/analyze-gaps")
def analyze_gaps(profile: LearnerProfile):
    """Analyze skill gaps for a learner."""
    gap = analyze_skill_gap(profile)
    return {
        "user_id": gap.user_id,
        "missing_skills": gap.missing_skills,
        "priority_skills": gap.priority_skills,
        "skill_scores": gap.skill_scores,
    }

@app.post("/get-recommendations")
def get_recommendations(profile: LearnerProfile):
    """Get ranked resource recommendations."""
    gap = analyze_skill_gap(profile)
    
    # Get resources from RAG system
    resources = rag_system.retrieve(gap.priority_skills, limit=50)
    
    # Rank resources
    result = recommend_resources(profile, gap, resources, top_n=10)
    
    return {
        "recommendations": [
            {
                "resource_id": r.resource_id,
                "title": r.title,
                "score": r.score,
                "reason": r.reason,
                "priority": r.priority,
            }
            for r in result.recommendations
        ],
        "total": result.total_recommendations,
        "average_score": result.average_score,
    }

@app.post("/generate-path")
def generate_path(profile: LearnerProfile):
    """Generate a personalized learning path."""
    gap = analyze_skill_gap(profile)
    resources = rag_system.retrieve(gap.priority_skills, limit=50)
    recommendations = recommend_resources(profile, gap, resources).recommendations
    
    path = generate_learning_path(profile, gap, recommendations)
    
    return {
        "user_id": path.user_id,
        "career_goal": path.career_goal,
        "nodes": [
            {
                "position": n.position,
                "title": n.recommendation.title,
                "skill": n.recommendation.primary_skill,
                "status": n.status,
            }
            for n in path.nodes
        ],
    }

@app.post("/update-profile")
def update_profile(profile: LearnerProfile, updates: dict):
    """Update learner profile with completion data."""
    updated = update_learner_profile(profile, **updates)
    return {"user_id": updated.user_id, "updated": True}
```

## Configuration & Customization

### Custom Recommendation Weights

```python
from pathfinder_ai.recommendation.ranker import ScoringWeights

custom_weights = ScoringWeights(
    skill_gap_weight=0.40,
    career_relevance_weight=0.20,
    difficulty_match_weight=0.15,
    prerequisite_match_weight=0.10,
    interest_match_weight=0.10,
    time_fit_weight=0.05,
)

result = recommend_resources(
    profile, gap, resources, weights=custom_weights
)
```

### Custom LLM Service

```python
from pathfinder_ai.services import AIService

class OpenAIService(AIService):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def generate_explanation(self, context: dict) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": f"Explain: {context}"}
            ]
        )
        return response.choices[0].message.content
```

## Performance Considerations

- **Skill Gap Analysis**: O(n × m) where n = required skills, m = current skills
- **Recommendation Ranking**: O(r × s) where r = resources, s = scoring factors
- **Topological Sort**: O(n + e) where n = resources, e = prerequisites
- **Caching**: Consider caching career definitions and career-to-skill mappings

## Future Improvements

1. **LLM Integration**: Connect OpenAI/Gemini for dynamic explanation generation
2. **Caching**: Redis cache for frequently accessed career data
3. **A/B Testing**: Framework for testing different recommendation algorithms
4. **Collaborative Filtering**: Recommend paths based on similar learners
5. **Skill Decay**: Account for skill forgetting over time
6. **Dynamic Weights**: ML model to learn optimal recommendation weights
7. **Prerequisite Learning**: Discover prerequisites from completion patterns
8. **Career Progression**: Track skills needed for career advancement

## Team Integration

### Bhabana's Role: AI/ML Developer
- Maintain and improve skill gap analysis
- Optimize recommendation algorithm
- Add new careers and skills
- Monitor recommendation quality

### Harsh's Role: RAG & Backend
- Implement document retrieval
- Manage embeddings and vector DB
- Handle FastAPI endpoints
- Provide retrieved resources to AI module

### Shivansh's Role: Cloud & Database
- Set up PostgreSQL for persistence
- Configure cloud infrastructure
- Manage data backup and replication

### Aditya's Role: Frontend
- Build UI for recommendations
- Visualize learning paths
- Display progress tracking

## Version History

**v0.1.0** (Current)
- Initial implementation
- All core features complete
- Comprehensive testing
- Documentation complete

## License

MIT License - See LICENSE file

## Contact

**Bhabana Kalita** - Team Lead, AI/ML Developer
- GitHub: @bhabana2504
- Galgotias University
