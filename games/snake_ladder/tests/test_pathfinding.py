"""
Unit Tests for Pathfinding Algorithms
Tests BFS, DFS, and algorithm comparison
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.game_logic import SnakeLadderBoard
from algorithms.pathfinding import (
    find_min_moves_bfs,
    find_min_moves_dfs,
    compare_algorithms,
    validate_answer,
    PathfindingResult
)


class TestBFSAlgorithm(unittest.TestCase):
    """Test cases for BFS pathfinding algorithm."""
    
    def test_bfs_simple_board_no_obstacles(self):
        """Test BFS on simple board without snakes or ladders."""
        board = SnakeLadderBoard(6)
        board.ladders = {}
        board.snakes = {}
        
        result = find_min_moves_bfs(board)
        
        self.assertIsInstance(result, PathfindingResult)
        self.assertGreater(result.min_moves, 0)
        self.assertGreater(result.execution_time_ms, 0)
        self.assertEqual(result.algorithm, "bfs")
    
    def test_bfs_returns_positive_moves(self):
        """Test that BFS returns positive number of moves."""
        board = SnakeLadderBoard(8)
        result = find_min_moves_bfs(board)
        
        self.assertGreaterEqual(result.min_moves, 1)
    
    def test_bfs_execution_time_recorded(self):
        """Test that BFS records execution time."""
        board = SnakeLadderBoard(8)
        result = find_min_moves_bfs(board)
        
        self.assertGreater(result.execution_time_ms, 0)
        self.assertIsInstance(result.execution_time_ms, float)
    
    def test_bfs_result_has_path(self):
        """Test that BFS result includes path."""
        board = SnakeLadderBoard(8)
        result = find_min_moves_bfs(board)
        
        self.assertIsInstance(result.path, list)
        self.assertGreater(len(result.path), 0)
        # Path should start at 1 and end at total_cells
        self.assertEqual(result.path[0], 1)
        self.assertEqual(result.path[-1], board.total_cells)
    
    def test_bfs_with_ladders_only(self):
        """Test BFS with only ladders (should reduce moves)."""
        board = SnakeLadderBoard(8)
        board.snakes = {}
        # Ensure we have at least one ladder
        board.ladders[3] = 20
        
        result = find_min_moves_bfs(board)
        
        # Should find optimal path
        self.assertGreater(result.min_moves, 0)
    
    def test_bfs_consistency(self):
        """Test that BFS returns same result for same board."""
        board = SnakeLadderBoard(8)
        
        result1 = find_min_moves_bfs(board)
        result2 = find_min_moves_bfs(board)
        
        self.assertEqual(result1.min_moves, result2.min_moves)
    
    def test_bfs_to_dict(self):
        """Test PathfindingResult to_dict method."""
        board = SnakeLadderBoard(8)
        result = find_min_moves_bfs(board)
        
        result_dict = result.to_dict()
        
        self.assertIn('min_moves', result_dict)
        self.assertIn('execution_time_ms', result_dict)
        self.assertIn('algorithm', result_dict)
        self.assertIn('path', result_dict)
        self.assertEqual(result_dict['algorithm'], 'bfs')


class TestDFSAlgorithm(unittest.TestCase):
    """Test cases for DFS pathfinding algorithm."""
    
    def test_dfs_simple_board(self):
        """Test DFS on simple board."""
        board = SnakeLadderBoard(6)
        board.ladders = {}
        board.snakes = {}
        
        result = find_min_moves_dfs(board)
        
        self.assertIsInstance(result, PathfindingResult)
        self.assertGreater(result.min_moves, 0)
        self.assertGreater(result.execution_time_ms, 0)
        self.assertEqual(result.algorithm, "dfs")
    
    def test_dfs_returns_positive_moves(self):
        """Test that DFS returns positive number of moves."""
        board = SnakeLadderBoard(8)
        result = find_min_moves_dfs(board)
        
        self.assertGreaterEqual(result.min_moves, 1)
    
    def test_dfs_execution_time_recorded(self):
        """Test that DFS records execution time."""
        board = SnakeLadderBoard(8)
        result = find_min_moves_dfs(board)
        
        self.assertGreater(result.execution_time_ms, 0)
        self.assertIsInstance(result.execution_time_ms, float)
    
    def test_dfs_result_has_path(self):
        """Test that DFS result includes path."""
        board = SnakeLadderBoard(8)
        result = find_min_moves_dfs(board)
        
        self.assertIsInstance(result.path, list)
        self.assertGreater(len(result.path), 0)
        # Path should start at 1 and end at total_cells
        self.assertEqual(result.path[0], 1)
        self.assertEqual(result.path[-1], board.total_cells)
    
    def test_dfs_consistency(self):
        """Test that DFS returns same result for same board."""
        board = SnakeLadderBoard(8)
        
        result1 = find_min_moves_dfs(board)
        result2 = find_min_moves_dfs(board)
        
        self.assertEqual(result1.min_moves, result2.min_moves)


class TestAlgorithmComparison(unittest.TestCase):
    """Test cases for algorithm comparison."""
    
    def test_compare_algorithms_returns_both_results(self):
        """Test that compare_algorithms returns both BFS and DFS results."""
        board = SnakeLadderBoard(8)
        
        bfs_result, dfs_result = compare_algorithms(board)
        
        self.assertIsInstance(bfs_result, PathfindingResult)
        self.assertIsInstance(dfs_result, PathfindingResult)
        self.assertEqual(bfs_result.algorithm, "bfs")
        self.assertEqual(dfs_result.algorithm, "dfs")
    
    def test_both_algorithms_find_same_minimum(self):
        """Test that both algorithms find the same minimum moves."""
        board = SnakeLadderBoard(8)
        
        bfs_result, dfs_result = compare_algorithms(board)
        
        # Both should find the optimal solution
        self.assertEqual(bfs_result.min_moves, dfs_result.min_moves,
                        "BFS and DFS should find same minimum moves")
    
    def test_algorithms_on_different_board_sizes(self):
        """Test algorithms on different board sizes."""
        for size in [6, 8, 10]:
            board = SnakeLadderBoard(size)
            
            bfs_result, dfs_result = compare_algorithms(board)
            
            self.assertGreater(bfs_result.min_moves, 0)
            self.assertGreater(dfs_result.min_moves, 0)
            self.assertEqual(bfs_result.min_moves, dfs_result.min_moves)


class TestAnswerValidation(unittest.TestCase):
    """Test cases for answer validation."""
    
    def test_validate_answer_correct(self):
        """Test validation with correct answer."""
        self.assertTrue(validate_answer(5, 5))
        self.assertTrue(validate_answer(10, 10))
        self.assertTrue(validate_answer(1, 1))
    
    def test_validate_answer_incorrect(self):
        """Test validation with incorrect answer."""
        self.assertFalse(validate_answer(5, 6))
        self.assertFalse(validate_answer(10, 8))
        self.assertFalse(validate_answer(3, 5))
    
    def test_validate_answer_invalid_input(self):
        """Test validation with invalid input."""
        with self.assertRaises(ValueError):
            validate_answer("5", 5)
        
        with self.assertRaises(ValueError):
            validate_answer(5.5, 5)
    
    def test_validate_answer_negative(self):
        """Test validation with negative answer."""
        with self.assertRaises(ValueError):
            validate_answer(-1, 5)


class TestPerformance(unittest.TestCase):
    """Test cases for algorithm performance."""
    
    def test_bfs_performance_small_board(self):
        """Test BFS performance on small board."""
        board = SnakeLadderBoard(6)
        result = find_min_moves_bfs(board)
        
        # Should complete quickly (under 100ms)
        self.assertLess(result.execution_time_ms, 100,
                       "BFS should complete quickly on small board")
    
    def test_dfs_performance_small_board(self):
        """Test DFS performance on small board."""
        board = SnakeLadderBoard(6)
        result = find_min_moves_dfs(board)
        
        # Should complete quickly (under 100ms)
        self.assertLess(result.execution_time_ms, 100,
                       "DFS should complete quickly on small board")
    
    def test_bfs_performance_large_board(self):
        """Test BFS performance on large board."""
        board = SnakeLadderBoard(12)
        result = find_min_moves_bfs(board)
        
        # Should still complete in reasonable time (under 1000ms)
        self.assertLess(result.execution_time_ms, 1000,
                       "BFS should complete in reasonable time on large board")
    
    def test_algorithms_complete_in_reasonable_time(self):
        """Test that both algorithms complete in reasonable time."""
        board = SnakeLadderBoard(10)
        
        bfs_result, dfs_result = compare_algorithms(board)
        
        self.assertLess(bfs_result.execution_time_ms, 1000)
        self.assertLess(dfs_result.execution_time_ms, 1000)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases for pathfinding."""
    
    def test_minimum_board_size(self):
        """Test pathfinding on minimum board size."""
        board = SnakeLadderBoard(6)
        
        bfs_result = find_min_moves_bfs(board)
        dfs_result = find_min_moves_dfs(board)
        
        self.assertGreater(bfs_result.min_moves, 0)
        self.assertGreater(dfs_result.min_moves, 0)
    
    def test_maximum_board_size(self):
        """Test pathfinding on maximum board size."""
        board = SnakeLadderBoard(12)
        
        bfs_result = find_min_moves_bfs(board)
        dfs_result = find_min_moves_dfs(board)
        
        self.assertGreater(bfs_result.min_moves, 0)
        self.assertGreater(dfs_result.min_moves, 0)
    
    def test_board_with_many_ladders(self):
        """Test pathfinding on board with many ladders."""
        board = SnakeLadderBoard(8)
        # Add extra ladders
        board.ladders[2] = 15
        board.ladders[5] = 25
        board.ladders[10] = 35
        
        result = find_min_moves_bfs(board)
        
        # Should still find valid path
        self.assertGreater(result.min_moves, 0)
    
    def test_board_with_many_snakes(self):
        """Test pathfinding on board with many snakes."""
        board = SnakeLadderBoard(8)
        # Add extra snakes
        board.snakes[30] = 10
        board.snakes[40] = 15
        board.snakes[50] = 20
        
        result = find_min_moves_bfs(board)
        
        # Should still find valid path
        self.assertGreater(result.min_moves, 0)


def run_tests():
    """Run all unit tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBFSAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestDFSAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestAlgorithmComparison))
    suite.addTests(loader.loadTestsFromTestCase(TestAnswerValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
