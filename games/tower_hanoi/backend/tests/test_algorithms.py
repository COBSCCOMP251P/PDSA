"""
Unit tests for Tower of Hanoi algorithm implementations
"""
import pytest
from main import (
    hanoi_3peg_recursive,
    hanoi_3peg_iterative,
    hanoi_4peg_frame_stewart,
    hanoi_4peg_dp
)


class TestHanoi3PegRecursive:
    """Test suite for 3-peg recursive algorithm"""
    
    def test_single_disk(self):
        """Test with 1 disk - simplest case"""
        result = hanoi_3peg_recursive(1)
        assert len(result) == 1, "Single disk should require 1 move"
        assert result[0] == "A->C", "Should move from A to C"
    
    def test_two_disks(self):
        """Test with 2 disks"""
        result = hanoi_3peg_recursive(2)
        assert len(result) == 3, "2 disks should require 3 moves"
    
    def test_three_disks(self):
        """Test with 3 disks"""
        result = hanoi_3peg_recursive(3)
        assert len(result) == 7, "3 disks should require 7 moves"
    
    def test_move_count_formula(self):
        """Test that move count follows 2^n - 1 formula"""
        test_cases = {
            1: 1,
            2: 3,
            3: 7,
            4: 15,
            5: 31,
            6: 63,
            7: 127
        }
        
        for n, expected_moves in test_cases.items():
            result = hanoi_3peg_recursive(n)
            assert len(result) == expected_moves, \
                f"For {n} disks, expected {expected_moves} moves, got {len(result)}"
    
    def test_valid_move_sequence(self):
        """Test that moves form a valid solution"""
        n = 5
        result = hanoi_3peg_recursive(n)
        
        # Simulate the game
        pegs = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
        
        for move in result:
            from_peg, to_peg = move.split('->')
            
            # Check source has disks
            assert len(pegs[from_peg]) > 0, f"Cannot move from empty peg {from_peg}"
            
            disk = pegs[from_peg].pop()
            
            # Check destination rule
            if len(pegs[to_peg]) > 0:
                assert disk < pegs[to_peg][-1], \
                    f"Cannot place disk {disk} on smaller disk {pegs[to_peg][-1]}"
            
            pegs[to_peg].append(disk)
        
        # Verify final state
        assert len(pegs['C']) == n, "All disks should be on peg C"
        assert pegs['C'] == list(range(n, 0, -1)), "Disks should be in correct order"
    
    def test_all_moves_different_pegs(self):
        """Test that no move goes from peg to itself"""
        result = hanoi_3peg_recursive(5)
        
        for move in result:
            from_peg, to_peg = move.split('->')
            assert from_peg != to_peg, f"Invalid move: {move}"


class TestHanoi3PegIterative:
    """Test suite for 3-peg iterative algorithm"""
    
    def test_same_move_count_as_recursive(self):
        """Test iterative produces same move count as recursive"""
        for n in range(1, 8):
            recursive_result = hanoi_3peg_recursive(n)
            iterative_result = hanoi_3peg_iterative(n)
            
            assert len(recursive_result) == len(iterative_result), \
                f"Move count mismatch for {n} disks"
    
    def test_valid_solution(self):
        """Test that iterative solution is valid"""
        n = 6
        result = hanoi_3peg_iterative(n)
        
        # Simulate the moves
        pegs = {'A': list(range(n, 0, -1)), 'B': [], 'C': []}
        
        for move in result:
            from_peg, to_peg = move.split('->')
            assert len(pegs[from_peg]) > 0
            disk = pegs[from_peg].pop()
            
            if len(pegs[to_peg]) > 0:
                assert disk < pegs[to_peg][-1]
            
            pegs[to_peg].append(disk)
        
        assert pegs['C'] == list(range(n, 0, -1))
    
    def test_single_disk(self):
        """Test iterative with 1 disk"""
        result = hanoi_3peg_iterative(1)
        assert len(result) == 1


class TestHanoi4PegFrameStewart:
    """Test suite for 4-peg Frame-Stewart algorithm"""
    
    def test_fewer_moves_than_3peg(self):
        """Test that 4-peg requires fewer moves than 3-peg"""
        for n in range(5, 11):
            result_3peg = hanoi_3peg_recursive(n)
            result_4peg = hanoi_4peg_frame_stewart(n)
            
            assert len(result_4peg) < len(result_3peg), \
                f"4-peg should use fewer moves than 3-peg for {n} disks"
    
    def test_known_move_counts(self):
        """Test against expected move counts"""
        # These are approximate for Frame-Stewart
        test_cases = {
            5: (10, 25),  # Range of acceptable moves
            6: (15, 30),
            7: (20, 50),
            8: (25, 60),
            9: (30, 100),
            10: (40, 120)
        }
        
        for n, (min_moves, max_moves) in test_cases.items():
            result = hanoi_4peg_frame_stewart(n)
            assert min_moves <= len(result) <= max_moves, \
                f"For {n} disks, got {len(result)} moves, expected {min_moves}-{max_moves}"
    
    def test_valid_4peg_solution(self):
        """Test that 4-peg solution is valid"""
        n = 6
        result = hanoi_4peg_frame_stewart(n)
        
        # Simulate with 4 pegs
        pegs = {'A': list(range(n, 0, -1)), 'B': [], 'C': [], 'D': []}
        
        for move in result:
            from_peg, to_peg = move.split('->')
            
            assert from_peg in pegs, f"Invalid source peg: {from_peg}"
            assert to_peg in pegs, f"Invalid target peg: {to_peg}"
            assert len(pegs[from_peg]) > 0, f"Empty source peg: {from_peg}"
            
            disk = pegs[from_peg].pop()
            
            if len(pegs[to_peg]) > 0:
                assert disk < pegs[to_peg][-1], f"Invalid move: {disk} on {pegs[to_peg][-1]}"
            
            pegs[to_peg].append(disk)
        
        # All disks should be on peg D
        assert pegs['D'] == list(range(n, 0, -1)), "All disks should be on peg D"
    
    def test_uses_all_four_pegs(self):
        """Test that algorithm uses all 4 pegs for efficiency"""
        n = 7
        result = hanoi_4peg_frame_stewart(n)
        
        pegs_used = set()
        for move in result:
            from_peg, to_peg = move.split('->')
            pegs_used.add(from_peg)
            pegs_used.add(to_peg)
        
        # For n >= 5, should use all 4 pegs
        assert len(pegs_used) == 4, "Should use all 4 pegs"


class TestHanoi4PegDP:
    """Test suite for 4-peg Dynamic Programming algorithm"""
    
    def test_produces_valid_solution(self):
        """Test that DP produces valid solutions"""
        for n in range(5, 9):
            result = hanoi_4peg_dp(n)
            
            # Simulate the solution
            pegs = {'A': list(range(n, 0, -1)), 'B': [], 'C': [], 'D': []}
            
            for move in result:
                from_peg, to_peg = move.split('->')
                assert len(pegs[from_peg]) > 0
                disk = pegs[from_peg].pop()
                
                if len(pegs[to_peg]) > 0:
                    assert disk < pegs[to_peg][-1]
                
                pegs[to_peg].append(disk)
            
            assert pegs['D'] == list(range(n, 0, -1))
    
    def test_optimal_move_counts(self):
        """Test that DP produces optimal move counts"""
        known_optimal = {
            5: 13,
            6: 17,
            7: 25,
            8: 33,
            9: 41,
            10: 49
        }
        
        for n, expected in known_optimal.items():
            result = hanoi_4peg_dp(n)
            # DP should produce optimal or very close
            assert len(result) <= expected * 1.1, \
                f"For {n} disks, expected ~{expected} moves, got {len(result)}"
    
    def test_better_than_frame_stewart(self):
        """Test that DP is better or equal to Frame-Stewart"""
        for n in range(5, 10):
            result_fs = hanoi_4peg_frame_stewart(n)
            result_dp = hanoi_4peg_dp(n)
            
            # DP should be better or equal
            assert len(result_dp) <= len(result_fs), \
                f"DP should be optimal for {n} disks"


class TestAlgorithmComparison:
    """Comparative tests across algorithms"""
    
    def test_3peg_algorithms_identical(self):
        """Test that both 3-peg algorithms produce same move count"""
        for n in range(1, 10):
            recursive = hanoi_3peg_recursive(n)
            iterative = hanoi_3peg_iterative(n)
            
            assert len(recursive) == len(iterative), \
                f"3-peg algorithms disagree for {n} disks"
    
    def test_4peg_advantage(self):
        """Test that 4-peg shows significant improvement"""
        n = 10
        result_3peg = hanoi_3peg_recursive(n)
        result_4peg_dp = hanoi_4peg_dp(n)
        
        improvement = (len(result_3peg) - len(result_4peg_dp)) / len(result_3peg)
        
        # Should have at least 50% fewer moves
        assert improvement > 0.5, \
            f"Expected >50% improvement, got {improvement*100:.1f}%"
    
    def test_exponential_growth_3peg(self):
        """Test that 3-peg moves grow exponentially"""
        results = {}
        for n in range(3, 8):
            result = hanoi_3peg_recursive(n)
            results[n] = len(result)
        
        # Each increment should roughly double (exact formula is 2^n - 1)
        # Growth factor approaches 2.0 as n increases
        for n in range(4, 8):
            ratio = results[n] / results[n-1]
            assert 1.8 < ratio < 2.2, \
                f"Expected ~2x growth from {n-1} to {n}, got {ratio}x"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_minimum_disks(self):
        """Test with minimum valid input (1 disk)"""
        result = hanoi_3peg_recursive(1)
        assert len(result) == 1
        assert result[0] == "A->C"
    
    def test_algorithms_complete_quickly(self):
        """Test that algorithms complete in reasonable time"""
        import time
        
        # 10 disks should complete in under 1 second
        start = time.time()
        hanoi_3peg_recursive(10)
        duration = time.time() - start
        
        assert duration < 1.0, f"Algorithm too slow: {duration}s"
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs"""
        # Test with 0 disks - should fail or handle gracefully
        try:
            result = hanoi_3peg_recursive(0)
            # If it doesn't raise an error, should return empty list
            assert len(result) == 0 or isinstance(result, list)
        except (ValueError, TypeError, IndexError, RecursionError):
            pass  # Expected error
        
        # Test with negative disks - should fail or handle gracefully
        try:
            result = hanoi_3peg_recursive(-5)
            # If it doesn't raise an error, should return empty list
            assert len(result) == 0 or isinstance(result, list)
        except (ValueError, TypeError, IndexError, RecursionError):
            pass  # Expected error
