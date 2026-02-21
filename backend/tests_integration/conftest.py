"""
Integration test configuration and fixtures using SQLite.
"""

import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.database import SQLDatabase
from app.security import hash_password


@pytest.fixture(scope="function")
def test_db():
    """Provide a fresh SQLite database for each integration test."""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    
    database_url = f"sqlite:///{db_path}"
    db = SQLDatabase(database_url)
    
    yield db
    
    # Clean up - close the session and delete the database file
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def client(test_db):
    """Provide a test client with a fresh SQLite database."""
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
    
    yield TestClient(app)

    # Restore original db instances
    database_module.db = original_db
    if original_deps_db is not None:
        dependencies_module.db = original_deps_db


@pytest.fixture
def test_user(test_db):
    """Create a test user and return both user object and clear password."""
    password = "testpass123"
    user = test_db.create_user(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password(password)
    )
    return {"id": user.id, "username": user.username, "email": user.email, "password": password}


@pytest.fixture
def test_user_2(test_db):
    """Create a second test user for multi-user scenarios."""
    password = "anotherpass456"
    user = test_db.create_user(
        username="testuser2",
        email="test2@example.com",
        password_hash=hash_password(password)
    )
    return {"id": user.id, "username": user.username, "email": user.email, "password": password}


@pytest.fixture
def auth_token(client, test_user):
    """Get an authentication token for the test user."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    return data["token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers with a valid token."""
    return {"Authorization": f"Bearer {auth_token}"}
