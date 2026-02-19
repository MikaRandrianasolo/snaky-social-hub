# API Requirements Analysis - Snaky Social Hub

## Summary

This document provides a comprehensive analysis of the frontend's API requirements for the Snaky Social Hub project.

## Quick Overview

### Total Endpoints Required: 8

| Category | Count | Status |
|----------|-------|--------|
| Authentication | 4 | ✅ Specified |
| Leaderboard | 2 | ✅ Specified |
| Live Games | 2 | ✅ Specified |

---

## Authentication Requirements

### Endpoints

1. **POST /auth/signup** - Register a new user
   - Input: username, email, password
   - Output: User (id, username, email)
   - Error Handling: Duplicate email (409)

2. **POST /auth/login** - Authenticate user
   - Input: email, password
   - Output: User + JWT token
   - Error Handling: Invalid credentials (401)

3. **POST /auth/logout** - Terminate session
   - Required: Bearer token
   - Output: Success message
   - Error Handling: Not authenticated (401)

4. **GET /auth/me** - Get current user
   - Required: Bearer token
   - Output: User (id, username, email)
   - Error Handling: Not authenticated (401)

### Authentication Method
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <token>`
- **Obtained from**: `/auth/login` or `/auth/signup` endpoints

---

## Leaderboard Requirements

### Endpoints

1. **GET /leaderboard** - Retrieve leaderboard
   - Query params: `mode` (optional: "pass-through" | "walls")
   - Output: Array of LeaderboardEntry (sorted by score desc)
   - Features: Filtering by game mode

2. **POST /leaderboard** - Submit score
   - Required: Bearer token
   - Input: score (integer >= 0), mode ("pass-through" | "walls")
   - Output: LeaderboardEntry
   - Error Handling: Not authenticated (401), Invalid score (400)

### Data Structure

```typescript
LeaderboardEntry {
  id: string (UUID)
  username: string
  score: number
  mode: "pass-through" | "walls"
  date: string (YYYY-MM-DD)
}
```

### Key Features
- Multiple scores per user allowed
- Auto capture of current date
- Automatic sorting by score (highest first)
- Mode-based filtering support

---

## Live Games Requirements

### Endpoints

1. **GET /games** - Retrieve all active games
   - Output: Array of LiveGame
   - No auth required
   - Real-time data

2. **GET /games/{gameId}** - Retrieve specific game
   - Path param: gameId
   - Output: LiveGame or 404 error
   - No auth required

### Data Structure

```typescript
LiveGame {
  id: string
  username: string
  score: number (>= 0)
  mode: "pass-through" | "walls"
  startedAt: string (ISO 8601 datetime)
}
```

### Key Features
- Real-time game monitoring
- Display active player sessions
- Game mode indication
- Timestamp tracking

---

## Shared Data Models

### User
```typescript
{
  id: string (UUID format)
  username: string (1-255 characters)
  email: string (valid email format)
}
```

### Game Modes
- `"pass-through"` - Snake passes through walls
- `"walls"` - Snake collides with walls (game ends)

---

## Error Handling Requirements

All error responses should follow this format:

```json
{
  "error": "Human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "details": {}  // optional
}
```

### Expected HTTP Status Codes
- `200` - Successful GET/POST operations
- `201` - Resource created (POST endpoints)
- `400` - Validation errors
- `401` - Authentication required or invalid credentials
- `404` - Resource not found
- `409` - Resource conflict (e.g., email already exists)

---

## Response Timing Expectations

Based on frontend test code, expected response times:
- Authentication operations: ~500ms
- Leaderboard operations: ~300ms
- Live games retrieval: ~300ms

---

## Security Requirements

1. **Password Security**
   - Minimum 6 characters
   - Should be hashed on server side
   - Never returned in responses

2. **Email Validation**
   - Prevent duplicate registrations
   - Validate email format

3. **JWT Token**
   - Include in Authorization header for protected endpoints
   - Used for authentication on: logout, submit score
   - GET /auth/me requires authentication

4. **Protected Endpoints**
   - POST /auth/logout
   - POST /leaderboard
   - GET /auth/me

5. **Public Endpoints**
   - POST /auth/signup
   - POST /auth/login
   - GET /leaderboard
   - GET /games
   - GET /games/{id}

---

## Frontend Testing Coverage

The frontend has comprehensive tests for all endpoints:

### Test File: `/frontend/src/test/api.test.ts`

**Authentication Tests (6)**
- User registration with validation
- Login with valid credentials
- Rejection of invalid login
- Prevention of duplicate emails
- Logout functionality
- Current user retrieval

**Leaderboard Tests (4)**
- Sorted results (descending by score)
- Mode-based filtering
- Score submission authentication
- Rejection when not logged in

**Live Games Tests (3)**
- List all games
- Retrieve specific game by ID
- Return null for unknown game ID

---

## Implementation Checklist

### Phase 1: Core Setup
- [ ] Choose backend framework (Node.js recommended for parity with frontend)
- [ ] Set up database schema for Users, LeaderboardEntries, LiveGames
- [ ] Implement JWT token generation/validation
- [ ] Set up CORS configuration

### Phase 2: Authentication
- [ ] Implement POST /auth/signup
- [ ] Implement POST /auth/login
- [ ] Implement POST /auth/logout
- [ ] Implement GET /auth/me
- [ ] Add password hashing (bcrypt recommended)

### Phase 3: Leaderboard
- [ ] Implement GET /leaderboard
- [ ] Implement POST /leaderboard
- [ ] Add mode filtering logic
- [ ] Add automatic date capture
- [ ] Ensure proper sorting

### Phase 4: Live Games
- [ ] Implement GET /games
- [ ] Implement GET /games/{gameId}
- [ ] Determine game lifecycle management

### Phase 5: Testing & Deployment
- [ ] Run frontend tests against backend
- [ ] Implement validation for all inputs
- [ ] Set up error logging
- [ ] Deploy and configure production server

---

## Development Notes

1. **Database Schema Considerations**
   - User table with indexed email field
   - LeaderboardEntry table with indexes on score and mode
   - LiveGame table with timestamp indexing
   - Consider TTL for removing old live game entries

2. **API Response Consistency**
   - All responses should be JSON
   - Include appropriate HTTP status codes
   - Maintain consistent error response format

3. **Frontend Integration**
   - Frontend is configured to call `http://localhost:3000/api` in development
   - Token-based auth is required for protected endpoints
   - Frontend tests can be run against the backend during development

4. **Scaling Considerations**
   - Live games may need real-time updates (WebSocket)
   - Leaderboard caching could improve performance
   - Consider pagination for large leaderboards

---

## Files Created

1. **openapi.yaml** - OpenAPI 3.1.0 specification (machine-readable)
2. **API_DOCUMENTATION.md** - Detailed API documentation with examples
3. **API_REQUIREMENTS_ANALYSIS.md** - This file

---

## Next Steps

1. Review the OpenAPI specification in `openapi.yaml`
2. Use API documentation for backend implementation
3. Set up database schema according to data models
4. Implement endpoints in suggested order (Phase 1-5)
5. Run frontend tests against the backend once ready
