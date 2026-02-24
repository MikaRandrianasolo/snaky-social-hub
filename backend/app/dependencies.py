"""
Dependency injection for FastAPI routes.
"""

from fastapi import Depends, HTTPException, status, Header
from app.security import decode_token
from app import database
from app.database import db
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current authenticated user from JWT token."""
    logger.info(f"[Auth] get_current_user called - auth header present: {authorization is not None}")
    
    if authorization is None:
        logger.warning("[Auth] No authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No credentials provided",
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"[Auth] Invalid authorization header format: {parts}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    token = parts[1]
    logger.info(f"[Auth] Decoding token: {token[:20]}...")
    payload = decode_token(token)
    
    if payload is None:
        logger.warning("[Auth] Token decoding failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    
    logger.info(f"[Auth] Token payload: {payload}")
    user_id = payload.get("sub")
    if user_id is None:
        logger.warning("[Auth] No 'sub' claim in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )
    
    logger.info(f"[Auth] Looking up user: {user_id}")
    # Get db from the module to allow for patching in tests
    current_db = database.db
    user = current_db.get_user_by_id(user_id)
    
    if user is None:
        logger.error(f"[Auth] User not found for ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    logger.info(f"[Auth] User authenticated: {user.username}")
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
