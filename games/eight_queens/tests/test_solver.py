import pytest
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from algorithms.sequential_solver import EightQueensSolver
from algorithms.validation import EightQueensValidator, ConflictAnalyzer


class TestEightQueensSolver:
    """Test cases for the EightQueensSolver class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.solver = EightQueensSolver()
    
    def test_solver_initialization(self):
        """Test that solver initializes correctly."""
        assert self.solver.board_size == 8
        assert len(self.solver.queens) == 8
        assert all(pos == -1 for pos in self.solver.queens)
        assert self.solver.solutions == []
    
    def test_solve_first_solution(self):
        """Test finding the first solution."""
        solution = self.solver.solve_first()
        
        # Should find a valid solution
        assert solution is not None
        assert len(solution) == 8
        assert all(0 <= pos <= 7 for pos in solution)
        assert len(set(solution)) == 8  # All different columns
        
        # Verify it's a valid solution
        assert self.solver.is_complete_solution(solution)
    
    def test_solve_all_solutions(self):
        """Test finding all 92 solutions."""
        solutions = self.solver.solve_all()
        
        # Should find exactly 92 solutions
        assert len(solutions) == 92
        
        # Each solution should be valid
        for solution in solutions:
            assert len(solution) == 8
            assert all(0 <= pos <= 7 for pos in solution)
            assert len(set(solution)) == 8  # All different columns
            assert self.solver.is_complete_solution(solution)
    
    def test_conflict_detection(self):
        """Test the conflict detection logic."""
        # Test safe placement
        self.solver.queens = [-1, -1, -1, -1, -1, -1, -1, -1]
        assert self.solver._is_safe_placement(0, 0) == True
        
        # Place first queen and test conflicts
        self.solver.queens[0] = 0
        assert self.solver._is_safe_placement(1, 0) == False  # Same column
        assert self.solver._is_safe_placement(1, 1) == False  # Diagonal
        assert self.solver._is_safe_placement(1, 2) == True   # Safe
        
        # Place second queen and test more conflicts
        self.solver.queens[1] = 2
        assert self.solver._is_safe_placement(2, 0) == False  # Same column as first
        assert self.solver._is_safe_placement(2, 2) == False  # Same column as second
        assert self.solver._is_safe_placement(2, 4) == False  # Diagonal with second
        assert self.solver._is_safe_placement(2, 5) == True   # Safe
    
    def test_known_solution(self):
        """Test with a known valid solution."""
        known_solution = [0, 2, 5, 7, 1, 3, 6, 4]  # Valid 8-queens solution
        
        assert self.solver.is_complete_solution(known_solution)
        
        # Test board display
        board = self.solver.get_board_display(known_solution)
        assert len(board) == 8
        assert len(board[0]) == 8
        
        # Count queens on board
        queen_count = sum(row.count('Q') for row in board)
        assert queen_count == 8
    
    def test_step_by_step_solving(self):
        """Test step-by-step solving with recording."""
        solution, steps = self.solver.solve_step_by_step()
        
        assert solution is not None
        assert len(steps) > 0
        assert all('action' in step for step in steps)
        assert all('message' in step for step in steps)
        
        # Should end with solution found
        final_step = steps[-1]
        assert final_step['action'] == 'solution_found'


class TestEightQueensValidator:
    """Test cases for the EightQueensValidator class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.validator = EightQueensValidator()
    
    def test_validator_initialization(self):
        """Test that validator initializes correctly."""
        assert self.validator.board_size == 8
        assert self.validator.solver is not None
    
    def test_valid_move_validation(self):
        """Test move validation logic."""
        queens = [-1, -1, -1, -1, -1, -1, -1, -1]
        
        # First move should always be valid
        assert self.validator.is_valid_move(queens, 0, 0) == True
        assert self.validator.is_valid_move(queens, 0, 7) == True
        
        # Place first queen and test conflicts
        queens[0] = 0
        assert self.validator.is_valid_move(queens, 1, 0) == False  # Same column
        assert self.validator.is_valid_move(queens, 1, 1) == False  # Diagonal
        assert self.validator.is_valid_move(queens, 1, 2) == True   # Valid move
        
        # Test placing in same row as existing queen
        assert self.validator.is_valid_move(queens, 0, 3) == False  # Row already occupied
    
    def test_safe_moves_detection(self):
        """Test finding all safe moves for a position."""
        queens = [-1, -1, -1, -1, -1, -1, -1, -1]
        
        # Empty board should have many safe moves
        safe_moves = self.validator.get_safe_moves(queens)
        assert len(safe_moves) == 64  # All squares are safe initially
        
        # Place some queens and test
        queens[0] = 0
        queens[1] = 2
        safe_moves = self.validator.get_safe_moves(queens)
        assert len(safe_moves) < 64  # Should be fewer safe moves
        assert (0, 1) not in safe_moves  # Should not include occupied rows
        assert (1, 3) not in safe_moves  # Should not include occupied rows
    
    def test_hint_generation(self):
        """Test hint generation for partial solutions."""
        queens = [-1, -1, -1, -1, -1, -1, -1, -1]
        
        # Should be able to get hint for empty board
        hint = self.validator.get_next_hint(queens)
        assert hint is not None
        assert len(hint) == 2  # (row, col)
        assert 0 <= hint[0] <= 7
        assert 0 <= hint[1] <= 7
    
    def test_complete_solution_validation(self):
        """Test validation of complete solutions."""
        # Test valid solution
        valid_solution = [0, 2, 5, 7, 1, 3, 6, 4]
        result = self.validator.validate_complete_solution(valid_solution)
        
        assert result['is_valid'] == True
        assert result['is_complete'] == True
        assert len(result['conflicts']) == 0
        
        # Test invalid solution (column conflict)
        invalid_solution = [0, 0, 5, 7, 1, 3, 6, 4]  # Two queens in column 0
        result = self.validator.validate_complete_solution(invalid_solution)
        
        assert result['is_valid'] == False
        assert len(result['conflicts']) > 0
        assert any(conflict['type'] == 'column' for conflict in result['conflicts'])
        
        # Test incomplete solution
        incomplete_solution = [0, 2, 5, 7, -1, -1, -1, -1]
        result = self.validator.validate_complete_solution(incomplete_solution)
        
        assert result['is_complete'] == False
        assert result['is_valid'] == False
    
    def test_progress_tracking(self):
        """Test progress information generation."""
        queens = [-1, -1, -1, -1, -1, -1, -1, -1]
        
        # Empty board progress
        progress = self.validator.get_progress_info(queens)
        assert progress['queens_placed'] == 0
        assert progress['queens_remaining'] == 8
        assert progress['progress_percentage'] == 0
        
        # Partial solution progress
        queens[0] = 0
        queens[1] = 2
        progress = self.validator.get_progress_info(queens)
        assert progress['queens_placed'] == 2
        assert progress['queens_remaining'] == 6
        assert progress['progress_percentage'] == 25


class TestConflictAnalyzer:
    """Test cases for the ConflictAnalyzer class."""
    
    def test_position_conflict_analysis(self):
        """Test detailed conflict analysis for positions."""
        queens = [0, -1, -1, -1, -1, -1, -1, -1]
        
        # Test column conflict
        conflicts = ConflictAnalyzer.analyze_position_conflicts(queens, 1, 0)
        assert conflicts['has_conflict'] == True
        assert 'column' in conflicts['conflict_types']
        assert (0, 0) in conflicts['conflicting_queens']
        
        # Test diagonal conflict
        conflicts = ConflictAnalyzer.analyze_position_conflicts(queens, 1, 1)
        assert conflicts['has_conflict'] == True
        assert 'diagonal' in conflicts['conflict_types']
        
        # Test safe position
        conflicts = ConflictAnalyzer.analyze_position_conflicts(queens, 1, 2)
        assert conflicts['has_conflict'] == False
    
    def test_attack_pattern_generation(self):
        """Test generation of queen attack patterns."""
        # Queen at (0, 0)
        attacked = ConflictAnalyzer.get_attack_pattern(0, 0)
        
        # Should attack entire first row and first column
        assert (0, 7) in attacked  # Row attack
        assert (7, 0) in attacked  # Column attack
        assert (3, 3) in attacked  # Diagonal attack
        
        # Should not include queen's own position
        assert (0, 0) not in attacked
        
        # Test queen in center
        attacked = ConflictAnalyzer.get_attack_pattern(3, 3)
        assert len(attacked) > 20  # Should attack many squares
        assert (3, 0) in attacked  # Row attack
        assert (0, 3) in attacked  # Column attack
        assert (0, 0) in attacked  # Diagonal attack
        assert (7, 7) in attacked  # Diagonal attack


# Test runner function for development
def run_tests():
    """Run all tests and print results."""
    import traceback
    
    test_classes = [TestEightQueensSolver, TestEightQueensValidator, TestConflictAnalyzer]
    
    for test_class in test_classes:
        print(f"\\nRunning {test_class.__name__}...")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            try:
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                method = getattr(test_instance, method_name)
                method()
                print(f"  ✓ {method_name}")
                
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")
                traceback.print_exc()
    
    print("\\nTest run complete!")


if __name__ == "__main__":
    run_tests()