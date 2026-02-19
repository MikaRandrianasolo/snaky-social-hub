"""
Authentication endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from datetime import timedelta
from app.models import UserCreate, UserLogin, User, AuthResponse
from app.database import db
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=User, status_code=201)
async def signup(user_data: UserCreate):
    """Create a new user account."""
    # Check if email already exists
    if db.user_exists_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
            headers={"X-Error-Code": "EMAIL_DUPLICATE"},
        )
    
    # Hash password and create user
    password_hash = hash_password(user_data.password)
    user = db.create_user(user_data.username, user_data.email, password_hash)
    
    return User(id=user.id, username=user.username, email=user.email)


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """Login with email and password."""
    user = db.get_user_by_email(credentials.email)
    
    if user is None or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"X-Error-Code": "INVALID_CREDENTIALS"},
        )
    
    # Create JWT token
    token = create_access_token(data={"sub": user.id})
    
    return AuthResponse(
        user=User(id=user.id, username=user.username, email=user.email),
        token=token
    )


@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout current user."""
    # In a real app, we'd invalidate the token (e.g., add to blacklist)
    # For now, just return success
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=User)
async def get_current_user_endpoint(current_user = Depends(get_current_user)):
    """Get current authenticated user."""
    return User(id=current_user.id, username=current_user.username, email=current_user.email)
