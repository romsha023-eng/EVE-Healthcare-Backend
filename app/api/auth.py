from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import Token, UserLogin, UserResponse, UserSignUp
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user (USER or ADMIN role). Duplicate emails return 400 Bad Request.",
)
def signup(user_in: UserSignUp, db: Session = Depends(get_db)):
    return register_user(db, user_in)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email and password, returning a JWT access token.",
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, credentials)
