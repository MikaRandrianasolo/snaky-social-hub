"""
Dependency injection for FastAPI routes.
"""

from fastapi import Depends, HTTPException, status, Header
from app.security import decode_token
from app import database
from app.database import db
from typing import Optional


async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user from JWT token."""
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No credentials provided",
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    token = parts[1]
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )
    
    # Get db from the module to allow for patching in tests
    current_db = database.db
    user = current_db.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


async def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Get current user if authenticated, otherwise None."""
    if authorization is None:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    token = parts[1]
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    # Get db from the module to allow for patching in tests
    current_db = database.db
    user = current_db.get_user_by_id(user_id)
    return user if user else None
