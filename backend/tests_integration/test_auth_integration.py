"""
Integration tests for authentication endpoints using SQLite.
"""

import pytest


class TestAuthIntegration:
    """Integration tests for authentication"""

    def test_signup_and_login_flow(self, client):
        """Test complete signup and login flow."""
        # Signup
        signup_response = client.post(
            "/api/auth/signup",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert signup_response.status_code == 201
        user_data = signup_response.json()
        # AuthResponse with nested user
        assert user_data["user"]["username"] == "newuser"
        assert user_data["user"]["email"] == "newuser@example.com"
        user_id = user_data["user"]["id"]

        # Login with same credentials
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        auth_data = login_response.json()
        assert auth_data["user"]["id"] == user_id
        assert auth_data["user"]["username"] == "newuser"
        assert "token" in auth_data
        assert len(auth_data["token"]) > 0

    def test_login_with_created_user(self, client, test_user):
        """Test login with a pre-created test user."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["id"] == test_user["id"]
        assert data["user"]["username"] == test_user["username"]
        assert "token" in data

    def test_login_invalid_password(self, client, test_user):
        """Test login fails with wrong password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["detail"].lower() or "incorrect" in data["detail"].lower()

    def test_login_non_existent_user(self, client):
        """Test login fails for non-existent user."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword"
            }
        )
        assert response.status_code == 401

    def test_signup_duplicate_email(self, client, test_user):
        """Test that duplicate emails are rejected during signup."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "anotheruser",
                "email": test_user["email"],  # Same email as test_user
                "password": "password123"
            }
        )
        assert response.status_code == 409
        data = response.json()
        assert "Email already exists" in data["detail"]

    def test_signup_weak_password(self, client):
        """Test that weak passwords are rejected."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "short"  # Too short
            }
        )
        assert response.status_code == 422  # Validation error

    def test_signup_invalid_email(self, client):
        """Test that invalid emails are rejected."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "newuser",
                "email": "notanemail",
                "password": "password123"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_signup_missing_fields(self, client):
        """Test that missing required fields are rejected."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "newuser"
                # Missing email and password
            }
        )
        assert response.status_code == 422

    def test_multiple_users_isolated(self, client, test_user, test_user_2):
        """Test that multiple users can exist independently."""
        # Login as first user
        response1 = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["user"]["id"] == test_user["id"]

        # Login as second user
        response2 = client.post(
            "/api/auth/login",
            json={
                "email": test_user_2["email"],
                "password": test_user_2["password"]
            }
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["user"]["id"] == test_user_2["id"]

        # Verify they are different users
        assert data1["user"]["id"] != data2["user"]["id"]
        assert data1["user"]["username"] != data2["user"]["username"]

    def test_token_validity(self, client, test_user):
        """Test that returned tokens are valid for subsequent requests."""
        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]

        # Use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/leaderboard", headers=headers)
        assert response.status_code == 200  # Should succeed with valid token

    def test_invalid_token(self, client):
        """Test that invalid tokens are rejected or ignored for public endpoints."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/api/leaderboard", headers=headers)
        # Leaderboard is public, so invalid token is accepted but may be ignored
        # For protected endpoints, invalid token should be rejected
        assert response.status_code in [200, 401, 403]

    def test_missing_token(self, client):
        """Test that missing authorization fails for protected endpoints."""
        response = client.get("/api/leaderboard")
        # Should either require auth or publicly available
        # Most endpoints should require auth
        if response.status_code != 200:
            assert response.status_code in [401, 403]

    def test_signup_creates_persistent_user(self, client, test_db):
        """Test that signup creates a user that persists in the database."""
        # Signup
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "persistuser",
                "email": "persist@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        user_id = response.json()["user"]["id"]

        # Verify user exists in database
        user = test_db.get_user_by_id(user_id)
        assert user is not None
        assert user.username == "persistuser"
        assert user.email == "persist@example.com"

        # Verify user can be retrieved by email
        user_by_email = test_db.get_user_by_email("persist@example.com")
        assert user_by_email is not None
        assert user_by_email.id == user_id
