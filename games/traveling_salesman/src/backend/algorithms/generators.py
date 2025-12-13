import random
from typing import List

def generate_distance_matrix() -> List[List[float]]:
    """Create a random 10x10 symmetric distance matrix with one-decimal km values."""
    matrix = [[0.0 for _ in range(10)] for _ in range(10)]
    for i in range(10):
        for j in range(i + 1, 10):
            value = round(random.uniform(50, 100), 1)
            matrix[i][j] = value
            matrix[j][i] = value
    return matrix
