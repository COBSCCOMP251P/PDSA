"""
Test Suite for Tower of Hanoi Algorithms
Verifies correctness and performance of all algorithms
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recursive_3peg import RecursiveThreePeg
from iterative_3peg import IterativeThreePeg
from recursive_4peg import RecursiveFourPeg
from iterative_4peg import IterativeFourPeg


def validate_solution(sequence, n, source='A', destination='C', peg_count=3):
    """
    Validate that a move sequence correctly solves the puzzle
    
    Args:
        sequence: List of moves in format "X->Y"
        n: Number of disks
        source: Starting peg
        destination: Goal peg
        peg_count: Number of pegs
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Initialize towers
    towers = {chr(65 + i): [] for i in range(peg_count)}  # A, B, C, (D)
    
    # Place all disks on source tower (largest to smallest)
    for disk in range(n, 0, -1):
        towers[source].append(disk)
    
    # Apply each move
    for i, move in enumerate(sequence):
        try:
            from_peg, to_peg = move.split('->')
            
            # Check if source peg has disks
            if not towers[from_peg]:
                return False, f"Move {i+1}: Cannot move from empty peg {from_peg}"
            
            # Get disk to move
            disk = towers[from_peg].pop()
            
            # Check if move is legal (smaller disk on top)
            if towers[to_peg] and towers[to_peg][-1] < disk:
                return False, f"Move {i+1}: Cannot place disk {disk} on smaller disk {towers[to_peg][-1]}"
            
            # Make the move
            towers[to_peg].append(disk)
            
        except Exception as e:
            return False, f"Move {i+1}: Invalid move format - {str(e)}"
    
    # Check if all disks are on destination
    if len(towers[destination]) != n:
        return False, f"Not all disks reached destination. {len(towers[destination])}/{n} disks on {destination}"
    
    # Check if disks are in correct order (largest to smallest)
    for i in range(n):
        if towers[destination][i] != n - i:
            return False, f"Disks not in correct order on destination"
    
    return True, "Valid solution"


def test_algorithm(algorithm_class, name, test_cases):
    """Test a single algorithm with multiple test cases"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    solver = algorithm_class()
    all_passed = True
    
    for test in test_cases:
        n = test['n']
        expected_moves = test.get('expected_moves')
        peg_count = test.get('peg_count', 3)
        
        # Determine pegs based on peg count
        if peg_count == 3:
            result = solver.solve(n, 'A', 'C', 'B')
            dest = 'C'
        else:
            result = solver.solve(n, 'A', 'D', 'B', 'C')
            dest = 'D'
        
        # Validate solution
        is_valid, message = validate_solution(result['sequence'], n, 'A', dest, peg_count)
        
        # Check move count
        move_count_ok = True
        if expected_moves and result['moves'] != expected_moves:
            move_count_ok = False
        
        # Print results
        status = "✅ PASS" if (is_valid and move_count_ok) else "❌ FAIL"
        print(f"\n{status} - {n} disks, {peg_count} pegs:")
        print(f"  Moves: {result['moves']}", end="")
        if expected_moves:
            print(f" (Expected: {expected_moves})", end="")
        print()
        print(f"  Runtime: {result['runtime_ms']:.4f}ms")
        print(f"  Validation: {message}")
        
        if not is_valid or not move_count_ok:
            all_passed = False
            if not move_count_ok:
                print(f"  ⚠️  Move count mismatch!")
    
    return all_passed


def main():
    """Run all algorithm tests"""
    print("🗼 Tower of Hanoi Algorithm Test Suite")
    print("=" * 60)
    
    # Test cases for 3-peg algorithms
    test_cases_3peg = [
        {'n': 3, 'expected_moves': 7, 'peg_count': 3},
        {'n': 4, 'expected_moves': 15, 'peg_count': 3},
        {'n': 5, 'expected_moves': 31, 'peg_count': 3},
        {'n': 6, 'expected_moves': 63, 'peg_count': 3},
        {'n': 7, 'expected_moves': 127, 'peg_count': 3}
    ]
    
    # Test cases for 4-peg algorithms
    test_cases_4peg = [
        {'n': 3, 'peg_count': 4},
        {'n': 4, 'peg_count': 4},
        {'n': 5, 'expected_moves': 13, 'peg_count': 4},
        {'n': 6, 'expected_moves': 17, 'peg_count': 4},
        {'n': 7, 'expected_moves': 21, 'peg_count': 4}
    ]
    
    all_tests_passed = True
    
    # Test 3-peg algorithms
    all_tests_passed &= test_algorithm(RecursiveThreePeg, "Recursive 3-Peg", test_cases_3peg)
    all_tests_passed &= test_algorithm(IterativeThreePeg, "Iterative 3-Peg", test_cases_3peg)
    
    # Test 4-peg algorithms
    all_tests_passed &= test_algorithm(RecursiveFourPeg, "Recursive 4-Peg (Frame-Stewart)", test_cases_4peg)
    all_tests_passed &= test_algorithm(IterativeFourPeg, "Iterative 4-Peg (Frame-Stewart)", test_cases_4peg)
    
    # Summary
    print(f"\n{'='*60}")
    if all_tests_passed:
        print("🎉 All tests PASSED!")
    else:
        print("❌ Some tests FAILED!")
    print(f"{'='*60}\n")
    
    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
