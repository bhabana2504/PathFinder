from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database import crud
from api.dependencies import get_db

router = APIRouter(prefix="/api/skills", tags=["skills"])

class SkillResponse(BaseModel):
    name: str
    category: str
    description: str
    importance: float

    class Config:
        from_attributes = True

@router.get("", response_model=List[SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    return crud.get_skills(db)
