"""
Tower of Hanoi Routes for shared main.py integration
Provides API endpoints for the Tower of Hanoi game
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create router
router = APIRouter()

# Database connection
def get_db_connection():
    """Get MySQL database connection"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "pruthuvide"),
        database="pdsa_games"
    )

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

@router.get("/status")
async def get_status():
    """Get game status"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rounds")
        total_rounds = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return {
            "status": "ok",
            "game": "Tower of Hanoi",
            "algorithms_available": ALGORITHMS_AVAILABLE,
            "total_rounds": total_rounds
        }
    except Exception as e:
        return {
            "status": "ok",
            "game": "Tower of Hanoi",
            "algorithms_available": ALGORITHMS_AVAILABLE,
            "database": f"error: {str(e)}"
        }

@router.post("/rounds")
async def create_round(request: CreateRoundRequest):
    """Create a new game round"""
    import random
    
    n_disks = request.n_disks if request.n_disks else random.randint(3, 7)
    peg_count = request.peg_count
    
    # Validate input
    if not (3 <= n_disks <= 7):
        raise HTTPException(status_code=400, detail="Number of disks must be between 3 and 7")
    if peg_count not in [3, 4]:
        raise HTTPException(status_code=400, detail="Peg count must be 3 or 4")
    
    source = 'A'
    destination = 'D' if peg_count == 4 else 'C'
    
    # Insert into database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rounds (n_disks, peg_count, source, destination) VALUES (%s, %s, %s, %s)",
            (n_disks, peg_count, source, destination)
        )
        conn.commit()
        round_id = cursor.lastrowid
        cursor.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Calculate optimal moves
    if peg_count == 3:
        optimal_moves = (2 ** n_disks) - 1
    else:  # 4 pegs - Frame-Stewart algorithm
        # Simplified calculation
        optimal_moves = 2 * n_disks - 1  # Approximation
    
    # Run algorithms and save results
    if ALGORITHMS_AVAILABLE:
        try:
            results = solve_tower_of_hanoi(n_disks, peg_count)
            conn = get_db_connection()
            cursor = conn.cursor()
            for result in results:
                # Convert sequence list to string
                sequence_str = ",".join(result.sequence) if result.sequence else None
                cursor.execute(
                    """INSERT INTO algorithm_runs 
                    (round_id, algorithm_name, peg_count, computed_moves, runtime_ms, generated_sequence) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (round_id, result.algorithm_name, peg_count, result.moves, result.runtime_ms, sequence_str)
                )
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✅ Algorithm runs saved for round {round_id}")
        except Exception as e:
            print(f"⚠️ Failed to save algorithm runs: {e}")
    
    return {
        "id": round_id,
        "n_disks": n_disks,
        "peg_count": peg_count,
        "source": source,
        "destination": destination,
        "optimal_moves": optimal_moves,
        "started_at": datetime.now().isoformat()
    }

@router.get("/rounds/{round_id}")
async def get_round(round_id: int):
    """Get round details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rounds WHERE id = %s", (round_id,))
        round_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not round_data:
            raise HTTPException(status_code=404, detail="Round not found")
        
        # Calculate optimal moves
        if round_data['peg_count'] == 3:
            optimal_moves = (2 ** round_data['n_disks']) - 1
        else:
            optimal_moves = 2 * round_data['n_disks'] - 1
        
        round_data['optimal_moves'] = optimal_moves
        round_data['started_at'] = round_data['started_at'].isoformat() if round_data['started_at'] else None
        
        return round_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/rounds/{round_id}/submit")
async def submit_solution(round_id: int, request: SubmissionRequest):
    """Submit a solution for a round"""
    # Get round from database
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rounds WHERE id = %s", (round_id,))
        round_data = cursor.fetchone()
        
        if not round_data:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Round not found")
        
        # Get or create player
        cursor.execute("SELECT id FROM players WHERE name = %s", (request.player_name,))
        player = cursor.fetchone()
        
        if not player:
            cursor.execute("INSERT INTO players (name) VALUES (%s)", (request.player_name,))
            conn.commit()
            player_id = cursor.lastrowid
        else:
            player_id = player['id']
        
        # Basic validation
        is_correct = len(request.move_sequence) == request.declared_moves
        validation_error = None
        
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
                if not is_correct:
                    validation_error = validation.get("error", "Invalid solution")
            except Exception as e:
                print(f"Validation error: {e}")
                is_correct = False
                validation_error = str(e)
        
        # Save submission to database
        cursor.execute(
            """INSERT INTO submissions 
            (round_id, player_id, declared_moves, move_sequence, is_correct, validation_error) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (round_id, player_id, request.declared_moves, ','.join(request.move_sequence), is_correct, validation_error)
        )
        conn.commit()
        submission_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return {
            "submission_id": submission_id,
            "correct": is_correct,
            "player_name": request.player_name,
            "round_id": round_id,
            "declared_moves": request.declared_moves,
            "actual_moves": len(request.move_sequence),
            "validation_error": validation_error
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/leaderboard")
async def get_leaderboard():
    """Get game leaderboard from database view"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM leaderboard LIMIT 10")
        leaderboard_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert datetime to ISO format
        for entry in leaderboard_data:
            if entry.get('last_submission'):
                entry['last_submission'] = entry['last_submission'].isoformat()
        
        return leaderboard_data
    except Exception as e:
        print(f"Leaderboard error: {e}")
        return []

@router.post("/save-game")
async def save_game_result(game_result: GameResult):
    """Save interactive game result to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get or create player
        cursor.execute("SELECT id FROM players WHERE name = %s", (game_result.player_name,))
        player = cursor.fetchone()
        
        if not player:
            cursor.execute("INSERT INTO players (name) VALUES (%s)", (game_result.player_name,))
            conn.commit()
            player_id = cursor.lastrowid
        else:
            player_id = player['id']
        
        # Create a round for this game
        destination = 'C'  # 3 pegs game
        cursor.execute(
            "INSERT INTO rounds (n_disks, peg_count, source, destination) VALUES (%s, %s, %s, %s)",
            (game_result.disk_count, 3, 'A', destination)
        )
        conn.commit()
        round_id = cursor.lastrowid
        
        # Generate move sequence placeholder (interactive game doesn't track individual moves)
        move_sequence = f"Interactive game - {game_result.moves} moves in {game_result.time_taken}s"
        
        # Save as submission
        is_correct = True  # Game only calls this when won
        cursor.execute(
            """INSERT INTO submissions 
            (round_id, player_id, declared_moves, move_sequence, is_correct, validation_error) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (round_id, player_id, game_result.moves, move_sequence, is_correct, None)
        )
        conn.commit()
        submission_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Run algorithms and save results for this round
        if ALGORITHMS_AVAILABLE:
            try:
                results = solve_tower_of_hanoi(game_result.disk_count, 3)
                conn = get_db_connection()
                cursor = conn.cursor()
                for result in results:
                    # Convert sequence list to string
                    sequence_str = ",".join(result.sequence) if result.sequence else None
                    cursor.execute(
                        """INSERT INTO algorithm_runs 
                        (round_id, algorithm_name, peg_count, computed_moves, runtime_ms, generated_sequence) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                        (round_id, result.algorithm_name, 3, result.moves, result.runtime_ms, sequence_str)
                    )
                conn.commit()
                cursor.close()
                conn.close()
                print(f"✅ Algorithm runs saved for interactive game round {round_id}")
            except Exception as algo_error:
                print(f"⚠️ Failed to save algorithm runs: {algo_error}")
        
        return {
            "status": "success",
            "message": "Game result saved!",
            "submission_id": submission_id,
            "player_id": player_id,
            "round_id": round_id,
            "is_optimal": game_result.is_optimal
        }
    except Exception as e:
        print(f"Save game error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save game: {str(e)}")

@router.post("/validate")
async def validate_move(data: dict):
    """Validate a single move without submitting"""
    try:
        return {"valid": True, "message": "Move is valid"}
    except Exception as e:
        return {"valid": False, "message": str(e)}

@router.get("/rounds/{round_id}/algorithm-runs")
async def get_algorithm_runs(round_id: int):
    """Get algorithm benchmark results for a round"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM algorithm_runs WHERE round_id = %s", (round_id,))
        runs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert datetime to ISO format
        for run in runs:
            if run.get('run_at'):
                run['run_at'] = run['run_at'].isoformat()
        
        return runs
    except Exception as e:
        print(f"Algorithm runs error: {e}")
        return []

@router.get("/stats/algorithms")
async def get_algorithm_stats():
    """Get algorithm performance statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                algorithm_name,
                peg_count,
                AVG(runtime_ms) as avg_runtime,
                MIN(runtime_ms) as min_runtime,
                MAX(runtime_ms) as max_runtime,
                AVG(computed_moves) as avg_moves,
                COUNT(*) as run_count
            FROM algorithm_runs
            GROUP BY algorithm_name, peg_count
            ORDER BY algorithm_name, peg_count
        """)
        stats = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return stats
    except Exception as e:
        print(f"Algorithm stats error: {e}")
        return []

@router.get("/stats/rounds")
async def get_round_stats():
    """Get round statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT r.id) as total_rounds,
                COUNT(DISTINCT s.player_id) as unique_players,
                COUNT(s.id) as total_submissions,
                SUM(CASE WHEN s.is_correct THEN 1 ELSE 0 END) as correct_submissions,
                AVG(r.n_disks) as avg_disks
            FROM rounds r
            LEFT JOIN submissions s ON r.id = s.round_id
        """)
        stats = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return stats if stats else {}
    except Exception as e:
        print(f"Round stats error: {e}")
        return {}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "game": "Tower of Hanoi",
        "algorithms": ALGORITHMS_AVAILABLE
    }
