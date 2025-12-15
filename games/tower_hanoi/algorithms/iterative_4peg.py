"""
Iterative 4-Peg Tower of Hanoi Algorithm
Stack-based Frame-Stewart implementation
"""

import time
from typing import List


class IterativeFourPeg:
    """
    Iterative Frame-Stewart algorithm for 4-peg Tower of Hanoi
    
    Time Complexity: O(2^√n) approximately
    Space Complexity: O(n) for explicit stack
    Uses stack to avoid recursion depth limits
    """
    
    def __init__(self):
        self.name = "Iterative 4-Peg"
        self.move_sequence = []
        self.optimal_k_cache = {}
        
    def solve(self, n: int, source: str = 'A', destination: str = 'D',
              auxiliary1: str = 'B', auxiliary2: str = 'C') -> dict:
        """
        Solve 4-peg Tower of Hanoi using iterative Frame-Stewart
        
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
        self.optimal_k_cache = {}
        
        start_time = time.perf_counter()
        auxiliaries = [auxiliary1, auxiliary2]
        move_count = self._solve_iterative(n, source, destination, auxiliaries)
        end_time = time.perf_counter()
        
        runtime_ms = (end_time - start_time) * 1000
        
        return {
            'moves': move_count,
            'sequence': self.move_sequence.copy(),
            'runtime_ms': runtime_ms,
            'algorithm_name': self.name
        }
    
    def _solve_iterative(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """
        Iterative Frame-Stewart using explicit stack
        
        Stack items: (n_disks, src, dest, aux_list, phase)
        phase: 0=initial, 1=after moving k to aux1, 2=after moving n-k to dest
        """
        if n == 0:
            return 0
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        # Pre-calculate optimal k values
        self._precompute_optimal_k(n)
        
        stack = [(n, source, destination, auxiliaries, 0)]
        move_count = 0
        
        while stack:
            n_disks, src, dest, aux_list, phase = stack.pop()
            
            if n_disks == 1:
                self._add_move(src, dest)
                move_count += 1
                continue
            
            if n_disks == 0:
                continue
            
            aux1 = aux_list[0] if len(aux_list) > 0 else 'B'
            aux2 = aux_list[1] if len(aux_list) > 1 else 'C'
            
            k = self._find_optimal_k(n_disks)
            
            if phase == 0:
                # Push phases in reverse order
                # Phase 2: Move k disks from aux1 to dest (4-peg)
                if k > 0:
                    stack.append((k, aux1, dest, [src, aux2], 0))
                
                # Phase 1: Move n-k disks from src to dest (3-peg)
                if n_disks - k > 0:
                    stack.append((n_disks - k, src, dest, [aux2], -1))  # -1 indicates 3-peg mode
                
                # Phase 0: Move k disks from src to aux1 (4-peg)
                if k > 0:
                    stack.append((k, src, aux1, [dest, aux2], 0))
            
            elif phase == -1:
                # 3-peg classical mode
                if n_disks == 1:
                    self._add_move(src, dest)
                    move_count += 1
                else:
                    # Standard 3-peg decomposition
                    stack.append((n_disks - 1, aux_list[0], dest, [src], -1))
                    stack.append((1, src, dest, [], -1))
                    stack.append((n_disks - 1, src, aux_list[0], [dest], -1))
        
        return move_count
    
    def _precompute_optimal_k(self, max_n: int):
        """Pre-compute optimal k values for efficiency"""
        for n in range(1, max_n + 1):
            self._find_optimal_k(n)
    
    def _find_optimal_k(self, n: int) -> int:
        """Find the optimal split point k for Frame-Stewart"""
        if n <= 1:
            return 1
        if n in self.optimal_k_cache:
            return self.optimal_k_cache[n]
        
        min_moves = float('inf')
        best_k = 1
        
        for k in range(1, n):
            moves_top = self._calculate_moves(k)
            moves_bottom = (2 ** (n - k)) - 1
            total_moves = 2 * moves_top + moves_bottom
            
            if total_moves < min_moves:
                min_moves = total_moves
                best_k = k
        
        self.optimal_k_cache[n] = best_k
        return best_k
    
    def _calculate_moves(self, n: int) -> int:
        """Calculate minimum moves for n disks (4-peg)"""
        if n == 0:
            return 0
        if n == 1:
            return 1
        if n == 2:
            return 3
        
        min_moves = float('inf')
        for k in range(1, n):
            moves = 2 * self._calculate_moves(k) + (2 ** (n - k) - 1)
            min_moves = min(min_moves, moves)
        
        return min_moves
    
    def _add_move(self, from_peg: str, to_peg: str):
        """Add a move to the sequence"""
        self.move_sequence.append(f"{from_peg}->{to_peg}")


# Example usage
if __name__ == "__main__":
    solver = IterativeFourPeg()
    
    print("🗼 Iterative 4-Peg Tower of Hanoi (Frame-Stewart)")
    print("=" * 50)
    
    for n in range(3, 8):
        result = solver.solve(n)
        optimal_3peg = 2**n - 1
        print(f"\n{n} disks:")
        print(f"  Moves: {result['moves']}")
        print(f"  Runtime: {result['runtime_ms']:.4f}ms")
        print(f"  3-peg optimal: {optimal_3peg}")
        print(f"  Improvement: {optimal_3peg - result['moves']} moves")
