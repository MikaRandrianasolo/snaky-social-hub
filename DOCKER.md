# Snaky Social Hub - Docker Setup

This project uses Docker Compose to run the entire application stack with PostgreSQL, FastAPI backend, and Nginx frontend.

## Prerequisites

- Docker Desktop (or Docker + Docker Compose)
- At least 2GB available RAM
- Port 80, 5432, and 8000 available on your system

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd snaky-social-hub

# Copy example environment file and configure if needed
cp .env.example .env
```

### 2. Build and Start Services

```bash
# Build all containers and start services
docker-compose up -d

# Or with verbose output
docker-compose up

# Build without cache (useful if dependencies changed)
docker-compose build --no-cache && docker-compose up -d
```

### 3. Verify Services Are Running

```bash
# Check all services
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## Accessing the Application

- **Frontend**: http://localhost/ (or http://localhost:80)
- **Backend API**: http://localhost/api/
- **API Documentation**: http://localhost/docs (Swagger UI)
- **API ReDoc**: http://localhost/redoc
- **PostgreSQL**: localhost:5432

Default credentials (defined in `.env`):
- Database User: `snaky_user`
- Database Password: `snaky_password`
- Database Name: `snaky_db`

## Common Commands

### Development

```bash
# Start in development mode
docker-compose up -d

# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove all data (including database)
docker-compose down -v

# Rebuild a specific service
docker-compose build backend
docker-compose build frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Follow logs for multiple services
docker-compose logs -f backend postgres
```

### Database Access

```bash
# Connect to PostgreSQL using psql
docker-compose exec postgres psql -U snaky_user -d snaky_db

# Or with password prompt
PGPASSWORD=snaky_password docker-compose exec postgres psql -U snaky_user -d snaky_db
```

### Backend Access

```bash
# Run commands in backend container
docker-compose exec backend uv run pytest tests/

# Run integration tests with PostgreSQL
docker-compose exec backend uv run pytest tests_integration/

# Open backend shell
docker-compose exec backend /bin/bash
```

## Architecture

```
┌─────────────────────────────────────────┐
│           User's Browser                │
└────────────────┬────────────────────────┘
                 │ HTTP/HTTPS
┌────────────────▼──────────────────────────────┐
│            Nginx (Frontend)                   │
│  - Serves React SPA                           │
│  - Proxies /api/* to backend                  │
│  - Proxies /docs, /redoc to backend           │
└────────────────┬──────────────────────────────┘
                 │ HTTP
┌────────────────▼──────────────────────────┐
│       FastAPI Backend (Python)            │
│  - REST API endpoints                     │
│  - Authentication & JWT tokens            │
│  - Game leaderboard management            │
└────────────────┬──────────────────────────┘
                 │ SQL Over TCP
┌────────────────▼──────────────────────────┐
│      PostgreSQL Database                  │
│  - Users table                            │
│  - Leaderboard entries                    │
│  - Live games tracking                    │
└──────────────────────────────────────────┘
```

## Environment Variables

See `.env.example` for all available options. Key variables:

- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_DB`: Database name
- `ENV IRONMENT`: Set to `production` for production deployments
- `BACKEND_PORT`: Backend service port (internal)
- `FRONTEND_PORT`: Frontend service port (external)

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 80
sudo lsof -i :80
sudo kill -9 <PID>

# Or use a different port in .env
FRONTEND_PORT=8080
```

### Database Connection Refused

```bash
# Ensure postgres service is healthy
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Backend Can't Connect to Database

```bash
# Check network
docker network ls
docker network inspect <snaky-network-name>

# Verify DNS resolution
docker-compose exec backend nslookup postgres

# Check backend logs
docker-compose logs -f backend
```

### Rebuild Everything Fresh

```bash
# Remove all containers, volumes, networks
docker-compose down -v

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d
```

## Performance Tips

- Use named volumes for PostgreSQL data persistence
- Enable gzip compression in Nginx (already configured)
- Set appropriate limits in docker-compose.yml

## Security Notes

- **Development Only**: The `.env` file contains example credentials. Change them in production.
- **CORS**: Currently set to allow all origins. Restrict in production.
- **Database Password**: Use strong, randomly-generated passwords in production
- **SSL/TLS**: Consider adding SSL certificates in production

See the main README.md for more information about the application.
