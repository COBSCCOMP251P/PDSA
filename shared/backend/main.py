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

# Import game routes
try:
    from games.eight_queens.api.routes import router as eight_queens_router
    app.include_router(eight_queens_router)
except ImportError:
    print("Warning: Eight Queens routes not found. Game may not be fully functional.")

# Mount static files with correct paths
app.mount("/games", StaticFiles(directory=str(project_root / "games")), name="games")
# Mount static files
app.mount("/shared", StaticFiles(directory=project_root / "shared" / "frontend"), name="shared")
app.mount("/games/eight_queens/frontend", StaticFiles(directory=project_root / "games" / "eight_queens" / "frontend"), name="eight_queens_frontend")

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

# Eight Queens routes (Member 5) - Original and simple gaming version
try:
    from games.eight_queens.api.routes import router as eight_queens_router
    from games.eight_queens.api.simple_gaming_routes import router as eight_queens_gaming_router
    app.include_router(eight_queens_router)
    app.include_router(eight_queens_gaming_router)
    print("✅ Eight Queens routes loaded (original + simple gaming)")
except ImportError as e:
    print(f"⚠️  Eight Queens routes not found: {e}")

# Snake Ladder routes (Member 1)
try:
    from games.snake_ladder.api.routes import router as snake_ladder_router
    app.include_router(snake_ladder_router, prefix="/api/snake-ladder", tags=["Snake Ladder"])
    print("✅ Snake Ladder routes loaded")
except ImportError:
    print("⚠️  Snake Ladder routes not implemented yet")

# Traffic Simulation routes (Member 2)
try:
    from games.traffic_simulation.api.routes import router as traffic_router
    app.include_router(traffic_router, prefix="/api/traffic", tags=["Traffic Simulation"])
    print("✅ Traffic Simulation routes loaded")
except ImportError:
    print("⚠️  Traffic Simulation routes not implemented yet")

# Traveling Salesman routes (Member 3)
try:
    from games.traveling_salesman.api.routes import router as tsp_router
    app.include_router(tsp_router, prefix="/api/tsp", tags=["Traveling Salesman"])
    print("✅ Traveling Salesman routes loaded")
except ImportError:
    print("⚠️  Traveling Salesman routes not implemented yet")

# Tower of Hanoi routes (Member 4)
try:
    from games.tower_hanoi.api.routes import router as hanoi_router
    app.include_router(hanoi_router, prefix="/api/hanoi", tags=["Tower of Hanoi"])
    print("✅ Tower of Hanoi routes loaded")
except ImportError:
    print("⚠️  Tower of Hanoi routes not implemented yet")

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