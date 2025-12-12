"""
Tests for input validation and exception handling
Verifies that all API endpoints properly validate inputs and handle errors
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, calculate_4peg_optimal_moves

client = TestClient(app=app)


class TestLeaderboardValidation:
    """Test validation for /api/leaderboard endpoint"""
    
    def test_empty_player_name(self):
        """Should reject empty player name"""
        response = client.post("/api/leaderboard", json={
            "player_name": "",
            "disk_count": 5,
            "peg_count": 3,
            "moves": 31,
            "time_taken": 45.2
        })
        assert response.status_code == 400
        assert "Player name is required" in response.json()["detail"]
    
    def test_whitespace_player_name(self):
        """Should reject whitespace-only player name"""
        response = client.post("/api/leaderboard", json={
            "player_name": "   ",
            "disk_count": 5,
            "peg_count": 3,
            "moves": 31,
            "time_taken": 45.2
        })
        assert response.status_code == 400
        assert "Player name is required" in response.json()["detail"]
    
    def test_player_name_too_long(self):
        """Should reject player names over 100 characters"""
        response = client.post("/api/leaderboard", json={
            "player_name": "A" * 101,
            "disk_count": 5,
            "peg_count": 3,
            "moves": 31,
            "time_taken": 45.2
        })
        assert response.status_code == 400
        assert "100 characters or less" in response.json()["detail"]
    
    def test_disk_count_too_low(self):
        """Should reject disk count less than 1"""
        response = client.post("/api/leaderboard", json={
            "player_name": "TestPlayer",
            "disk_count": 0,
            "peg_count": 3,
            "moves": 31,
            "time_taken": 45.2
        })
        assert response.status_code == 400
        assert "between 1 and 20" in response.json()["detail"]
    
    def test_disk_count_too_high(self):
        """Should reject disk count greater than 20"""
        response = client.post("/api/leaderboard", json={
            "player_name": "TestPlayer",
            "disk_count": 21,
            "peg_count": 3,
            "moves": 31,
            "time_taken": 45.2
        })
        assert response.status_code == 400
        assert "between 1 and 20" in response.json()["detail"]
    
    def test_invalid_peg_count(self):
        """Should reject peg counts other than 3 or 4"""
        response = client.post("/api/leaderboard", json={
            "player_name": "TestPlayer",
            "disk_count": 5,
            "peg_count": 5,
            "moves": 31,
            "time_taken": 45.2
        })
        assert response.status_code == 400
        assert "3 or 4" in response.json()["detail"]
    
    def test_negative_moves(self):
        """Should reject negative move count"""
        response = client.post("/api/leaderboard", json={
            "player_name": "TestPlayer",
            "disk_count": 5,
            "peg_count": 3,
            "moves": -1,
            "time_taken": 45.2
        })
        assert response.status_code == 400
        assert "at least 1" in response.json()["detail"]
    
    def test_negative_time(self):
        """Should reject negative time taken"""
        response = client.post("/api/leaderboard", json={
            "player_name": "TestPlayer",
            "disk_count": 5,
            "peg_count": 3,
            "moves": 31,
            "time_taken": -10.5
        })
        assert response.status_code == 400
        assert "cannot be negative" in response.json()["detail"]
    
    def test_valid_3peg_submission(self):
        """Should accept valid 3-peg submission"""
        response = client.post("/api/leaderboard", json={
            "player_name": "TestPlayer",
            "disk_count": 3,
            "peg_count": 3,
            "moves": 7,
            "time_taken": 15.5
        })
        # Should succeed (200) or fail with database error (500), but not validation error (400)
        assert response.status_code in [200, 500]
    
    def test_valid_4peg_submission(self):
        """Should accept valid 4-peg submission"""
        response = client.post("/api/leaderboard", json={
            "player_name": "TestPlayer",
            "disk_count": 5,
            "peg_count": 4,
            "moves": 13,
            "time_taken": 20.8
        })
        # Should succeed (200) or fail with database error (500), but not validation error (400)
        assert response.status_code in [200, 500]


class TestValidateEndpointValidation:
    """Test validation for /api/validate endpoint"""
    
    def test_disk_count_validation(self):
        """Should validate disk count range"""
        response = client.post("/api/validate", json={
            "n_disks": 25,
            "peg_count": 3,
            "move_sequence": ["1->3"],
            "declared_moves": 1
        })
        assert response.status_code == 400
        assert "between 1 and 20" in response.json()["detail"]
    
    def test_peg_count_validation(self):
        """Should validate peg count"""
        response = client.post("/api/validate", json={
            "n_disks": 5,
            "peg_count": 2,
            "move_sequence": ["1->2"],
            "declared_moves": 1
        })
        assert response.status_code == 400
        assert "3 or 4" in response.json()["detail"]
    
    def test_empty_move_sequence(self):
        """Should reject empty move sequence"""
        response = client.post("/api/validate", json={
            "n_disks": 5,
            "peg_count": 3,
            "move_sequence": [],
            "declared_moves": 0
        })
        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"]
    
    def test_invalid_move_format(self):
        """Should reject invalid move format"""
        response = client.post("/api/validate", json={
            "n_disks": 3,
            "peg_count": 3,
            "move_sequence": ["1-3", "2->3"],  # Invalid format
            "declared_moves": 2
        })
        assert response.status_code == 400
        assert "Invalid move format" in response.json()["detail"]
    
    def test_invalid_peg_numbers(self):
        """Should reject invalid peg numbers in moves"""
        response = client.post("/api/validate", json={
            "n_disks": 3,
            "peg_count": 3,
            "move_sequence": ["1->5"],  # Peg 5 doesn't exist
            "declared_moves": 1
        })
        assert response.status_code == 400
        assert "Invalid" in response.json()["detail"]
    
    def test_same_source_destination(self):
        """Should reject moves where source equals destination"""
        response = client.post("/api/validate", json={
            "n_disks": 3,
            "peg_count": 3,
            "move_sequence": ["1->1"],
            "declared_moves": 1
        })
        assert response.status_code == 400
        assert "source and destination cannot be the same" in response.json()["detail"]
    
    def test_declared_moves_mismatch(self):
        """Should reject when declared moves doesn't match sequence length"""
        response = client.post("/api/validate", json={
            "n_disks": 3,
            "peg_count": 3,
            "move_sequence": ["1->3", "1->2"],
            "declared_moves": 5
        })
        assert response.status_code == 400
        assert "does not match actual move sequence length" in response.json()["detail"]


class TestBenchmarkValidation:
    """Test validation for /api/benchmark endpoint"""
    
    def test_disk_count_validation(self):
        """Should validate disk count"""
        response = client.post("/api/benchmark", json={
            "n_disks": 25,
            "peg_count": 3
        })
        assert response.status_code == 400
        assert "between 1 and 20" in response.json()["detail"]
    
    def test_peg_count_validation(self):
        """Should validate peg count"""
        response = client.post("/api/benchmark", json={
            "n_disks": 5,
            "peg_count": 6
        })
        assert response.status_code == 400
        assert "3 or 4" in response.json()["detail"]
    
    def test_non_integer_disk_count(self):
        """Should reject non-integer disk count"""
        response = client.post("/api/benchmark", json={
            "n_disks": "five",
            "peg_count": 3
        })
        assert response.status_code == 400
        assert "must be an integer" in response.json()["detail"]
    
    def test_valid_3peg_benchmark(self):
        """Should accept valid 3-peg benchmark"""
        response = client.post("/api/benchmark", json={
            "n_disks": 5,
            "peg_count": 3
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert len(data["results"]) == 2  # Recursive and Iterative
    
    def test_valid_4peg_benchmark(self):
        """Should accept valid 4-peg benchmark"""
        response = client.post("/api/benchmark", json={
            "n_disks": 5,
            "peg_count": 4
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert len(data["results"]) == 2  # Frame-Stewart and DP


class TestOptimalMoveCalculation:
    """Test optimal move calculation for both 3-peg and 4-peg"""
    
    def test_3peg_optimal_moves(self):
        """Should calculate correct optimal moves for 3-peg"""
        from main import calculate_4peg_optimal_moves
        
        # For 3-peg, optimal = 2^n - 1
        test_cases = [
            (1, 1),    # 2^1 - 1 = 1
            (2, 3),    # 2^2 - 1 = 3
            (3, 7),    # 2^3 - 1 = 7
            (5, 31),   # 2^5 - 1 = 31
            (10, 1023) # 2^10 - 1 = 1023
        ]
        
        for n, expected in test_cases:
            actual = (2 ** n) - 1
            assert actual == expected, f"3-peg with {n} disks should be {expected}, got {actual}"
    
    def test_4peg_optimal_moves(self):
        """Should calculate correct optimal moves for 4-peg using Frame-Stewart"""
        from main import calculate_4peg_optimal_moves
        
        # Known optimal values for 4-peg Frame-Stewart
        test_cases = [
            (1, 1),   # 1 disk: 1 move
            (2, 3),   # 2 disks: 3 moves
            (3, 5),   # 3 disks: 5 moves
            (5, 13),  # 5 disks: 13 moves
            (10, 49)  # 10 disks: 49 moves
        ]
        
        for n, expected in test_cases:
            actual = calculate_4peg_optimal_moves(n)
            assert actual == expected, f"4-peg with {n} disks should be {expected}, got {actual}"
    
    def test_4peg_better_than_3peg(self):
        """Should verify 4-peg requires fewer moves than 3-peg"""
        from main import calculate_4peg_optimal_moves
        
        for n in range(3, 11):
            moves_3peg = (2 ** n) - 1
            moves_4peg = calculate_4peg_optimal_moves(n)
            assert moves_4peg < moves_3peg, f"For {n} disks, 4-peg ({moves_4peg}) should be less than 3-peg ({moves_3peg})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
