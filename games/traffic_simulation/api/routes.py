"""
Traffic Simulation Routes - Wrapper for main.py compatibility
"""

from fastapi import APIRouter

# Create router that main.py expects
router = APIRouter()

# Try to import from traffic_routes
try:
    from .traffic_routes import router as traffic_router
    # Copy all routes from traffic_routes
    for route in traffic_router.routes:
        router.routes.append(route)
except ImportError as e:
    print(f"Warning: Could not import traffic_routes: {e}")
    
    # Fallback: Create basic placeholder routes
    @router.get("/status")
    async def get_status():
        return {
            "status": "ok",
            "game": "Traffic Simulation",
            "message": "Traffic simulation routes placeholder"
        }
