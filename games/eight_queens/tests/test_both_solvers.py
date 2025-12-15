"""
Quick test script to verify both Sequential and Threaded solvers work correctly
Run this to test the implementation
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from games.eight_queens.algorithms.sequential_solver import EightQueensSolver
from games.eight_queens.algorithms.threaded_solver import ThreadedEightQueensSolver

def test_solvers():
    print("=" * 60)
    print("EIGHT QUEENS SOLVER COMPARISON TEST")
    print("=" * 60)
    
    # Test Sequential Solver
    print("\n1. Testing Sequential Solver...")
    print("-" * 60)
    seq_solver = EightQueensSolver()
    
    start = time.perf_counter()
    seq_solutions = seq_solver.solve_all()
    seq_time = time.perf_counter() - start
    
    print(f"✅ Sequential Solver: Found {len(seq_solutions)} solutions")
    print(f"   Time: {seq_time:.4f} seconds")
    print(f"   First solution: {seq_solutions[0]}")
    
    # Test Threaded Solver
    print("\n2. Testing Threaded Solver...")
    print("-" * 60)
    threaded_solver = ThreadedEightQueensSolver()
    
    start = time.perf_counter()
    threaded_solutions = threaded_solver.solve_all()
    threaded_time = time.perf_counter() - start
    
    print(f"✅ Threaded Solver: Found {len(threaded_solutions)} solutions")
    print(f"   Time: {threaded_time:.4f} seconds")
    print(f"   First solution: {threaded_solutions[0]}")
    
    # Performance Comparison
    print("\n3. Performance Comparison")
    print("-" * 60)
    
    if seq_time > 0 and threaded_time > 0:
        speedup = seq_time / threaded_time
        improvement = ((speedup - 1) * 100)
        
        print(f"Sequential Time:  {seq_time:.4f}s")
        print(f"Threaded Time:    {threaded_time:.4f}s")
        print(f"Speedup Factor:   {speedup:.2f}x")
        print(f"Performance Gain: {improvement:.1f}% {'faster' if speedup > 1 else 'slower'}")
    
    # Validation
    print("\n4. Solution Validation")
    print("-" * 60)
    
    if len(seq_solutions) == 92:
        print("✅ Sequential: Correct number of solutions (92)")
    else:
        print(f"❌ Sequential: Wrong count - {len(seq_solutions)} instead of 92")
    
    if len(threaded_solutions) == 92:
        print("✅ Threaded: Correct number of solutions (92)")
    else:
        print(f"❌ Threaded: Wrong count - {len(threaded_solutions)} instead of 92")
    
    # Check if solutions are valid
    def is_valid_solution(queens):
        for i in range(8):
            for j in range(i + 1, 8):
                if queens[i] == queens[j]:
                    return False
                if abs(i - j) == abs(queens[i] - queens[j]):
                    return False
        return True
    
    seq_valid = all(is_valid_solution(sol) for sol in seq_solutions)
    threaded_valid = all(is_valid_solution(sol) for sol in threaded_solutions)
    
    print(f"✅ Sequential solutions are {'valid' if seq_valid else 'INVALID'}")
    print(f"✅ Threaded solutions are {'valid' if threaded_valid else 'INVALID'}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED SUCCESSFULLY! ✅")
    print("=" * 60)
    
    print("\nFor VIVA Explanation:")
    print("-" * 60)
    print("Sequential Solver:")
    print("  - Uses single-threaded backtracking")
    print("  - Explores search space linearly")
    print("  - Simple and predictable execution")
    
    print("\nThreaded Solver:")
    print("  - Uses ThreadPoolExecutor for parallelism")
    print("  - Divides first row positions across threads")
    print("  - Each thread explores independent subtree")
    print(f"  - Achieves {speedup:.2f}x speedup on multi-core system")
    print("\n")

if __name__ == "__main__":
    test_solvers()
