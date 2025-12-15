import itertools
import time
from typing import List, Tuple
from .base import compute_route_distance

def brute_force_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
    """Exact search over all permutations of selected cities."""
    start_time = time.perf_counter()
    best_route: List[str] = []
    best_distance = float("inf")
    for perm in itertools.permutations(selected_cities):
        route = [home_city, *perm, home_city]
        distance = compute_route_distance(route, matrix)
        if distance < best_distance:
            best_distance = distance
            best_route = list(route)
    elapsed = time.perf_counter() - start_time
    return best_route, round(best_distance, 1), elapsed
