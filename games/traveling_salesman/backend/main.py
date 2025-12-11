from fastapi import Depends, FastAPI, HTTPException, status  # FastAPI primitives.
from fastapi.middleware.cors import CORSMiddleware  # CORS support.
from sqlalchemy.orm import Session  # SQLAlchemy session type.
from . import schemas, tsp_algorithms  # Local modules.
from .database import Base, engine, get_db  # DB utilities.
from .models import AlgorithmTime, GameRound  # ORM models.

# Initialize application.
app = FastAPI(title="Traveling Salesman Game API")  # Main FastAPI app.

# Enable permissive CORS for local development and student use.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity.
    allow_credentials=True,  # Allow cookies if needed.
    allow_methods=["*"],  # Allow all HTTP methods.
    allow_headers=["*"],  # Allow all headers.
)  # CORS configuration.


@app.on_event("startup")
def startup() -> None:
    """Create tables on startup if they do not exist."""  # Auto-migration helper.
    Base.metadata.create_all(bind=engine)  # Create schema.


@app.post("/generate-matrix", response_model=schemas.MatrixResponse, status_code=status.HTTP_200_OK)
def generate_matrix() -> schemas.MatrixResponse:
    """Generate a symmetric distance matrix and random home city."""  # Endpoint description.
    matrix = tsp_algorithms.generate_distance_matrix()  # Build matrix.
    home_city = tsp_algorithms.CITIES[tsp_algorithms.random.randint(0, 9)]  # Pick random city.
    return schemas.MatrixResponse(home_city=home_city, distance_matrix=matrix)  # Response payload.


@app.post(
    "/calculate-player-route",
    response_model=schemas.CalculatePlayerRouteResponse,
    status_code=status.HTTP_200_OK,
)
def calculate_player_route(payload: schemas.CalculatePlayerRouteRequest) -> schemas.CalculatePlayerRouteResponse:
    """Calculate the distance of the player's chosen route."""  # Endpoint description.
    route = [payload.home_city, *payload.player_order, payload.home_city]  # Build full route.
    distance = tsp_algorithms.compute_route_distance(route, payload.distance_matrix)  # Compute distance.
    return schemas.CalculatePlayerRouteResponse(route=route, distance=distance)  # Response payload.


@app.post("/solve-tsp", response_model=schemas.SolveTspResponse, status_code=status.HTTP_200_OK)
def solve_tsp(payload: schemas.SolveTspRequest) -> schemas.SolveTspResponse:
    """Run brute force, nearest neighbor, and DP algorithms."""  # Endpoint description.
    if not payload.selected_cities:  # Validate selection.
        raise HTTPException(status_code=400, detail="At least one city must be selected.")  # Inform client.
    brute_route, brute_distance, brute_time = tsp_algorithms.brute_force_tsp(
        payload.home_city, payload.selected_cities, payload.distance_matrix
    )  # Run brute force.
    nn_route, nn_distance, nn_time = tsp_algorithms.nearest_neighbor_tsp(
        payload.home_city, payload.selected_cities, payload.distance_matrix
    )  # Run nearest neighbor.
    dp_route, dp_distance, dp_time = tsp_algorithms.dynamic_programming_tsp(
        payload.home_city, payload.selected_cities, payload.distance_matrix
    )  # Run DP Held-Karp.
    return schemas.SolveTspResponse(
        brute_force=schemas.AlgorithmResult(route=brute_route, distance=brute_distance, time_seconds=brute_time),
        nearest_neighbor=schemas.AlgorithmResult(route=nn_route, distance=nn_distance, time_seconds=nn_time),
        dynamic_programming=schemas.AlgorithmResult(route=dp_route, distance=dp_distance, time_seconds=dp_time),
    )  # Aggregate results.


@app.post("/save-result", response_model=schemas.SaveResultResponse, status_code=status.HTTP_201_CREATED)
def save_result(payload: schemas.SaveResultRequest, db: Session = Depends(get_db)) -> schemas.SaveResultResponse:
    """Persist a completed game round and its timings."""  # Endpoint description.
    try:
        game_round = GameRound(
            player_name=payload.player_name,
            home_city=payload.home_city,
            selected_cities=",".join(payload.selected_cities),
            brute_force_distance=payload.brute_force_distance,
            nearest_neighbor_distance=payload.nearest_neighbor_distance,
            dp_distance=payload.dp_distance,
            player_distance=payload.player_distance,
            player_score=payload.score,
        )  # ORM object for main row.
        db.add(game_round)  # Stage for commit.
        db.flush()  # Acquire generated ID.

        timing = AlgorithmTime(
            round_id=game_round.id,
            brute_force_time=payload.algorithm_times.brute_force_time,
            nearest_neighbor_time=payload.algorithm_times.nearest_neighbor_time,
            dp_time=payload.algorithm_times.dp_time,
        )  # ORM object for timing row.
        db.add(timing)  # Stage timing row.
        db.commit()  # Persist transaction.
    except Exception as exc:  # Catch DB errors.
        db.rollback()  # Undo partial writes.
        raise HTTPException(status_code=500, detail=f"Failed to save result: {exc}")  # Report error.
    return schemas.SaveResultResponse(message="Result saved successfully.")  # Success response.


@app.get("/health", status_code=status.HTTP_200_OK)
def healthcheck() -> dict:
    """Simple health endpoint for readiness checks."""  # Health description.
    return {"status": "ok"}  # Health payload.


