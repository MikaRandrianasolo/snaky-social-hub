# Snaky Social Hub - Backend API

FastAPI backend for the Snaky Social Hub game platform.

## Setup

### Install Dependencies

Using `uv` (as specified in AGENTS.md):

```bash
uv sync
```

### Run the Server

```bash
uv run python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation at: `http://localhost:8000/docs`

### Run Tests

```bash
uv run pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Mock database layer
│   ├── models.py            # Pydantic models (schemas)
│   ├── security.py          # JWT authentication
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── leaderboard.py   # Leaderboard endpoints
│   │   └── games.py         # Live games endpoints
│   └── dependencies.py      # Dependency injection
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_auth.py         # Auth tests
│   ├── test_leaderboard.py  # Leaderboard tests
│   └── test_games.py        # Games tests
├── pyproject.toml           # Project configuration
└── README.md
```

## Features

- ✅ User authentication with JWT tokens
- ✅ Leaderboard management with game mode filtering
- ✅ Live games tracking
- ✅ Mock database (easily replaceable)
- ✅ Comprehensive test suite
- ✅ CORS support
- ✅ Automatic API documentation (Swagger UI)

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Leaderboard
- `GET /api/leaderboard` - Get leaderboard (filterable by mode)
- `POST /api/leaderboard` - Submit score

### Live Games
- `GET /api/games` - Get all active games
- `GET /api/games/{gameId}` - Get specific game

## Configuration

Default settings:
- Host: `127.0.0.1`
- Port: `8000`
- JWT Secret: (random, can be overridden with env var)
- CORS Origins: `*` (for development)

## Testing

Run all tests:
```bash
uv run pytest tests/
```

Run specific test file:
```bash
uv run pytest tests/test_auth.py -v
```

Run with coverage:
```bash
uv run pytest tests/ --cov=app --cov-report=html
```
