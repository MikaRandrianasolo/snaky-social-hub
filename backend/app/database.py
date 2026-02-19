"""
Mock database layer - stores data in memory.
In production, replace this with real database ORM (SQLAlchemy, etc.)
"""

from typing import Optional, List, Dict
from datetime import datetime, date
import uuid


class User:
    def __init__(self, id: str, username: str, email: str, password_hash: str):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash


class LeaderboardEntry:
    def __init__(self, id: str, username: str, score: int, mode: str, entry_date: date):
        self.id = id
        self.username = username
        self.score = score
        self.mode = mode
        self.date = entry_date


class LiveGameRecord:
    def __init__(self, id: str, username: str, score: int, mode: str, started_at: datetime):
        self.id = id
        self.username = username
        self.score = score
        self.mode = mode
        self.startedAt = started_at


class MockDatabase:
    """In-memory mock database."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.users_by_email: Dict[str, User] = {}
        self.leaderboard: List[LeaderboardEntry] = []
        self.live_games: Dict[str, LiveGameRecord] = {}
        self._seed_data()

    def _seed_data(self):
        """Seed with mock data similar to frontend tests."""
        mock_leaderboard = [
            {"username": "PixelViper", "score": 2450, "mode": "walls", "date": "2026-02-17"},
            {"username": "NeonByte", "score": 2100, "mode": "pass-through", "date": "2026-02-16"},
            {"username": "RetroGlitch", "score": 1890, "mode": "walls", "date": "2026-02-17"},
            {"username": "CyberSnake", "score": 1750, "mode": "pass-through", "date": "2026-02-15"},
            {"username": "ArcadeKing", "score": 1620, "mode": "walls", "date": "2026-02-16"},
            {"username": "GlowWorm", "score": 1500, "mode": "pass-through", "date": "2026-02-14"},
            {"username": "BitCrusher", "score": 1380, "mode": "walls", "date": "2026-02-17"},
            {"username": "SnakeEyes", "score": 1200, "mode": "pass-through", "date": "2026-02-13"},
            {"username": "VoidRunner", "score": 1050, "mode": "walls", "date": "2026-02-16"},
            {"username": "PhosphorGlow", "score": 900, "mode": "pass-through", "date": "2026-02-15"},
        ]
        
        for entry in mock_leaderboard:
            lb_entry = LeaderboardEntry(
                id=str(uuid.uuid4()),
                username=entry["username"],
                score=entry["score"],
                mode=entry["mode"],
                entry_date=datetime.strptime(entry["date"], "%Y-%m-%d").date()
            )
            self.leaderboard.append(lb_entry)

        # Mock live games
        mock_games = [
            {"id": "live1", "username": "PixelViper", "score": 340, "mode": "walls", "startedAt": "2026-02-17T14:30:00Z"},
            {"id": "live2", "username": "NeonByte", "score": 120, "mode": "pass-through", "startedAt": "2026-02-17T14:45:00Z"},
            {"id": "live3", "username": "RetroGlitch", "score": 560, "mode": "walls", "startedAt": "2026-02-17T14:20:00Z"},
        ]
        
        for game in mock_games:
            lg = LiveGameRecord(
                id=game["id"],
                username=game["username"],
                score=game["score"],
                mode=game["mode"],
                started_at=datetime.fromisoformat(game["startedAt"].replace("Z", "+00:00"))
            )
            self.live_games[game["id"]] = lg

    # User operations
    def create_user(self, username: str, email: str, password_hash: str) -> User:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        user = User(user_id, username, email, password_hash)
        self.users[user_id] = user
        self.users_by_email[email] = user
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.users_by_email.get(email)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)

    def user_exists_by_email(self, email: str) -> bool:
        """Check if user exists by email."""
        return email in self.users_by_email

    # Leaderboard operations
    def get_all_leaderboard_entries(self, mode: Optional[str] = None) -> List[LeaderboardEntry]:
        """Get leaderboard entries, optionally filtered by mode."""
        if mode:
            entries = [e for e in self.leaderboard if e.mode == mode]
        else:
            entries = self.leaderboard[:]
        
        # Sort by score descending
        entries.sort(key=lambda x: x.score, reverse=True)
        return entries

    def add_leaderboard_entry(self, username: str, score: int, mode: str, entry_date: date) -> LeaderboardEntry:
        """Add a new leaderboard entry."""
        entry = LeaderboardEntry(
            id=str(uuid.uuid4()),
            username=username,
            score=score,
            mode=mode,
            entry_date=entry_date
        )
        self.leaderboard.append(entry)
        return entry

    # Live games operations
    def get_all_live_games(self) -> List[LiveGameRecord]:
        """Get all live games."""
        return list(self.live_games.values())

    def get_live_game_by_id(self, game_id: str) -> Optional[LiveGameRecord]:
        """Get a specific live game."""
        return self.live_games.get(game_id)

    def add_live_game(self, game_id: str, username: str, score: int, mode: str, started_at: datetime) -> LiveGameRecord:
        """Add a new live game."""
        game = LiveGameRecord(game_id, username, score, mode, started_at)
        self.live_games[game_id] = game
        return game

    def remove_live_game(self, game_id: str) -> bool:
        """Remove a live game."""
        if game_id in self.live_games:
            del self.live_games[game_id]
            return True
        return False


# Global database instance
db = MockDatabase()
