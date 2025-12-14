from typing import List, Tuple

# City labels supported by the game.
CITIES = [chr(code) for code in range(ord("A"), ord("J") + 1)]  # Cities A-J.

def city_to_index(city: str) -> int:
    """Map city label to matrix index."""
    return CITIES.index(city)

def compute_route_distance(route: List[str], matrix: List[List[float]]) -> float:
    """Compute total distance for a given route sequence."""
    distance = 0.0
    for current, nxt in zip(route, route[1:]):
        distance += float(matrix[city_to_index(current)][city_to_index(nxt)])
    return round(distance, 1)

def score_player(optimal_distance: float, player_distance: float) -> int:
    """Compute player score using provided formula."""
    if player_distance <= 0:
        return 10
    score = int((optimal_distance / player_distance) * 100)
    return max(10, min(score, 100))
