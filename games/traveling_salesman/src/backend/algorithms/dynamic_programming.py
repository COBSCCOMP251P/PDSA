import time
from typing import List, Tuple
from .base import city_to_index

def dynamic_programming_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
    """Held-Karp dynamic programming solution for exact optimal route and distance."""
    start_time = time.perf_counter()
    nodes = selected_cities
    n = len(nodes)

    # dp[mask][j] = min distance to reach nodes in mask ending at node j.
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

    # Reconstruct route
    route_nodes: List[str] = []
    mask = full_mask
    last = best_last
    while last != -1:
        route_nodes.append(nodes[last])
        prev = parent[mask][last]
        mask = mask ^ (1 << last)
        last = prev
    route_nodes.reverse()

    full_route = [home_city, *route_nodes, home_city]
    elapsed = time.perf_counter() - start_time
    return full_route, round(best_distance, 1), elapsed
