"""
Recursive 3-Peg Tower of Hanoi Algorithm
Classic recursive implementation with O(2^n) time complexity
"""

import time
from typing import List


class RecursiveThreePeg:
    """
    Classic recursive algorithm for 3-peg Tower of Hanoi
    
    Time Complexity: O(2^n)
    Space Complexity: O(n) for recursion stack
    Optimal Moves: 2^n - 1
    """
    
    def __init__(self):
        self.name = "Recursive 3-Peg"
        self.move_sequence = []
        
    def solve(self, n: int, source: str = 'A', destination: str = 'C', auxiliary: str = 'B') -> dict:
        """
        Solve Tower of Hanoi puzzle using recursive approach
        
        Args:
            n: Number of disks
            source: Source peg label (default 'A')
            destination: Destination peg label (default 'C')
            auxiliary: Auxiliary peg label (default 'B')
            
        Returns:
            dict: Contains moves, sequence, runtime_ms, and algorithm_name
        """
        self.move_sequence = []
        
        start_time = time.perf_counter()
        move_count = self._solve_recursive(n, source, destination, auxiliary)
        end_time = time.perf_counter()
        
        runtime_ms = (end_time - start_time) * 1000
        
        return {
            'moves': move_count,
            'sequence': self.move_sequence.copy(),
            'runtime_ms': runtime_ms,
            'algorithm_name': self.name
        }
    
    def _solve_recursive(self, n: int, source: str, destination: str, auxiliary: str) -> int:
        """
        Recursive helper function
        
        Algorithm:
        1. Move n-1 disks from source to auxiliary (using destination as temp)
        2. Move the largest disk from source to destination
        3. Move n-1 disks from auxiliary to destination (using source as temp)
        """
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        # Move n-1 disks to auxiliary peg
        moves1 = self._solve_recursive(n - 1, source, auxiliary, destination)
        
        # Move the largest disk to destination
        self._add_move(source, destination)
        moves2 = 1
        
        # Move n-1 disks from auxiliary to destination
        moves3 = self._solve_recursive(n - 1, auxiliary, destination, source)
        
        return moves1 + moves2 + moves3
    
    def _add_move(self, from_peg: str, to_peg: str):
        """Add a move to the sequence"""
        self.move_sequence.append(f"{from_peg}->{to_peg}")


# Example usage
if __name__ == "__main__":
    solver = RecursiveThreePeg()
    
    print("🗼 Recursive 3-Peg Tower of Hanoi")
    print("=" * 50)
    
    for n in range(3, 8):
        result = solver.solve(n)
        print(f"\n{n} disks:")
        print(f"  Moves: {result['moves']}")
        print(f"  Runtime: {result['runtime_ms']:.4f}ms")
        print(f"  Optimal: {2**n - 1} (Achieved: {result['moves'] == 2**n - 1})")
