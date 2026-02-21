# Development Guide

This guide shows you how to run and develop the Snaky Social Hub application.

## Quick Start

### Run Everything at Once 
The easiest way to get started is to run both the frontend and backend simultaneously using `concurrently`:

```bash
make dev
```

This will:
- Start the frontend development server on http://localhost:8080
- Start the backend API server on http://localhost:8000
- Show output from both in a single terminal with color-coded prefixes
- Automatically restart both services when you make code changes

### Using npm instead of make

If you prefer to use npm directly from the frontend directory:

```bash
cd frontend
npm run dev:all
```

## Individual Server Commands

### Run Frontend Only
```bash
make dev-frontend
# or
cd frontend && npm run dev
```

Frontend runs on: http://localhost:8080

### Run Backend Only
```bash
make dev-backend
# or
cd backend && make dev
```

Backend runs on: http://localhost:8000

## Testing

### Test Everything (Frontend + Backend)
```bash
make test
```

### Test Frontend Only
```bash
make test-frontend
# or
cd frontend && npm test
```

### Test Backend Only
```bash
make test-backend
# or
cd backend && make test
```

### Frontend Tests with Watch Mode
Continuously re-run tests as files change:

```bash
make test-watch
# or
cd frontend && npm run test:watch
```

## Code Quality

### Lint Code
```bash
make lint
```

Runs:
- Frontend: ESLint
- Backend: pylint

### Format Code
```bash
make format
```

Formats:
- Frontend: (not configured)
- Backend: black

## Available URLs

When running with `make dev`:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:8080 |
| **Backend API** | http://localhost:8000 |
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **API Root** | http://localhost:8000/ |

## Project Information

View detailed project info:

```bash
make info
```

Shows:
- Frontend & backend paths
- Port numbers
- Database info
- All available API endpoints

## Cleanup & Reset

### Clean Build Artifacts
Remove all build files and cache:

```bash
make clean
```

### Fresh Install
Clean everything and reinstall all dependencies:

```bash
make reset
```

This runs `make clean install` which:
- Removes node_modules, dist, build directories
- Removes Python cache and venv
- Reinstalls all dependencies fresh

## Backend Makefile Commands

The backend has its own Makefile with additional commands:

```bash
cd backend
make help  # See all backend commands
```

### Backend-Specific Commands

```bash
make dev              # Run with hot reload
make dev-quiet        # Run with minimal output
make test             # Run all tests
make test-watch       # Run tests in watch mode
make test-coverage    # Generate coverage report
make lint             # Check code quality
make format           # Auto-format code
make format-check     # Check formatting without changes
make clean            # Clean cache and temp files
make db-reset         # Reset database
make info             # Show endpoint information
```

## File Structure

```
snaky-social-hub/
├── Makefile              # Root Makefile (full-stack commands)
├── frontend/
│   ├── Makefile         # (not needed, uses npm scripts)
│   ├── package.json     # npm scripts with concurrently
│   ├── src/
│   │   ├── services/api.ts  # API integration
│   │   ├── hooks/useAuth.tsx
│   │   └── ...
│   └── ...
└── backend/
    ├── Makefile         # Backend-specific commands
    ├── main.py          # FastAPI app entry point
    ├── app/
    │   ├── models.py
    │   ├── database.py
    │   ├── security.py
    │   └── routers/
    └── ...
```

## Typical Development Workflow

1. **Start the full stack:**
   ```bash
   make dev
   ```
   
2. **Open the app in your browser:**
   - Frontend: http://localhost:8080
   - API Docs: http://localhost:8000/docs

3. **Make changes:**
   - Edit frontend code → Hot reload at :8080
   - Edit backend code → Auto-restart at :8000

4. **Run tests when you're done:**
   ```bash
   make test
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

## Troubleshooting

### Port Already in Use

If you get "Address already in use" error:

```bash
# Kill all node processes
pkill -f "node"

# Kill all Python uvicorn processes
pkill -f "uvicorn"

# Then try again
make dev
```

### Check Server Status
```bash
make status
```

This curl-checks both servers and shows if they're running.

### Dependencies Out of Sync

If you're getting dependency errors:

```bash
make reset  # Clean install everything
make dev    # Try again
```

## Environment Variables

Currently, the development setup uses:

**Frontend:**
- `VITE_API_BASE_URL` - Optional (defaults to http://localhost:8000/api)

**Backend:**
- `DATABASE_URL` - Optional (using in-memory mock DB by default)
- Defaults work fine for local development

### Persisting leaderboard (SQLite)

By default the backend uses the in-memory mock DB so scores are lost on restart. To persist scores between restarts during development, run the backend with a SQLite file-backed database:

```bash
# from the repo root
cd backend
make dev-persistent
# or explicitly:
DATABASE_URL=sqlite:///./snaky_dev.db uv run python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This creates `./snaky_dev.db` in the `backend` folder and will persist leaderboard entries and users.

## Production

When you're ready for production:

```bash
# Build frontend
cd frontend && npm run build

# Build/deploy backend
cd backend
# Use your deployment method (Docker, gunicorn, etc.)
```

## Next Steps

1. Review the code in `frontend/src/services/api.ts` to understand the API integration
2. Check `backend/main.py` to understand the FastAPI setup
3. Read the OpenAPI spec at `/openapi.yaml` for endpoint documentation
4. See `INTEGRATION_STATUS.md` for more integration details
