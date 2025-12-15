from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import game_routes

# Initialize application.
app = FastAPI(title="Traveling Salesman Game API")

# Enable permissive CORS for local development and student use.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup() -> None:
    """Create tables on startup if they do not exist."""
    Base.metadata.create_all(bind=engine)

app.include_router(game_routes.router)

@app.get("/health", status_code=status.HTTP_200_OK)
def healthcheck() -> dict:
    """Simple health endpoint for readiness checks."""
    return {"status": "ok"}
