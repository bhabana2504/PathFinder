import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import models
from models import LearnerProfile, LearningResource, Recommendation, SkillGapResult, PrerequisiteStatus

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, email: str, hashed_pw: str, name: str, user_id: str) -> models.User:
    db_user = models.User(id=user_id, email=email, hashed_password=hashed_pw, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_learner_profile(db: Session, user_id: str) -> Optional[LearnerProfile]:
    db_profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.id == user_id).first()
    if not db_profile:
        return None

    # Load skills
    current_skills = []
    skill_proficiency = {}
    for s in db_profile.skills:
        current_skills.append(s.skill_name)
        skill_proficiency[s.skill_name] = s.proficiency

    # Load interests
    interests = [i.interest for i in db_profile.interests]

    # Load completed resources
    completed_resources = [r.resource_id for r in db_profile.completed_resources]

    # Load assessments
    assessments_dict = {}
    # Fetch all assessments ordered by taken_at to get the latest score
    assessments = db.query(models.Assessment).filter(models.Assessment.learner_id == user_id).order_by(models.Assessment.taken_at.asc()).all()
    for a in assessments:
        assessments_dict[a.skill_name] = a.score

    # Feedback
    try:
        feedback = json.loads(db_profile.feedback_json) if db_profile.feedback_json else []
    except Exception:
        feedback = []

    return LearnerProfile(
        user_id=db_profile.id,
        career_goal=db_profile.career_goal,
        experience_level=db_profile.experience_level,
        current_skills=current_skills,
        skill_proficiency=skill_proficiency,
        interests=interests,
        learning_hours_per_week=db_profile.learning_hours_per_week,
        completed_resources=completed_resources,
        assessment_results=assessments_dict,
        feedback=feedback,
        created_at=db_profile.created_at.replace(tzinfo=timezone.utc),
        updated_at=db_profile.updated_at.replace(tzinfo=timezone.utc)
    )

def save_learner_profile(db: Session, pydantic_profile: LearnerProfile) -> None:
    # 1. Profile row
    db_profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.id == pydantic_profile.user_id).first()
    if not db_profile:
        db_profile = models.LearnerProfile(id=pydantic_profile.user_id)
        db.add(db_profile)

    db_profile.career_goal = pydantic_profile.career_goal
    db_profile.experience_level = pydantic_profile.experience_level
    db_profile.learning_hours_per_week = pydantic_profile.learning_hours_per_week
    db_profile.feedback_json = json.dumps(pydantic_profile.feedback)
    db_profile.updated_at = datetime.now(timezone.utc)

    # 2. Skills
    db.query(models.LearnerSkill).filter(models.LearnerSkill.learner_id == pydantic_profile.user_id).delete()
    # Add skills from proficiency or current_skills
    all_skills = set(pydantic_profile.current_skills) | set(pydantic_profile.skill_proficiency.keys())
    for s_name in all_skills:
        prof = pydantic_profile.skill_proficiency.get(s_name, 0.0)
        db_skill = models.LearnerSkill(learner_id=pydantic_profile.user_id, skill_name=s_name, proficiency=prof)
        db.add(db_skill)

    # 3. Interests
    db.query(models.LearnerInterest).filter(models.LearnerInterest.learner_id == pydantic_profile.user_id).delete()
    for interest in pydantic_profile.interests:
        db_interest = models.LearnerInterest(learner_id=pydantic_profile.user_id, interest=interest)
        db.add(db_interest)

    # 4. Completed resources
    db.query(models.CompletedResource).filter(models.CompletedResource.learner_id == pydantic_profile.user_id).delete()
    for r_id in pydantic_profile.completed_resources:
        db_comp = models.CompletedResource(learner_id=pydantic_profile.user_id, resource_id=r_id)
        db.add(db_comp)

    # 5. Assessments (Insert only new ones or keep sync)
    # Pydantic profile stores assessment_results dict. Let's make sure we have matching rows in database.
    # Note: assessment_results is a dict of skill -> score.
    # Let's inspect existing assessments. If the latest score for a skill doesn't match the current dict, insert it.
    for s_name, score in pydantic_profile.assessment_results.items():
        latest = db.query(models.Assessment).filter(
            models.Assessment.learner_id == pydantic_profile.user_id,
            models.Assessment.skill_name == s_name
        ).order_by(models.Assessment.taken_at.desc()).first()

        if not latest or latest.score != score:
            db_ass = models.Assessment(learner_id=pydantic_profile.user_id, skill_name=s_name, score=score)
            db.add(db_ass)

    db.commit()

# Careers
def get_careers(db: Session) -> List[models.Career]:
    return db.query(models.Career).all()

def get_career_by_name(db: Session, name: str) -> Optional[models.Career]:
    return db.query(models.Career).filter(models.Career.name == name).first()

# Skills
def get_skills(db: Session) -> List[models.Skill]:
    return db.query(models.Skill).all()

# Resources
def get_resources(db: Session) -> List[models.LearningResource]:
    return db.query(models.LearningResource).all()

def get_resource_by_id(db: Session, resource_id: str) -> Optional[models.LearningResource]:
    return db.query(models.LearningResource).filter(models.LearningResource.resource_id == resource_id).first()

def save_resource(db: Session, r: LearningResource) -> models.LearningResource:
    db_res = db.query(models.LearningResource).filter(models.LearningResource.resource_id == r.resource_id).first()
    if not db_res:
        db_res = models.LearningResource(resource_id=r.resource_id)
        db.add(db_res)

    db_res.title = r.title
    db_res.description = r.description
    db_res.resource_type = r.resource_type.value if hasattr(r.resource_type, 'value') else str(r.resource_type)
    db_res.primary_skill = r.primary_skill
    db_res.difficulty = r.difficulty.value if hasattr(r.difficulty, 'value') else str(r.difficulty)
    db_res.estimated_hours = r.estimated_hours
    db_res.url = r.url
    db_res.ratings = r.ratings
    db_res.completion_rate = r.completion_rate

    # Clear and insert associations
    db.query(models.ResourceSecondarySkill).filter(models.ResourceSecondarySkill.resource_id == r.resource_id).delete()
    for s in r.secondary_skills:
        db.add(models.ResourceSecondarySkill(resource_id=r.resource_id, skill_name=s))

    db.query(models.ResourcePrerequisite).filter(models.ResourcePrerequisite.resource_id == r.resource_id).delete()
    for p in r.prerequisites:
        db.add(models.ResourcePrerequisite(resource_id=r.resource_id, skill_name=p))

    db.query(models.ResourceTargetCareer).filter(models.ResourceTargetCareer.resource_id == r.resource_id).delete()
    for c in r.target_careers:
        db.add(models.ResourceTargetCareer(resource_id=r.resource_id, career_name=c))

    db.query(models.ResourceTag).filter(models.ResourceTag.resource_id == r.resource_id).delete()
    for t in r.tags:
        db.add(models.ResourceTag(resource_id=r.resource_id, tag=t))

    db.commit()
    db.refresh(db_res)
    return db_res

# Recommendations
def get_recommendations(db: Session, learner_id: str) -> List[models.Recommendation]:
    return db.query(models.Recommendation).filter(models.Recommendation.learner_id == learner_id).order_by(models.Recommendation.score.desc()).all()

def save_recommendations(db: Session, learner_id: str, recommendations: List[Recommendation]) -> None:
    db.query(models.Recommendation).filter(models.Recommendation.learner_id == learner_id).delete()
    for r in recommendations:
        db_rec = models.Recommendation(
            learner_id=learner_id,
            resource_id=r.resource_id,
            title=r.title,
            resource_type=r.resource_type,
            score=r.score,
            reason=r.reason,
            primary_skill=r.primary_skill,
            difficulty=r.difficulty,
            priority=r.priority,
            prerequisite_status=r.prerequisite_status.value if hasattr(r.prerequisite_status, 'value') else str(r.prerequisite_status),
            estimated_hours=r.estimated_hours,
            fits_schedule=r.fits_schedule,
            career_relevance=r.career_relevance,
            interest_match=r.interest_match,
            url=r.url
        )
        db.add(db_rec)
    db.commit()

# Learning Path
def get_learning_path(db: Session, learner_id: str) -> Optional[models.LearningPath]:
    return db.query(models.LearningPath).filter(models.LearningPath.learner_id == learner_id).first()

def save_learning_path(db: Session, learner_id: str, career_goal: str, completion_percentage: float, nodes: List[Dict]) -> None:
    db_path = db.query(models.LearningPath).filter(models.LearningPath.learner_id == learner_id).first()
    if not db_path:
        db_path = models.LearningPath(learner_id=learner_id)
        db.add(db_path)

    db_path.career_goal = career_goal
    db_path.completion_percentage = completion_percentage
    db_path.updated_at = datetime.now(timezone.utc)

    # Delete existing nodes
    db.query(models.LearningPathNode).filter(models.LearningPathNode.learner_id == learner_id).delete()
    for node in nodes:
        db_node = models.LearningPathNode(
            learner_id=learner_id,
            resource_id=node["resource_id"],
            position=node["position"],
            status=node["status"],
            percentage_complete=node["percentage_complete"]
        )
        db.add(db_node)
    db.commit()
