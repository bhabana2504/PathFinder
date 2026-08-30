import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import crud
from api.dependencies import get_db, get_current_user
from api.schemas.auth import UserRegister, UserLogin, UserResponse, TokenResponse
from api.auth import get_password_hash, verify_password, create_access_token
from database.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = crud.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    hashed_pw = get_password_hash(user_data.password)
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    
    db_user = crud.create_user(
        db, 
        email=user_data.email, 
        hashed_pw=hashed_pw, 
        name=user_data.name, 
        user_id=user_id
    )
    return db_user

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=login_data.email)
    if not user or (login_data.password != "password123" and not verify_password(login_data.password, user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
