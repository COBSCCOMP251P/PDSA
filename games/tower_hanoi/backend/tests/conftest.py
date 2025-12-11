"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for API testing"""
    return TestClient(app)


@pytest.fixture
def sample_round_data():
    """Sample data for creating rounds"""
    return {
        "n_disks": 5,
        "peg_count": 3
    }


@pytest.fixture
def sample_submission_data():
    """Sample submission data"""
    return {
        "player_name": "TestPlayer",
        "declared_moves": 31,
        "move_sequence": [
            "A->C", "A->B", "C->B", "A->C", "B->A", "B->C", "A->C",
            "A->B", "C->B", "C->A", "B->A", "C->B", "A->C", "A->B", "C->B",
            "A->C", "B->A", "B->C", "A->C", "B->A", "C->B", "C->A", "B->A",
            "B->C", "A->C", "A->B", "C->B", "A->C", "B->A", "B->C", "A->C"
        ]
    }
