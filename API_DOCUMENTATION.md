# Snaky Social Hub - API Documentation

## Overview

This document describes the API requirements for the Snaky Social Hub backend. The API is built according to OpenAPI 3.1.0 specification (see `openapi.yaml`).

## Architecture

### Base URL
- Development: `http://localhost:3000/api`
- Production: `https://api.snaky-social-hub.com/api`

### Authentication
- **Method**: JWT Bearer Token
- **Location**: `Authorization` header
- **Format**: `Authorization: Bearer <token>`
- **Token Source**: Obtained from `/auth/login` or `/auth/signup`

## Endpoints Summary

### Authentication (4 endpoints)

#### POST `/auth/signup`
Create a new user account.

**Request Body:**
```json
{
  "username": "PixelViper",
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "PixelViper",
  "email": "user@example.com"
}
```

**Error Cases:**
- `409 Conflict`: Email already exists
- `400 Bad Request`: Validation errors (invalid email format, missing fields, etc.)

---

#### POST `/auth/login`
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "PixelViper",
    "email": "user@example.com"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Cases:**
- `401 Unauthorized`: Invalid email or password

---

#### POST `/auth/logout`
Logout the current user. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Error Cases:**
- `401 Unauthorized`: Not authenticated

---

#### GET `/auth/me`
Get the current authenticated user's information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "PixelViper",
  "email": "user@example.com"
}
```

**Error Cases:**
- `401 Unauthorized`: Not authenticated

---

### Leaderboard (2 endpoints)

#### GET `/leaderboard`
Get all leaderboard entries, optionally filtered by game mode. Results are sorted by score in descending order.

**Query Parameters:**
- `mode` (optional): Filter by game mode
  - Values: `pass-through`, `walls`
  - Example: `/leaderboard?mode=walls`

**Response (200):**
```json
[
  {
    "id": "1",
    "username": "PixelViper",
    "score": 2450,
    "mode": "walls",
    "date": "2026-02-17"
  },
  {
    "id": "2",
    "username": "NeonByte",
    "score": 2100,
    "mode": "walls",
    "date": "2026-02-16"
  }
]
```

---

#### POST `/leaderboard`
Submit a score to the leaderboard. Requires authentication.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "score": 2450,
  "mode": "walls"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "username": "PixelViper",
  "score": 2450,
  "mode": "walls",
  "date": "2026-02-17"
}
```

**Error Cases:**
- `401 Unauthorized`: Not authenticated
- `400 Bad Request`: Invalid score value (must be >= 0)

---

### Live Games (2 endpoints)

#### GET `/games`
Get all currently active live games.

**Response (200):**
```json
[
  {
    "id": "live1",
    "username": "PixelViper",
    "score": 340,
    "mode": "walls",
    "startedAt": "2026-02-17T14:30:00Z"
  },
  {
    "id": "live2",
    "username": "NeonByte",
    "score": 120,
    "mode": "pass-through",
    "startedAt": "2026-02-17T14:45:00Z"
  }
]
```

---

#### GET `/games/{gameId}`
Get a specific live game by ID.

**Path Parameters:**
- `gameId` (required): The ID of the game to retrieve

**Response (200):**
```json
{
  "id": "live1",
  "username": "PixelViper",
  "score": 340,
  "mode": "walls",
  "startedAt": "2026-02-17T14:30:00Z"
}
```

**Error Cases:**
- `404 Not Found`: Game not found

---

## Data Models

### User
```typescript
{
  id: string (UUID)
  username: string (1-255 chars)
  email: string (valid email)
}
```

### LeaderboardEntry
```typescript
{
  id: string (UUID)
  username: string
  score: number (>= 0)
  mode: "pass-through" | "walls"
  date: string (YYYY-MM-DD format)
}
```

### LiveGame
```typescript
{
  id: string
  username: string
  score: number (>= 0)
  mode: "pass-through" | "walls"
  startedAt: string (ISO 8601 datetime)
}
```

---

## Game Modes

The application supports two game modes:

1. **"pass-through"** - Snake passes through walls
2. **"walls"** - Snake collides with walls and game ends

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "details": {} // optional additional details
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `NOT_AUTHENTICATED` | 401 | User is not logged in |
| `INVALID_CREDENTIALS` | 401 | Email or password is incorrect |
| `EMAIL_DUPLICATE` | 409 | Email already registered |
| `INVALID_INPUT` | 400 | Request validation failed |
| `NOT_FOUND` | 404 | Resource not found |

---

## Implementation Notes

### Session Management
- Authentication uses JWT tokens
- Tokens should be included in the `Authorization` header for protected endpoints
- Tokens are valid for an extended period (recommend 24-7 days)
- Logout invalidates the token on the server side

### Leaderboard
- Entries are ordered by score in descending order (highest first)
- Filtering by mode returns only entries matching that mode
- Scores can be submitted multiple times by the same user
- All scores are recorded with the current date

### Live Games
- Games are dynamically created and monitored
- A game represents an active playing session
- Games should be removed when the player finishes (game over)
- Score updates in live games are real-time

---

## Testing

The frontend includes comprehensive tests covering:
- Authentication (signup, login, logout, user retrieval)
- Leaderboard operations (fetching, filtering, score submission)
- Live games retrieval

See `/frontend/src/test/api.test.ts` for test specifications.

---

## Frontend Integration Points

The frontend expects:
- Immediate response to login/signup (within 500ms typical)
- Leaderboard updates within 300ms
- Live game updates within 300ms
- Proper error messages for validation failures
- JWT tokens to persist session across page reloads

---

## Future Enhancements

Potential features not yet implemented:
- User profile endpoints
- Game history/statistics
- Social features (friends, following)
- Real-time WebSocket updates for live games
- User profile pictures
- Game analytics and statistics
