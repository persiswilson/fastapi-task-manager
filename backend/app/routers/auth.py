from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserResponse, Token
from app.auth import hash_password, verify_password, create_access_token, settings

router = APIRouter(
    tags=["Authentication"]
)

# 1. USER REGISTRATION
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user into the database after hashing their password."""
    # Check if username is already taken
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    
    # Securely hash the password before saving
    hashed_pwd = hash_password(user_data.password)
    new_user = User(username=user_data.username, hashed_password=hashed_pwd)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 2. USER LOGIN (Generates JWT Token)
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Verifies user credentials and returns a secure JWT access token."""
    # Look up the user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Verify user exists and the password hashes match
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Calculate token expiration and encode the JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}