try:
    import pytest
except ImportError:
    pytest = None  # Will work without pytest

import sys
import time
import json
import hashlib
from pathlib import Path

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from algorithms.sequential_solver import EightQueensSolver
from algorithms.threaded_solver import ThreadedEightQueensSolver
from algorithms.validation import EightQueensValidator


# ============================================
# 1. SEQUENTIAL SOLVER TESTS
# ============================================

class TestSequentialSolver:
    """Tests for Sequential Backtracking Solver"""
    
    def setup_method(self):
        """Run before each test"""
        self.solver = EightQueensSolver()
    
    def test_finds_92_solutions(self):
        """Must find exactly 92 solutions"""
        solutions = self.solver.solve_all()
        assert len(solutions) == 92, f"Expected 92, got {len(solutions)}"
    
    def test_first_solution_is_valid(self):
        """First solution should be valid"""
        solution = self.solver.solve_first()
        assert solution is not None
        assert len(solution) == 8
        assert self.solver.is_complete_solution(solution)
    
    def test_all_solutions_are_valid(self):
        """Every solution must have no conflicts"""
        solutions = self.solver.solve_all()
        for i, sol in enumerate(solutions):
            assert self._is_valid(sol), f"Solution {i} is invalid: {sol}"
    
    def test_no_duplicate_solutions(self):
        """All 92 solutions must be unique"""
        solutions = self.solver.solve_all()
        solution_strings = [str(sol) for sol in solutions]
        unique = set(solution_strings)
        assert len(unique) == 92, "Found duplicate solutions!"
    
    def test_conflict_detection_same_column(self):
        """Detects queens in same column"""
        self.solver.queens = [0, -1, -1, -1, -1, -1, -1, -1]
        # Column 0 is taken, so row 1 col 0 should be unsafe
        assert self.solver._is_safe_placement(1, 0) == False
    
    def test_conflict_detection_diagonal(self):
        """Detects queens on diagonal"""
        self.solver.queens = [0, -1, -1, -1, -1, -1, -1, -1]
        # Queen at (0,0), so (1,1) is diagonal - unsafe
        assert self.solver._is_safe_placement(1, 1) == False
    
    def test_safe_position_allowed(self):
        """Safe positions should be allowed"""
        self.solver.queens = [0, -1, -1, -1, -1, -1, -1, -1]
        # (1, 2) should be safe
        assert self.solver._is_safe_placement(1, 2) == True
    
    def test_records_execution_time(self):
        """Can measure algorithm execution time"""
        start = time.perf_counter()
        self.solver.solve_all()
        elapsed = time.perf_counter() - start
        assert elapsed > 0, "Time should be recorded"
        assert elapsed < 10, "Should complete within 10 seconds"
    
    def _is_valid(self, queens):
        """Helper: Check if solution is valid"""
        for i in range(8):
            for j in range(i + 1, 8):
                if queens[i] == queens[j]:  # Same column
                    return False
                if abs(i - j) == abs(queens[i] - queens[j]):  # Diagonal
                    return False
        return True


# ============================================
# 2. THREADED SOLVER TESTS
# ============================================

class TestThreadedSolver:
    """Tests for Multi-Threaded Solver"""
    
    def setup_method(self):
        """Run before each test"""
        self.solver = ThreadedEightQueensSolver()
    
    def test_finds_92_solutions(self):
        """Must find exactly 92 solutions"""
        solutions = self.solver.solve_all()
        assert len(solutions) == 92, f"Expected 92, got {len(solutions)}"
    
    def test_first_solution_is_valid(self):
        """First solution should be valid"""
        solution = self.solver.solve_first()
        assert solution is not None
        assert len(solution) == 8
    
    def test_all_solutions_are_valid(self):
        """Every solution must have no conflicts"""
        solutions = self.solver.solve_all()
        for sol in solutions:
            assert self._is_valid(sol), f"Invalid solution: {sol}"
    
    def test_no_duplicate_solutions(self):
        """All 92 solutions must be unique"""
        solutions = self.solver.solve_all()
        solution_strings = [str(sol) for sol in solutions]
        unique = set(solution_strings)
        assert len(unique) == 92, "Found duplicate solutions!"
    
    def test_uses_multiple_threads(self):
        """Should use threading (max_workers not None or 1)"""
        # Default should use multiple workers
        assert self.solver.max_workers is None or self.solver.max_workers > 1
    
    def test_records_execution_time(self):
        """Can measure algorithm execution time"""
        start = time.perf_counter()
        self.solver.solve_all()
        elapsed = time.perf_counter() - start
        assert elapsed > 0, "Time should be recorded"
        assert elapsed < 10, "Should complete within 10 seconds"
    
    def _is_valid(self, queens):
        """Helper: Check if solution is valid"""
        for i in range(8):
            for j in range(i + 1, 8):
                if queens[i] == queens[j]:
                    return False
                if abs(i - j) == abs(queens[i] - queens[j]):
                    return False
        return True


# ============================================
# 3. ALGORITHM COMPARISON TESTS
# ============================================

class TestAlgorithmComparison:
    """Compare Sequential vs Threaded Performance"""
    
    def test_both_find_same_count(self):
        """Both algorithms should find 92 solutions"""
        seq = EightQueensSolver()
        threaded = ThreadedEightQueensSolver()
        
        seq_solutions = seq.solve_all()
        threaded_solutions = threaded.solve_all()
        
        assert len(seq_solutions) == 92
        assert len(threaded_solutions) == 92
    
    def test_both_find_same_solutions(self):
        """Both should find the same 92 solutions"""
        seq = EightQueensSolver()
        threaded = ThreadedEightQueensSolver()
        
        seq_solutions = set(tuple(s) for s in seq.solve_all())
        threaded_solutions = set(tuple(s) for s in threaded.solve_all())
        
        assert seq_solutions == threaded_solutions
    
    def test_can_compare_times(self):
        """Can record and compare execution times"""
        seq = EightQueensSolver()
        threaded = ThreadedEightQueensSolver()
        
        # Time sequential
        start = time.perf_counter()
        seq.solve_all()
        seq_time = time.perf_counter() - start
        
        # Time threaded
        start = time.perf_counter()
        threaded.solve_all()
        threaded_time = time.perf_counter() - start
        
        # Both times should be positive
        assert seq_time > 0
        assert threaded_time > 0
        
        # Can calculate speedup
        speedup = seq_time / threaded_time if threaded_time > 0 else 0
        assert speedup > 0


# ============================================
# 4. VALIDATION TESTS
# ============================================

class TestValidation:
    """Tests for Input Validation"""
    
    def setup_method(self):
        self.validator = EightQueensValidator()
    
    def test_valid_solution_passes(self):
        """Known valid solution should pass"""
        valid = [0, 4, 7, 5, 2, 6, 1, 3]  # One of 92 solutions
        result = self.validator.validate_complete_solution(valid)
        assert result['is_valid'] == True
        assert result['is_complete'] == True
    
    def test_invalid_solution_fails(self):
        """Invalid solution should fail"""
        invalid = [0, 0, 0, 0, 0, 0, 0, 0]  # All in column 0
        result = self.validator.validate_complete_solution(invalid)
        assert result['is_valid'] == False
    
    def test_incomplete_solution_detected(self):
        """Incomplete solution should be detected"""
        incomplete = [0, 4, -1, -1, -1, -1, -1, -1]
        result = self.validator.validate_complete_solution(incomplete)
        assert result['is_complete'] == False
    
    def test_column_conflict_detected(self):
        """Column conflicts should be detected"""
        conflict = [0, 0, 7, 5, 2, 6, 1, 3]  # Two queens in col 0
        result = self.validator.validate_complete_solution(conflict)
        assert result['is_valid'] == False
        assert any(c['type'] == 'column' for c in result['conflicts'])
    
    def test_diagonal_conflict_detected(self):
        """Diagonal conflicts should be detected"""
        conflict = [0, 1, 7, 5, 2, 6, 4, 3]  # (0,0) and (1,1) diagonal
        result = self.validator.validate_complete_solution(conflict)
        assert result['is_valid'] == False


# ============================================
# 5. SOLUTION HASH TESTS (for duplicate detection)
# ============================================

class TestSolutionHashing:
    """Tests for Solution Identification"""
    
    def test_same_solution_same_hash(self):
        """Same solution should produce same hash"""
        solution = [0, 4, 7, 5, 2, 6, 1, 3]
        hash1 = hashlib.md5(json.dumps(solution).encode()).hexdigest()
        hash2 = hashlib.md5(json.dumps(solution).encode()).hexdigest()
        assert hash1 == hash2
    
    def test_different_solutions_different_hash(self):
        """Different solutions should have different hashes"""
        sol1 = [0, 4, 7, 5, 2, 6, 1, 3]
        sol2 = [0, 5, 7, 2, 6, 3, 1, 4]
        hash1 = hashlib.md5(json.dumps(sol1).encode()).hexdigest()
        hash2 = hashlib.md5(json.dumps(sol2).encode()).hexdigest()
        assert hash1 != hash2
    
    def test_all_92_have_unique_hash(self):
        """All 92 solutions should have unique hashes"""
        solver = EightQueensSolver()
        solutions = solver.solve_all()
        
        hashes = set()
        for sol in solutions:
            h = hashlib.md5(json.dumps(sol).encode()).hexdigest()
            hashes.add(h)
        
        assert len(hashes) == 92


# ============================================
# 6. GAME LOGIC TESTS
# ============================================

class TestGameLogic:
    """Tests for Game Mechanics"""
    
    def test_empty_board_initialization(self):
        """Board should start empty"""
        solver = EightQueensSolver()
        assert all(pos == -1 for pos in solver.queens)
    
    def test_board_size_is_8(self):
        """Board size must be 8x8"""
        solver = EightQueensSolver()
        assert solver.board_size == 8
        assert len(solver.queens) == 8
    
    def test_queen_placement_range(self):
        """Queen positions must be 0-7"""
        solver = EightQueensSolver()
        solutions = solver.solve_all()
        for sol in solutions:
            for pos in sol:
                assert 0 <= pos <= 7
    
    def test_board_display_correct(self):
        """Board display shows queens correctly"""
        solver = EightQueensSolver()
        solution = [0, 4, 7, 5, 2, 6, 1, 3]
        board = solver.get_board_display(solution)
        
        # Count queens
        queen_count = sum(row.count('Q') for row in board)
        assert queen_count == 8
        
        # Check positions
        for row, col in enumerate(solution):
            assert board[row][col] == 'Q'


# ============================================
# 7. PROGRESS TRACKING TESTS
# ============================================

class TestProgressTracking:
    """Tests for Progress Information"""
    
    def setup_method(self):
        self.validator = EightQueensValidator()
    
    def test_empty_board_zero_progress(self):
        """Empty board should show 0% progress"""
        queens = [-1, -1, -1, -1, -1, -1, -1, -1]
        progress = self.validator.get_progress_info(queens)
        assert progress['queens_placed'] == 0
        assert progress['progress_percentage'] == 0
    
    def test_partial_board_correct_progress(self):
        """Partial board shows correct progress"""
        queens = [0, 4, -1, -1, -1, -1, -1, -1]  # 2 queens
        progress = self.validator.get_progress_info(queens)
        assert progress['queens_placed'] == 2
        assert progress['queens_remaining'] == 6
        assert progress['progress_percentage'] == 25
    
    def test_complete_board_100_progress(self):
        """Complete board shows 100% progress"""
        queens = [0, 4, 7, 5, 2, 6, 1, 3]
        progress = self.validator.get_progress_info(queens)
        assert progress['queens_placed'] == 8
        assert progress['progress_percentage'] == 100


# ============================================
# RUN ALL TESTS
# ============================================

def run_all_tests():
    """Run all tests and show results"""
    print("=" * 60)
    print("EIGHT QUEENS - COMPLETE TEST SUITE")
    print("=" * 60)
    
    test_classes = [
        TestSequentialSolver,
        TestThreadedSolver,
        TestAlgorithmComparison,
        TestValidation,
        TestSolutionHashing,
        TestGameLogic,
        TestProgressTracking
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📦 {test_class.__name__}")
        print("-" * 40)
        
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith('test_')]
        
        for method_name in methods:
            total_tests += 1
            try:
                if hasattr(instance, 'setup_method'):
                    instance.setup_method()
                
                getattr(instance, method_name)()
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                failed_tests.append((test_class.__name__, method_name, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {passed_tests} ✅")
    print(f"Failed:       {len(failed_tests)} {'❌' if failed_tests else ''}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print("\nFailed Tests:")
        for cls, method, error in failed_tests:
            print(f"  - {cls}.{method}: {error}")
    
    print("\n" + "=" * 60)
    
    return len(failed_tests) == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
