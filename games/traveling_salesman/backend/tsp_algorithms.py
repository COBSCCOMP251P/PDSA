import itertools  # Provides permutations for brute force search.
import random  # Used to generate random matrices and home city.
import time  # For runtime measurements.
from typing import List, Tuple, Dict  # Type hints for clarity.

# City labels supported by the game.
CITIES = [chr(code) for code in range(ord("A"), ord("J") + 1)]  # Cities A-J.


def city_to_index(city: str) -> int:
    """Map city label to matrix index."""  # Helper mapping function.
    return CITIES.index(city)  # Return position in CITIES list.


def generate_distance_matrix() -> List[List[float]]:
    """Create a random 10x10 symmetric distance matrix with one-decimal km values."""  # Matrix generator.
    matrix = [[0.0 for _ in range(10)] for _ in range(10)]  # Start with zeros.
    for i in range(10):  # Iterate rows.
        for j in range(i + 1, 10):  # Fill upper triangle.
            value = round(random.uniform(50, 100), 1)  # Random distance with one decimal.
            matrix[i][j] = value  # Assign upper value.
            matrix[j][i] = value  # Mirror for symmetry.
    return matrix  # Return completed matrix.


def compute_route_distance(route: List[str], matrix: List[List[float]]) -> float:
    """Compute total distance for a given route sequence."""  # Distance accumulator.
    distance = 0.0  # Initialize accumulator.
    for current, nxt in zip(route, route[1:]):  # Step through edges.
        distance += float(matrix[city_to_index(current)][city_to_index(nxt)])  # Add edge cost.
    return round(distance, 1)  # Return total distance to one decimal.


def brute_force_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
    """Exact search over all permutations of selected cities."""  # Brute force description.
    start_time = time.perf_counter()  # Start timer.
    best_route: List[str] = []  # Track best route.
    best_distance = float("inf")  # Track shortest distance.
    for perm in itertools.permutations(selected_cities):  # Try every ordering.
        route = [home_city, *perm, home_city]  # Build full route with return home.
        distance = compute_route_distance(route, matrix)  # Compute distance.
        if distance < best_distance:  # Check for improvement.
            best_distance = distance  # Store best distance.
            best_route = list(route)  # Store best route.
    elapsed = time.perf_counter() - start_time  # Stop timer.
    return best_route, round(best_distance, 1), elapsed  # Return result tuple.


def nearest_neighbor_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
    """Heuristic: always visit the nearest unvisited city next."""  # NN description.
    start_time = time.perf_counter()  # Start timer.
    unvisited = set(selected_cities)  # Track remaining cities.
    route = [home_city]  # Initialize route at home.
    current = home_city  # Set current city.
    while unvisited:  # Continue until all visited.
        current_index = city_to_index(current)  # Map to index.
        next_city = min(
            unvisited,
            key=lambda city: matrix[current_index][city_to_index(city)],  # Choose nearest.
        )  # Get closest city.
        route.append(next_city)  # Append chosen city.
        unvisited.remove(next_city)  # Mark visited.
        current = next_city  # Move current pointer.
    route.append(home_city)  # Return home.
    distance = compute_route_distance(route, matrix)  # Compute route distance.
    elapsed = time.perf_counter() - start_time  # Stop timer.
    return route, round(distance, 1), elapsed  # Return result tuple.


def dynamic_programming_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
    """Held-Karp dynamic programming solution for exact optimal route and distance."""  # DP description.
    start_time = time.perf_counter()  # Start timer.
    nodes = selected_cities  # Nodes excluding home.
    n = len(nodes)  # Number of nodes.

    # dp[mask][j] = min distance to reach nodes in mask ending at node j.
    dp = [[float("inf")] * n for _ in range(1 << n)]  # Initialize DP table.
    parent = [[-1] * n for _ in range(1 << n)]  # Track predecessors for path reconstruction.

    for idx, city in enumerate(nodes):  # Initialize base cases.
        dp[1 << idx][idx] = matrix[city_to_index(home_city)][city_to_index(city)]  # Distance from home.

    for mask in range(1 << n):  # Iterate all subsets.
        for last in range(n):  # Iterate possible last nodes.
            if not (mask & (1 << last)):  # Skip if last not in subset.
                continue  # Continue loop.
            for nxt in range(n):  # Try next node.
                if mask & (1 << nxt):  # Skip visited nodes.
                    continue  # Continue loop.
                new_mask = mask | (1 << nxt)  # Add next node to mask.
                candidate = dp[mask][last] + matrix[city_to_index(nodes[last])][city_to_index(nodes[nxt])]  # Candidate distance.
                if candidate < dp[new_mask][nxt]:  # Check improvement.
                    dp[new_mask][nxt] = candidate  # Update DP table.
                    parent[new_mask][nxt] = last  # Remember predecessor.

    full_mask = (1 << n) - 1  # Mask representing all visited.
    best_distance = float("inf")  # Track best closing distance.
    best_last = -1  # Track last node for optimal path.
    for last in range(n):  # Evaluate returning home.
        route_distance = dp[full_mask][last] + matrix[city_to_index(nodes[last])][city_to_index(home_city)]  # Close tour.
        if route_distance < best_distance:  # Check improvement.
            best_distance = route_distance  # Store best distance.
            best_last = last  # Store last node index.

    # Reconstruct optimal route.
    route_nodes: List[str] = []  # Holder for route without home.
    mask = full_mask  # Start from full mask.
    last = best_last  # Start from best last node.
    while last != -1:  # Continue until base.
        route_nodes.append(nodes[last])  # Append current node.
        prev = parent[mask][last]  # Find predecessor.
        mask = mask ^ (1 << last)  # Remove current from mask.
        last = prev  # Move to predecessor.
    route_nodes.reverse()  # Reverse to get forward order.

    full_route = [home_city, *route_nodes, home_city]  # Include home at start and end.
    elapsed = time.perf_counter() - start_time  # Stop timer.
    return full_route, round(best_distance, 1), elapsed  # Return optimal route, distance, runtime.


def score_player(optimal_distance: float, player_distance: float) -> int:
    """Compute player score using provided formula."""  # Scoring helper.
    if player_distance <= 0:  # Guard division by zero.
        return 10  # Minimal fallback score.
    score = int((optimal_distance / player_distance) * 100)  # Compute ratio.
    return max(10, min(score, 100))  # Clamp between 10 and 100.


