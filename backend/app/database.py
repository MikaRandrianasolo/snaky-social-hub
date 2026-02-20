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
        """Seed with comprehensive mock data for testing."""
        # Note: Test users are NOT pre-seeded to allow testing signup/login flow
        # Users can freely create accounts during testing
        
        # Comprehensive mock leaderboard with more entries
        mock_leaderboard = [
            {"username": "PixelViper", "score": 8950, "mode": "walls", "date": "2026-02-19"},
            {"username": "ShadowMaster", "score": 8420, "mode": "walls", "date": "2026-02-18"},
            {"username": "NeonByte", "score": 7850, "mode": "pass-through", "date": "2026-02-19"},
            {"username": "CyberSnake", "score": 7620, "mode": "walls", "date": "2026-02-19"},
            {"username": "RetroGlitch", "score": 7340, "mode": "pass-through", "date": "2026-02-18"},
            {"username": "ArcadeKing", "score": 6890, "mode": "walls", "date": "2026-02-17"},
            {"username": "GlowWorm", "score": 6750, "mode": "pass-through", "date": "2026-02-19"},
            {"username": "BitCrusher", "score": 6520, "mode": "walls", "date": "2026-02-18"},
            {"username": "VoidRunner", "score": 6180, "mode": "pass-through", "date": "2026-02-17"},
            {"username": "PhosphorGlow", "score": 5940, "mode": "walls", "date": "2026-02-19"},
            {"username": "EchoKnight", "score": 5670, "mode": "pass-through", "date": "2026-02-16"},
            {"username": "IceVenom", "score": 5420, "mode": "walls", "date": "2026-02-18"},
            {"username": "NovaStrike", "score": 5180, "mode": "pass-through", "date": "2026-02-19"},
            {"username": "HexEngineer", "score": 4950, "mode": "walls", "date": "2026-02-17"},
            {"username": "FrostByte", "score": 4720, "mode": "pass-through", "date": "2026-02-18"},
            {"username": "ThunderSnake", "score": 4580, "mode": "walls", "date": "2026-02-19"},
            {"username": "CrimsonWave", "score": 4320, "mode": "pass-through", "date": "2026-02-16"},
            {"username": "SilentViper", "score": 4150, "mode": "walls", "date": "2026-02-15"},
            {"username": "LunarEcho", "score": 3920, "mode": "pass-through", "date": "2026-02-19"},
            {"username": "InfernoPath", "score": 3750, "mode": "walls", "date": "2026-02-18"},
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

        # More live games in progress
        mock_games = [
            {"id": "game_001", "username": "PixelViper", "score": 890, "mode": "walls", "startedAt": "2026-02-19T10:15:00Z"},
            {"id": "game_002", "username": "ShadowMaster", "score": 650, "mode": "pass-through", "startedAt": "2026-02-19T10:22:00Z"},
            {"id": "game_003", "username": "NeonByte", "score": 1240, "mode": "walls", "startedAt": "2026-02-19T10:05:00Z"},
            {"id": "game_004", "username": "CyberSnake", "score": 520, "mode": "pass-through", "startedAt": "2026-02-19T10:28:00Z"},
            {"id": "game_005", "username": "RetroGlitch", "score": 780, "mode": "walls", "startedAt": "2026-02-19T10:18:00Z"},
            {"id": "game_006", "username": "ArcadeKing", "score": 310, "mode": "pass-through", "startedAt": "2026-02-19T10:32:00Z"},
            {"id": "game_007", "username": "GlowWorm", "score": 1050, "mode": "walls", "startedAt": "2026-02-19T10:10:00Z"},
            {"id": "game_008", "username": "BitCrusher", "score": 420, "mode": "pass-through", "startedAt": "2026-02-19T10:25:00Z"},
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
