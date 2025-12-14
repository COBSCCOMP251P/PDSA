from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import random

from ..algorithms import (
    generate_distance_matrix,
    brute_force_tsp,
    nearest_neighbor_tsp,
    dynamic_programming_tsp,
    compute_route_distance,
    CITIES,
)
from .. import schemas
from ..database import get_db
from ..models import AlgorithmTime, GameRound

router = APIRouter()

@router.post("/generate-matrix", response_model=schemas.MatrixResponse, status_code=status.HTTP_200_OK)
def generate_matrix() -> schemas.MatrixResponse:
    """Generate a symmetric distance matrix and random home city."""
    matrix = generate_distance_matrix()
    home_city = CITIES[random.randint(0, 9)]
    return schemas.MatrixResponse(home_city=home_city, distance_matrix=matrix)


@router.post(
    "/calculate-player-route",
    response_model=schemas.CalculatePlayerRouteResponse,
    status_code=status.HTTP_200_OK,
)
def calculate_player_route(payload: schemas.CalculatePlayerRouteRequest) -> schemas.CalculatePlayerRouteResponse:
    """Calculate the distance of the player's chosen route."""
    route = [payload.home_city, *payload.player_order, payload.home_city]
    distance = compute_route_distance(route, payload.distance_matrix)
    return schemas.CalculatePlayerRouteResponse(route=route, distance=distance)


@router.post("/solve-tsp", response_model=schemas.SolveTspResponse, status_code=status.HTTP_200_OK)
def solve_tsp(payload: schemas.SolveTspRequest) -> schemas.SolveTspResponse:
    """Run brute force, nearest neighbor, and DP algorithms."""
    if not payload.selected_cities:
        raise HTTPException(status_code=400, detail="At least one city must be selected.")
    brute_route, brute_distance, brute_time = brute_force_tsp(
        payload.home_city, payload.selected_cities, payload.distance_matrix
    )
    nn_route, nn_distance, nn_time = nearest_neighbor_tsp(
        payload.home_city, payload.selected_cities, payload.distance_matrix
    )
    dp_route, dp_distance, dp_time = dynamic_programming_tsp(
        payload.home_city, payload.selected_cities, payload.distance_matrix
    )
    return schemas.SolveTspResponse(
        brute_force=schemas.AlgorithmResult(route=brute_route, distance=brute_distance, time_seconds=brute_time),
        nearest_neighbor=schemas.AlgorithmResult(route=nn_route, distance=nn_distance, time_seconds=nn_time),
        dynamic_programming=schemas.AlgorithmResult(route=dp_route, distance=dp_distance, time_seconds=dp_time),
    )


@router.post("/save-result", response_model=schemas.SaveResultResponse, status_code=status.HTTP_201_CREATED)
def save_result(payload: schemas.SaveResultRequest, db: Session = Depends(get_db)) -> schemas.SaveResultResponse:
    """Persist a completed game round and its timings."""
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
        )
        db.add(game_round)
        db.flush()

        timing = AlgorithmTime(
            round_id=game_round.id,
            brute_force_time=payload.algorithm_times.brute_force_time,
            nearest_neighbor_time=payload.algorithm_times.nearest_neighbor_time,
            dp_time=payload.algorithm_times.dp_time,
        )
        db.add(timing)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save result: {exc}")
    return schemas.SaveResultResponse(message="Result saved successfully.")
