"""
FastAPI main application for Snaky Social Hub.
Run with: uvicorn main:app --reload
"""

import sys
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, leaderboard, games

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Snaky Social Hub API",
    description="API for the Snaky Social Hub game platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Log app startup
@app.on_event("startup")
async def startup_event():
    logger.info("🐍 Snaky Social Hub API is starting up...")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(leaderboard.router)
app.include_router(games.router)

# Serve frontend static files (SPA) from the built `frontend/dist` directory
# Use the container working directory to locate the built frontend: /app/frontend/dist
frontend_dist = Path.cwd() / "frontend" / "dist"
index_file = frontend_dist / "index.html"
if frontend_dist.exists() and index_file.exists():
    # Serve static files (assets) and allow SPA fallback via a wildcard route below
    app.mount("/static", StaticFiles(directory=str(frontend_dist)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        return FileResponse(str(index_file))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        # If the requested file exists in the dist folder, serve it; otherwise return index.html
        candidate = frontend_dist / full_path
        if candidate.exists() and candidate.is_file():
            return FileResponse(str(candidate))
        return FileResponse(str(index_file))
else:
    logger.warning(f"Frontend build not found at {frontend_dist}; root will show API docs")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
