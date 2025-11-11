"""
PDSA Interactive Games - FastAPI Backend
Main application entry point

This file sets up the FastAPI application and registers
all game routes. Individual games will add their routes here.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="PDSA Interactive Games API",
    description="Backend API for Algorithm & Data Structures Game Collection",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent.parent

# Mount static files with correct paths
app.mount("/games", StaticFiles(directory=str(project_root / "games")), name="games")
app.mount("/shared", StaticFiles(directory=str(project_root / "shared" / "frontend")), name="shared_frontend")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify backend is running"""
    return {
        "status": "healthy",
        "message": "PDSA Games Backend is running",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "PDSA Interactive Games API",
        "docs": "/docs",
        "health": "/api/health",
        "games": [
            "eight_queens",
            "snake_ladder", 
            "traffic_simulation",
            "traveling_salesman",
            "tower_hanoi"
        ]
    }

# Game route registration
# Individual game modules will register their routes here

# Example route structure for team members:
"""
# Eight Queens routes (Member 5)
from games.eight_queens.api.queens_routes import router as queens_router
app.include_router(queens_router, prefix="/api/queens", tags=["Eight Queens"])

# Snake Ladder routes (Member 1)
from games.snake_ladder.api.snake_ladder_routes import router as snake_ladder_router
app.include_router(snake_ladder_router, prefix="/api/snake-ladder", tags=["Snake Ladder"])

# Traffic Simulation routes (Member 2)
from games.traffic_simulation.api.traffic_routes import router as traffic_router
app.include_router(traffic_router, prefix="/api/traffic", tags=["Traffic Simulation"])

# Traveling Salesman routes (Member 3)
from games.traveling_salesman.api.tsp_routes import router as tsp_router
app.include_router(tsp_router, prefix="/api/tsp", tags=["Traveling Salesman"])

# Tower of Hanoi routes (Member 4)
from games.tower_hanoi.api.hanoi_routes import router as hanoi_router
app.include_router(hanoi_router, prefix="/api/hanoi", tags=["Tower of Hanoi"])
"""

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "localhost")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print(f"🚀 Starting PDSA Games Backend...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/api/health")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )