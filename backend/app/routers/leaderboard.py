"""
Leaderboard endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from datetime import date
from app.models import LeaderboardEntry, SubmitScoreRequest
from app.database import db
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=list[LeaderboardEntry])
async def get_leaderboard(mode: str = Query(None)):
    """Get leaderboard entries, optionally filtered by mode."""
    if mode is not None and mode not in ["pass-through", "walls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid game mode",
        )
    
    entries = db.get_all_leaderboard_entries(mode=mode)
    
    return [
        LeaderboardEntry(
            id=entry.id,
            username=entry.username,
            score=entry.score,
            mode=entry.mode,
            date=entry.date
        )
        for entry in entries
    ]


@router.post("", response_model=LeaderboardEntry, status_code=201)
async def submit_score(score_data: SubmitScoreRequest, current_user = Depends(get_current_user)):
    """Submit a score to the leaderboard."""
    # Validate score
    if score_data.score < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid score value",
            headers={"X-Error-Code": "INVALID_INPUT"},
        )
    
    # Validate mode
    if score_data.mode not in ["pass-through", "walls"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid game mode",
            headers={"X-Error-Code": "INVALID_INPUT"},
        )
    
    # Add to leaderboard
    entry = db.add_leaderboard_entry(
        username=current_user.username,
        score=score_data.score,
        mode=score_data.mode,
        entry_date=date.today()
    )
    
    return LeaderboardEntry(
        id=entry.id,
        username=entry.username,
        score=entry.score,
        mode=entry.mode,
        date=entry.date
    )
