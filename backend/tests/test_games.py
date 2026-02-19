"""
Tests for live games endpoints.
"""

import pytest


class TestGetLiveGames:
    """Tests for GET /games"""
    
    def test_get_all_live_games(self, client):
        """Test getting all live games."""
        response = client.get("/api/games")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify structure
        for game in data:
            assert "id" in game
            assert "username" in game
            assert "score" in game
            assert "mode" in game
            assert "startedAt" in game

    def test_live_games_have_valid_modes(self, client):
        """Test that all live games have valid game modes."""
        response = client.get("/api/games")
        assert response.status_code == 200
        data = response.json()
        
        for game in data:
            assert game["mode"] in ["pass-through", "walls"]

    def test_live_games_scores_non_negative(self, client):
        """Test that all live game scores are non-negative."""
        response = client.get("/api/games")
        assert response.status_code == 200
        data = response.json()
        
        for game in data:
            assert game["score"] >= 0

    def test_live_games_have_startedAt(self, client):
        """Test that all games have startedAt timestamp."""
        response = client.get("/api/games")
        assert response.status_code == 200
        data = response.json()
        
        for game in data:
            assert "startedAt" in game
            # Should be ISO 8601 format datetime
            assert "T" in game["startedAt"]


class TestGetGameById:
    """Tests for GET /games/{gameId}"""
    
    def test_get_game_by_id_success(self, client):
        """Test getting a specific game by ID."""
        # First get the list of games
        list_response = client.get("/api/games")
        assert list_response.status_code == 200
        games = list_response.json()
        assert len(games) > 0
        game_id = games[0]["id"]
        
        # Get specific game
        response = client.get(f"/api/games/{game_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == game_id
        assert "username" in data
        assert "score" in data
        assert "mode" in data
        assert "startedAt" in data

    def test_get_game_by_id_not_found(self, client):
        """Test getting a game that doesn't exist."""
        response = client.get("/api/games/nonexistent-game-id")
        assert response.status_code == 404
        data = response.json()
        assert "Game not found" in data["detail"]

    def test_get_game_returns_correct_data(self, client):
        """Test that game data is consistent."""
        # Get all games
        list_response = client.get("/api/games")
        all_games = list_response.json()
        
        # Get each game individually and verify data matches
        for expected_game in all_games:
            response = client.get(f"/api/games/{expected_game['id']}")
            assert response.status_code == 200
            actual_game = response.json()
            
            assert actual_game["id"] == expected_game["id"]
            assert actual_game["username"] == expected_game["username"]
            assert actual_game["score"] == expected_game["score"]
            assert actual_game["mode"] == expected_game["mode"]
            assert actual_game["startedAt"] == expected_game["startedAt"]


class TestLiveGamesIntegration:
    """Integration tests for live games."""
    
    def test_game_list_contains_multiple_games(self, client):
        """Test that game list contains multiple games with different users."""
        response = client.get("/api/games")
        assert response.status_code == 200
        games = response.json()
        
        # Should have multiple games with different users
        assert len(games) > 1
        usernames = {g["username"] for g in games}
        assert len(usernames) > 1

    def test_games_have_consistent_ids(self, client):
        """Test that game IDs are consistent across calls."""
        # Get games twice
        response1 = client.get("/api/games")
        response2 = client.get("/api/games")
        
        games1 = {g["id"]: g for g in response1.json()}
        games2 = {g["id"]: g for g in response2.json()}
        
        # Should have same game IDs
        assert set(games1.keys()) == set(games2.keys())

    def test_can_retrieve_all_games_individually(self, client):
        """Test that all games in list can be retrieved individually."""
        list_response = client.get("/api/games")
        games = list_response.json()
        
        for game in games:
            response = client.get(f"/api/games/{game['id']}")
            assert response.status_code == 200, f"Failed to get game {game['id']}"


class TestLiveGamesNoAuth:
    """Test that live games endpoints don't require authentication."""
    
    def test_get_games_no_auth(self, client):
        """Test that getting games doesn't require auth."""
        response = client.get("/api/games")
        assert response.status_code == 200

    def test_get_game_by_id_no_auth(self, client):
        """Test that getting specific game doesn't require auth."""
        # Get a game ID first
        list_response = client.get("/api/games")
        games = list_response.json()
        if games:
            game_id = games[0]["id"]
            response = client.get(f"/api/games/{game_id}")
            assert response.status_code == 200
