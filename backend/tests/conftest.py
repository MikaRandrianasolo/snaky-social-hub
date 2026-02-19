"""
Test configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from app.database import MockDatabase
from app.security import hash_password


@pytest.fixture
def test_db():
    """Provide a fresh mock database for each test."""
    # Create a new database instance for testing
    return MockDatabase()


@pytest.fixture
def client(test_db):
    """Provide a test client with a fresh database."""
    import app.database as database_module
    import app.dependencies as dependencies_module
    from main import app
    
    # Store the original db references
    original_db = database_module.db
    original_deps_db = dependencies_module.db if hasattr(dependencies_module, 'db') else None
    
    # Replace with test db in all modules
    database_module.db = test_db
    if original_deps_db is not None:
        dependencies_module.db = test_db
    
    # Also patch in routers
    import app.routers.auth as auth_module
    import app.routers.leaderboard as leaderboard_module
    import app.routers.games as games_module
    
    original_auth_db = auth_module.db
    original_leaderboard_db = leaderboard_module.db
    original_games_db = games_module.db
    
    auth_module.db = test_db
    leaderboard_module.db = test_db
    games_module.db = test_db
    
    yield TestClient(app)
    
    # Restore original db instances
    database_module.db = original_db
    if original_deps_db is not None:
        dependencies_module.db = original_deps_db
    auth_module.db = original_auth_db
    leaderboard_module.db = original_leaderboard_db
    games_module.db = original_games_db


@pytest.fixture
def test_user(test_db):
    """Create a test user and return both user object and clear password."""
    password = "testpass123"
    user = test_db.create_user(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password(password)
    )
    return {
        "user": user,
        "email": user.email,
        "password": password,
        "username": user.username
    }


@pytest.fixture
def logged_in_token(client, test_user):
    """Get an authentication token for a test user."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["token"]


@pytest.fixture
def auth_headers(logged_in_token):
    """Return authorization headers with valid token."""
    return {"Authorization": f"Bearer {logged_in_token}"}
