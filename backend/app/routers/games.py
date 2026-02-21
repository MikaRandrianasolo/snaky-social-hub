"""
Live games endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from app.models import LiveGame
from app import database

router = APIRouter(prefix="/api/games", tags=["Live Games"])


@router.get("", response_model=list[LiveGame])
async def get_live_games():
    """Get all active live games."""
    games = database.db.get_all_live_games()
    
    return [
        LiveGame(
            id=game.id,
            username=game.username,
            score=game.score,
            mode=game.mode,
            startedAt=game.startedAt
        )
        for game in games
    ]


@router.get("/{game_id}", response_model=LiveGame)
async def get_game_by_id(game_id: str):
    """Get a specific live game by ID."""
    game = database.db.get_live_game_by_id(game_id)
    
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found",
            headers={"X-Error-Code": "NOT_FOUND"},
        )
    
    return LiveGame(
        id=game.id,
        username=game.username,
        score=game.score,
        mode=game.mode,
        startedAt=game.startedAt
    )
