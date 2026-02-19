"""
Tests for leaderboard endpoints.
"""

import pytest


class TestGetLeaderboard:
    """Tests for GET /leaderboard"""
    
    def test_get_all_leaderboard(self, client):
        """Test getting all leaderboard entries."""
        response = client.get("/api/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Verify structure
        for entry in data:
            assert "id" in entry
            assert "username" in entry
            assert "score" in entry
            assert "mode" in entry
            assert "date" in entry

    def test_leaderboard_sorted_by_score(self, client):
        """Test that leaderboard is sorted by score descending."""
        response = client.get("/api/leaderboard")
        assert response.status_code == 200
        data = response.json()
        
        # Verify sorting
        for i in range(len(data) - 1):
            assert data[i]["score"] >= data[i + 1]["score"]

    def test_leaderboard_filter_by_walls_mode(self, client):
        """Test filtering leaderboard by 'walls' mode."""
        response = client.get("/api/leaderboard?mode=walls")
        assert response.status_code == 200
        data = response.json()
        
        # All entries should be 'walls' mode
        for entry in data:
            assert entry["mode"] == "walls"

    def test_leaderboard_filter_by_passthrough_mode(self, client):
        """Test filtering leaderboard by 'pass-through' mode."""
        response = client.get("/api/leaderboard?mode=pass-through")
        assert response.status_code == 200
        data = response.json()
        
        # All entries should be 'pass-through' mode
        for entry in data:
            assert entry["mode"] == "pass-through"

    def test_leaderboard_invalid_mode(self, client):
        """Test filtering with invalid game mode."""
        response = client.get("/api/leaderboard?mode=invalid")
        assert response.status_code == 400


class TestSubmitScore:
    """Tests for POST /leaderboard"""
    
    def test_submit_score_success(self, client, auth_headers, test_user):
        """Test submitting a score successfully."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": 1500,
                "mode": "walls"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 1500
        assert data["mode"] == "walls"
        assert data["username"] == test_user["username"]
        assert "id" in data
        assert "date" in data

    def test_submit_score_passthrough_mode(self, client, auth_headers):
        """Test submitting a score with pass-through mode."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": 2000,
                "mode": "pass-through"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["mode"] == "pass-through"

    def test_submit_score_zero_score(self, client, auth_headers):
        """Test submitting a zero score."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": 0,
                "mode": "walls"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["score"] == 0

    def test_submit_score_negative(self, client, auth_headers):
        """Test submitting a negative score (should fail)."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": -100,
                "mode": "walls"
            },
            headers=auth_headers
        )
        assert response.status_code == 422  # Pydantic validation error for negative number

    def test_submit_score_invalid_mode(self, client, auth_headers):
        """Test submitting with invalid game mode."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": 1000,
                "mode": "invalid"
            },
            headers=auth_headers
        )
        assert response.status_code == 422  # Pydantic validation error for invalid pattern

    def test_submit_score_missing_score(self, client, auth_headers):
        """Test submitting without score field."""
        response = client.post(
            "/api/leaderboard",
            json={"mode": "walls"},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_submit_score_missing_mode(self, client, auth_headers):
        """Test submitting without mode field."""
        response = client.post(
            "/api/leaderboard",
            json={"score": 1000},
            headers=auth_headers
        )
        assert response.status_code == 422

    def test_submit_score_without_auth(self, client):
        """Test score submission without authentication."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": 1000,
                "mode": "walls"
            }
        )
        assert response.status_code == 403

    def test_submit_score_invalid_token(self, client):
        """Test submitting with invalid token."""
        response = client.post(
            "/api/leaderboard",
            json={
                "score": 1000,
                "mode": "walls"
            },
            headers={"Authorization": "Bearer invalid"}
        )
        assert response.status_code == 401


class TestLeaderboardOperations:
    """Integration tests for leaderboard operations."""
    
    def test_multiple_score_submissions(self, client, auth_headers):
        """Test submitting multiple scores."""
        scores = [1000, 1500, 2000, 1200, 1800]
        
        for score in scores:
            response = client.post(
                "/api/leaderboard",
                json={"score": score, "mode": "walls"},
                headers=auth_headers
            )
            assert response.status_code == 201
        
        # Get leaderboard and verify all scores are there
        response = client.get("/api/leaderboard?mode=walls")
        assert response.status_code == 200
        data = response.json()
        submitted_scores = [e["score"] for e in data if e["score"] in scores]
        assert len(submitted_scores) == len(scores)

    def test_leaderboard_after_submission(self, client, auth_headers, test_user):
        """Test that submitted score appears in leaderboard."""
        # Submit a very high score
        submit_response = client.post(
            "/api/leaderboard",
            json={"score": 9999, "mode": "walls"},
            headers=auth_headers
        )
        assert submit_response.status_code == 201
        submitted_id = submit_response.json()["id"]
        
        # Get leaderboard and look for our score
        leaderboard_response = client.get("/api/leaderboard?mode=walls")
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()
        
        # Find our entry
        our_entry = next((e for e in leaderboard if e["id"] == submitted_id), None)
        assert our_entry is not None
        assert our_entry["score"] == 9999
        assert our_entry["username"] == test_user["username"]
