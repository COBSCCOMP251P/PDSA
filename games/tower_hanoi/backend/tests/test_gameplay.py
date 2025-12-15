"""
Unit tests for Tower of Hanoi gameplay functionality
Tests gameplay session saving, algorithm detection, and game flow

Note: These tests document the expected behavior and can serve as integration tests
when the backend server is running on port 8000.
"""
import pytest
from main import calculate_4peg_optimal_moves


class TestOptimalMoveCalculation:
    """Test suite for optimal move calculation"""
    
    def test_3peg_optimal_moves(self):
        """Test 3-peg optimal move calculation: 2^n - 1"""
        test_cases = {
            3: 7,    # 2^3 - 1 = 7
            4: 15,   # 2^4 - 1 = 15
            5: 31,   # 2^5 - 1 = 31
            6: 63,   # 2^6 - 1 = 63
            7: 127,  # 2^7 - 1 = 127
            8: 255,  # 2^8 - 1 = 255
            10: 1023 # 2^10 - 1 = 1023
        }
        
        for n, expected in test_cases.items():
            actual = (2 ** n) - 1
            assert actual == expected, f"3-peg optimal for {n} disks should be {expected}, got {actual}"
    
    def test_4peg_optimal_moves(self):
        """Test 4-peg optimal move calculation"""
        test_cases = {
            3: 5,
            4: 9,
            5: 13,
            6: 17,
            7: 25,   # Frame-Stewart optimal
            8: 33,
            10: 49
        }
        
        for n, expected in test_cases.items():
            actual = calculate_4peg_optimal_moves(n)
            assert actual == expected, f"4-peg optimal for {n} disks should be {expected}, got {actual}"
    
    def test_4peg_uses_fewer_moves_than_3peg(self):
        """Test that 4-peg always uses fewer moves than 3-peg for same disk count"""
        for n in range(3, 11):
            moves_3peg = (2 ** n) - 1
            moves_4peg = calculate_4peg_optimal_moves(n)
            assert moves_4peg < moves_3peg, \
                f"4-peg should use fewer moves than 3-peg for {n} disks"
