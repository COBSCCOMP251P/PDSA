"""
PDSA Interactive Games - FastAPI Backend
Main application entry point

This file sets up the FastAPI application and registers
all game routes. Individual games will add their routes here.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse 
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# Load environment variables
load_dotenv()

# --- 1. APP SETUP & CONFIGURATION ---
CURRENT_DIR = Path(__file__).resolve().parent
# Go up twice to reach the PDSA/ root
PROJECT_ROOT = CURRENT_DIR.parent.parent 
if str(PROJECT_ROOT) not in sys.path:
    # Add PDSA/ to the system path so Python can find 'games' and 'shared' packages
    sys.path.append(str(PROJECT_ROOT))

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

# --- 2. GAME ROUTE REGISTRATION & IMPORTS ---

# Import the Traffic Simulation router using the group's file structure:
# Path: PDSA/games/traffic_simulation/api/traffic_routes.py
try:
    from games.traffic_simulation.api.traffic_routes import router as traffic_router
except ImportError as e:
    # If the import fails, print an error to help with path debugging
    print(f"Error importing traffic_routes: {e}")
    # You might need to adjust the path if the structure is slightly different
    # Example: from traffic_simulation.games.api import traffic_routes as traffic_router
    sys.exit(1) # Exit if critical route can't be loaded
    
# Register the Traffic Simulation router
app.include_router(
    traffic_router,
    prefix="/api/traffic",
    tags=["Traffic Simulation"]
)

# --- 3. STATIC FILE / FRONTEND SETUP ---
SHARED_FRONTEND_DIR = PROJECT_ROOT / "shared" / "frontend"
TRAFFIC_FRONTEND_DIR = PROJECT_ROOT / "games" / "traffic_simulation" / "frontend"
# Check if the directory exists before mounting (optional but helpful check)
if not TRAFFIC_FRONTEND_DIR.is_dir():
    print(f"ERROR: Frontend directory not found at {TRAFFIC_FRONTEND_DIR}")
    sys.exit(1)
# Mount the Static Files Directory for ALL games' common assets and your game's assets.
# We map your specific frontend directory to a generic '/static' URL for simplicity.
# NOTE: If other games need their own unique static folders, this setup may need revision.
app.mount(
    "/static",
    StaticFiles(directory=SHARED_FRONTEND_DIR), # Pointing to YOUR frontend folder
    name="shared_static"
)
# 2. Add Mount for Traffic-Specific Assets (like traffic.js)
app.mount(
    "/traffic-static", 
    StaticFiles(directory=TRAFFIC_FRONTEND_DIR), 
    name="traffic_static"
)

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
@app.get("/", include_in_schema=False)
async def root():
    """Serves the main shared index.html file."""
    
    # 1. Define the full path to index.html
    index_file_path = SHARED_FRONTEND_DIR / "index.html"
    
    # 2. Check if the file exists and return it
    if index_file_path.is_file():
        return FileResponse(index_file_path)
    else:
        # Fallback to the original JSON response if the file is missing
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


# Traffic Simulation routes (Member 2)
# Endpoint to directly access your game (for easy testing/landing page link)
@app.get("/traffic", include_in_schema=False)
async def traffic_index():
# Use pathlib operator / for consistent path building
    traffic_file_path = TRAFFIC_FRONTEND_DIR / "traffic.html"
    
    if traffic_file_path.is_file():
        # Use str() to pass a standard path string to FileResponse
        return FileResponse(str(traffic_file_path))
    else:
        raise HTTPException(status_code=404, detail="Traffic Simulation HTML not found")
"""
# Eight Queens routes (Member 5)
from games.eight_queens.api.queens_routes import router as queens_router
app.include_router(queens_router, prefix="/api/queens", tags=["Eight Queens"])

# Snake Ladder routes (Member 1)
from games.snake_ladder.api.snake_ladder_routes import router as snake_ladder_router
app.include_router(snake_ladder_router, prefix="/api/snake-ladder", tags=["Snake Ladder"])

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