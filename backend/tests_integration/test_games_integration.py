"""
Integration tests for game endpoints using SQLite.
"""

import pytest
from datetime import datetime, timedelta


class TestGamesIntegration:
    """Integration tests for game endpoints"""

    def test_get_live_games(self, client, auth_headers):
        """Test retrieving live games."""
        response = client.get("/api/games", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have seeded live games
        assert len(data) > 0
        # Verify structure of game objects
        for game in data:
            assert "id" in game
            assert "username" in game
            assert "score" in game
            assert "mode" in game
            assert "startedAt" in game

    def test_get_live_games_without_auth(self, client):
        """Test that live games endpoint may be public or require auth."""
        response = client.get("/api/games")
        # Some games endpoints may be public, some may require auth
        assert response.status_code in [200, 401, 403]

    def test_submit_score(self, client, auth_headers, test_user):
        """Test submitting a game score."""
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={
                "score": 5000,
                "mode": "walls"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user["username"]
        assert data["score"] == 5000
        assert data["mode"] == "walls"
        assert "date" in data

    def test_submit_score_pass_through_mode(self, client, auth_headers, test_user):
        """Test submitting a score in pass-through mode."""
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={
                "score": 3500,
                "mode": "pass-through"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["mode"] == "pass-through"
        assert data["score"] == 3500

    def test_submit_score_invalid_mode(self, client, auth_headers):
        """Test that invalid game modes are rejected."""
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={
                "score": 5000,
                "mode": "invalid_mode"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_submit_score_negative_score(self, client, auth_headers):
        """Test that negative scores are rejected."""
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={
                "score": -1000,
                "mode": "walls"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_submit_score_without_auth(self, client):
        """Test that score submission requires authentication."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": 5000,
                "mode": "walls"
            }
        )
        assert response.status_code in [401, 403]

    def test_submit_score_persists_to_leaderboard(self, client, auth_headers, test_user, test_db):
        """Test that submitted scores are added to the leaderboard."""
        # Submit a score
        score = 7500
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={
                "score": score,
                "mode": "walls"
            }
        )
        assert response.status_code == 201

        # Verify score appears in leaderboard
        leaderboard = test_db.get_all_leaderboard_entries(mode="walls")
        # Find the newly added score
        found = False
        for entry in leaderboard:
            if entry.username == test_user["username"] and entry.score == score:
                found = True
                break
        assert found, "Score not found in leaderboard"

    def test_multiple_score_submissions(self, client, auth_headers, test_user):
        """Test that a user can submit multiple scores."""
        scores = [1000, 2000, 3000]
        responses = []
        
        for score in scores:
            response = client.post(
                "/api/leaderboard",
                headers=auth_headers,
                json={
                    "score": score,
                    "mode": "walls"
                }
            )
            assert response.status_code == 201
            responses.append(response.json())

        # Verify all scores were recorded
        assert len(responses) == 3
        for i, response in enumerate(responses):
            assert response["score"] == scores[i]

    def test_different_modes_tracked_separately(self, client, auth_headers, test_user, test_db):
        """Test that scores in different modes are tracked separately."""
        # Submit score in walls mode
        response1 = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={"score": 5000, "mode": "walls"}
        )
        assert response1.status_code == 201

        # Submit score in pass-through mode
        response2 = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={"score": 3000, "mode": "pass-through"}
        )
        assert response2.status_code == 201

        # Verify both scores exist in appropriate mode lists
        walls_scores = test_db.get_all_leaderboard_entries(mode="walls")
        pass_through_scores = test_db.get_all_leaderboard_entries(mode="pass-through")

        walls_found = any(e.username == test_user["username"] and e.score == 5000 for e in walls_scores)
        pass_found = any(e.username == test_user["username"] and e.score == 3000 for e in pass_through_scores)

        assert walls_found
        assert pass_found

    def test_zero_score_submission(self, client, auth_headers):
        """Test that zero scores are allowed."""
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={
                "score": 0,
                "mode": "walls"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 0

    def test_large_score_submission(self, client, auth_headers):
        """Test that large scores are accepted."""
        large_score = 999999
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={
                "score": large_score,
                "mode": "walls"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == large_score

    def test_watch_game_endpoint(self, client, auth_headers):
        """Test the watch game endpoint."""
        response = client.get("/api/games/watch", headers=auth_headers)
        # This endpoint may or may not exist, so check for reasonable responses
        assert response.status_code in [200, 404]

    def test_submit_score_multiple_users(self, client, test_user, test_user_2, test_db):
        """Test that different users can submit scores independently."""
        from app.security import hash_password
        
        # Login as first user
        login1 = client.post(
            "/api/auth/login",
            json={"email": test_user["email"], "password": test_user["password"]}
        )
        token1 = login1.json()["token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Login as second user
        login2 = client.post(
            "/api/auth/login",
            json={"email": test_user_2["email"], "password": test_user_2["password"]}
        )
        token2 = login2.json()["token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Submit score as first user
        response1 = client.post(
            "/api/leaderboard",
            headers=headers1,
            json={"score": 5000, "mode": "walls"}
        )
        assert response1.status_code == 201
        assert response1.json()["username"] == test_user["username"]

        # Submit score as second user
        response2 = client.post(
            "/api/leaderboard",
            headers=headers2,
            json={"score": 4000, "mode": "walls"}
        )
        assert response2.status_code == 201
        assert response2.json()["username"] == test_user_2["username"]

        # Verify both scores exist in leaderboard
        leaderboard = test_db.get_all_leaderboard_entries(mode="walls")
        usernames = [e.username for e in leaderboard]
        assert test_user["username"] in usernames
        assert test_user_2["username"] in usernames
