from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

# Allowed city labels for validation.
VALID_CITIES = {chr(code) for code in range(ord("A"), ord("J") + 1)}

def _validate_city(city: str) -> str:
    """Ensure a city label is within A-J."""
    city = city.upper()
    if city not in VALID_CITIES:
        raise ValueError("City must be between A and J.")
    return city

def _validate_matrix(matrix: List[List[float]]) -> List[List[float]]:
    """Confirm a 10x10 symmetric matrix with zero diagonal and 50-100 weights (floats allowed)."""
    if len(matrix) != 10 or any(len(row) != 10 for row in matrix):
        raise ValueError("Distance matrix must be 10x10.")
    for i in range(10):
        for j in range(10):
            value = matrix[i][j]
            if i == j and value != 0:
                raise ValueError("Diagonal entries must be 0.")
            if i != j and not (50 <= value <= 100):
                raise ValueError("Distances must be between 50 and 100.")
            if matrix[i][j] != matrix[j][i]:
                raise ValueError("Matrix must be symmetric.")
    return matrix

class MatrixResponse(BaseModel):
    """Response model for generated matrices."""
    home_city: str = Field(..., description="Randomly chosen home city.")
    distance_matrix: List[List[float]] = Field(..., description="10x10 symmetric matrix.")

class CalculatePlayerRouteRequest(BaseModel):
    """Request to calculate a player's route distance."""
    home_city: str = Field(..., description="Home city label A-J.")
    player_order: List[str] = Field(..., description="Order of cities the player will visit.")
    distance_matrix: List[List[float]] = Field(..., description="10x10 symmetric matrix.")

    @field_validator("home_city")
    @classmethod
    def validate_home(cls, v: str) -> str:
        return _validate_city(v)

    @field_validator("player_order")
    @classmethod
    def validate_order(cls, v: List[str]) -> List[str]:
        return [_validate_city(city) for city in v]

    @field_validator("distance_matrix")
    @classmethod
    def validate_matrix(cls, v: List[List[float]]) -> List[List[float]]:
        return _validate_matrix(v)

class CalculatePlayerRouteResponse(BaseModel):
    """Response containing the player's full route and distance."""
    route: List[str]
    distance: float

class AlgorithmResult(BaseModel):
    """Shared response model for algorithm outputs."""
    route: Optional[List[str]] = None
    distance: float
    time_seconds: float

class SolveTspRequest(BaseModel):
    """Request to solve TSP with three algorithms."""
    home_city: str = Field(..., description="Home city label A-J.")
    selected_cities: List[str] = Field(..., description="Cities the player chose to visit.")
    distance_matrix: List[List[float]] = Field(..., description="10x10 symmetric matrix.")

    @field_validator("home_city")
    @classmethod
    def validate_home(cls, v: str) -> str:
        return _validate_city(v)

    @field_validator("selected_cities")
    @classmethod
    def validate_selected(cls, v: List[str]) -> List[str]:
        cleaned = [_validate_city(city) for city in v]
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("Selected cities must be unique.")
        return cleaned

    @field_validator("distance_matrix")
    @classmethod
    def validate_matrix(cls, v: List[List[float]]) -> List[List[float]]:
        return _validate_matrix(v)

class SolveTspResponse(BaseModel):
    """Response containing all algorithm outputs."""
    brute_force: AlgorithmResult
    nearest_neighbor: AlgorithmResult
    dynamic_programming: AlgorithmResult

class AlgorithmTimesPayload(BaseModel):
    """Payload for saving runtime metrics."""
    brute_force_time: float
    nearest_neighbor_time: float
    dp_time: float

class SaveResultRequest(BaseModel):
    """Request to persist a completed game round."""
    player_name: str = Field(..., max_length=50, description="Name shown on leaderboard.")
    home_city: str = Field(..., description="Home city label A-J.")
    selected_cities: List[str] = Field(..., description="Cities the player selected.")
    player_distance: float = Field(..., ge=0, description="Player route distance.")
    brute_force_distance: float = Field(..., ge=0, description="Exact distance.")
    nearest_neighbor_distance: float = Field(..., ge=0, description="Heuristic distance.")
    dp_distance: float = Field(..., ge=0, description="DP optimal distance.")
    score: int = Field(..., ge=0, le=100, description="Player score out of 100.")
    algorithm_times: AlgorithmTimesPayload

    @field_validator("home_city")
    @classmethod
    def validate_home(cls, v: str) -> str:
        return _validate_city(v)

    @field_validator("selected_cities")
    @classmethod
    def validate_selected(cls, v: List[str]) -> List[str]:
        cleaned = [_validate_city(city) for city in v]
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("Selected cities must be unique.")
        return cleaned

class SaveResultResponse(BaseModel):
    """Response confirming persistence."""
    message: str
