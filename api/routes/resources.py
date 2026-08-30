from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import crud
from api.dependencies import get_db
from models.resources import LearningResource
from services.rag_service import to_pydantic_resource

router = APIRouter(prefix="/api/resources", tags=["resources"])

@router.get("", response_model=List[LearningResource])
def list_resources(db: Session = Depends(get_db)):
    db_resources = crud.get_resources(db)
    return [to_pydantic_resource(r) for r in db_resources]
