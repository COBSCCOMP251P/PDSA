"""
Tower of Hanoi Routes for shared main.py integration
Provides API endpoints for the Tower of Hanoi game
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Create router
router = APIRouter()

# Pydantic Models
class CreateRoundRequest(BaseModel):
    n_disks: Optional[int] = None
    peg_count: int = 3

class SubmissionRequest(BaseModel):
    player_name: str
    declared_moves: int
    move_sequence: List[str]

class GameResult(BaseModel):
    player_name: str
    disk_count: int
    moves: int
    time_taken: float
    is_optimal: bool = False

# Try to import algorithms using importlib to avoid path conflicts
try:
    import sys
    import os
    import importlib.util
    
    # Get backend folder path
    backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend')
    
    # Load algorithms module directly from file
    algorithms_spec = importlib.util.spec_from_file_location(
        "tower_hanoi_algorithms", 
        os.path.join(backend_path, "algorithms.py")
    )
    algorithms_module = importlib.util.module_from_spec(algorithms_spec)
    algorithms_spec.loader.exec_module(algorithms_module)
    
    # Load validator module directly from file
    validator_spec = importlib.util.spec_from_file_location(
        "tower_hanoi_validator", 
        os.path.join(backend_path, "validator.py")
    )
    validator_module = importlib.util.module_from_spec(validator_spec)
    validator_spec.loader.exec_module(validator_module)
    
    # Extract classes and functions
    AlgorithmRunner = algorithms_module.AlgorithmRunner
    solve_tower_of_hanoi = algorithms_module.solve_tower_of_hanoi
    GameValidator = validator_module.GameValidator
    parse_move_sequence = validator_module.parse_move_sequence
    
    algorithm_runner = AlgorithmRunner()
    game_validator = GameValidator()
    ALGORITHMS_AVAILABLE = True
except Exception as e:
    print(f"Tower of Hanoi algorithms not available: {e}")
    ALGORITHMS_AVAILABLE = False
    algorithm_runner = None
    game_validator = None

# In-memory game storage
active_rounds: Dict[int, Dict] = {}
round_counter = 0
leaderboard: List[Dict] = []

@router.get("/status")
async def get_status():
    """Get game status"""
    return {
        "status": "ok",
        "game": "Tower of Hanoi",
        "algorithms_available": ALGORITHMS_AVAILABLE,
        "active_rounds": len(active_rounds)
    }

@router.post("/rounds")
async def create_round(request: CreateRoundRequest):
    """Create a new game round"""
    global round_counter
    
    import random
    
    n_disks = request.n_disks if request.n_disks else random.randint(3, 7)
    peg_count = request.peg_count
    
    round_counter += 1
    round_id = round_counter
    
    # Calculate optimal moves
    if peg_count == 3:
        optimal_moves = (2 ** n_disks) - 1
    else:  # 4 pegs - Frame-Stewart algorithm
        # Simplified calculation
        optimal_moves = 2 * n_disks - 1  # Approximation
    
    round_data = {
        "id": round_id,
        "n_disks": n_disks,
        "peg_count": peg_count,
        "source": "A",
        "destination": "C" if peg_count == 3 else "D",
        "optimal_moves": optimal_moves,
        "started_at": datetime.now().isoformat()
    }
    
    active_rounds[round_id] = round_data
    
    return round_data

@router.get("/rounds/{round_id}")
async def get_round(round_id: int):
    """Get round details"""
    if round_id not in active_rounds:
        raise HTTPException(status_code=404, detail="Round not found")
    return active_rounds[round_id]

@router.post("/rounds/{round_id}/submit")
async def submit_solution(round_id: int, request: SubmissionRequest):
    """Submit a solution for a round"""
    if round_id not in active_rounds:
        raise HTTPException(status_code=404, detail="Round not found")
    
    round_data = active_rounds[round_id]
    
    # Basic validation
    is_correct = len(request.move_sequence) == request.declared_moves
    
    if ALGORITHMS_AVAILABLE and game_validator:
        try:
            # Parse moves
            parsed_moves = parse_move_sequence(request.move_sequence)
            
            # Validate
            validation = game_validator.validate(
                n_disks=round_data["n_disks"],
                source=round_data["source"],
                destination=round_data["destination"],
                moves=parsed_moves
            )
            is_correct = validation.get("valid", False)
        except Exception as e:
            print(f"Validation error: {e}")
    
    return {
        "correct": is_correct,
        "player_name": request.player_name,
        "round_id": round_id,
        "declared_moves": request.declared_moves,
        "actual_moves": len(request.move_sequence),
        "validation_details": {
            "optimal_moves": round_data.get("optimal_moves"),
            "is_optimal": len(request.move_sequence) == round_data.get("optimal_moves")
        }
    }

@router.get("/leaderboard")
async def get_leaderboard():
    """Get game leaderboard"""
    return sorted(leaderboard, key=lambda x: (x.get("correct_submissions", 0), -x.get("best_moves", 999)), reverse=True)[:10]

@router.post("/leaderboard")
async def submit_to_leaderboard(result: GameResult):
    """Submit game result to leaderboard"""
    # Find or create player entry
    player_entry = next((p for p in leaderboard if p["name"] == result.player_name), None)
    
    if player_entry:
        player_entry["total_submissions"] = player_entry.get("total_submissions", 0) + 1
        if result.is_optimal:
            player_entry["correct_submissions"] = player_entry.get("correct_submissions", 0) + 1
        if player_entry.get("best_moves") is None or result.moves < player_entry["best_moves"]:
            player_entry["best_moves"] = result.moves
    else:
        leaderboard.append({
            "name": result.player_name,
            "total_submissions": 1,
            "correct_submissions": 1 if result.is_optimal else 0,
            "best_moves": result.moves,
            "last_submission": datetime.now().isoformat()
        })
    
    return {"status": "success", "message": "Score submitted"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "game": "Tower of Hanoi",
        "algorithms": ALGORITHMS_AVAILABLE
    }
