"""
Integration Tests for Snake and Ladder Game
Tests complete game flow and API integration
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.game_logic import SnakeLadderBoard, generate_answer_choices
from algorithms.pathfinding import find_min_moves_bfs, find_min_moves_dfs, validate_answer


class TestGameFlow(unittest.TestCase):
    """Test complete game flow from start to finish."""
    
    def test_complete_game_flow(self):
        """Test complete game flow: setup, play, validate."""
        # Setup
        board_size = 8
        board = SnakeLadderBoard(board_size)
        
        # Calculate answers
        bfs_result = find_min_moves_bfs(board)
        dfs_result = find_min_moves_dfs(board)
        
        # Verify both algorithms found a solution
        self.assertGreater(bfs_result.min_moves, 0)
        self.assertGreater(dfs_result.min_moves, 0)
        self.assertEqual(bfs_result.min_moves, dfs_result.min_moves)
        
        # Generate answer choices
        correct_answer = bfs_result.min_moves
        choices = generate_answer_choices(correct_answer)
        
        # Verify choices
        self.assertEqual(len(choices), 3)
        self.assertIn(correct_answer, choices)
        
        # Simulate player choosing correct answer
        player_answer = correct_answer
        is_correct = validate_answer(player_answer, correct_answer)
        
        self.assertTrue(is_correct)
    
    def test_game_flow_incorrect_answer(self):
        """Test game flow with incorrect answer."""
        board = SnakeLadderBoard(8)
        
        bfs_result = find_min_moves_bfs(board)
        correct_answer = bfs_result.min_moves
        
        # Player chooses wrong answer
        player_answer = correct_answer + 1
        is_correct = validate_answer(player_answer, correct_answer)
        
        self.assertFalse(is_correct)
    
    def test_multiple_game_rounds(self):
        """Test multiple game rounds with different boards."""
        for _ in range(5):
            board = SnakeLadderBoard(8)
            
            bfs_result = find_min_moves_bfs(board)
            dfs_result = find_min_moves_dfs(board)
            
            self.assertEqual(bfs_result.min_moves, dfs_result.min_moves)
            self.assertGreater(bfs_result.min_moves, 0)


class TestBoardPersistence(unittest.TestCase):
    """Test board state persistence and reconstruction."""
    
    def test_board_save_and_load(self):
        """Test saving and loading board state."""
        # Create original board
        original_board = SnakeLadderBoard(8)
        
        # Calculate solution
        original_result = find_min_moves_bfs(original_board)
        
        # Save board state
        board_dict = original_board.to_dict()
        
        # Reconstruct board
        loaded_board = SnakeLadderBoard.from_dict(board_dict)
        
        # Calculate solution again
        loaded_result = find_min_moves_bfs(loaded_board)
        
        # Should get same result
        self.assertEqual(original_result.min_moves, loaded_result.min_moves)
    
    def test_json_persistence(self):
        """Test JSON serialization and deserialization."""
        original_board = SnakeLadderBoard(8)
        
        # Serialize to JSON
        json_str = original_board.to_json()
        
        # Deserialize from JSON
        loaded_board = SnakeLadderBoard.from_json(json_str)
        
        # Verify boards are identical
        self.assertEqual(original_board.n, loaded_board.n)
        self.assertEqual(original_board.total_cells, loaded_board.total_cells)
        self.assertEqual(original_board.ladders, loaded_board.ladders)
        self.assertEqual(original_board.snakes, loaded_board.snakes)


class TestAlgorithmConsistency(unittest.TestCase):
    """Test consistency between algorithms."""
    
    def test_algorithms_agree_on_solution(self):
        """Test that both algorithms agree on minimum moves."""
        for size in [6, 8, 10, 12]:
            with self.subTest(size=size):
                board = SnakeLadderBoard(size)
                
                bfs_result = find_min_moves_bfs(board)
                dfs_result = find_min_moves_dfs(board)
                
                self.assertEqual(bfs_result.min_moves, dfs_result.min_moves,
                               f"Algorithms disagree for board size {size}")
    
    def test_algorithms_find_optimal_path(self):
        """Test that algorithms find optimal path."""
        # Create a controlled board
        board = SnakeLadderBoard(8)
        board.ladders = {3: 22, 5: 18}
        board.snakes = {30: 10, 40: 15}
        
        bfs_result = find_min_moves_bfs(board)
        dfs_result = find_min_moves_dfs(board)
        
        # Both should find same optimal solution
        self.assertEqual(bfs_result.min_moves, dfs_result.min_moves)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_board_size(self):
        """Test error handling for invalid board size."""
        with self.assertRaises(ValueError):
            SnakeLadderBoard(5)  # Too small
        
        with self.assertRaises(ValueError):
            SnakeLadderBoard(13)  # Too large
    
    def test_invalid_answer_validation(self):
        """Test error handling for invalid answers."""
        with self.assertRaises(ValueError):
            validate_answer(-1, 5)  # Negative answer
        
        with self.assertRaises(ValueError):
            validate_answer("5", 5)  # String answer


class TestStatisticsCalculation(unittest.TestCase):
    """Test statistics and metrics calculation."""
    
    def test_execution_time_tracking(self):
        """Test that execution time is properly tracked."""
        board = SnakeLadderBoard(8)
        
        bfs_result = find_min_moves_bfs(board)
        dfs_result = find_min_moves_dfs(board)
        
        # Execution times should be positive
        self.assertGreater(bfs_result.execution_time_ms, 0)
        self.assertGreater(dfs_result.execution_time_ms, 0)
        
        # Should be reasonable (under 1 second)
        self.assertLess(bfs_result.execution_time_ms, 1000)
        self.assertLess(dfs_result.execution_time_ms, 1000)
    
    def test_performance_comparison(self):
        """Test performance comparison between algorithms."""
        board = SnakeLadderBoard(10)
        
        bfs_result = find_min_moves_bfs(board)
        dfs_result = find_min_moves_dfs(board)
        
        # Both should complete successfully
        self.assertIsNotNone(bfs_result)
        self.assertIsNotNone(dfs_result)
        
        # Record which is faster (for statistics)
        if bfs_result.execution_time_ms < dfs_result.execution_time_ms:
            faster = "BFS"
        else:
            faster = "DFS"
        
        # Just verify we can determine which is faster
        self.assertIn(faster, ["BFS", "DFS"])


class TestAnswerChoiceGeneration(unittest.TestCase):
    """Test answer choice generation."""
    
    def test_answer_choices_quality(self):
        """Test quality of generated answer choices."""
        for correct_answer in [3, 5, 7, 10, 15]:
            with self.subTest(correct_answer=correct_answer):
                choices = generate_answer_choices(correct_answer)
                
                # Should have 3 choices
                self.assertEqual(len(choices), 3)
                
                # Should include correct answer
                self.assertIn(correct_answer, choices)
                
                # All should be unique
                self.assertEqual(len(choices), len(set(choices)))
                
                # All should be positive
                for choice in choices:
                    self.assertGreater(choice, 0)
    
    def test_answer_choices_reasonable_range(self):
        """Test that wrong choices are in reasonable range."""
        correct_answer = 10
        choices = generate_answer_choices(correct_answer)
        
        # Remove correct answer
        wrong_choices = [c for c in choices if c != correct_answer]
        
        # Wrong choices should be reasonably close
        for wrong in wrong_choices:
            difference = abs(wrong - correct_answer)
            self.assertLessEqual(difference, 10,
                               "Wrong choices should be reasonably close to correct answer")


def run_tests():
    """Run all integration tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGameFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestBoardPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestAlgorithmConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestStatisticsCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestAnswerChoiceGeneration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
