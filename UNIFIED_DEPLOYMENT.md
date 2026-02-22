# Unified Container Deployment Guide

## Summary

Your Snaky Social Hub is now packaged as a **single Docker container** that includes:
- ✅ Frontend (React/Vite) - served by Nginx
- ✅ Backend (FastAPI) - running on localhost:8000  
- ✅ Nginx reverse proxy - serves frontend and proxies API requests
- ✅ Both services managed by Supervisor

**Image size:** ~448MB

---

## Quick Start - Local Development

### Using the unified docker-compose.yml:

```bash
# Build and start (includes PostgreSQL database)
docker compose -f docker-compose.unified.yml up --build

# On first run, initialize your database:
docker exec snaky-app python -m app.models  # or your migration command

# Access the application:
# Frontend: http://localhost
# Backend API: http://localhost/api
# API Docs: http://localhost/docs
```

---

## File Structure

**New files created:**

| File | Purpose |
|------|---------|
| [Dockerfile](Dockerfile) | Unified multi-stage build (frontend + backend) |
| [docker-compose.unified.yml](docker-compose.unified.yml) | Compose config for unified container |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Complete cloud deployment options |

**Original files (unchanged, still available):**
- `docker-compose.yml` - Original multi-container setup (dev mode)
- `backend/Dockerfile` - Backend-only image
- `frontend/Dockerfile` - Frontend-only image

---

## Build Locally

```bash
# Build the image
docker build -t snaky-app:latest .

# Run with external database
docker run -d \
  --name snaky-app \
  -p 80:80 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/snaky_db \
  snaky-app:latest
```

---

## Architecture

```
┌─────────────────────────────┐
│      Docker Container       │
├─────────────────────────────┤
│      Supervisor (PID 1)      │
├─────────────────────────────┤
│  ┌─────────┐  ┌───────────┐ │
│  │  Nginx  │  │  FastAPI  │ │
│  │ :80     │  │ :8000     │ │
│  └────┬────┘  └─────┬─────┘ │
│       │              │       │
│  Reverse Proxy & Static Files
│       │              │       │
└───────┼──────────────┼───────┘
        │              │
        └──────────────┘
       Port 80 (exposed)
```

---

## Next Steps

### For Local Testing:
```bash
docker compose -f docker-compose.unified.yml up --build
```

### For Production Deployment:
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on:
- **Google Cloud Run** (serverless, $0-5/month)
- **AWS ECS/Fargate** (scalable, $10-50/month) 
- **Azure App Service** (enterprise, $5-20/month)
- **Railway.app** (GitHub auto-deploy, ~$10/month)
- **DigitalOcean Droplet** (VPS, $5-10/month)
- **Self-hosted** (cheapest, requires management)

---

## Environment Variables

Required when deploying:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
ENVIRONMENT=production
```

---

## Pushing to Container Registry

### Docker Hub (simplest):
```bash
docker login
docker tag snaky-app:latest yourusername/snaky-app:latest
docker push yourusername/snaky-app:latest
```

### Google Container Registry:
```bash
docker tag snaky-app:latest gcr.io/PROJECT_ID/snaky-app:latest
docker push gcr.io/PROJECT_ID/snaky-app:latest
```

### AWS ECR:
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag snaky-app:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/snaky-app:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/snaky-app:latest
```

---

## Troubleshooting

### Logs from container:
```bash
docker logs snaky-app
# Or for supervisor logs:
docker exec snaky-app tail -f /var/log/supervisor/supervisord.log
```

### Test if services are running:
```bash
docker exec snaky-app curl http://localhost/docs  # API Docs
docker exec snaky-app ps aux  # See all processes
```

### Database connection issues:
```bash
# Check if database URL is set
docker exec snaky-app echo $DATABASE_URL

# Test database connection
docker exec snaky-app python -c "from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL')); connection = engine.connect()"
```

---

## FAQ

**Q: Can I still use the old multi-container setup?**  
A: Yes! The original `docker-compose.yml` and individual Dockerfiles are unchanged.

**Q: Why Supervisor instead of separate containers?**  
A: Easier deployment to managed container services (Cloud Run, App Service, etc.)

**Q: Is this production-ready?**  
A: Yes, but you should add:
- Health checks
- Logging aggregation
- Database backups
- HTTPS/SSL certificates
- Monitoring and alerting

**Q: Can I separate backend/frontend later?**  
A: Yes, just use the original Dockerfiles again.

---

## Performance Notes

- **Startup time:** ~10-15 seconds (first boot slower)
- **Container size:** 448MB (Node + Python dependencies)
- **Available services:** Frontend @ /, Backend @ /api, Docs @ /docs
- **Scaling:** For horizontal scaling, use Kubernetes or container orchestration

---

## Monitoring

Once deployed, monitor:
- CPU/Memory usage
- Request latency
- Error rates
- Database performance
- Log files

Most cloud platforms provide dashboards built-in.

---

For detailed deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md)
