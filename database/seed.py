from sqlalchemy.orm import Session
from database import models
from database.connection import SessionLocal, engine
from config.careers import CAREER_SKILLS, SKILL_DEFINITIONS
from sample_data import SAMPLE_RESOURCES
from database import crud
from models.resources import LearningResource

def seed_database():
    # Make sure tables exist
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Seeding database...")

        # 1. Seed Skills
        print("Seeding skills and prerequisites...")
        for skill_name, defs in SKILL_DEFINITIONS.items():
            db_skill = db.query(models.Skill).filter(models.Skill.name == skill_name).first()
            if not db_skill:
                db_skill = models.Skill(
                    name=skill_name,
                    category=defs["category"],
                    description=defs.get("description", ""),
                    importance=defs.get("importance", 0.5)
                )
                db.add(db_skill)
            else:
                db_skill.category = defs["category"]
                db_skill.description = defs.get("description", "")
                db_skill.importance = defs.get("importance", 0.5)

            # Prereqs
            db.query(models.SkillPrerequisite).filter(models.SkillPrerequisite.skill_name == skill_name).delete()
            for prereq in defs.get("prerequisites", []):
                db.add(models.SkillPrerequisite(skill_name=skill_name, prerequisite_name=prereq))
        
        db.commit()

        # 2. Seed Careers
        print("Seeding careers and skill mappings...")
        for career_name, skill_tiers in CAREER_SKILLS.items():
            db_career = db.query(models.Career).filter(models.Career.name == career_name).first()
            if not db_career:
                db_career = models.Career(name=career_name, description=f"{career_name} career path")
                db.add(db_career)

            db.query(models.CareerSkill).filter(models.CareerSkill.career_name == career_name).delete()
            for tier, skills in skill_tiers.items():
                for skill_name in skills:
                    db.add(models.CareerSkill(career_name=career_name, skill_name=skill_name, tier=tier))
        
        db.commit()

        # 3. Seed Learning Resources
        print("Seeding learning resources...")
        for resource in SAMPLE_RESOURCES:
            crud.save_resource(db, resource)

        print("Successfully seeded database!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
