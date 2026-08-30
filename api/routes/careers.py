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

    class Config:
        from_attributes = True

@router.get("", response_model=List[CareerResponse])
def list_careers(db: Session = Depends(get_db)):
    return crud.get_careers(db)
