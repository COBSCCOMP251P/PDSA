from typing import List, Optional  # Type hints for clarity.
from pydantic import BaseModel, Field, field_validator  # Data validation.

# Allowed city labels for validation.
VALID_CITIES = {chr(code) for code in range(ord("A"), ord("J") + 1)}  # Cities A-J.


def _validate_city(city: str) -> str:
    """Ensure a city label is within A-J."""  # Helper validator.
    city = city.upper()  # Normalize input.
    if city not in VALID_CITIES:  # Validate membership.
        raise ValueError("City must be between A and J.")  # Clear error message.
    return city  # Return normalized value.


def _validate_matrix(matrix: List[List[float]]) -> List[List[float]]:
    """Confirm a 10x10 symmetric matrix with zero diagonal and 50-100 weights (floats allowed)."""  # Matrix validation.
    if len(matrix) != 10 or any(len(row) != 10 for row in matrix):  # Size check.
        raise ValueError("Distance matrix must be 10x10.")  # Shape requirement.
    for i in range(10):  # Iterate rows.
        for j in range(10):  # Iterate columns.
            value = matrix[i][j]  # Current entry.
            if i == j and value != 0:  # Diagonal rule.
                raise ValueError("Diagonal entries must be 0.")  # Enforce rule.
            if i != j and not (50 <= value <= 100):  # Range rule.
                raise ValueError("Distances must be between 50 and 100.")  # Enforce bounds.
            if matrix[i][j] != matrix[j][i]:  # Symmetry rule.
                raise ValueError("Matrix must be symmetric.")  # Enforce symmetry.
    return matrix  # Return validated matrix.


class MatrixResponse(BaseModel):
    """Response model for generated matrices."""  # Brief description.

    home_city: str = Field(..., description="Randomly chosen home city.")  # Home city label.
    distance_matrix: List[List[float]] = Field(..., description="10x10 symmetric matrix.")  # Generated matrix.


class CalculatePlayerRouteRequest(BaseModel):
    """Request to calculate a player's route distance."""  # Brief description.

    home_city: str = Field(..., description="Home city label A-J.")  # Home city input.
    player_order: List[str] = Field(..., description="Order of cities the player will visit.")  # Visit order.
    distance_matrix: List[List[float]] = Field(..., description="10x10 symmetric matrix.")  # Matrix input.

    @field_validator("home_city")
    @classmethod
    def validate_home(cls, v: str) -> str:
        return _validate_city(v)  # Validate home city.

    @field_validator("player_order")
    @classmethod
    def validate_order(cls, v: List[str]) -> List[str]:
        return [_validate_city(city) for city in v]  # Validate each city.

    @field_validator("distance_matrix")
    @classmethod
    def validate_matrix(cls, v: List[List[float]]) -> List[List[float]]:
        return _validate_matrix(v)  # Validate matrix shape and values.


class CalculatePlayerRouteResponse(BaseModel):
    """Response containing the player's full route and distance."""  # Brief description.

    route: List[str]  # Player route including home city at start/end.
    distance: float  # Total distance for the route.


class AlgorithmResult(BaseModel):
    """Shared response model for algorithm outputs."""  # Brief description.

    route: Optional[List[str]] = None  # Route when applicable.
    distance: float  # Computed distance.
    time_seconds: float  # Runtime in seconds.


class SolveTspRequest(BaseModel):
    """Request to solve TSP with three algorithms."""  # Brief description.

    home_city: str = Field(..., description="Home city label A-J.")  # Home city input.
    selected_cities: List[str] = Field(..., description="Cities the player chose to visit.")  # Selected cities.
    distance_matrix: List[List[float]] = Field(..., description="10x10 symmetric matrix.")  # Matrix input.

    @field_validator("home_city")
    @classmethod
    def validate_home(cls, v: str) -> str:
        return _validate_city(v)  # Validate home city.

    @field_validator("selected_cities")
    @classmethod
    def validate_selected(cls, v: List[str]) -> List[str]:
        cleaned = [_validate_city(city) for city in v]  # Validate each city.
        if len(set(cleaned)) != len(cleaned):  # Prevent duplicates.
            raise ValueError("Selected cities must be unique.")  # Enforce uniqueness.
        return cleaned  # Return validated list.

    @field_validator("distance_matrix")
    @classmethod
    def validate_matrix(cls, v: List[List[float]]) -> List[List[float]]:
        return _validate_matrix(v)  # Validate matrix shape and values.


class SolveTspResponse(BaseModel):
    """Response containing all algorithm outputs."""  # Brief description.

    brute_force: AlgorithmResult  # Exact algorithm result.
    nearest_neighbor: AlgorithmResult  # Heuristic algorithm result.
    dynamic_programming: AlgorithmResult  # DP algorithm result.


class AlgorithmTimesPayload(BaseModel):
    """Payload for saving runtime metrics."""  # Brief description.

    brute_force_time: float  # Runtime in seconds.
    nearest_neighbor_time: float  # Runtime in seconds.
    dp_time: float  # Runtime in seconds.


class SaveResultRequest(BaseModel):
    """Request to persist a completed game round."""  # Brief description.

    player_name: str = Field(..., max_length=50, description="Name shown on leaderboard.")  # Player name input.
    home_city: str = Field(..., description="Home city label A-J.")  # Home city input.
    selected_cities: List[str] = Field(..., description="Cities the player selected.")  # Selected cities input.
    player_distance: float = Field(..., ge=0, description="Player route distance.")  # Player distance input.
    brute_force_distance: float = Field(..., ge=0, description="Exact distance.")  # Brute force distance.
    nearest_neighbor_distance: float = Field(..., ge=0, description="Heuristic distance.")  # NN distance.
    dp_distance: float = Field(..., ge=0, description="DP optimal distance.")  # DP distance.
    score: int = Field(..., ge=0, le=100, description="Player score out of 100.")  # Score input.
    algorithm_times: AlgorithmTimesPayload  # Timing payload.

    @field_validator("home_city")
    @classmethod
    def validate_home(cls, v: str) -> str:
        return _validate_city(v)  # Validate home city.

    @field_validator("selected_cities")
    @classmethod
    def validate_selected(cls, v: List[str]) -> List[str]:
        cleaned = [_validate_city(city) for city in v]  # Validate each city.
        if len(set(cleaned)) != len(cleaned):  # Prevent duplicates.
            raise ValueError("Selected cities must be unique.")  # Enforce uniqueness.
        return cleaned  # Return validated list.


class SaveResultResponse(BaseModel):
    """Response confirming persistence."""  # Brief description.

    message: str  # Human-readable status.


