# Backend Implementation Quick Start

## 📋 Overview

This guide provides a quick reference for implementing the Snaky Social Hub backend API based on the specifications defined in this project.

## 📚 Documentation Files

### Primary Resources

1. **openapi.yaml** - Complete OpenAPI 3.1.0 specification
   - Machine-readable API definition
   - All endpoints, request/response schemas
   - Error responses and status codes
   - Security schemes (JWT)
   - **Use for**: Code generation tools, API documentation portals, API testing tools

2. **API_DOCUMENTATION.md** - Detailed human-readable documentation
   - Complete endpoint descriptions with examples
   - Authentication and session management
   - Data model specifications
   - Error codes and handling
   - Implementation notes
   - **Use for**: Understanding requirements, implementation guidance

3. **API_REQUIREMENTS_ANALYSIS.md** - Requirements analysis and checklist
   - Summary of all endpoints
   - Feature breakdown
   - Implementation phases
   - Testing expectations
   - Development notes
   - **Use for**: Planning, prioritization, task tracking

## 🚀 Quick Start

### Step 1: Review the API Spec
Start with **openapi.yaml** to understand the complete API structure.

### Step 2: Understand Requirements
Read **API_DOCUMENTATION.md** for detailed explanations and examples.

### Step 3: Plan Implementation
Use **API_REQUIREMENTS_ANALYSIS.md** as a checklist.

### Step 4: Generate or Build
Choose one of:
- **Option A**: Use OpenAPI code generators (automatically create boilerplate)
  - Tools: openapi-generator, swagger-codegen, protobufs
- **Option B**: Manual implementation following the spec

### Step 5: Test
Use the frontend tests to validate your implementation:
```bash
cd frontend
npm run test
```

## 📋 Endpoint Checklist

### Authentication (4 endpoints)
- [ ] **POST /auth/signup** - Register new user
- [ ] **POST /auth/login** - User authentication
- [ ] **POST /auth/logout** - Session termination
- [ ] **GET /auth/me** - Get current user

### Leaderboard (2 endpoints)
- [ ] **GET /leaderboard** - Retrieve scores (with mode filtering)
- [ ] **POST /leaderboard** - Submit new score

### Live Games (2 endpoints)
- [ ] **GET /games** - List all active games
- [ ] **GET /games/{gameId}** - Get specific game

## 🗄️ Database Schema Outline

```sql
-- Users Table
CREATE TABLE users (
  id UUID PRIMARY KEY,
  username VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leaderboard Entries Table
CREATE TABLE leaderboard_entries (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  username VARCHAR(255) NOT NULL,  -- denormalized for convenience
  score INTEGER NOT NULL DEFAULT 0,
  mode VARCHAR(20) NOT NULL,  -- 'pass-through' or 'walls'
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Live Games Table
CREATE TABLE live_games (
  id VARCHAR(255) PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  username VARCHAR(255) NOT NULL,  -- denormalized for convenience
  score INTEGER NOT NULL DEFAULT 0,
  mode VARCHAR(20) NOT NULL,  -- 'pass-through' or 'walls'
  started_at TIMESTAMP NOT NULL,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_leaderboard_score_desc ON leaderboard_entries(score DESC);
CREATE INDEX idx_leaderboard_mode ON leaderboard_entries(mode);
CREATE INDEX idx_leaderboard_date ON leaderboard_entries(date);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_live_games_started_at ON live_games(started_at);
```

## 🔐 Security Checklist

- [ ] Password hashing (bcrypt recommended, min cost factor 10)
- [ ] JWT token generation (RS256 or HS256)
- [ ] CORS configuration (allow frontend origin)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] Rate limiting on auth endpoints
- [ ] HTTPS in production
- [ ] Secure token storage (httpOnly cookies or secure headers)

## 🧪 Testing Against Frontend

The frontend has 42 passing tests that validate all API functionality:

```bash
# From frontend directory
npm run test  # Run all tests
npm run test:watch  # Run tests in watch mode
```

Key test file: `frontend/src/test/api.test.ts`

## 🔄 Integration Points

### Authentication Flow
1. User signs up → token returned
2. User logs in → token returned
3. Token used for protected endpoints
4. Token sent in `Authorization: Bearer <token>` header

### Expected Response Times
- Auth operations: ~500ms
- Leaderboard: ~300ms
- Live games: ~300ms

## 📱 Frontend Configuration

The frontend is configured to:
- **Development**: `http://localhost:3000/api`
- **Production**: `https://api.snaky-social-hub.com/api`

Update the base URL in `/frontend/src/services/api.ts` when deploying.

## 🛠️ Recommended Tech Stack

- **Framework**: Express.js, Fastify, or similar Node.js framework
- **Database**: PostgreSQL, MongoDB, or MySQL
- **Authentication**: JsonWebToken (jsonwebtoken npm package)
- **Password Hashing**: bcrypt
- **Validation**: joi or zod
- **Testing**: Jest or Vitest

## 📖 Example Implementation Pattern

```typescript
// Example endpoint structure
app.post('/auth/login', async (req, res) => {
  try {
    // 1. Validate input
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({
        error: 'Email and password required',
        code: 'INVALID_INPUT'
      });
    }

    // 2. Find user and verify password
    const user = await User.findByEmail(email);
    if (!user || !await bcrypt.compare(password, user.password_hash)) {
      return res.status(401).json({
        error: 'Invalid email or password',
        code: 'INVALID_CREDENTIALS'
      });
    }

    // 3. Generate token
    const token = jwt.sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '7d' }
    );

    // 4. Return user data and token
    return res.json({
      user: {
        id: user.id,
        username: user.username,
        email: user.email
      },
      token
    });
  } catch (error) {
    return res.status(500).json({
      error: 'Internal server error',
      code: 'INTERNAL_ERROR'
    });
  }
});
```

## 🚄 Development Workflow

1. **Set up project structure**
   - Initialize Node.js project
   - Install dependencies
   - Set up database

2. **Implement in phases** (see API_REQUIREMENTS_ANALYSIS.md)
   - Phase 1: Core setup
   - Phase 2: Authentication
   - Phase 3: Leaderboard
   - Phase 4: Live Games
   - Phase 5: Testing & Deployment

3. **Run frontend tests** after each phase
   - Tests validate integration
   - Quick feedback loop

4. **Deploy**
   - Set production environment variables
   - Configure CORS properly
   - Use HTTPS
   - Set appropriate token expiration

## 📞 Important Details

### JWT Claims (Recommended)
```json
{
  "userId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234654290
}
```

### Validation Rules
- **Username**: 1-255 characters
- **Email**: Valid email format, unique
- **Password**: Minimum 6 characters
- **Score**: Non-negative integer
- **Game Mode**: "pass-through" or "walls" only

### Response Codes Summary
- `200` - Successful GET/request
- `201` - Resource created
- `400` - Bad request/validation error
- `401` - Unauthorized/invalid credentials
- `404` - Not found
- `409` - Conflict (duplicate)
- `500` - Server error

## ✅ Verification Checklist

Before marking complete:
- [ ] All 8 endpoints implemented
- [ ] All tests passing (`npm run test`)
- [ ] Proper error handling for all cases
- [ ] Input validation on all endpoints
- [ ] JWT authentication working
- [ ] CORS configured
- [ ] Database schema implemented
- [ ] Response format matches spec
- [ ] HTTP status codes correct
- [ ] Security best practices followed

## 🎯 Next Steps

1. Choose your technology stack
2. Set up project repository
3. Initialize backend project
4. Create database schema
5. Implement Phase 1 (Core setup)
6. Test each endpoint as implemented
7. Repeat for Phases 2-5

---

**Need help?** Refer to the detailed documentation files:
- `openapi.yaml` - Technical specification
- `API_DOCUMENTATION.md` - Implementation guide
- `API_REQUIREMENTS_ANALYSIS.md` - Requirements breakdown
