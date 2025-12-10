import math  # For infinity comparisons.
from backend import tsp_algorithms  # Algorithms under test.


def sample_matrix():
    """Provide a simple deterministic 10x10 matrix for testing."""  # Test helper.
    base = [[0.0] * 10 for _ in range(10)]  # Start with zeros.
    for i in range(10):  # Fill symmetric distances.
        for j in range(i + 1, 10):  # Upper triangle.
            base[i][j] = base[j][i] = float(50 + (i + j))  # Deterministic weight.
    return base  # Return matrix.


def test_brute_force_optimal_route():
    """Brute force should find the minimal route for small sets."""  # Assertion description.
    matrix = sample_matrix()  # Use deterministic matrix.
    route, distance, _ = tsp_algorithms.brute_force_tsp("A", ["B", "C"], matrix)  # Run algorithm.
    assert route[0] == "A" and route[-1] == "A"  # Must start/end at home.
    assert distance > 0  # Distance should be positive.
    assert math.isclose(distance, tsp_algorithms.compute_route_distance(route, matrix), rel_tol=1e-9)  # Distance consistency.


def test_nearest_neighbor_returns_all_nodes():
    """Nearest neighbor should visit each selected city exactly once."""  # Assertion description.
    matrix = sample_matrix()  # Deterministic distances.
    route, distance, _ = tsp_algorithms.nearest_neighbor_tsp("A", ["B", "C", "D"], matrix)  # Run algorithm.
    assert route.count("A") == 2  # Home should appear twice.
    assert set(route[1:-1]) == {"B", "C", "D"}  # All cities visited.
    assert math.isclose(distance, tsp_algorithms.compute_route_distance(route, matrix), rel_tol=1e-9)  # Distance consistency.


def test_dynamic_programming_matches_brute_force_for_small_case():
    """DP distance should match brute force for the same inputs."""  # Assertion description.
    matrix = sample_matrix()  # Deterministic distances.
    brute_route, brute_distance, _ = tsp_algorithms.brute_force_tsp("A", ["B", "C", "D"], matrix)  # Brute force result.
    dp_route, dp_distance, _ = tsp_algorithms.dynamic_programming_tsp("A", ["B", "C", "D"], matrix)  # DP result.
    assert math.isclose(dp_distance, brute_distance, rel_tol=1e-9)  # Optimality match.
    assert math.isfinite(dp_distance)  # Ensure finite distance.
    assert dp_route[0] == "A" and dp_route[-1] == "A"  # Route should start/end at home.


def test_score_player_clamped_between_10_and_100():
    """Score helper should respect bounds."""  # Assertion description.
    assert tsp_algorithms.score_player(100, 50) == 100  # Perfect score capped at 100.
    assert tsp_algorithms.score_player(100, 1000) == 10  # Minimum score is 10.


