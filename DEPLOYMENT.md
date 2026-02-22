# Cloud Deployment Guide for Snaky Social Hub

## Unified Container Overview

Your application is now packaged as a single Docker container that includes:
- **Frontend**: React/Vite app served by Nginx
- **Backend**: FastAPI Python application  
- **Nginx**: Reverse proxy that routes requests appropriately

**To build and run locally:**
```bash
docker compose -f docker-compose.unified.yml up --build
```

This starts both the application container and PostgreSQL database.

---

## Cloud Deployment Options

### Option 1: **Docker Cloud (Recommended for Simplicity)**

**Docker Hub Container Registry**
- Push image to Docker Hub
- Run anywhere Docker is available
- No vendor lock-in

```bash
# Build and tag image
docker build -t yourusername/snaky-app:latest .

# Push to Docker Hub
docker push yourusername/snaky-app:latest

# Deploy with Docker CLI or Docker Desktop Cloud
```

---

### Option 2: **Google Cloud Run (Serverless - Fast & Easy)**

**Pros:**
- No server management
- Pay only for what you use
- Auto-scaling
- Fast deployment time (2-5 minutes)

**Cons:**
- Must be stateless between requests
- Limited to 3600s max request duration
- More expensive at scale

**Setup:**
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login

# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/snaky-app

# Deploy to Cloud Run
gcloud run deploy snaky-app \
  --image gcr.io/PROJECT_ID/snaky-app \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars DATABASE_URL=postgresql://... \
  --allow-unauthenticated
```

**Database:** Use Cloud SQL (managed PostgreSQL)

---

### Option 3: **AWS (Multiple Options)**

#### 3a. **ECS (Elastic Container Service) + RDS** - Recommended
**Pros:**
- Industry standard
- Full control
- Mature ecosystem
- Good load balancing

```bash
# Push to ECR (Elastic Container Registry)
aws ecr get-login-password --region us-east-1 | docker login -u AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag snaky-app:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/snaky-app:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/snaky-app:latest

# Then deploy via ECS Console or Fargate
```

#### 3b. **Elastic Beanstalk**
**Pros:**
- Simplest AWS option
- Automatic scaling
- CI/CD integration

```bash
eb init -p docker snaky-social-hub --region us-east-1
eb create snaky-env
eb deploy
```

#### 3c. **Lightsail**
**Pros:**
- Cheapest option
- Predictable pricing
- Simple management

---

### Option 4: **Azure (App Service)**

**Pros:**
- Good Windows/Linux balance
- Tight Azure ecosystem integration
- Good for Microsoft shops

```bash
# Login to Azure
az login

# Create Container Registry
az acr create --resource-group myResourceGroup --name snaky --sku Basic

# Build and push
az acr build --registry snaky --image snaky-app:latest .

# Create App Service
az appservice plan create --name snaky-plan --resource-group myResourceGroup --sku B1 --is-linux

az webapp create --name snaky-app --plan snaky-plan --resource-group myResourceGroup --deployment-container-image-name snaky.azurecr.io/snaky-app:latest
```

---

### Option 5: **Railway.app (Developer Friendly)**

**Pros:**
- GitHub integration (auto-deploy on push)
- First $5/month free
- Simple environment setup
- Database included

**Setup:**
1. Push code to GitHub
2. Connect GitHub to Railway.app
3. Select this repository
4. Railway auto-builds and deploys
5. Set `DATABASE_URL` environment variable

**Cost:** ~$5-10/month per service

---

### Option 6: **Render (Modern Alternative)**

**Pros:**
- Simple deployment from GitHub
- Free tier available
- Automatic SSL
- Built-in PostgreSQL option

**Setup:**
1. Connect GitHub repository
2. Create new Web Service
3. Select Docker
4. Deploy

**Cost:** $12/month for starter instance

---

### Option 7: **DigitalOcean App Platform**

**Pros:**
- Predictable pricing ($5-12/month)
- Simple git integration
- Managed PostgreSQL available
- Good for small projects

**Setup:**
```bash
# Install doctl CLI
brew install doctl

doctl auth init

# Create app from docker-compose
doctl apps create --spec docker-compose.unified.yml
```

---

### Option 8: **Self-hosted on VPS**

**Services:**
- DigitalOcean Droplet ($6/month)
- Linode ($5/month)
- Vultr ($5/month)
- AWS EC2

**Setup:**
```bash
# SSH into server
ssh root@your_server_ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Pull and run
docker run -d \
  --name snaky \
  -p 80:80 \
  -e DATABASE_URL=postgresql://... \
  yourusername/snaky-app:latest

# Use Nginx/Let's Encrypt for HTTPS
apt install certbot python3-certbot-nginx
```

**Benefits:** Full control, cheapest option
**Cons:** Requires servers management

---

## Recommended Deployment Path

### **Development/Testing:**
```bash
docker compose -f docker-compose.unified.yml up
```

### **For Production:**

**Quick & Easy (Recommended for MVP):**
→ **Railway.app** or **Render** (push to GitHub, auto-deploys)

**Corporate/Serious Project:**
→ **AWS ECS + RDS** or **Google Cloud Run + Cloud SQL**

**Lowest Cost:**
→ **DigitalOcean Droplet** with Docker + managed PostgreSQL

**Most Scalable:**
→ **Kubernetes (EKS, GKE)** - requires more setup

---

## Environment Variables for Production

You'll need these in your cloud deployment:
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
ENVIRONMENT=production
# Add any other backend config needed
```

## HTTPS/SSL

Most cloud providers handle this automatically. For self-hosted, use:
- Let's Encrypt (free)
- Certbot + Nginx
- Or use Cloudflare as reverse proxy

---

## Next Steps

1. **Choose a platform** based on your needs
2. **Create database** (or use cloud-managed option)
3. **Set environment variables** for database access
4. **Push container image** to registry
5. **Deploy** and test
6. **Monitor** logs and performance

Would you like help with a specific deployment platform?
