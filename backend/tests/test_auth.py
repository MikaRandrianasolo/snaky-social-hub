"""
Tests for authentication endpoints.
"""

import pytest


class TestSignup:
    """Tests for POST /auth/signup"""
    
    def test_signup_success(self, client):
        """Test successful user signup."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data

    def test_signup_duplicate_email(self, client, test_user):
        """Test that duplicate emails are rejected."""
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

    def test_signup_missing_username(self, client):
        """Test signup with missing username."""
        response = client.post(
            "/api/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_signup_missing_email(self, client):
        """Test signup with missing email."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "password": "password123"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_signup_invalid_email(self, client):
        """Test signup with invalid email format."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "password123"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_signup_short_password(self, client):
        """Test signup with password too short."""
        response = client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422  # Validation error


class TestLogin:
    """Tests for POST /auth/login"""
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == test_user["email"]
        assert data["user"]["username"] == test_user["username"]
        assert "token" in data
        assert isinstance(data["token"], str)

    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_missing_email(self, client):
        """Test login without email."""
        response = client.post(
            "/api/auth/login",
            json={"password": "password123"}
        )
        assert response.status_code == 422

    def test_login_missing_password(self, client):
        """Test login without password."""
        response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422


class TestLogout:
    """Tests for POST /auth/logout"""
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert "message" in response.json()

    def test_logout_without_token(self, client):
        """Test logout without authentication token."""
        response = client.post("/api/auth/logout")
        assert response.status_code == 403  # Forbidden - no credentials

    def test_logout_with_invalid_token(self, client):
        """Test logout with invalid token."""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401  # Unauthorized


class TestGetCurrentUser:
    """Tests for GET /auth/me"""
    
    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test getting current user info."""
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user["user"].id
        assert data["username"] == test_user["username"]
        assert data["email"] == test_user["email"]

    def test_get_current_user_without_token(self, client):
        """Test getting current user without token."""
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # Forbidden - no credentials

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401  # Unauthorized


class TestAuthFlow:
    """Integration tests for the auth flow."""
    
    def test_signup_then_login(self, client):
        """Test signing up and then logging in."""
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
        user_id = signup_response.json()["id"]
        
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        
        # Get current user with token
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["id"] == user_id
    
    def test_signup_login_logout_flow(self, client):
        """Test full signup -> login -> logout flow."""
        # Signup
        client.post(
            "/api/auth/signup",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Login
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Verify we can access protected endpoint
        me_response = client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        
        # Logout
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        # In a real app with token blacklisting, the token would be invalid now
        # For this mock implementation, we just verify the endpoint works
