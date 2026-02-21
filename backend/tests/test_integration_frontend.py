from fastapi.testclient import TestClient
from main import app
import app.database as database


def test_signup_login_submit_and_leaderboard_workflow(client):
    # Use the provided `client` fixture which sets up a fresh mock DB

    # Signup
    signup_resp = client.post("/api/auth/signup", json={
        "username": "testplayer",
        "email": "testplayer@example.com",
        "password": "password123"
    })
    assert signup_resp.status_code == 201
    data = signup_resp.json()
    assert data["username"] == "testplayer"
    assert data["email"] == "testplayer@example.com"

    # Login
    login_resp = client.post("/api/auth/login", json={
        "email": "testplayer@example.com",
        "password": "password123"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}

    # Submit a score
    submit_resp = client.post("/api/leaderboard", json={"score": 500, "mode": "walls"}, headers=headers)
    assert submit_resp.status_code == 201
    entry = submit_resp.json()
    assert entry["username"] == "testplayer"
    assert entry["score"] == 500

    # Fetch leaderboard and ensure our entry is present
    lb_resp = client.get("/api/leaderboard")
    assert lb_resp.status_code == 200
    entries = lb_resp.json()
    usernames = [e["username"] for e in entries]
    assert "testplayer" in usernames
