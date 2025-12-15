"""
Iterative 3-Peg Tower of Hanoi Algorithm
Stack-based iterative implementation
"""

import time
from typing import List


class IterativeThreePeg:
    """
    Iterative algorithm for 3-peg Tower of Hanoi using explicit stack
    
    Time Complexity: O(2^n)
    Space Complexity: O(n) for explicit stack
    Optimal Moves: 2^n - 1
    """
    
    def __init__(self):
        self.name = "Iterative 3-Peg"
        self.move_sequence = []
        
    def solve(self, n: int, source: str = 'A', destination: str = 'C', auxiliary: str = 'B') -> dict:
        """
        Solve Tower of Hanoi puzzle using iterative approach with explicit stack
        
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
        move_count = self._solve_iterative(n, source, destination, auxiliary)
        end_time = time.perf_counter()
        
        runtime_ms = (end_time - start_time) * 1000
        
        return {
            'moves': move_count,
            'sequence': self.move_sequence.copy(),
            'runtime_ms': runtime_ms,
            'algorithm_name': self.name
        }
    
    def _solve_iterative(self, n: int, source: str, destination: str, auxiliary: str) -> int:
        """
        Iterative solution using explicit stack to simulate recursion
        
        Stack contains tuples: (n_disks, source, destination, auxiliary)
        More memory efficient than recursive approach for large n
        """
        # Stack to hold (n, source, destination, auxiliary) tuples
        stack = [(n, source, destination, auxiliary)]
        move_count = 0
        
        while stack:
            n_disks, src, dest, aux = stack.pop()
            
            if n_disks == 1:
                self._add_move(src, dest)
                move_count += 1
            else:
                # Push operations in reverse order (stack is LIFO)
                # 3. Move n-1 disks from auxiliary to destination
                stack.append((n_disks - 1, aux, dest, src))
                
                # 2. Move largest disk from source to destination
                stack.append((1, src, dest, aux))
                
                # 1. Move n-1 disks from source to auxiliary
                stack.append((n_disks - 1, src, aux, dest))
        
        return move_count
    
    def _add_move(self, from_peg: str, to_peg: str):
        """Add a move to the sequence"""
        self.move_sequence.append(f"{from_peg}->{to_peg}")


# Example usage
if __name__ == "__main__":
    solver = IterativeThreePeg()
    
    print("🗼 Iterative 3-Peg Tower of Hanoi")
    print("=" * 50)
    
    for n in range(3, 8):
        result = solver.solve(n)
        print(f"\n{n} disks:")
        print(f"  Moves: {result['moves']}")
        print(f"  Runtime: {result['runtime_ms']:.4f}ms")
        print(f"  Optimal: {2**n - 1} (Achieved: {result['moves'] == 2**n - 1})")
