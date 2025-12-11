# Traveling Salesman Algorithms

Core algorithms now live in `backend/tsp_algorithms.py` and are exercised by `backend/tests/test_algorithms.py`.

Implemented methods:
- Brute Force (exact permutations)
- Nearest Neighbor (heuristic)
- Held–Karp Dynamic Programming (exact optimal distance)
- Scoring helper for player results

All algorithms operate on cities A–J with a symmetric 10×10 distance matrix (50–100, zero diagonal).
