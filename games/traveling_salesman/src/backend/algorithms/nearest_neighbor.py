import time
from typing import List, Tuple
from .base import compute_route_distance, city_to_index

def nearest_neighbor_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
    """Heuristic: always visit the nearest unvisited city next."""
    start_time = time.perf_counter()
    unvisited = set(selected_cities)
    route = [home_city]
    current = home_city
    while unvisited:
        current_index = city_to_index(current)
        next_city = min(
            unvisited,
            key=lambda city: matrix[current_index][city_to_index(city)],
        )
        route.append(next_city)
        unvisited.remove(next_city)
        current = next_city
    route.append(home_city)
    distance = compute_route_distance(route, matrix)
    elapsed = time.perf_counter() - start_time
    return route, round(distance, 1), elapsed
