"""
FastAPI main application for Snaky Social Hub.
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, leaderboard, games

app = FastAPI(
    title="Snaky Social Hub API",
    description="API for the Snaky Social Hub game platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

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


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with welcome message and links to documentation."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Snaky Social Hub API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
            h1 {
                color: #667eea;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }
            .info {
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border-left: 4px solid #667eea;
            }
            .endpoints {
                margin: 30px 0;
            }
            .endpoint-group {
                margin-bottom: 25px;
            }
            .group-title {
                font-size: 16px;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
                text-transform: uppercase;
                font-size: 14px;
            }
            .endpoint {
                background: #f9f9f9;
                padding: 10px 15px;
                margin-bottom: 8px;
                border-radius: 4px;
                border-left: 3px solid #764ba2;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
            .method {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 3px;
                margin-right: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            .post { background: #17a2b8; color: white; }
            .get { background: #28a745; color: white; }
            .links {
                display: flex;
                gap: 15px;
                margin-top: 30px;
                flex-wrap: wrap;
                justify-content: center;
            }
            .btn {
                display: inline-block;
                padding: 12px 24px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
                transition: all 0.3s ease;
                border: 2px solid #667eea;
                color: #667eea;
                background: white;
            }
            .btn:hover {
                background: #667eea;
                color: white;
                transform: translateY(-2px);
            }
            .btn.primary {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
            .btn.primary:hover {
                background: #764ba2;
                border-color: #764ba2;
            }
            code {
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                color: #d73a49;
            }
            .footer {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #999;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐍 Snaky Social Hub API</h1>
            <p class="subtitle">Backend API for the Snaky Social Hub game platform</p>
            
            <div class="info">
                <strong>✅ Server Status:</strong> Running and ready to accept requests
            </div>

            <div class="endpoints">
                <div class="endpoint-group">
                    <div class="group-title">🔐 Authentication</div>
                    <div class="endpoint"><span class="method post">POST</span> /api/auth/signup</div>
                    <div class="endpoint"><span class="method post">POST</span> /api/auth/login</div>
                    <div class="endpoint"><span class="method post">POST</span> /api/auth/logout</div>
                    <div class="endpoint"><span class="method get">GET</span> /api/auth/me</div>
                </div>

                <div class="endpoint-group">
                    <div class="group-title">🏆 Leaderboard</div>
                    <div class="endpoint"><span class="method get">GET</span> /api/leaderboard</div>
                    <div class="endpoint"><span class="method post">POST</span> /api/leaderboard</div>
                </div>

                <div class="endpoint-group">
                    <div class="group-title">🎮 Live Games</div>
                    <div class="endpoint"><span class="method get">GET</span> /api/games</div>
                    <div class="endpoint"><span class="method get">GET</span> /api/games/{gameId}</div>
                </div>

                <div class="endpoint-group">
                    <div class="group-title">💚 Health Check</div>
                    <div class="endpoint"><span class="method get">GET</span> /health</div>
                </div>
            </div>

            <div class="links">
                <a href="/docs" class="btn primary">📚 Interactive API Docs (Swagger UI)</a>
                <a href="/redoc" class="btn">📖 API Documentation (ReDoc)</a>
                <a href="/openapi.json" class="btn">📋 OpenAPI Schema</a>
            </div>

            <div class="footer">
                <p>Snaky Social Hub © 2026 | Version 1.0.0</p>
                <p>Built with FastAPI • Powered by Python</p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
