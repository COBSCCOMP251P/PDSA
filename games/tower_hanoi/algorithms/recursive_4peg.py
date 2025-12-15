"""
Recursive 4-Peg Tower of Hanoi Algorithm (Frame-Stewart)
Optimal recursive solution for multi-peg Tower of Hanoi
"""

import time
from typing import List


class RecursiveFourPeg:
    """
    Frame-Stewart algorithm for 4-peg Tower of Hanoi
    
    Time Complexity: O(2^√n) approximately
    Space Complexity: O(n) for recursion stack
    Finds optimal solution by trying different split points
    """
    
    def __init__(self):
        self.name = "Recursive 4-Peg"
        self.move_sequence = []
        self.memo = {}
        
    def solve(self, n: int, source: str = 'A', destination: str = 'D', 
              auxiliary1: str = 'B', auxiliary2: str = 'C') -> dict:
        """
        Solve 4-peg Tower of Hanoi using Frame-Stewart algorithm
        
        Args:
            n: Number of disks
            source: Source peg label (default 'A')
            destination: Destination peg label (default 'D')
            auxiliary1: First auxiliary peg (default 'B')
            auxiliary2: Second auxiliary peg (default 'C')
            
        Returns:
            dict: Contains moves, sequence, runtime_ms, and algorithm_name
        """
        self.move_sequence = []
        self.memo = {}
        
        start_time = time.perf_counter()
        auxiliaries = [auxiliary1, auxiliary2]
        move_count = self._solve_frame_stewart(n, source, destination, auxiliaries)
        end_time = time.perf_counter()
        
        runtime_ms = (end_time - start_time) * 1000
        
        return {
            'moves': move_count,
            'sequence': self.move_sequence.copy(),
            'runtime_ms': runtime_ms,
            'algorithm_name': self.name
        }
    
    def _solve_frame_stewart(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """
        Frame-Stewart algorithm: tries different k values to minimize moves
        
        For each k:
        1. Move top k disks to auxiliary using all 4 pegs
        2. Move bottom (n-k) disks to destination using 3 pegs (classical)
        3. Move k disks from auxiliary to destination using all 4 pegs
        """
        if n == 0:
            return 0
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        min_moves = float('inf')
        best_k = 1
        
        # Try all possible k values (1 to n-1)
        for k in range(1, n):
            temp_sequence = self.move_sequence.copy()
            
            aux1, aux2 = auxiliaries[0], auxiliaries[1]
            
            # Calculate moves for this k
            moves1 = self._solve_frame_stewart(k, source, aux1, [destination, aux2])
            moves2 = self._solve_three_peg(n - k, source, destination, aux2)
            moves3 = self._solve_frame_stewart(k, aux1, destination, [source, aux2])
            
            total_moves = moves1 + moves2 + moves3
            
            if total_moves < min_moves:
                min_moves = total_moves
                best_k = k
            
            self.move_sequence = temp_sequence
        
        # Execute the optimal solution
        aux1, aux2 = auxiliaries[0], auxiliaries[1]
        
        moves1 = self._solve_frame_stewart(best_k, source, aux1, [destination, aux2])
        moves2 = self._solve_three_peg(n - best_k, source, destination, aux2)
        moves3 = self._solve_frame_stewart(best_k, aux1, destination, [source, aux2])
        
        return moves1 + moves2 + moves3
    
    def _solve_three_peg(self, n: int, source: str, destination: str, auxiliary: str) -> int:
        """Classic 3-peg recursive solution"""
        if n == 0:
            return 0
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        moves1 = self._solve_three_peg(n - 1, source, auxiliary, destination)
        self._add_move(source, destination)
        moves2 = 1
        moves3 = self._solve_three_peg(n - 1, auxiliary, destination, source)
        
        return moves1 + moves2 + moves3
    
    def _add_move(self, from_peg: str, to_peg: str):
        """Add a move to the sequence"""
        self.move_sequence.append(f"{from_peg}->{to_peg}")


# Example usage
if __name__ == "__main__":
    solver = RecursiveFourPeg()
    
    print("🗼 Recursive 4-Peg Tower of Hanoi (Frame-Stewart)")
    print("=" * 50)
    
    for n in range(3, 8):
        result = solver.solve(n)
        optimal_3peg = 2**n - 1
        print(f"\n{n} disks:")
        print(f"  Moves: {result['moves']}")
        print(f"  Runtime: {result['runtime_ms']:.4f}ms")
        print(f"  3-peg optimal: {optimal_3peg}")
        print(f"  Improvement: {optimal_3peg - result['moves']} moves")
