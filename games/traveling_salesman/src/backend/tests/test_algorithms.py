import math
from .. import algorithms

def sample_matrix():
    """Provide a simple deterministic 10x10 matrix for testing."""
    base = [[0.0] * 10 for _ in range(10)]
    for i in range(10):
        for j in range(i + 1, 10):
            base[i][j] = base[j][i] = float(50 + (i + j))
    return base

def test_brute_force_optimal_route():
    """Brute force should find the minimal route for small sets."""
    matrix = sample_matrix()
    route, distance, _ = algorithms.brute_force_tsp("A", ["B", "C"], matrix)
    assert route[0] == "A" and route[-1] == "A"
    assert distance > 0
    assert math.isclose(distance, algorithms.compute_route_distance(route, matrix), rel_tol=1e-9)

def test_nearest_neighbor_returns_all_nodes():
    """Nearest neighbor should visit each selected city exactly once."""
    matrix = sample_matrix()
    route, distance, _ = algorithms.nearest_neighbor_tsp("A", ["B", "C", "D"], matrix)
    assert route.count("A") == 2
    assert set(route[1:-1]) == {"B", "C", "D"}
    assert math.isclose(distance, algorithms.compute_route_distance(route, matrix), rel_tol=1e-9)

def test_dynamic_programming_matches_brute_force_for_small_case():
    """DP distance should match brute force for the same inputs."""
    matrix = sample_matrix()
    brute_route, brute_distance, _ = algorithms.brute_force_tsp("A", ["B", "C", "D"], matrix)
    dp_route, dp_distance, _ = algorithms.dynamic_programming_tsp("A", ["B", "C", "D"], matrix)
    assert math.isclose(dp_distance, brute_distance, rel_tol=1e-9)
    assert math.isfinite(dp_distance)
    assert dp_route[0] == "A" and dp_route[-1] == "A"

def test_score_player_clamped_between_10_and_100():
    """Score helper should respect bounds."""
    assert algorithms.score_player(100, 50) == 100
    assert algorithms.score_player(100, 1000) == 10
