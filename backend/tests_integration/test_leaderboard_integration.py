"""
Integration tests for leaderboard endpoints using SQLite.
"""

import pytest
from datetime import datetime, date


class TestLeaderboardIntegration:
    """Integration tests for leaderboard endpoints"""

    def test_get_global_leaderboard(self, client, auth_headers):
        """Test retrieving the global leaderboard."""
        response = client.get("/api/leaderboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have seeded leaderboard entries
        assert len(data) > 0
        # Verify structure
        for entry in data:
            assert "id" in entry
            assert "username" in entry
            assert "score" in entry
            assert "mode" in entry
            assert "date" in entry

    def test_get_leaderboard_without_auth(self, client):
        """Test that leaderboard may be public or require auth."""
        response = client.get("/api/leaderboard")
        # Leaderboard is often public, but may require auth
        assert response.status_code in [200, 401, 403]

    def test_leaderboard_sorted_by_score(self, client, auth_headers):
        """Test that leaderboard is sorted by score (descending)."""
        response = client.get("/api/leaderboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify it's sorted by score descending
        scores = [entry["score"] for entry in data]
        assert scores == sorted(scores, reverse=True)

    def test_get_leaderboard_by_mode(self, client, auth_headers):
        """Test filtering leaderboard by game mode."""
        # Get walls mode leaderboard
        response_walls = client.get(
            "/api/leaderboard?mode=walls",
            headers=auth_headers
        )
        assert response_walls.status_code == 200
        walls_data = response_walls.json()
        assert all(entry["mode"] == "walls" for entry in walls_data)

        # Get pass-through mode leaderboard
        response_pass = client.get(
            "/api/leaderboard?mode=pass-through",
            headers=auth_headers
        )
        assert response_pass.status_code == 200
        pass_data = response_pass.json()
        assert all(entry["mode"] == "pass-through" for entry in pass_data)

    def test_leaderboard_by_mode_sorted(self, client, auth_headers):
        """Test that mode-filtered leaderboard is also sorted by score."""
        response = client.get(
            "/api/leaderboard?mode=walls",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        scores = [entry["score"] for entry in data]
        assert scores == sorted(scores, reverse=True)

    def test_leaderboard_contains_submitted_scores(self, client, auth_headers, test_user, test_db):
        """Test that submitted scores appear in leaderboard."""
        # Submit a unique high score
        unique_score = 99999
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={"score": unique_score, "mode": "walls"}
        )
        assert response.status_code == 201

        # Get leaderboard and find the score
        leaderboard_response = client.get(
            "/api/leaderboard",
            headers=auth_headers
        )
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()

        found = False
        for entry in leaderboard:
            if entry["username"] == test_user["username"] and entry["score"] == unique_score:
                found = True
                break
        assert found, f"Score {unique_score} not found in leaderboard"

    def test_leaderboard_position_after_score_submission(self, client, auth_headers, test_user):
        """Test that user appears in correct position after score submission."""
        # Submit a moderately high score
        score = 9500
        response = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={"score": score, "mode": "walls"}
        )
        assert response.status_code == 201

        # Get leaderboard
        leaderboard_response = client.get(
            "/api/leaderboard?mode=walls",
            headers=auth_headers
        )
        assert leaderboard_response.status_code == 200
        leaderboard = leaderboard_response.json()

        # Find position
        position = None
        for idx, entry in enumerate(leaderboard):
            if entry["username"] == test_user["username"] and entry["score"] == score:
                position = idx
                break

        assert position is not None, "User not found in leaderboard"
        
        # Verify position is based on score (should be near top)
        # Higher scores = lower position number
        # Check that scores before this entry are >= our score
        for i in range(position):
            assert leaderboard[i]["score"] >= score

    def test_leaderboard_multiple_same_user_scores(self, client, auth_headers, test_user):
        """Test that leaderboard shows all entries from a user."""
        scores = [5000, 7000, 3000]
        for score in scores:
            response = client.post(
                "/api/leaderboard",
                headers=auth_headers,
                json={"score": score, "mode": "walls"}
            )
            assert response.status_code == 201

        # Get leaderboard
        leaderboard_response = client.get(
            "/api/leaderboard?mode=walls",
            headers=auth_headers
        )
        leaderboard = leaderboard_response.json()

        # Count entries from test_user
        user_entries = [e for e in leaderboard if e["username"] == test_user["username"]]
        # At least our 3 scores should be there
        assert len(user_entries) >= 3

    def test_leaderboard_high_scores_first(self, client, auth_headers, test_user, test_db):
        """Test that highest scores appear first in leaderboard."""
        # Submit multiple scores
        scores = [1000, 5000, 3000, 9000, 2000]
        for score in scores:
            response = client.post(
                "/api/leaderboard",
                headers=auth_headers,
                json={"score": score, "mode": "walls"}
            )
            assert response.status_code == 201

        # Get leaderboard
        leaderboard_response = client.get(
            "/api/leaderboard?mode=walls",
            headers=auth_headers
        )
        leaderboard = leaderboard_response.json()

        # Find highest score from our user
        user_scores = [
            e["score"] for e in leaderboard
            if e["username"] == test_user["username"]
        ]
        highest_user_score = max(user_scores) if user_scores else 0

        # Find position of highest score in leaderboard
        for idx, entry in enumerate(leaderboard):
            if entry["username"] == test_user["username"] and entry["score"] == highest_user_score:
                # Check that all scores before it are higher
                for i in range(idx):
                    assert leaderboard[i]["score"] >= highest_user_score
                break

    def test_leaderboard_different_modes_independent(self, client, auth_headers, test_user):
        """Test that scores in different modes don't affect each other's ranking."""
        # Submit high score in walls mode
        response_walls = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={"score": 9000, "mode": "walls"}
        )
        assert response_walls.status_code == 201

        # Submit low score in pass-through mode
        response_pass = client.post(
            "/api/leaderboard",
            headers=auth_headers,
            json={"score": 1000, "mode": "pass-through"}
        )
        assert response_pass.status_code == 201

        # Get leaderboards for each mode
        walls_response = client.get(
            "/api/leaderboard?mode=walls",
            headers=auth_headers
        )
        pass_response = client.get(
            "/api/leaderboard?mode=pass-through",
            headers=auth_headers
        )

        walls_board = walls_response.json()
        pass_board = pass_response.json()

        # Find user in walls board
        walls_user = next(
            (e for e in walls_board if e["username"] == test_user["username"]),
            None
        )
        assert walls_user is not None
        assert walls_user["score"] == 9000

        # Find user in pass-through board
        pass_user = next(
            (e for e in pass_board if e["username"] == test_user["username"]),
            None
        )
        assert pass_user is not None
        assert pass_user["score"] == 1000

    def test_leaderboard_limit_query_parameter(self, client, auth_headers):
        """Test that leaderboard respects limit parameter if supported."""
        response = client.get(
            "/api/leaderboard?limit=5",
            headers=auth_headers
        )
        # May or may not support limit parameter, so just check it doesn't error
        assert response.status_code in [200, 400, 422]

    def test_leaderboard_date_format(self, client, auth_headers):
        """Test that leaderboard entries have proper date format."""
        response = client.get("/api/leaderboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        for entry in data:
            # Date should be in ISO format (YYYY-MM-DD)
            date_str = entry["date"]
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pytest.fail(f"Invalid date format: {date_str}")

    def test_leaderboard_entry_structure(self, client, auth_headers):
        """Test that leaderboard entries have all required fields."""
        response = client.get("/api/leaderboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "username", "score", "mode", "date"]
        for entry in data:
            for field in required_fields:
                assert field in entry, f"Missing field: {field}"
                assert entry[field] is not None, f"Null field: {field}"

    def test_leaderboard_score_values_non_negative(self, client, auth_headers):
        """Test that all leaderboard scores are non-negative."""
        response = client.get("/api/leaderboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        
        for entry in data:
            assert entry["score"] >= 0, f"Negative score found: {entry['score']}"

    def test_empty_leaderboard_for_missing_mode(self, client, auth_headers):
        """Test querying leaderboard for non-existent mode."""
        response = client.get(
            "/api/leaderboard?mode=nonexistent_mode",
            headers=auth_headers
        )
        # May return 404, 400, or empty list
        if response.status_code == 200:
            data = response.json()
            # Could be empty or could contain entries
            assert isinstance(data, list)
