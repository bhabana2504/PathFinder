from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database import crud
from api.dependencies import get_db

router = APIRouter(prefix="/api/careers", tags=["careers"])

class CareerResponse(BaseModel):
    name: str
    description: str
    required_skills: List[str] = []

    class Config:
        from_attributes = True

@router.get("", response_model=List[CareerResponse])
def list_careers(db: Session = Depends(get_db)):
    careers = crud.get_careers(db)
    result = []
    for c in careers:
        skills = [s.skill_name for s in c.skills if s.tier == "required"]
        if not skills:
            skills = [s.skill_name for s in c.skills]
        result.append({
            "name": c.name,
            "description": c.description,
            "required_skills": skills
        })
    return result
