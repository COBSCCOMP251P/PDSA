"""
Tower of Hanoi Algorithm Implementations
Provides four different algorithms with runtime measurement:
- 3-peg: recursive and iterative
- 4-peg: Frame-Stewart and dynamic programming
"""

import time
from typing import List, Tuple, Dict, Any
from abc import ABC, abstractmethod


class AlgorithmResult:
    """Container for algorithm execution results"""
    
    def __init__(self, moves: int, sequence: List[str], runtime_ms: float, algorithm_name: str):
        self.moves = moves
        self.sequence = sequence
        self.runtime_ms = runtime_ms
        self.algorithm_name = algorithm_name
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'moves': self.moves,
            'sequence': self.sequence,
            'runtime_ms': self.runtime_ms,
            'algorithm_name': self.algorithm_name
        }


class TowerOfHanoiAlgorithm(ABC):
    """Abstract base class for Tower of Hanoi algorithms"""
    
    def __init__(self, name: str):
        self.name = name
        self.move_sequence = []
    
    @abstractmethod
    def _solve(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """Implement the actual algorithm logic"""
        pass
    
    def solve(self, n: int, source: str = 'A', destination: str = 'D', auxiliaries: List[str] = None) -> AlgorithmResult:
        """
        Solve Tower of Hanoi and measure runtime
        
        Args:
            n: Number of disks
            source: Source peg label
            destination: Destination peg label
            auxiliaries: List of auxiliary peg labels
        
        Returns:
            AlgorithmResult with moves, sequence, runtime, and algorithm name
        """
        if auxiliaries is None:
            auxiliaries = ['B', 'C']
        
        self.move_sequence = []
        
        start_time = time.perf_counter()
        move_count = self._solve(n, source, destination, auxiliaries)
        end_time = time.perf_counter()
        
        runtime_ms = (end_time - start_time) * 1000
        
        return AlgorithmResult(
            moves=move_count,
            sequence=self.move_sequence.copy(),
            runtime_ms=runtime_ms,
            algorithm_name=self.name
        )
    
    def _add_move(self, from_peg: str, to_peg: str):
        """Add a move to the sequence"""
        self.move_sequence.append(f"{from_peg}->{to_peg}")


class RecursiveThreePegAlgorithm(TowerOfHanoiAlgorithm):
    """Classic recursive algorithm for 3-peg Tower of Hanoi"""
    
    def __init__(self):
        super().__init__("Recursive 3-Peg")
    
    def _solve(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """
        Classic recursive solution: move(n, from, to, aux)
        Time complexity: O(2^n)
        Move count: 2^n - 1
        """
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        auxiliary = auxiliaries[0]  # Use first auxiliary peg
        
        # Move n-1 disks to auxiliary peg
        moves1 = self._solve(n - 1, source, auxiliary, [destination] + auxiliaries[1:])
        
        # Move the largest disk to destination
        self._add_move(source, destination)
        moves2 = 1
        
        # Move n-1 disks from auxiliary to destination
        moves3 = self._solve(n - 1, auxiliary, destination, [source] + auxiliaries[1:])
        
        return moves1 + moves2 + moves3


class IterativeThreePegAlgorithm(TowerOfHanoiAlgorithm):
    """Iterative algorithm for 3-peg Tower of Hanoi using stack simulation"""
    
    def __init__(self):
        super().__init__("Iterative 3-Peg")
    
    def _solve(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """
        Iterative solution using explicit stack to simulate recursion
        More memory efficient than recursive approach
        """
        auxiliary = auxiliaries[0]
        
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


class FrameStewartAlgorithm(TowerOfHanoiAlgorithm):
    """Frame-Stewart algorithm for 4-peg Tower of Hanoi"""
    
    def __init__(self):
        super().__init__("Frame-Stewart 4-Peg")
        self.memo = {}  # Memoization for optimal k values
    
    def _solve(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """
        Frame-Stewart algorithm: tries different k values to minimize moves
        For each k, moves top k disks using 4 pegs, then bottom n-k using 3 pegs
        """
        if n == 0:
            return 0
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        # Memoization key
        key = (n, source, destination, tuple(sorted(auxiliaries)))
        if key in self.memo:
            return self.memo[key]
        
        min_moves = float('inf')
        best_k = 1
        
        # Try all possible k values (1 to n-1)
        for k in range(1, n):
            # Calculate moves for this k without actually performing them
            temp_sequence = self.move_sequence.copy()
            
            aux1, aux2 = auxiliaries[0], auxiliaries[1]
            
            # Move top k disks to first auxiliary using 4 pegs
            moves1 = self._solve_frame_stewart_helper(k, source, aux1, [destination, aux2])
            
            # Move bottom n-k disks to destination using 3 pegs (classical)
            moves2 = self._solve_three_peg_helper(n - k, source, destination, aux2)
            
            # Move k disks from auxiliary to destination using 4 pegs
            moves3 = self._solve_frame_stewart_helper(k, aux1, destination, [source, aux2])
            
            total_moves = moves1 + moves2 + moves3
            
            if total_moves < min_moves:
                min_moves = total_moves
                best_k = k
            
            # Restore sequence to try next k
            self.move_sequence = temp_sequence
        
        # Execute the optimal solution
        aux1, aux2 = auxiliaries[0], auxiliaries[1]
        
        # Execute with best k
        moves1 = self._solve_frame_stewart_helper(best_k, source, aux1, [destination, aux2])
        moves2 = self._solve_three_peg_helper(n - best_k, source, destination, aux2)
        moves3 = self._solve_frame_stewart_helper(best_k, aux1, destination, [source, aux2])
        
        total_moves = moves1 + moves2 + moves3
        self.memo[key] = total_moves
        return total_moves
    
    def _solve_frame_stewart_helper(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """Recursive helper for Frame-Stewart with 4 pegs"""
        if n == 0:
            return 0
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        return self._solve(n, source, destination, auxiliaries)
    
    def _solve_three_peg_helper(self, n: int, source: str, destination: str, auxiliary: str) -> int:
        """Helper for 3-peg classical solution within Frame-Stewart"""
        if n == 0:
            return 0
        if n == 1:
            self._add_move(source, destination)
            return 1
        
        # Classic 3-peg recursion
        moves1 = self._solve_three_peg_helper(n - 1, source, auxiliary, destination)
        self._add_move(source, destination)
        moves2 = 1
        moves3 = self._solve_three_peg_helper(n - 1, auxiliary, destination, source)
        
        return moves1 + moves2 + moves3


class DynamicProgrammingFourPegAlgorithm(TowerOfHanoiAlgorithm):
    """Dynamic Programming approach for 4-peg Tower of Hanoi"""
    
    def __init__(self):
        super().__init__("DP 4-Peg")
        self.dp_table = {}  # Memoization table for optimal move counts
        self.solution_cache = {}  # Cache for actual move sequences
    
    def _solve(self, n: int, source: str, destination: str, auxiliaries: List[str]) -> int:
        """
        Dynamic programming solution that finds optimal move count
        and reconstructs the sequence
        """
        # Calculate optimal moves using DP
        optimal_moves = self._calculate_optimal_moves(n)
        
        # Generate the actual sequence
        self._generate_sequence(n, source, destination, auxiliaries)
        
        return optimal_moves
    
    def _calculate_optimal_moves(self, n: int) -> int:
        """Calculate minimum moves for n disks using DP"""
        if n in self.dp_table:
            return self.dp_table[n]
        
        if n == 0:
            return 0
        if n == 1:
            return 1
        if n == 2:
            self.dp_table[n] = 3
            return 3
        
        # For 4-peg DP: try all possible splits
        min_moves = float('inf')
        
        for i in range(1, n):
            # Move top i disks to auxiliary using optimal 4-peg solution
            moves_top = self._calculate_optimal_moves(i)
            
            # Move bottom n-i disks using classical 3-peg (2^(n-i) - 1)
            moves_bottom = (2 ** (n - i)) - 1
            
            # Move top i disks from auxiliary to destination
            moves_final = self._calculate_optimal_moves(i)
            
            total_moves = 2 * moves_top + moves_bottom
            min_moves = min(min_moves, total_moves)
        
        self.dp_table[n] = min_moves
        return min_moves
    
    def _generate_sequence(self, n: int, source: str, destination: str, auxiliaries: List[str]):
        """Generate the actual move sequence using the DP solution"""
        if n == 0:
            return
        if n == 1:
            self._add_move(source, destination)
            return
        
        # Find the optimal split point
        optimal_moves = self.dp_table[n]
        aux1, aux2 = auxiliaries[0], auxiliaries[1]
        
        for i in range(1, n):
            moves_top = self._calculate_optimal_moves(i)
            moves_bottom = (2 ** (n - i)) - 1
            
            if 2 * moves_top + moves_bottom == optimal_moves:
                # This is the optimal split
                
                # Move top i disks to first auxiliary
                self._generate_sequence(i, source, aux1, [destination, aux2])
                
                # Move bottom n-i disks to destination using 3-peg
                self._generate_three_peg_sequence(n - i, source, destination, aux2)
                
                # Move top i disks from auxiliary to destination
                self._generate_sequence(i, aux1, destination, [source, aux2])
                
                break
    
    def _generate_three_peg_sequence(self, n: int, source: str, destination: str, auxiliary: str):
        """Generate sequence for classical 3-peg solution"""
        if n == 0:
            return
        if n == 1:
            self._add_move(source, destination)
            return
        
        # Classic 3-peg recursion
        self._generate_three_peg_sequence(n - 1, source, auxiliary, destination)
        self._add_move(source, destination)
        self._generate_three_peg_sequence(n - 1, auxiliary, destination, source)


class AlgorithmRunner:
    """Manages and runs all Tower of Hanoi algorithms"""
    
    def __init__(self):
        self.three_peg_algorithms = [
            RecursiveThreePegAlgorithm(),
            IterativeThreePegAlgorithm()
        ]
        
        self.four_peg_algorithms = [
            FrameStewartAlgorithm(),
            DynamicProgrammingFourPegAlgorithm()
        ]
    
    def run_all_algorithms(self, n: int, peg_count: int, source: str = 'A', destination: str = 'D') -> List[AlgorithmResult]:
        """
        Run all appropriate algorithms for the given configuration
        
        Args:
            n: Number of disks
            peg_count: Number of pegs (3 or 4)
            source: Source peg label
            destination: Destination peg label
        
        Returns:
            List of AlgorithmResult objects
        """
        results = []
        
        if peg_count == 3:
            auxiliaries = ['B', 'C']
            for algorithm in self.three_peg_algorithms:
                try:
                    result = algorithm.solve(n, source, destination, auxiliaries)
                    results.append(result)
                except Exception as e:
                    print(f"Error running {algorithm.name}: {e}")
        
        elif peg_count == 4:
            auxiliaries = ['B', 'C']
            for algorithm in self.four_peg_algorithms:
                try:
                    result = algorithm.solve(n, source, destination, auxiliaries)
                    results.append(result)
                except Exception as e:
                    print(f"Error running {algorithm.name}: {e}")
        
        return results
    
    def get_algorithm_by_name(self, name: str) -> TowerOfHanoiAlgorithm:
        """Get a specific algorithm by name"""
        all_algorithms = self.three_peg_algorithms + self.four_peg_algorithms
        for algorithm in all_algorithms:
            if algorithm.name == name:
                return algorithm
        raise ValueError(f"Algorithm '{name}' not found")


# Convenience function for external use
def solve_tower_of_hanoi(n: int, peg_count: int, source: str = 'A', destination: str = 'D') -> List[AlgorithmResult]:
    """
    Solve Tower of Hanoi using all available algorithms
    
    Args:
        n: Number of disks (5-10)
        peg_count: Number of pegs (3 or 4)
        source: Source peg label
        destination: Destination peg label
    
    Returns:
        List of algorithm results
    """
    runner = AlgorithmRunner()
    return runner.run_all_algorithms(n, peg_count, source, destination)


if __name__ == "__main__":
    # Example usage and benchmarking
    print("🗼 Tower of Hanoi Algorithm Benchmarking")
    print("=" * 50)
    
    for n in range(5, 11):
        print(f"\n📊 Benchmarking {n} disks:")
        
        # 3-peg algorithms
        print("  3-Peg Algorithms:")
        results_3 = solve_tower_of_hanoi(n, 3)
        for result in results_3:
            print(f"    {result.algorithm_name}: {result.moves} moves, {result.runtime_ms:.3f}ms")
        
        # 4-peg algorithms (only for smaller n to avoid long runtimes)
        if n <= 8:
            print("  4-Peg Algorithms:")
            results_4 = solve_tower_of_hanoi(n, 4)
            for result in results_4:
                print(f"    {result.algorithm_name}: {result.moves} moves, {result.runtime_ms:.3f}ms")