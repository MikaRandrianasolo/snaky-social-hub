# Deploying Snaky Social Hub to Render

## Prerequisites

1. **GitHub Account** - Repository with code pushed
2. **Render Account** - Sign up at https://render.com (free tier available)

---

## Step 1: Prepare Your Repository

✅ Already done! Your code needs:
- ✅ `Dockerfile` in root (already created)
- ✅ `.env.example` (already exists)
- ✅ `render.yaml` (already created)

Push any uncommitted changes:
```bash
git add -A
git commit -m "chore: Add Render deployment configuration"
git push origin main
```

---

## Step 2: Create Render Account & Connect GitHub

1. Go to https://render.com
2. Click **"Sign up"** → Choose "GitHub"
3. Authorize Render to access your GitHub repositories
4. You'll be redirected to Render dashboard

---

## Step 3: Deploy Using render.yaml (Recommended)

This automatically deploys both the web service and database:

1. In Render dashboard, click **"New +"** → **"Blueprint"**
2. Enter repository URL: `https://github.com/YOUR_USERNAME/snaky-social-hub`
3. Click **"Connect"**
4. Render will automatically detect `render.yaml`
5. Review the services:
   - **snaky-app** (Web service using your Dockerfile)
   - **snaky-db** (PostgreSQL database)
6. Click **"Deploy"**

**Deployment takes ~3-5 minutes**

---

## Step 4: Configure Environment Variables (if needed)

The `render.yaml` automatically configures `DATABASE_URL` from the database. If you need additional variables:

1. Go to your deployed service in Render dashboard
2. Click **"Environment"** tab
3. Add any additional variables needed by your backend

**Note:** The `DATABASE_URL` is automatically injected from the PostgreSQL database service.

---

## Step 5: Verify Deployment

Once the service is deployed (green "Running" badge):

1. Click the service name → **"Logs"** tab to see startup logs
2. Your app URL: `https://snaky-app.onrender.com` (or custom domain)
3. Test the application:
   - Frontend: `https://snaky-app.onrender.com`
   - API Docs: `https://snaky-app.onrender.com/docs`
   - API: `https://snaky-app.onrender.com/api`

---

## Step 6: Set Up Auto-Deployment

Your code is **already configured for auto-deploy** in `render.yaml`:
```yaml
autoDeploy: true
```

This means:
- Every `git push` to `main` automatically redeploys your app
- No need to manually trigger deployments
- View deployment history in Render dashboard

---

## Alternative: Deploy Without render.yaml (Manual)

If you prefer to manually create services:

### Create Web Service:
1. Click **"New +"** → **"Web Service"**
2. Select your repository
3. Configure:
   - **Name:** `snaky-app`
   - **Region:** Oregon (or closest to you)
   - **Runtime:** Docker
   - **Build Command:** (leave empty - Dockerfile is used)
   - **Start Command:** (leave empty - Dockerfile handles it)
4. Click **"Create Web Service"**

### Create PostgreSQL Database:
1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `snaky-db`
   - **Region:** Same as web service
   - **Database:** `snaky_db`
   - **User:** `snaky_user`
3. Click **"Create Database"**

### Link Database to Web Service:
1. Go to **snaky-app** service
2. Click **"Environment"**
3. Add variable:
   - **Key:** `DATABASE_URL`
   - **Value:** (copy from snaky-db service's Connection String)
4. Redeploy service

---

## Useful Render Command Line

Install Render CLI for advanced automation:
```bash
npm install -g @render-oss/render-cli

# Login
render login

# Deploy from CLI
render deploy --repo YOUR_GITHUB_REPO
```

---

## Custom Domain Setup

Want `snake-game.com` instead of `.onrender.com`?

1. In Render dashboard, go to your service
2. Click **"Settings"** → **"Custom Domain"**
3. Follow DNS instructions for your domain provider
4. Takes ~5 minutes to propagate

---

## Troubleshooting

### Deployment stuck/failing?
1. Check **Logs** tab for errors
2. Common issues:
   - Database connection timeout → Check `DATABASE_URL` is set
   - Port issues → Ensure app listens on `80` (Render requirement)
   - Build errors → Run `docker build -t test .` locally to debug

### App crashes after deployment?
```bash
# Check logs
Click service → Logs tab → Search for errors
```

### Database not connecting?
1. Verify `DATABASE_URL` environment variable exists
2. Check PostgreSQL service is running (green status)
3. Restart the web service from dashboard

---

## Monitoring & Logs

### View Live Logs:
- Dashboard → Select service → **Logs** tab
- Shows real-time output from your app

### View Metrics:
- Dashboard → Select service → **Metrics** tab
- CPU, Memory, Network usage

### Set Up Alerts:
- Dashboard → **Notifications** 
- Get alerted on deployment failures or service issues

---

## Pricing

- **Starter Web Service:** $7/month (after free tier)
- **PostgreSQL Database:** $15/month
- **Total:** ~$22/month for production

**Free tier includes:**
- 750 runtime hours/month (free tier services)
- 100 GB database storage (shared)
- Up to 5 services

---

## Next Steps

1. ✅ Code pushed to GitHub
2. ⏳ Create Render account
3. ⏳ Deploy using render.yaml
4. ⏳ Test deployed application
5. ⏳ Set up custom domain (optional)
6. ⏳ Monitor performance

**Questions?** See [Render Docs](https://render.com/docs)
