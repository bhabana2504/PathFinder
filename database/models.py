from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Table, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("LearnerProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(String, ForeignKey("users.id"), primary_key=True)
    career_goal = Column(String, nullable=False)
    experience_level = Column(String, nullable=False)  # beginner, intermediate, advanced
    learning_hours_per_week = Column(Float, default=10.0)
    feedback_json = Column(String, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")
    skills = relationship("LearnerSkill", back_populates="profile", cascade="all, delete-orphan")
    interests = relationship("LearnerInterest", back_populates="profile", cascade="all, delete-orphan")
    completed_resources = relationship("CompletedResource", back_populates="profile", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="profile", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="profile", cascade="all, delete-orphan")
    learning_path = relationship("LearningPath", uselist=False, back_populates="profile", cascade="all, delete-orphan")

class LearnerSkill(Base):
    __tablename__ = "learner_skills"

    learner_id = Column(String, ForeignKey("learner_profiles.id"), primary_key=True)
    skill_name = Column(String, primary_key=True)
    proficiency = Column(Float, default=0.0)

    profile = relationship("LearnerProfile", back_populates="skills")

class LearnerInterest(Base):
    __tablename__ = "learner_interests"

    learner_id = Column(String, ForeignKey("learner_profiles.id"), primary_key=True)
    interest = Column(String, primary_key=True)

    profile = relationship("LearnerProfile", back_populates="interests")

class Skill(Base):
    __tablename__ = "skills"

    name = Column(String, primary_key=True)
    category = Column(String, nullable=False)
    description = Column(String, default="")
    importance = Column(Float, default=0.5)

class Career(Base):
    __tablename__ = "careers"

    name = Column(String, primary_key=True)
    description = Column(String, default="")

    skills = relationship("CareerSkill", back_populates="career", cascade="all, delete-orphan")

class CareerSkill(Base):
    __tablename__ = "career_skills"

    career_name = Column(String, ForeignKey("careers.name"), primary_key=True)
    skill_name = Column(String, primary_key=True)
    tier = Column(String, nullable=False)  # required, core, optional

    career = relationship("Career", back_populates="skills")

class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisites"

    skill_name = Column(String, primary_key=True)
    prerequisite_name = Column(String, primary_key=True)

class LearningResource(Base):
    __tablename__ = "learning_resources"

    resource_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    resource_type = Column(String, nullable=False)  # course, tutorial, article, video, etc.
    primary_skill = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)  # beginner, intermediate, advanced, expert
    estimated_hours = Column(Float, default=5.0)
    url = Column(String, nullable=True)
    ratings = Column(Float, default=4.0)
    completion_rate = Column(Float, default=0.7)

    secondary_skills = relationship("ResourceSecondarySkill", cascade="all, delete-orphan")
    prerequisites = relationship("ResourcePrerequisite", cascade="all, delete-orphan")
    target_careers = relationship("ResourceTargetCareer", cascade="all, delete-orphan")
    tags = relationship("ResourceTag", cascade="all, delete-orphan")

class ResourceSecondarySkill(Base):
    __tablename__ = "resource_secondary_skills"

    resource_id = Column(String, ForeignKey("learning_resources.resource_id"), primary_key=True)
    skill_name = Column(String, primary_key=True)

class ResourcePrerequisite(Base):
    __tablename__ = "resource_prerequisites"

    resource_id = Column(String, ForeignKey("learning_resources.resource_id"), primary_key=True)
    skill_name = Column(String, primary_key=True)

class ResourceTargetCareer(Base):
    __tablename__ = "resource_target_careers"

    resource_id = Column(String, ForeignKey("learning_resources.resource_id"), primary_key=True)
    career_name = Column(String, primary_key=True)

class ResourceTag(Base):
    __tablename__ = "resource_tags"

    resource_id = Column(String, ForeignKey("learning_resources.resource_id"), primary_key=True)
    tag = Column(String, primary_key=True)

class CompletedResource(Base):
    __tablename__ = "completed_resources"

    learner_id = Column(String, ForeignKey("learner_profiles.id"), primary_key=True)
    resource_id = Column(String, primary_key=True)
    completed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rating = Column(Float, nullable=True)

    profile = relationship("LearnerProfile", back_populates="completed_resources")

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    learner_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    skill_name = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    taken_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("LearnerProfile", back_populates="assessments")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    learner_id = Column(String, ForeignKey("learner_profiles.id"), nullable=False)
    resource_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    primary_skill = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    prerequisite_status = Column(String, nullable=False)
    estimated_hours = Column(Float, nullable=False)
    fits_schedule = Column(Boolean, nullable=False)
    career_relevance = Column(Float, nullable=False)
    interest_match = Column(Float, nullable=False)
    url = Column(String, nullable=True)
    recommended_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("LearnerProfile", back_populates="recommendations")

class LearningPath(Base):
    __tablename__ = "learning_paths"

    learner_id = Column(String, ForeignKey("learner_profiles.id"), primary_key=True)
    career_goal = Column(String, nullable=False)
    completion_percentage = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    profile = relationship("LearnerProfile", back_populates="learning_path")
    nodes = relationship("LearningPathNode", back_populates="learning_path", cascade="all, delete-orphan")

class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    learner_id = Column(String, ForeignKey("learning_paths.learner_id"), nullable=False)
    resource_id = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    status = Column(String, nullable=False)  # locked, available, in_progress, completed
    percentage_complete = Column(Float, default=0.0)

    learning_path = relationship("LearningPath", back_populates="nodes")
