"""
Unit Tests for Tower of Hanoi Move Validator
Tests validation logic, error detection, and edge cases
"""

import pytest
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from validator import (
    GameState,
    ValidationError,
    MoveValidator,
    GameValidator,
    validate_tower_of_hanoi_solution,
    parse_move_sequence
)


class TestGameState:
    """Test GameState class functionality"""
    
    def test_game_state_initialization(self):
        """Test GameState initializes correctly"""
        state = GameState(3, 3, 'A', 'D')
        
        assert state.n_disks == 3
        assert state.peg_count == 3
        assert state.source == 'A'
        assert state.destination == 'D'
        assert state.move_count == 0
        
        # Check initial configuration
        assert state.pegs['A'] == [3, 2, 1]  # Largest at bottom
        assert state.pegs['B'] == []
        assert state.pegs['C'] == []
        assert 'D' not in state.pegs  # 3-peg game
        
        assert state.valid_pegs == {'A', 'B', 'C'}
    
    def test_game_state_4_peg_initialization(self):
        """Test GameState with 4 pegs"""
        state = GameState(4, 4, 'A', 'D')
        
        assert state.pegs['A'] == [4, 3, 2, 1]
        assert state.pegs['D'] == []
        assert state.valid_pegs == {'A', 'B', 'C', 'D'}
    
    def test_get_top_disk(self):
        """Test getting top disk from pegs"""
        state = GameState(3, 3)
        
        assert state.get_top_disk('A') == 1  # Smallest disk on top
        assert state.get_top_disk('B') is None  # Empty peg
        
        # Move a disk and test
        state.pegs['B'].append(state.pegs['A'].pop())
        assert state.get_top_disk('A') == 2
        assert state.get_top_disk('B') == 1
    
    def test_is_complete(self):
        """Test completion detection"""
        state = GameState(3, 3, 'A', 'D')
        
        assert not state.is_complete()  # Initially not complete
        
        # Move all disks to destination
        state.pegs['D'] = [3, 2, 1]
        state.pegs['A'] = []
        
        assert state.is_complete()
        
        # Wrong order should not be complete
        state.pegs['D'] = [1, 2, 3]
        assert not state.is_complete()
    
    def test_copy_state(self):
        """Test state copying"""
        original = GameState(3, 3)
        copy = original.copy()
        
        assert copy.n_disks == original.n_disks
        assert copy.pegs == original.pegs
        assert copy.pegs is not original.pegs  # Deep copy
        
        # Modify copy shouldn't affect original
        copy.pegs['B'].append(1)
        assert original.pegs['B'] == []
    
    def test_get_state_string(self):
        """Test state string representation"""
        state = GameState(2, 3)
        state_str = state.get_state_string()
        
        assert 'A: [2, 1]' in state_str
        assert 'B: []' in state_str
        assert 'C: []' in state_str


class TestMoveValidator:
    """Test MoveValidator class functionality"""
    
    def test_validate_move_format(self):
        """Test move format validation"""
        validator = MoveValidator()
        
        # Valid moves
        valid, error, pegs = validator.validate_move_format('A->B')
        assert valid
        assert error is None
        assert pegs == ('A', 'B')
        
        valid, error, pegs = validator.validate_move_format('X->Z')
        assert valid
        assert pegs == ('X', 'Z')
        
        # Invalid moves
        invalid_moves = [
            'AB',           # No arrow
            'A->',          # Missing destination
            '->B',          # Missing source
            'A->A',         # Same source and destination
            'A-B',          # Wrong arrow format
            '',             # Empty string
            'A -> B',       # Spaces (should fail strict format)
            123,            # Not a string
        ]
        
        for move in invalid_moves:
            valid, error, pegs = validator.validate_move_format(move)
            assert not valid, f"Move '{move}' should be invalid"
            assert error is not None
            assert pegs is None
    
    def test_validate_move_sequence_valid(self):
        """Test validation of valid move sequences"""
        validator = MoveValidator()
        initial_state = GameState(3, 3, 'A', 'C')
        
        # Valid 3-disk solution
        valid_moves = ['A->C', 'A->B', 'C->B', 'A->C', 'B->A', 'B->C', 'A->C']
        
        is_valid, errors, final_state = validator.validate_move_sequence(valid_moves, initial_state)
        
        assert is_valid
        assert len(errors) == 0
        assert final_state.is_complete()
        assert final_state.move_count == 7
    
    def test_validate_move_sequence_empty(self):
        """Test validation of empty move sequence"""
        validator = MoveValidator()
        initial_state = GameState(3, 3)
        
        is_valid, errors, final_state = validator.validate_move_sequence([], initial_state)
        
        assert not is_valid
        assert len(errors) == 1
        assert errors[0].error_type == 'SEQUENCE_TOO_SHORT'
    
    def test_validate_move_sequence_invalid_format(self):
        """Test validation with invalid move formats"""
        validator = MoveValidator()
        initial_state = GameState(3, 3)
        
        invalid_moves = ['A->B', 'INVALID', 'C->A']
        
        is_valid, errors, final_state = validator.validate_move_sequence(invalid_moves, initial_state)
        
        assert not is_valid
        assert len(errors) >= 1
        assert any(error.error_type == 'INVALID_FORMAT' for error in errors)
    
    def test_validate_move_sequence_invalid_peg(self):
        """Test validation with invalid peg labels"""
        validator = MoveValidator()
        initial_state = GameState(3, 3)  # Only A, B, C pegs
        
        invalid_moves = ['A->D']  # D not available in 3-peg
        
        is_valid, errors, final_state = validator.validate_move_sequence(invalid_moves, initial_state)
        
        assert not is_valid
        assert len(errors) >= 1
        assert any(error.error_type == 'INVALID_PEG' for error in errors)
    
    def test_validate_move_sequence_empty_source(self):
        """Test validation with moves from empty pegs"""
        validator = MoveValidator()
        initial_state = GameState(3, 3)
        
        invalid_moves = ['B->A']  # B is empty initially
        
        is_valid, errors, final_state = validator.validate_move_sequence(invalid_moves, initial_state)
        
        assert not is_valid
        assert len(errors) >= 1
        assert any(error.error_type == 'EMPTY_SOURCE' for error in errors)
    
    def test_validate_move_sequence_larger_on_smaller(self):
        """Test validation with larger disk on smaller disk"""
        validator = MoveValidator()
        initial_state = GameState(3, 3)
        
        # Move small disk first, then try to put large disk on it
        invalid_moves = ['A->B', 'A->B']  # Second move puts disk 2 on disk 1
        
        is_valid, errors, final_state = validator.validate_move_sequence(invalid_moves, initial_state)
        
        assert not is_valid
        assert len(errors) >= 1
        assert any(error.error_type == 'LARGER_ON_SMALLER' for error in errors)
    
    def test_validate_move_sequence_incomplete(self):
        """Test validation with incomplete solution"""
        validator = MoveValidator()
        initial_state = GameState(3, 3, 'A', 'C')
        
        # Valid moves but incomplete solution
        incomplete_moves = ['A->C', 'A->B']
        
        is_valid, errors, final_state = validator.validate_move_sequence(incomplete_moves, initial_state)
        
        assert not is_valid
        assert len(errors) >= 1
        assert any(error.error_type == 'INCOMPLETE_SOLUTION' for error in errors)
        assert not final_state.is_complete()
    
    def test_validate_declared_moves(self):
        """Test declared move count validation"""
        validator = MoveValidator()
        
        # Matching counts
        valid, message = validator.validate_declared_moves(7, 7)
        assert valid
        
        # Non-matching counts
        valid, message = validator.validate_declared_moves(5, 7)
        assert not valid
        
        # With tolerance
        valid, message = validator.validate_declared_moves(6, 7, tolerance=1)
        assert valid
        
        # Negative declared count
        valid, message = validator.validate_declared_moves(-1, 5)
        assert not valid
    
    def test_get_detailed_error_report(self):
        """Test error report generation"""
        validator = MoveValidator()
        
        # No errors
        report = validator.get_detailed_error_report([])
        assert "All moves are valid" in report
        
        # With errors
        error = ValidationError(1, 'A->A', 'SAME_PEG', 'Source and destination are same')
        report = validator.get_detailed_error_report([error])
        
        assert "1 validation error" in report
        assert "Move #1" in report
        assert "A->A" in report
        assert "Source and destination are same" in report


class TestGameValidator:
    """Test GameValidator class functionality"""
    
    def test_validate_submission_valid(self):
        """Test validation of valid submission"""
        validator = GameValidator()
        
        # Valid 3-disk solution
        moves = ['A->C', 'A->B', 'C->B', 'A->C', 'B->A', 'B->C', 'A->C']
        
        result = validator.validate_submission(3, 3, moves, 7)
        
        assert result['is_valid']
        assert result['move_sequence_valid']
        assert result['declared_moves_valid']
        assert result['puzzle_completed']
        assert result['total_moves'] == 7
        assert result['error_count'] == 0
    
    def test_validate_submission_invalid_moves(self):
        """Test validation with invalid moves"""
        validator = GameValidator()
        
        # Invalid moves
        moves = ['A->B', 'A->B']  # Second move invalid
        
        result = validator.validate_submission(3, 3, moves, 2)
        
        assert not result['is_valid']
        assert not result['move_sequence_valid']
        assert result['declared_moves_valid']  # Declared count matches actual
        assert not result['puzzle_completed']
        assert result['error_count'] > 0
    
    def test_validate_submission_wrong_declared_count(self):
        """Test validation with wrong declared count"""
        validator = GameValidator()
        
        # Valid moves but wrong declared count
        moves = ['A->C', 'A->B', 'C->B', 'A->C', 'B->A', 'B->C', 'A->C']
        
        result = validator.validate_submission(3, 3, moves, 5)  # Declared 5, actual 7
        
        assert not result['is_valid']  # Overall invalid due to declared count
        assert result['move_sequence_valid']
        assert not result['declared_moves_valid']
        assert result['puzzle_completed']
    
    def test_validate_submission_4_peg(self):
        """Test validation for 4-peg game"""
        validator = GameValidator()
        
        # Simple valid 2-disk, 4-peg solution
        moves = ['A->B', 'A->D', 'B->D']
        
        result = validator.validate_submission(2, 4, moves, 3, destination='D')
        
        assert result['is_valid']
        assert result['puzzle_completed']


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_validate_tower_of_hanoi_solution(self):
        """Test the main convenience function"""
        # Valid solution
        moves = ['A->C', 'A->B', 'C->B', 'A->C', 'B->A', 'B->C', 'A->C']
        result = validate_tower_of_hanoi_solution(3, 3, moves, 7)
        
        assert result['is_valid']
        assert result['puzzle_completed']
        
        # Invalid solution
        moves = ['A->B', 'A->B']  # Invalid
        result = validate_tower_of_hanoi_solution(3, 3, moves, 2)
        
        assert not result['is_valid']
    
    def test_parse_move_sequence(self):
        """Test move sequence parsing"""
        # Comma-separated
        moves = parse_move_sequence('A->B, A->C, B->C')
        assert moves == ['A->B', 'A->C', 'B->C']
        
        # Newline-separated
        moves = parse_move_sequence('A->B\nA->C\nB->C')
        assert moves == ['A->B', 'A->C', 'B->C']
        
        # Space-separated
        moves = parse_move_sequence('A->B A->C B->C')
        assert moves == ['A->B', 'A->C', 'B->C']
        
        # Mixed separators
        moves = parse_move_sequence('A->B, A->C; B->C\nC->A')
        assert moves == ['A->B', 'A->C', 'B->C', 'C->A']
        
        # Empty string
        moves = parse_move_sequence('')
        assert moves == []
        
        # With extra whitespace
        moves = parse_move_sequence('  A->B  ,  A->C  ')
        assert moves == ['A->B', 'A->C']


class TestValidationErrorHandling:
    """Test error handling and edge cases"""
    
    def test_validation_error_creation(self):
        """Test ValidationError creation and serialization"""
        state = GameState(3, 3)
        error = ValidationError(
            move_index=5,
            move='A->B',
            error_type='TEST_ERROR',
            message='Test error message',
            state=state
        )
        
        error_dict = error.to_dict()
        
        assert error_dict['move_index'] == 5
        assert error_dict['move'] == 'A->B'
        assert error_dict['error_type'] == 'TEST_ERROR'
        assert error_dict['message'] == 'Test error message'
        assert 'A: [3, 2, 1]' in error_dict['state']
    
    def test_large_sequence_validation(self):
        """Test validation with suspiciously large sequences"""
        validator = MoveValidator()
        initial_state = GameState(5, 3)
        
        # Create very long sequence (much longer than needed)
        long_sequence = ['A->B'] * 1000
        
        is_valid, errors, final_state = validator.validate_move_sequence(long_sequence, initial_state)
        
        assert not is_valid
        # Should have error about sequence being too long
        assert any(error.error_type == 'SEQUENCE_TOO_LONG' for error in errors)
    
    def test_boundary_disk_counts(self):
        """Test validation with boundary disk counts"""
        validator = GameValidator()
        
        # Minimum disk count (edge case)
        moves = ['A->C']
        result = validator.validate_submission(1, 3, moves, 1, destination='C')
        assert result['is_valid']
        
        # Test with larger disk count
        # Generate a longer valid sequence for 4 disks
        # 2^4 - 1 = 15 moves for 4 disks
        # This is a simplified test - in practice we'd use the algorithm to generate
        moves_4_disk = ['A->B'] * 15  # Placeholder - not a real solution
        result = validator.validate_submission(4, 3, moves_4_disk, 15)
        # This will fail validation (not a real solution) but tests the system handles 4 disks
        assert not result['is_valid']  # Expected to fail with placeholder moves
        assert result['total_moves'] == 15
    
    def test_different_peg_configurations(self):
        """Test validation with different peg configurations"""
        validator = GameValidator()
        
        # 4-peg configuration
        moves = ['A->B', 'A->D', 'B->D']  # Simple 2-disk solution
        result = validator.validate_submission(2, 4, moves, 3, destination='D')
        assert result['is_valid']
        
        # Custom source and destination
        moves = ['X->Y', 'X->Z', 'Y->Z']
        result = validator.validate_submission(2, 3, moves, 3, source='X', destination='Z')
        assert result['is_valid']


class TestValidationPerformance:
    """Test validation performance and scalability"""
    
    def test_validation_performance(self):
        """Test that validation completes in reasonable time"""
        validator = GameValidator()
        
        # Create moderately complex valid sequence
        moves = ['A->C'] + ['A->B'] * 50 + ['B->C'] * 50  # Not a real solution, just for performance test
        
        import time
        start_time = time.time()
        
        result = validator.validate_submission(8, 3, moves, len(moves))
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Should complete within reasonable time (< 1 second for this size)
        assert validation_time < 1.0, f"Validation took {validation_time:.3f}s, too slow"
    
    def test_memory_usage(self):
        """Test that validation doesn't use excessive memory"""
        validator = GameValidator()
        
        # Create large sequence
        large_moves = ['A->B', 'B->A'] * 500  # 1000 moves total
        
        # This should not crash due to memory issues
        result = validator.validate_submission(10, 3, large_moves, len(large_moves))
        
        # Will be invalid (not a real solution) but should handle the size
        assert result['total_moves'] == 1000


if __name__ == "__main__":
    # Run tests with coverage reporting
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=validator",
        "--cov-report=term-missing",
        "--cov-report=html"
    ])