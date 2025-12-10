"""
Unit Tests for Tower of Hanoi Algorithms
Tests correctness, performance, and edge cases for all algorithm implementations
"""

import pytest
import time
import sys
import os

# Add backend directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from algorithms import (
    RecursiveThreePegAlgorithm,
    IterativeThreePegAlgorithm,
    FrameStewartAlgorithm,
    DynamicProgrammingFourPegAlgorithm,
    AlgorithmRunner,
    solve_tower_of_hanoi
)


class TestAlgorithmResults:
    """Test algorithm result correctness and consistency"""
    
    @pytest.mark.parametrize("n_disks", [3, 4, 5, 6, 7, 8])
    def test_three_peg_recursive_correctness(self, n_disks):
        """Test recursive 3-peg algorithm produces correct results"""
        algorithm = RecursiveThreePegAlgorithm()
        result = algorithm.solve(n_disks)
        
        # Check move count follows 2^n - 1 formula
        expected_moves = 2**n_disks - 1
        assert result.moves == expected_moves, f"Expected {expected_moves} moves, got {result.moves}"
        
        # Check sequence length matches move count
        assert len(result.sequence) == result.moves, "Sequence length doesn't match move count"
        
        # Check all moves are valid format
        for move in result.sequence:
            assert '->' in move, f"Invalid move format: {move}"
            source, dest = move.split('->')
            assert source in ['A', 'B', 'C'], f"Invalid source peg: {source}"
            assert dest in ['A', 'B', 'C'], f"Invalid destination peg: {dest}"
            assert source != dest, f"Source and destination cannot be same: {move}"
    
    @pytest.mark.parametrize("n_disks", [3, 4, 5, 6, 7, 8])
    def test_three_peg_iterative_correctness(self, n_disks):
        """Test iterative 3-peg algorithm produces correct results"""
        algorithm = IterativeThreePegAlgorithm()
        result = algorithm.solve(n_disks)
        
        # Should match recursive algorithm results
        expected_moves = 2**n_disks - 1
        assert result.moves == expected_moves
        assert len(result.sequence) == result.moves
    
    def test_three_peg_algorithms_consistency(self):
        """Test that both 3-peg algorithms produce same results"""
        recursive = RecursiveThreePegAlgorithm()
        iterative = IterativeThreePegAlgorithm()
        
        for n in range(3, 8):
            rec_result = recursive.solve(n)
            iter_result = iterative.solve(n)
            
            # Both should have same move count
            assert rec_result.moves == iter_result.moves, f"Move count mismatch for n={n}"
            
            # Both sequences should be valid (don't need to be identical)
            assert len(rec_result.sequence) == len(iter_result.sequence)
    
    @pytest.mark.parametrize("n_disks", [3, 4, 5, 6, 7])  # Smaller range for 4-peg due to complexity
    def test_four_peg_frame_stewart_correctness(self, n_disks):
        """Test Frame-Stewart algorithm correctness"""
        algorithm = FrameStewartAlgorithm()
        result = algorithm.solve(n_disks, auxiliaries=['B', 'C'])
        
        # Should use fewer moves than 3-peg solution
        three_peg_moves = 2**n_disks - 1
        assert result.moves <= three_peg_moves, f"4-peg should use ≤ moves than 3-peg"
        
        # Check sequence validity
        assert len(result.sequence) == result.moves
        for move in result.sequence:
            assert '->' in move, f"Invalid move format: {move}"
            source, dest = move.split('->')
            assert source in ['A', 'B', 'C', 'D'], f"Invalid source peg: {source}"
            assert dest in ['A', 'B', 'C', 'D'], f"Invalid destination peg: {dest}"
    
    @pytest.mark.parametrize("n_disks", [3, 4, 5, 6])  # Even smaller range for DP due to complexity
    def test_four_peg_dp_correctness(self, n_disks):
        """Test DP 4-peg algorithm correctness"""
        algorithm = DynamicProgrammingFourPegAlgorithm()
        result = algorithm.solve(n_disks, auxiliaries=['B', 'C'])
        
        # Should use fewer moves than 3-peg solution
        three_peg_moves = 2**n_disks - 1
        assert result.moves <= three_peg_moves
        
        # Check sequence validity
        assert len(result.sequence) == result.moves


class TestAlgorithmPerformance:
    """Test algorithm performance and runtime measurement"""
    
    def test_runtime_measurement_accuracy(self):
        """Test that runtime measurement is reasonably accurate"""
        algorithm = RecursiveThreePegAlgorithm()
        
        # Run multiple times to check consistency
        runtimes = []
        for _ in range(5):
            result = algorithm.solve(6)  # Medium complexity
            runtimes.append(result.runtime_ms)
        
        # All runtimes should be positive
        assert all(rt > 0 for rt in runtimes), "All runtimes should be positive"
        
        # Runtimes should be reasonably consistent (within 10x of each other)
        min_runtime = min(runtimes)
        max_runtime = max(runtimes)
        assert max_runtime / min_runtime < 10, "Runtime measurements too inconsistent"
    
    def test_algorithm_efficiency_comparison(self):
        """Test that 4-peg algorithms are more efficient than 3-peg for larger n"""
        n = 7  # Large enough to show difference
        
        # 3-peg algorithms
        recursive_3 = RecursiveThreePegAlgorithm()
        result_3 = recursive_3.solve(n)
        
        # 4-peg algorithms
        frame_stewart = FrameStewartAlgorithm()
        result_4 = frame_stewart.solve(n, auxiliaries=['B', 'C'])
        
        # 4-peg should use fewer moves
        assert result_4.moves < result_3.moves, "4-peg should be more efficient"
        
        # Verify the improvement is significant (at least 20% fewer moves)
        improvement = (result_3.moves - result_4.moves) / result_3.moves
        assert improvement > 0.2, f"Expected >20% improvement, got {improvement:.2%}"


class TestAlgorithmEdgeCases:
    """Test algorithm behavior with edge cases"""
    
    def test_single_disk(self):
        """Test all algorithms with single disk"""
        algorithms = [
            RecursiveThreePegAlgorithm(),
            IterativeThreePegAlgorithm(),
            FrameStewartAlgorithm(),
            DynamicProgrammingFourPegAlgorithm()
        ]
        
        for algorithm in algorithms:
            result = algorithm.solve(1)
            assert result.moves == 1, f"{algorithm.name} should use 1 move for 1 disk"
            assert len(result.sequence) == 1, f"{algorithm.name} should have 1 move in sequence"
            assert result.sequence[0] == 'A->D', f"{algorithm.name} should move A->D"
    
    def test_zero_disks(self):
        """Test algorithms with zero disks (edge case)"""
        # Only test algorithms that handle n=0
        frame_stewart = FrameStewartAlgorithm()
        dp_algorithm = DynamicProgrammingFourPegAlgorithm()
        
        for algorithm in [frame_stewart, dp_algorithm]:
            result = algorithm.solve(0)
            assert result.moves == 0, f"{algorithm.name} should use 0 moves for 0 disks"
            assert len(result.sequence) == 0, f"{algorithm.name} should have empty sequence"
    
    def test_different_peg_labels(self):
        """Test algorithms work with different peg labels"""
        algorithm = RecursiveThreePegAlgorithm()
        result = algorithm.solve(3, source='X', destination='Z', auxiliaries=['Y'])
        
        assert result.moves == 7  # Still 2^3 - 1
        
        # Check all moves use correct peg labels
        for move in result.sequence:
            source, dest = move.split('->')
            assert source in ['X', 'Y', 'Z'], f"Invalid source peg: {source}"
            assert dest in ['X', 'Y', 'Z'], f"Invalid destination peg: {dest}"


class TestAlgorithmRunner:
    """Test the AlgorithmRunner class functionality"""
    
    def test_runner_initialization(self):
        """Test AlgorithmRunner initializes correctly"""
        runner = AlgorithmRunner()
        
        assert len(runner.three_peg_algorithms) == 2
        assert len(runner.four_peg_algorithms) == 2
        
        # Check algorithm names
        three_peg_names = [alg.name for alg in runner.three_peg_algorithms]
        four_peg_names = [alg.name for alg in runner.four_peg_algorithms]
        
        assert 'Recursive 3-Peg' in three_peg_names
        assert 'Iterative 3-Peg' in three_peg_names
        assert 'Frame-Stewart 4-Peg' in four_peg_names
        assert 'DP 4-Peg' in four_peg_names
    
    def test_run_all_algorithms_3_peg(self):
        """Test running all 3-peg algorithms"""
        runner = AlgorithmRunner()
        results = runner.run_all_algorithms(5, 3)
        
        assert len(results) == 2, "Should run 2 algorithms for 3-peg"
        
        for result in results:
            assert result.moves == 31, "All 3-peg algorithms should use 31 moves for 5 disks"
            assert len(result.sequence) == 31
            assert result.runtime_ms > 0
    
    def test_run_all_algorithms_4_peg(self):
        """Test running all 4-peg algorithms"""
        runner = AlgorithmRunner()
        results = runner.run_all_algorithms(5, 4)
        
        assert len(results) == 2, "Should run 2 algorithms for 4-peg"
        
        for result in results:
            assert result.moves <= 31, "4-peg should use ≤ 31 moves for 5 disks"
            assert len(result.sequence) == result.moves
            assert result.runtime_ms > 0
    
    def test_get_algorithm_by_name(self):
        """Test getting algorithms by name"""
        runner = AlgorithmRunner()
        
        recursive_alg = runner.get_algorithm_by_name('Recursive 3-Peg')
        assert isinstance(recursive_alg, RecursiveThreePegAlgorithm)
        
        frame_stewart_alg = runner.get_algorithm_by_name('Frame-Stewart 4-Peg')
        assert isinstance(frame_stewart_alg, FrameStewartAlgorithm)
        
        # Test invalid name
        with pytest.raises(ValueError):
            runner.get_algorithm_by_name('Nonexistent Algorithm')


class TestConvenienceFunction:
    """Test the convenience function for external use"""
    
    def test_solve_tower_of_hanoi_function(self):
        """Test the solve_tower_of_hanoi convenience function"""
        # Test 3-peg
        results_3 = solve_tower_of_hanoi(5, 3)
        assert len(results_3) == 2
        assert all(r.moves == 31 for r in results_3)
        
        # Test 4-peg
        results_4 = solve_tower_of_hanoi(5, 4)
        assert len(results_4) == 2
        assert all(r.moves <= 31 for r in results_4)
    
    def test_solve_with_custom_pegs(self):
        """Test solving with custom peg labels"""
        results = solve_tower_of_hanoi(3, 3, source='X', destination='Z')
        
        for result in results:
            assert result.moves == 7
            # Check moves use correct peg labels
            for move in result.sequence:
                source, dest = move.split('->')
                assert source in ['X', 'Y', 'Z']
                assert dest in ['X', 'Y', 'Z']


class TestAlgorithmMemoization:
    """Test memoization functionality in algorithms"""
    
    def test_frame_stewart_memoization(self):
        """Test Frame-Stewart algorithm uses memoization effectively"""
        algorithm = FrameStewartAlgorithm()
        
        # Run same problem twice
        result1 = algorithm.solve(6, auxiliaries=['B', 'C'])
        result2 = algorithm.solve(6, auxiliaries=['B', 'C'])
        
        # Results should be identical
        assert result1.moves == result2.moves
        
        # Second run should be faster due to memoization
        assert result2.runtime_ms <= result1.runtime_ms * 1.5  # Allow some variance
    
    def test_dp_algorithm_memoization(self):
        """Test DP algorithm uses memoization effectively"""
        algorithm = DynamicProgrammingFourPegAlgorithm()
        
        # Run same problem twice
        result1 = algorithm.solve(5, auxiliaries=['B', 'C'])
        result2 = algorithm.solve(5, auxiliaries=['B', 'C'])
        
        # Results should be identical
        assert result1.moves == result2.moves
        assert result1.sequence == result2.sequence


class TestAlgorithmSequenceValidation:
    """Test that algorithm-generated sequences are valid and solve the puzzle"""
    
    def validate_sequence_manually(self, n_disks, sequence, peg_count=3):
        """Manually validate that a sequence solves the Tower of Hanoi puzzle"""
        # Initialize pegs
        pegs = {'A': list(range(n_disks, 0, -1)), 'B': [], 'C': []}
        if peg_count == 4:
            pegs['D'] = []
        
        valid_pegs = set(pegs.keys())
        
        # Execute each move
        for i, move in enumerate(sequence):
            if '->' not in move:
                return False, f"Invalid move format at {i}: {move}"
            
            source, dest = move.split('->')
            
            # Check valid pegs
            if source not in valid_pegs or dest not in valid_pegs:
                return False, f"Invalid peg at move {i}: {move}"
            
            # Check source has disks
            if not pegs[source]:
                return False, f"Empty source peg at move {i}: {move}"
            
            # Check destination constraint
            disk = pegs[source][-1]
            if pegs[dest] and pegs[dest][-1] < disk:
                return False, f"Larger on smaller at move {i}: {move}"
            
            # Execute move
            pegs[dest].append(pegs[source].pop())
        
        # Check if puzzle is solved
        target_peg = 'D' if peg_count == 4 else 'C'  # Assuming destination is D for 4-peg, C for 3-peg
        expected_stack = list(range(n_disks, 0, -1))
        
        if pegs[target_peg] != expected_stack:
            return False, f"Puzzle not solved. Final state: {pegs}"
        
        return True, "Valid solution"
    
    @pytest.mark.parametrize("n_disks", [3, 4, 5])
    def test_recursive_3_peg_sequence_validity(self, n_disks):
        """Test that recursive 3-peg generates valid sequences"""
        algorithm = RecursiveThreePegAlgorithm()
        result = algorithm.solve(n_disks, destination='C')  # Use C as destination for 3-peg
        
        is_valid, message = self.validate_sequence_manually(n_disks, result.sequence, 3)
        assert is_valid, f"Invalid sequence: {message}"
    
    @pytest.mark.parametrize("n_disks", [3, 4, 5])
    def test_iterative_3_peg_sequence_validity(self, n_disks):
        """Test that iterative 3-peg generates valid sequences"""
        algorithm = IterativeThreePegAlgorithm()
        result = algorithm.solve(n_disks, destination='C')  # Use C as destination for 3-peg
        
        is_valid, message = self.validate_sequence_manually(n_disks, result.sequence, 3)
        assert is_valid, f"Invalid sequence: {message}"
    
    @pytest.mark.parametrize("n_disks", [3, 4, 5])
    def test_frame_stewart_sequence_validity(self, n_disks):
        """Test that Frame-Stewart generates valid sequences"""
        algorithm = FrameStewartAlgorithm()
        result = algorithm.solve(n_disks, auxiliaries=['B', 'C'])
        
        is_valid, message = self.validate_sequence_manually(n_disks, result.sequence, 4)
        assert is_valid, f"Invalid sequence: {message}"


if __name__ == "__main__":
    # Run tests with coverage reporting
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=algorithms",
        "--cov-report=term-missing",
        "--cov-report=html"
    ])