from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: str
    username: str
    email: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: User
    token: str


class SubmitScoreRequest(BaseModel):
    score: int = Field(..., ge=0)
    mode: str = Field(..., pattern="^(pass-through|walls)$")


class LeaderboardEntry(BaseModel):
    id: str
    username: str
    score: int = Field(..., ge=0)
    mode: str
    date: date

    class Config:
        from_attributes = True


class LiveGame(BaseModel):
    id: str
    username: str
    score: int = Field(..., ge=0)
    mode: str
    startedAt: datetime

    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: str
    code: str
    details: Optional[dict] = None
