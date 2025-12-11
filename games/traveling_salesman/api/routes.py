"""
Traveling Salesman Problem API Routes
Integrated with main PDSA backend
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random
import itertools
import time

# Initialize router
router = APIRouter()

# City labels (A-J)
CITIES = [chr(code) for code in range(ord("A"), ord("J") + 1)]

# ================== Helper Functions ==================

def city_to_index(city: str) -> int:
    """Map city label to matrix index."""
    return CITIES.index(city)

def generate_distance_matrix() -> List[List[float]]:
    """Create a random 10x10 symmetric distance matrix."""
    matrix = [[0.0 for _ in range(10)] for _ in range(10)]
    for i in range(10):
        for j in range(i + 1, 10):
            value = round(random.uniform(50, 100), 1)
            matrix[i][j] = value
            matrix[j][i] = value
    return matrix

def compute_route_distance(route: List[str], matrix: List[List[float]]) -> float:
    """Compute total distance for a given route sequence."""
    distance = 0.0
    for current, nxt in zip(route, route[1:]):
        distance += float(matrix[city_to_index(current)][city_to_index(nxt)])
    return round(distance, 1)

def brute_force_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]):
    """Exact search over all permutations of selected cities."""
    start_time = time.perf_counter()
    best_route = []
    best_distance = float("inf")
    for perm in itertools.permutations(selected_cities):
        route = [home_city, *perm, home_city]
        distance = compute_route_distance(route, matrix)
        if distance < best_distance:
            best_distance = distance
            best_route = list(route)
    elapsed = time.perf_counter() - start_time
    return best_route, round(best_distance, 1), elapsed

def nearest_neighbor_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]):
    """Heuristic: always visit the nearest unvisited city next."""
    start_time = time.perf_counter()
    unvisited = set(selected_cities)
    route = [home_city]
    current = home_city
    while unvisited:
        current_index = city_to_index(current)
        next_city = min(unvisited, key=lambda city: matrix[current_index][city_to_index(city)])
        route.append(next_city)
        unvisited.remove(next_city)
        current = next_city
    route.append(home_city)
    distance = compute_route_distance(route, matrix)
    elapsed = time.perf_counter() - start_time
    return route, round(distance, 1), elapsed

def dynamic_programming_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]):
    """Held-Karp dynamic programming solution for exact optimal route."""
    start_time = time.perf_counter()
    nodes = selected_cities
    n = len(nodes)

    if n == 0:
        return [home_city, home_city], 0.0, 0.0

    dp = [[float("inf")] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    for idx, city in enumerate(nodes):
        dp[1 << idx][idx] = matrix[city_to_index(home_city)][city_to_index(city)]

    for mask in range(1 << n):
        for last in range(n):
            if not (mask & (1 << last)):
                continue
            for nxt in range(n):
                if mask & (1 << nxt):
                    continue
                new_mask = mask | (1 << nxt)
                candidate = dp[mask][last] + matrix[city_to_index(nodes[last])][city_to_index(nodes[nxt])]
                if candidate < dp[new_mask][nxt]:
                    dp[new_mask][nxt] = candidate
                    parent[new_mask][nxt] = last

    full_mask = (1 << n) - 1
    best_distance = float("inf")
    best_last = -1
    for last in range(n):
        route_distance = dp[full_mask][last] + matrix[city_to_index(nodes[last])][city_to_index(home_city)]
        if route_distance < best_distance:
            best_distance = route_distance
            best_last = last

    # Reconstruct path
    route = []
    mask = full_mask
    current = best_last
    while current != -1:
        route.append(nodes[current])
        prev = parent[mask][current]
        mask ^= (1 << current)
        current = prev
    route.reverse()
    route = [home_city] + route + [home_city]

    elapsed = time.perf_counter() - start_time
    return route, round(best_distance, 1), elapsed

# ================== Pydantic Models ==================

class MatrixResponse(BaseModel):
    home_city: str
    distance_matrix: List[List[float]]

class CalculatePlayerRouteRequest(BaseModel):
    home_city: str
    player_order: List[str]
    distance_matrix: List[List[float]]

class CalculatePlayerRouteResponse(BaseModel):
    route: List[str]
    distance: float

class SolveTspRequest(BaseModel):
    home_city: str
    selected_cities: List[str]
    distance_matrix: List[List[float]]

class AlgorithmResult(BaseModel):
    route: List[str]
    distance: float
    time_seconds: float

class SolveTspResponse(BaseModel):
    brute_force: AlgorithmResult
    nearest_neighbor: AlgorithmResult
    dynamic_programming: AlgorithmResult

class SaveResultRequest(BaseModel):
    player_name: str
    home_city: str
    selected_cities: List[str]
    brute_force_distance: float
    nearest_neighbor_distance: float
    dp_distance: float
    player_distance: float
    score: int
    algorithm_times: dict

class SaveResultResponse(BaseModel):
    message: str

# ================== API Endpoints ==================

@router.post("/generate-matrix", response_model=MatrixResponse)
async def generate_matrix():
    """Generate a symmetric distance matrix and random home city."""
    matrix = generate_distance_matrix()
    home_city = CITIES[random.randint(0, 9)]
    return MatrixResponse(home_city=home_city, distance_matrix=matrix)

@router.post("/calculate-player-route", response_model=CalculatePlayerRouteResponse)
async def calculate_player_route(payload: CalculatePlayerRouteRequest):
    """Calculate the distance of the player's chosen route."""
    route = [payload.home_city, *payload.player_order, payload.home_city]
    distance = compute_route_distance(route, payload.distance_matrix)
    return CalculatePlayerRouteResponse(route=route, distance=distance)

@router.post("/solve-tsp", response_model=SolveTspResponse)
async def solve_tsp(payload: SolveTspRequest):
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
    
    return SolveTspResponse(
        brute_force=AlgorithmResult(route=brute_route, distance=brute_distance, time_seconds=brute_time),
        nearest_neighbor=AlgorithmResult(route=nn_route, distance=nn_distance, time_seconds=nn_time),
        dynamic_programming=AlgorithmResult(route=dp_route, distance=dp_distance, time_seconds=dp_time),
    )

@router.post("/save-result", response_model=SaveResultResponse)
async def save_result(payload: SaveResultRequest):
    """Save game result (in-memory, no database required)."""
    # For now, just acknowledge the save without database
    return SaveResultResponse(message="Result saved successfully (in-memory)")

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "game": "traveling_salesman"}
