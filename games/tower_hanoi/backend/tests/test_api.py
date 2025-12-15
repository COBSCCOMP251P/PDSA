"""
Unit tests for Tower of Hanoi API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Create test client
@pytest.fixture(scope="module")
def client():
    """Create test client for API testing"""
    with TestClient(app) as test_client:
        yield test_client


class TestHealthEndpoint:
    """Test suite for health check endpoint"""
    
    def test_health_check(self, client):
        """Test that health endpoint returns 200"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestBenchmarkEndpoint:
    """Test suite for benchmark endpoint"""
    
    def test_benchmark_3peg_valid(self, client):
        """Test benchmark with 3-peg configuration"""
        payload = {
            "num_disks": 5,
            "num_pegs": 3
        }
        
        response = client.post("/api/benchmark", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "algorithms" in data
        assert len(data["algorithms"]) == 2, "Should have 2 algorithms for 3-peg"
        
        # Check recursive algorithm
        recursive = next(a for a in data["algorithms"] if a["algorithm_name"] == "Recursive")
        assert "runtime_ms" in recursive
        assert "computed_moves" in recursive
        assert recursive["computed_moves"] == 31  # 2^5 - 1
    
    def test_benchmark_4peg_valid(self, client):
        """Test benchmark with 4-peg configuration"""
        payload = {
            "num_disks": 8,
            "num_pegs": 4
        }
        
        response = client.post("/api/benchmark", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["algorithms"]) == 2, "Should have 2 algorithms for 4-peg"
        
        # Check both algorithms present
        algorithm_names = [a["algorithm_name"] for a in data["algorithms"]]
        assert "Frame-Stewart" in algorithm_names
        assert "Dynamic Programming" in algorithm_names
    
    def test_benchmark_records_time(self, client):
        """Test that benchmark records execution time"""
        payload = {
            "num_disks": 6,
            "num_pegs": 3
        }
        
        response = client.post("/api/benchmark", json=payload)
        data = response.json()
        
        for algorithm in data["algorithms"]:
            assert algorithm["runtime_ms"] > 0, \
                f"Runtime should be positive for {algorithm['algorithm_name']}"
            assert algorithm["runtime_ms"] < 1000, \
                f"Runtime seems too high for {algorithm['algorithm_name']}"
    
    def test_benchmark_4peg_fewer_moves(self, client):
        """Test that 4-peg algorithms use fewer moves"""
        payload_3peg = {"num_disks": 10, "num_pegs": 3}
        payload_4peg = {"num_disks": 10, "num_pegs": 4}
        
        response_3peg = client.post("/api/benchmark", json=payload_3peg)
        response_4peg = client.post("/api/benchmark", json=payload_4peg)
        
        data_3peg = response_3peg.json()
        data_4peg = response_4peg.json()
        
        moves_3peg = data_3peg["algorithms"][0]["computed_moves"]
        moves_4peg = max(a["computed_moves"] for a in data_4peg["algorithms"])
        
        assert moves_4peg < moves_3peg, "4-peg should use fewer moves"
    
    def test_benchmark_consistent_results(self, client):
        """Test that repeated calls give consistent move counts"""
        payload = {
            "num_disks": 7,
            "num_pegs": 3
        }
        
        response1 = client.post("/api/benchmark", json=payload)
        response2 = client.post("/api/benchmark", json=payload)
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Move counts should be identical
        moves1 = [a["computed_moves"] for a in data1["algorithms"]]
        moves2 = [a["computed_moves"] for a in data2["algorithms"]]
        
        assert moves1 == moves2, "Move counts should be consistent"


class TestRoundsEndpoint:
    """Test suite for rounds management endpoint"""
    
    def test_get_rounds(self, client):
        """Test getting rounds list"""
        response = client.get("/api/rounds")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list), "Should return list of rounds"


class TestAPIPerformance:
    """Test API performance"""
    
    def test_response_time_reasonable(self, client):
        """Test that API responds quickly"""
        import time
        
        start = time.time()
        response = client.post("/api/benchmark", json={
            "num_disks": 10,
            "num_pegs": 4
        })
        duration = time.time() - start
        
        assert duration < 2.0, f"API took too long: {duration}s"
        assert response.status_code == 200

