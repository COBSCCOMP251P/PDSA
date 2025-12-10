"""
Eight Queens Gaming Routes with MySQL Database
Provides enhanced gaming experience with database persistence

Author: PDSA Course Project  
Date: November 24, 2025
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator as pydantic_validator
from typing import List, Optional, Dict, Any
import time
import logging
import json
import hashlib
import html  # For XSS sanitization

# Algorithm imports
from ..algorithms.sequential_solver import EightQueensSolver as SequentialSolver
from ..algorithms.threaded_solver import ThreadedEightQueensSolver as ThreadedSolver
from ..algorithms.validation import EightQueensValidator

# Database imports
import mysql.connector
from mysql.connector import Error

# Simple gaming router
router = APIRouter(prefix="/api/eight-queens-game", tags=["Eight Queens Gaming"])
logger = logging.getLogger(__name__)

# Global instances
sequential_solver = SequentialSolver()
threaded_solver = ThreadedSolver()
queens_validator = EightQueensValidator()  # Renamed to avoid conflict with pydantic validator

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'pruthuvide',
    'database': 'eight_queens_game',
    'autocommit': True
}

def get_db_connection():
    """Get database connection"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# In-memory storage for active game sessions (for performance during gameplay)
game_sessions = {}  # session_id -> session_data

# =============================================
# SIMPLE GAME MODELS
# =============================================

class PlayerRegistration(BaseModel):
    """Model for player registration"""
    name: str = Field(..., min_length=3, max_length=50)
    # Email removed - only username required
    
    @pydantic_validator('name')
    def sanitize_name(cls, v):
        """Sanitize name to prevent XSS"""
        return html.escape(v.strip())

class PlayerLogin(BaseModel):
    """Model for player login"""
    name: str = Field(..., min_length=3, max_length=50)
    
    @pydantic_validator('name')
    def sanitize_name(cls, v):
        """Sanitize name to prevent XSS"""
        return html.escape(v.strip())

class GameStart(BaseModel):
    """Model for starting a new game with difficulty"""
    player_name: str = Field(..., min_length=1, max_length=100)
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    algorithm_type: str = Field(default="sequential", pattern="^(sequential|threaded)$")
    
    @pydantic_validator('player_name')
    def sanitize_player_name(cls, v):
        """Sanitize player name to prevent XSS"""
        return html.escape(v.strip())

class GameMove(BaseModel):
    """Model for making a move in the game"""
    session_id: int = Field(..., gt=0)
    row: int = Field(..., ge=0, le=7)
    col: int = Field(..., ge=0, le=7)
    action: str = Field(..., pattern="^(place|remove)$")

class GameReset(BaseModel):
    """Model for resetting a game"""
    session_id: int = Field(..., gt=0)

class HintRequest(BaseModel):
    """Model for requesting a hint"""
    session_id: int = Field(..., gt=0)
    hint_type: str = Field(..., pattern="^(safe_position|conflict_highlight|next_move|solution_count)$")

class GameResponse(BaseModel):
    """Standard game response model"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    game_state: Optional[Dict[str, Any]] = None


class SolutionSubmission(BaseModel):
    """Model for submitting a solution with full validation"""
    session_id: int = Field(..., gt=0, description="Game session ID")
    solution: List[int] = Field(..., min_items=8, max_items=8, description="8-element board state")
    completion_time_seconds: float = Field(default=0, ge=0, description="Time to complete in seconds")
    hints_used: int = Field(default=0, ge=0, description="Number of hints used")
    undo_count: int = Field(default=0, ge=0, description="Number of undos used")
    
    @pydantic_validator('solution')
    def validate_solution_values(cls, v):
        """Validate that all solution values are in valid range -1 to 7"""
        if len(v) != 8:
            raise ValueError('Solution must have exactly 8 elements')
        for i, pos in enumerate(v):
            if not isinstance(pos, int):
                raise ValueError(f'Position at row {i} must be an integer, got {type(pos).__name__}')
            if pos < -1 or pos > 7:
                raise ValueError(f'Position at row {i} must be between -1 and 7, got {pos}')
        return v


class GameExitRequest(BaseModel):
    """Model for exiting a game with progress saving"""
    session_id: int = Field(..., gt=0, description="Game session ID")
    current_board: List[int] = Field(default_factory=lambda: [-1]*8, min_items=8, max_items=8)
    hints_used: int = Field(default=0, ge=0)
    undos_used: int = Field(default=0, ge=0)
    time_elapsed: float = Field(default=0, ge=0)
    
    @pydantic_validator('current_board')
    def validate_board_values(cls, v):
        """Validate board values are in range -1 to 7"""
        for i, pos in enumerate(v):
            if not isinstance(pos, int) or pos < -1 or pos > 7:
                raise ValueError(f'Invalid board position at row {i}')
        return v

# =============================================
# DIFFICULTY SETTINGS
# =============================================

DIFFICULTY_SETTINGS = {
    "easy": {
        "name": "Easy Mode",
        "max_hints": 999,
        "undo_allowed": True,
        "time_limit_seconds": None,
        "visual_hints": True,
        "starting_queens": 2,
        "base_score": 50
    },
    "medium": {
        "name": "Medium Mode", 
        "max_hints": 3,
        "undo_allowed": True,
        "time_limit_seconds": 1800,  # 30 minutes
        "visual_hints": True,
        "starting_queens": 0,
        "base_score": 100
    },
    "hard": {
        "name": "Hard Mode",
        "max_hints": 1,
        "undo_allowed": False,
        "time_limit_seconds": 600,  # 10 minutes
        "visual_hints": False,
        "starting_queens": 0,
        "base_score": 200
    }
}

# =============================================
# UTILITY FUNCTIONS
# =============================================

def find_conflicts(board: List[int]) -> List[Dict[str, int]]:
    """Find conflicts in the board configuration"""
    conflicts = []
    for row1 in range(8):
        if board[row1] == -1:
            continue
        col1 = board[row1]
        
        for row2 in range(row1 + 1, 8):
            if board[row2] == -1:
                continue
            col2 = board[row2]
            
            # Same column or diagonal conflict
            if col1 == col2 or abs(row1 - row2) == abs(col1 - col2):
                conflicts.append({"row": row1, "col": col1})
                conflicts.append({"row": row2, "col": col2})
    
    # Remove duplicates
    unique_conflicts = []
    seen = set()
    for conflict in conflicts:
        key = (conflict["row"], conflict["col"])
        if key not in seen:
            unique_conflicts.append(conflict)
            seen.add(key)
    
    return unique_conflicts


def recover_session_from_db(session_id: int) -> Optional[Dict[str, Any]]:
    """
    Try to recover a game session from the database.
    Returns session dict if found, None otherwise.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT gs.*, p.name as player_name 
            FROM game_sessions gs 
            JOIN players p ON gs.player_id = p.id 
            WHERE gs.id = %s AND gs.status = 'in_progress'
        """, (session_id,))
        db_session = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if db_session:
            difficulty = db_session['difficulty'] or 'medium'
            settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["medium"])
            session = {
                "id": db_session['id'],
                "player_id": db_session['player_id'],
                "player_name": db_session['player_name'],
                "difficulty": difficulty,
                "algorithm_type": db_session.get('algorithm_type', 'sequential'),
                "settings": settings,
                "board": json.loads(db_session['current_board']) if db_session['current_board'] else [-1]*8,
                "start_time": time.time() - (db_session.get('completion_time_seconds') or 0),
                "hints_used": db_session.get('hints_used', 0) or 0,
                "undos_used": db_session.get('undo_count', 0) or 0,
                "move_history": [],
                "completed": False,
                "final_score": 0
            }
            # Cache in memory for future use
            game_sessions[session_id] = session
            logger.info(f"Session {session_id} recovered from database")
            return session
    except Exception as e:
        logger.error(f"Error recovering session {session_id} from database: {e}")
    return None


def get_session_or_recover(session_id: int) -> Optional[Dict[str, Any]]:
    """Get session from memory or recover from database"""
    session = game_sessions.get(session_id)
    if not session:
        session = recover_session_from_db(session_id)
    return session


def get_safe_positions(board: List[int]) -> List[tuple]:
    """Get safe positions for placing queens"""
    safe_positions = []
    
    for row in range(8):
        for col in range(8):
            if board[row] == col:  # Position occupied
                continue
            
            # Test if position is safe
            test_board = board.copy()
            test_board[row] = col
            
            if not has_conflicts_at(test_board, row, col):
                safe_positions.append((row, col))
    
    return safe_positions

def has_conflicts_at(board: List[int], target_row: int, target_col: int) -> bool:
    """Check if placing a queen at target position creates conflicts"""
    for row in range(8):
        col = board[row]
        if col == -1 or (row == target_row):
            continue
        
        # Column or diagonal conflict
        if col == target_col or abs(row - target_row) == abs(col - target_col):
            return True
    
    return False

def create_starting_board(difficulty: str) -> List[int]:
    """Create a starting board based on difficulty"""
    board = [-1] * 8
    
    if difficulty == "easy":
        # Pre-place two queens in safe positions for easy mode
        board[0] = 0  # Queen at (0, 0)
        board[1] = 2  # Queen at (1, 2)
    
    return board

# =============================================
# GAME ENDPOINTS
# =============================================

@router.post("/game/start", response_model=GameResponse)
async def start_new_game(game_start: GameStart):
    """Start a new game session with authenticated player"""
    
    # Find player by name in database
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM players WHERE LOWER(name) = LOWER(%s)", (game_start.player_name,))
        player = cursor.fetchone()
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found. Please register first.")
        
        # Create game session in database
        starting_board = create_starting_board(game_start.difficulty)
        board_json = json.dumps(starting_board)
        insert_query = """
            INSERT INTO game_sessions (player_id, difficulty, algorithm_type, 
                                     execution_time_ms, status, initial_board, current_board)
            VALUES (%s, %s, %s, 0, %s, %s, %s)
        """
        cursor.execute(insert_query, (player['id'], game_start.difficulty, game_start.algorithm_type, 'in_progress', board_json, board_json))
        session_id = cursor.lastrowid
    finally:
        connection.close()
    
    # Get difficulty settings
    settings = DIFFICULTY_SETTINGS.get(game_start.difficulty, DIFFICULTY_SETTINGS["medium"])
    
    # Store session in memory for quick access during gameplay
    session = {
        "id": session_id,
        "player_id": player['id'],
        "player_name": game_start.player_name,
        "difficulty": game_start.difficulty,
        "algorithm_type": game_start.algorithm_type,
        "settings": settings,
        "board": starting_board,
        "start_time": time.time(),
        "hints_used": 0,
        "undos_used": 0,
        "move_history": [],
        "completed": False,
        "final_score": 0
    }
    
    # For backward compatibility, keep in-memory copy during active gameplay
    game_sessions[session_id] = session
    
    return GameResponse(
        status="success",
        message=f"New {game_start.difficulty} game started for {game_start.player_name}!",
        data={
            "session_id": session_id,
            "player_id": player['id'],
            "difficulty": game_start.difficulty,
            "settings": settings
        },
        game_state={
            "board": starting_board,
            "hints_available": settings["max_hints"],
            "undo_available": settings["undo_allowed"],
            "time_limit": settings["time_limit_seconds"],
            "visual_hints": settings["visual_hints"]
        }
    )

@router.post("/game/move", response_model=GameResponse)
async def make_game_move(move: GameMove):
    """Make a move in the game"""
    try:
        # Try memory first, then database fallback
        session = get_session_or_recover(move.session_id)
        if not session:
            return GameResponse(
                status="error",
                message="Game session not found. Please start a new game."
            )
        
        # Apply move
        board = session["board"].copy()
        if move.action == "place":
            board[move.row] = move.col
        elif move.action == "remove":
            board[move.row] = -1
        
        # Update session
        session["board"] = board
        session["move_history"].append({
            "row": move.row,
            "col": move.col,
            "action": move.action,
            "timestamp": time.time()
        })
        
        # Check for conflicts
        conflicts = find_conflicts(board)
        
        # Check completion
        is_complete = all(pos != -1 for pos in board)
        is_valid = len(conflicts) == 0
        
        return GameResponse(
            status="success",
            message=f"Queen {'placed' if move.action == 'place' else 'removed'} at ({move.row}, {move.col})",
            game_state={
                "board": board,
                "conflicts": conflicts,
                "is_complete": is_complete,
                "is_valid": is_valid,
                "move_count": len(session["move_history"])
            }
        )
    except Exception as e:
        logger.error(f"Error making move: {e}")
        return GameResponse(
            status="error",
            message="Failed to process move. Please try again."
        )

@router.post("/game/reset", response_model=GameResponse)
async def reset_game(reset_request: GameReset):
    """Reset the game board to initial state"""
    try:
        # Try memory first, then database fallback
        session = get_session_or_recover(reset_request.session_id)
        if not session:
            return GameResponse(
                status="error",
                message="Game session not found. Please start a new game."
            )
        
        # Create fresh board based on difficulty
        difficulty = session.get("difficulty", "medium")
        new_board = create_starting_board(difficulty)
        
        # Reset session state
        session["board"] = new_board
        session["move_history"] = []
        session["hints_used"] = 0
        session["undos_used"] = 0
        session["start_time"] = time.time()
        
        return GameResponse(
            status="success",
            message="Game reset successfully",
            game_state={
                "board": new_board,
                "conflicts": [],
                "is_complete": False,
                "is_valid": True,
                "move_count": 0
            }
        )
    except Exception as e:
        logger.error(f"Error resetting game: {e}")
        return GameResponse(
            status="error",
            message="Failed to reset game. Please try again."
        )

@router.post("/game/hint", response_model=GameResponse)
async def get_game_hint(hint_request: HintRequest):
    """Get a hint for the current game"""
    try:
        # Try memory first, then database fallback
        session = get_session_or_recover(hint_request.session_id)
        if not session:
            return GameResponse(
                status="error",
                message="Game session not found. Please start a new game."
            )
        
        # Check hint availability
        max_hints = session["settings"]["max_hints"]
        if max_hints != 999 and session["hints_used"] >= max_hints:
            return GameResponse(
                status="error",
                message=f"No more hints available (used {session['hints_used']}/{max_hints})"
            )
        
        # Generate hint
        board = session["board"]
        hint_data = {}
        
        if hint_request.hint_type == "safe_position":
            safe_positions = get_safe_positions(board)
            hint_data = {
                "type": "safe_positions",
                "positions": safe_positions[:3],  # Show top 3
                "message": f"Found {len(safe_positions)} safe positions"
            }
        
        elif hint_request.hint_type == "conflict_highlight":
            conflicts = find_conflicts(board)
            hint_data = {
                "type": "conflicts",
                "conflicts": conflicts,
                "message": f"Found {len(conflicts)} conflicts to resolve"
            }
        
        elif hint_request.hint_type == "next_move":
            safe_positions = get_safe_positions(board)
            next_row = next((i for i, pos in enumerate(board) if pos == -1), 0)
            
            if safe_positions:
                next_move = next((pos for pos in safe_positions if pos[0] == next_row), safe_positions[0])
                hint_data = {
                    "type": "next_move",
                    "suggested_row": next_move[0],
                    "suggested_col": next_move[1],
                    "message": f"Try placing a queen at row {next_move[0]}, column {next_move[1]}"
                }
            else:
                hint_data = {
                    "type": "next_move",
                    "message": "No safe moves available. Consider removing some queens."
                }
        
        # Update hints used
        session["hints_used"] += 1
        
        return GameResponse(
            status="success",
            message="Hint provided",
            data={
                "hint": hint_data,
                "hints_remaining": max_hints - session["hints_used"] if max_hints != 999 else "unlimited"
            }
        )
    except Exception as e:
        logger.error(f"Error getting hint: {e}")
        return GameResponse(
            status="error",
            message="Failed to generate hint. Please try again."
        )

@router.post("/game/submit")
async def submit_solution(submission: SolutionSubmission):
    """Submit the final solution and check if it's a new unique solution"""
    # Extract validated data from Pydantic model
    session_id = submission.session_id
    solution = submission.solution
    completion_time_seconds = submission.completion_time_seconds
    hints_used = submission.hints_used 
    undo_count = submission.undo_count
    
    # Try to get session from memory first, then fall back to database
    session = get_session_or_recover(session_id)
    if not session:
        return {"status": "error", "message": "Game session not found or already completed"}
    
    board = solution if solution else session["board"]
    
    # Validate solution
    if not all(pos != -1 for pos in board):
        return {"status": "error", "message": "Board is not complete"}
    
    conflicts = find_conflicts(board)
    if conflicts:
        return {"status": "error", "message": f"Solution has {len(conflicts)} conflicts"}
    
    # Check if solution matches one of the 92 valid solutions
    solution_hash = hashlib.md5(json.dumps(board).encode()).hexdigest()
    
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Check if this solution exists and if it's already been found
        cursor.execute("""
            SELECT solution_id, is_found, found_by_player_id 
            FROM EightQueensSolutions 
            WHERE solution_hash = %s
        """, (solution_hash,))
        
        solution_record = cursor.fetchone()
        
        if not solution_record:
            return {
                "status": "error",
                "message": "Invalid solution - not one of the 92 valid Eight Queens solutions"
            }
        
        # Check if already found
        if solution_record['is_found']:
            # Get previous finder's name
            cursor.execute("SELECT name FROM players WHERE id = %s", (solution_record['found_by_player_id'],))
            previous_finder = cursor.fetchone()
            previous_finder_name = previous_finder['name'] if previous_finder else "Another player"
            
            # Still save as duplicate submission
            cursor.execute("""
                INSERT INTO EightQueensResults 
                (session_id, player_id, player_name, solution_submitted, 
                 algorithm_type, execution_time_ms, is_correct, is_duplicate, previous_finder_name)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE, TRUE, %s)
            """, (
                session["id"], session["player_id"], session["player_name"],
                json.dumps(board), session.get("algorithm_type", "sequential"),
                completion_time_seconds * 1000, previous_finder_name
            ))
            
            cursor.close()
            connection.close()
            
            return {
                "status": "duplicate",
                "message": f"This solution was already found by {previous_finder_name}!",
                "data": {
                    "is_valid": True,
                    "is_duplicate": True,
                    "found_by": previous_finder_name,
                    "hint": "Try placing queens in different positions to find a unique solution!"
                }
            }
        
        # Mark solution as found
        cursor.execute("""
            UPDATE EightQueensSolutions 
            SET is_found = TRUE, 
                found_by_player_id = %s, 
                found_at = NOW()
            WHERE solution_id = %s
        """, (session["player_id"], solution_record['solution_id']))
        
        # Get total progress
        cursor.execute("SELECT COUNT(*) as total, SUM(is_found) as found FROM EightQueensSolutions")
        progress = cursor.fetchone()
        solutions_found = int(progress['found']) if progress['found'] else 0
        total_solutions = int(progress['total'])
        
        # Check if this is the 92nd solution (all found!)
        all_solutions_found = False
        if solutions_found >= total_solutions:
            all_solutions_found = True
            logger.info(f"🎉 ALL 92 SOLUTIONS FOUND! Player {session['player_name']} found the last one!")
            
            # Reset all flags for next round
            cursor.execute("""
                UPDATE EightQueensSolutions 
                SET is_found = FALSE, found_by_player_id = NULL, found_at = NULL
            """)
            
            # This player still gets credit for finding it
            cursor.execute("""
                UPDATE EightQueensSolutions 
                SET is_found = TRUE, found_by_player_id = %s, found_at = NOW()
                WHERE solution_id = %s
            """, (session["player_id"], solution_record['solution_id']))
            
            solutions_found = 1  # Reset counter for display
            logger.info("Solution flags reset. New discovery challenge started!")
    
    except Exception as e:
        logger.error(f"Error checking solution: {e}")
        connection.close()
        raise HTTPException(status_code=500, detail="Error processing solution")
    
    # === RUN BOTH ALGORITHMS FOR TIMING COMPARISON (PDSA Requirement) ===
    import time as time_module
    
    # Sequential timing
    seq_start = time_module.perf_counter()
    _ = sequential_solver.solve_all()
    sequential_time_ms = (time_module.perf_counter() - seq_start) * 1000
    
    # Threaded timing
    thread_start = time_module.perf_counter()
    _ = threaded_solver.solve_all()
    threaded_time_ms = (time_module.perf_counter() - thread_start) * 1000
    
    speedup_factor = sequential_time_ms / threaded_time_ms if threaded_time_ms > 0 else 1
    
    logger.info(f"Algorithm timing - Sequential: {sequential_time_ms:.3f}ms, Threaded: {threaded_time_ms:.3f}ms, Speedup: {speedup_factor:.2f}x")
    
    # Calculate score
    completion_time = completion_time_seconds if completion_time_seconds > 0 else (time.time() - session["start_time"])
    base_score = session["settings"]["base_score"]
    time_bonus = max(0, 300 - completion_time) if completion_time < 300 else 0
    hint_penalty = hints_used * 10
    score = max(0, base_score + time_bonus - hint_penalty)
    
    # Update session
    session["completed"] = True
    session["final_score"] = int(score)
    session["completion_time"] = completion_time
    session["hints_used"] = hints_used
    session["undos_used"] = undo_count
    
    # Save successful submission to EightQueensResults
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO EightQueensResults 
            (session_id, player_id, player_name, solution_id, solution_submitted, 
             algorithm_type, execution_time_ms, is_correct, is_duplicate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, FALSE)
        """, (
            session["id"], session["player_id"], session["player_name"],
            solution_record['solution_id'], json.dumps(board),
            session.get("algorithm_type", "sequential"),
            completion_time * 1000
        ))
        
        # Update game session as completed
        cursor.execute("""
            UPDATE game_sessions 
            SET status = 'completed', 
                game_completed = 1,
                is_completed = 1,
                session_end = NOW(),
                current_board = %s,
                score = %s,
                hints_used = %s,
                undo_count = %s,
                completion_time_seconds = %s,
                sequential_time_ms = %s,
                threaded_time_ms = %s,
                speedup_factor = %s
            WHERE id = %s
        """, (
            json.dumps(board),
            int(score),
            session["hints_used"],
            session["undos_used"],
            int(completion_time),
            round(sequential_time_ms, 3),
            round(threaded_time_ms, 3),
            round(speedup_factor, 2),
            session["id"]
        ))
        
        # Update player statistics
        cursor.execute("""
            UPDATE players 
            SET total_games_played = total_games_played + 1,
                games_completed = games_completed + 1,
                highest_score = GREATEST(highest_score, %s),
                last_played = NOW()
            WHERE id = %s
        """, (int(score), session["player_id"]))
        
    finally:
        cursor.close()
        connection.close()
    
    # Clean up memory session
    if session["id"] in game_sessions:
        del game_sessions[session["id"]]
    
    # Prepare success message
    if all_solutions_found:
        message = f"🏆 INCREDIBLE! You found the 92nd solution! All solutions discovered! Challenge has been reset for new players."
    else:
        message = f"🎉 NEW SOLUTION DISCOVERED! You found solution #{solutions_found} of 92!"
    
    return {
        "status": "success",
        "message": message,
        "data": {
            "score": int(score),
            "completion_time": int(completion_time),
            "hints_used": session["hints_used"],
            "undo_count": session["undos_used"],
            "is_valid": True,
            "is_new_discovery": True,
            "all_found": all_solutions_found,
            "solutions_found": solutions_found,
            "total_solutions": total_solutions,
            "progress_percentage": round((solutions_found / total_solutions) * 100, 1),
            "algorithm_comparison": {
                "sequential_time_ms": round(sequential_time_ms, 3),
                "threaded_time_ms": round(threaded_time_ms, 3),
                "speedup": f"{speedup_factor:.2f}x",
                "faster_algorithm": "threaded" if speedup_factor > 1 else "sequential"
            }
        }
    }

@router.post("/algorithms/compare")
async def compare_algorithms():
    """
    Run BOTH Sequential and Threaded solvers and return timing comparison.
    This satisfies the PDSA requirement to record time for BOTH algorithms per game round.
    """
    import time as time_module
    
    # Run Sequential Solver
    seq_start = time_module.perf_counter()
    seq_solutions = sequential_solver.solve_all()
    seq_time_ms = (time_module.perf_counter() - seq_start) * 1000
    
    # Run Threaded Solver
    thread_start = time_module.perf_counter()
    thread_solutions = threaded_solver.solve_all()
    thread_time_ms = (time_module.perf_counter() - thread_start) * 1000
    
    # Calculate speedup
    speedup = seq_time_ms / thread_time_ms if thread_time_ms > 0 else 1
    time_saved = seq_time_ms - thread_time_ms
    
    # Save to database for the 15-round chart requirement
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO algorithm_comparisons 
            (sequential_time_ms, threaded_time_ms, speedup_factor, solutions_count, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (round(seq_time_ms, 3), round(thread_time_ms, 3), round(speedup, 2), len(seq_solutions)))
        cursor.close()
        connection.close()
        logger.info(f"Algorithm comparison saved: Seq={seq_time_ms:.3f}ms, Thread={thread_time_ms:.3f}ms")
    except Exception as e:
        logger.warning(f"Could not save comparison to DB: {e}")
    
    return {
        "status": "success",
        "data": {
            "sequential": {
                "time_ms": round(seq_time_ms, 3),
                "solutions_found": len(seq_solutions)
            },
            "threaded": {
                "time_ms": round(thread_time_ms, 3),
                "solutions_found": len(thread_solutions)
            },
            "comparison": {
                "speedup": f"{speedup:.2f}x",
                "faster_algorithm": "threaded" if speedup > 1 else "sequential",
                "time_saved_ms": round(time_saved, 3),
                "improvement_percent": round((1 - (1/speedup)) * 100, 1) if speedup > 0 else 0
            }
        }
    }


@router.get("/algorithms/history")
async def get_algorithm_comparison_history():
    """
    Get the last 15 algorithm comparison runs for the Individual Report chart.
    """
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id as round_number, sequential_time_ms, threaded_time_ms, 
                   speedup_factor, solutions_count, created_at
            FROM algorithm_comparisons
            ORDER BY created_at DESC
            LIMIT 15
        """)
        comparisons = cursor.fetchall()
        cursor.close()
        connection.close()
        
        # Calculate statistics
        if comparisons:
            seq_times = [c['sequential_time_ms'] for c in comparisons if c['sequential_time_ms']]
            thread_times = [c['threaded_time_ms'] for c in comparisons if c['threaded_time_ms']]
            
            stats = {
                "total_rounds": len(comparisons),
                "avg_sequential_ms": round(sum(seq_times) / len(seq_times), 3) if seq_times else 0,
                "avg_threaded_ms": round(sum(thread_times) / len(thread_times), 3) if thread_times else 0,
                "avg_speedup": round(sum(seq_times) / sum(thread_times), 2) if thread_times and sum(thread_times) > 0 else 1
            }
        else:
            stats = {"total_rounds": 0}
        
        return {
            "status": "success",
            "data": {
                "comparisons": comparisons,
                "statistics": stats
            }
        }
    except Exception as e:
        logger.error(f"Error getting comparison history: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if connection:
            connection.close()


@router.get("/solutions/progress")
async def get_solutions_progress():
    """Get progress on discovering all 92 solutions"""
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get total progress
        cursor.execute("""
            SELECT COUNT(*) as total, SUM(is_found) as found 
            FROM EightQueensSolutions
        """)
        progress = cursor.fetchone()
        
        solutions_found = int(progress['found']) if progress['found'] else 0
        total_solutions = int(progress['total'])
        
        # Get recent discoveries
        cursor.execute("""
            SELECT p.name as player_name, eq.found_at
            FROM EightQueensSolutions eq
            JOIN players p ON eq.found_by_player_id = p.id
            WHERE eq.is_found = TRUE
            ORDER BY eq.found_at DESC
            LIMIT 10
        """)
        recent_discoveries = cursor.fetchall()
        
        # Get top discoverers
        cursor.execute("""
            SELECT p.name as player_name, COUNT(*) as solutions_found
            FROM EightQueensSolutions eq
            JOIN players p ON eq.found_by_player_id = p.id
            WHERE eq.is_found = TRUE
            GROUP BY p.id, p.name
            ORDER BY solutions_found DESC
            LIMIT 5
        """)
        top_discoverers = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return {
            "status": "success",
            "data": {
                "solutions_found": solutions_found,
                "total_solutions": total_solutions,
                "remaining": total_solutions - solutions_found,
                "progress_percentage": round((solutions_found / total_solutions) * 100, 1),
                "recent_discoveries": recent_discoveries,
                "top_discoverers": top_discoverers
            }
        }
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        connection.close()
        return {"status": "error", "message": "Error fetching progress"}

@router.post("/solutions/reset")
async def reset_all_solutions():
    """
    Manually reset all solution found flags.
    Use this for testing or when you want to restart the discovery challenge.
    """
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get current statistics before reset
        cursor.execute("SELECT COUNT(*) as total, SUM(is_found) as found FROM EightQueensSolutions")
        before_stats = cursor.fetchone()
        
        # Reset all flags
        cursor.execute("""
            UPDATE EightQueensSolutions 
            SET is_found = FALSE, found_by_player_id = NULL, found_at = NULL
        """)
        
        affected_rows = cursor.rowcount
        
        cursor.close()
        connection.close()
        
        logger.info(f"Manual reset: {affected_rows} solutions reset to unfound state")
        
        return {
            "status": "success",
            "message": f"All {affected_rows} solutions have been reset!",
            "data": {
                "solutions_reset": affected_rows,
                "previously_found": int(before_stats['found']) if before_stats['found'] else 0,
                "total_solutions": int(before_stats['total'])
            }
        }
    except Exception as e:
        logger.error(f"Error resetting solutions: {e}")
        connection.close()
        return {"status": "error", "message": "Error resetting solutions"}

@router.post("/solutions/test-mark-all-found")
async def test_mark_all_found():
    """
    TEST ONLY: Mark all solutions as found to test auto-reset.
    This simulates the scenario where all 92 solutions have been discovered.
    """
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        
        # Get a test player ID (use first player or create dummy)
        cursor.execute("SELECT id FROM players LIMIT 1")
        player = cursor.fetchone()
        test_player_id = player[0] if player else 1
        
        # Mark all as found
        cursor.execute("""
            UPDATE EightQueensSolutions 
            SET is_found = TRUE, 
                found_by_player_id = %s, 
                found_at = NOW()
        """, (test_player_id,))
        
        affected = cursor.rowcount
        
        cursor.close()
        connection.close()
        
        logger.info(f"TEST: Marked {affected} solutions as found for testing auto-reset")
        
        return {
            "status": "success",
            "message": f"TEST: Marked all {affected} solutions as found. Next submission will trigger auto-reset!",
            "data": {"marked_as_found": affected}
        }
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        connection.close()
        return {"status": "error", "message": str(e)}

@router.get("/info/difficulties")
async def get_difficulty_info():
    """Get difficulty level information"""
    return {
        "difficulty_levels": {
            level: {
                "name": settings["name"],
                "max_hints": "Unlimited" if settings["max_hints"] == 999 else settings["max_hints"],
                "undo_allowed": settings["undo_allowed"],
                "time_limit": f"{settings['time_limit_seconds']//60} minutes" if settings["time_limit_seconds"] else "No limit",
                "visual_hints": settings["visual_hints"],
                "base_score": settings["base_score"]
            }
            for level, settings in DIFFICULTY_SETTINGS.items()
        }
    }

@router.get("/leaderboards/{difficulty}")
async def get_leaderboard(difficulty: str):
    """Get leaderboard (mock data for demo)"""
    mock_leaderboard = [
        {"player_name": "Player1", "score": 250, "completion_time": 180, "hints_used": 0},
        {"player_name": "Player2", "score": 200, "completion_time": 240, "hints_used": 1},
        {"player_name": "Player3", "score": 150, "completion_time": 300, "hints_used": 2}
    ]
    
    return {
        "status": "success", 
        "data": {
            "difficulty": difficulty,
            "leaderboard": mock_leaderboard
        }
    }

@router.post("/players/register")
async def register_player(registration: PlayerRegistration):
    """Register a new player with username validation"""
    try:
        # Check if username already exists in database
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM players WHERE LOWER(name) = LOWER(%s)", (registration.name,))
            if cursor.fetchone():
                raise HTTPException(status_code=409, detail="Username already exists. Please choose a different username.")
            
            # Create new player in database
            insert_query = """
                INSERT INTO players (name)
                VALUES (%s)
            """
            cursor.execute(insert_query, (registration.name,))
            player_id = cursor.lastrowid
        finally:
            connection.close()
        
        return {
            "status": "success",
            "message": f"Welcome to Eight Queens, {registration.name}! Profile created successfully.",
            "data": {
                "player_id": player_id,
                "name": registration.name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Player registration error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create player profile")

@router.get("/players/{player_name}/profile")
async def get_player_profile(player_name: str):
    """Get player profile and statistics"""
    try:
        # Find player by name in database
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM players WHERE LOWER(name) = LOWER(%s)", (player_name,))
            player = cursor.fetchone()
            
            if not player:
                raise HTTPException(status_code=404, detail="Player not found")
            
            # Get player game statistics
            cursor.execute("""
                SELECT difficulty, COUNT(*) as games_played,
                       SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as games_completed,
                       MAX(score) as best_score,
                       AVG(score) as avg_score,
                       SUM(score) as total_score,
                       MIN(CASE WHEN is_completed = 1 THEN completion_time_seconds END) as best_time
                FROM game_sessions 
                WHERE player_id = %s 
                GROUP BY difficulty
            """, (player['id'],))
            difficulty_stats = cursor.fetchall()
            
            # Get total games count
            cursor.execute("SELECT COUNT(*) as total_games FROM game_sessions WHERE player_id = %s", (player['id'],))
            total_games_result = cursor.fetchone()
            total_games = total_games_result['total_games'] if total_games_result else 0
        finally:
            connection.close()
        
        return {
            "status": "success",
            "message": "Player profile retrieved",
            "data": {
                "player_info": {
                    "id": player['id'],
                    "name": player['name'],
                    "created_at": player['created_at'].timestamp() if player['created_at'] else None
                },
                "total_games_played": total_games,
                "solutions_found": player.get('total_solutions_found', 0),
                "highest_score": player.get('highest_score', 0),
                "difficulty_stats": difficulty_stats,
                "total_games": total_games,
                "recent_activity": []
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get player profile error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve player profile")


@router.get("/players/{player_name}/solutions")
async def get_player_solutions(player_name: str):
    """Get all solutions discovered by a specific player"""
    try:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Find player
            cursor.execute("SELECT id FROM players WHERE LOWER(name) = LOWER(%s)", (player_name,))
            player = cursor.fetchone()
            
            if not player:
                return {"status": "error", "message": "Player not found", "data": {"solutions": []}}
            
            # Get solutions found by this player
            cursor.execute("""
                SELECT eq.solution_id, eq.solution_hash, eq.found_at,
                       s.solution_array, s.solution_number
                FROM EightQueensSolutions eq
                LEFT JOIN solutions s ON eq.solution_id = s.id
                WHERE eq.found_by_player_id = %s AND eq.is_found = TRUE
                ORDER BY eq.found_at DESC
            """, (player['id'],))
            solutions = cursor.fetchall()
            
            # Format solutions for response
            formatted_solutions = []
            for sol in solutions:
                formatted_solutions.append({
                    "solution_number": sol.get('solution_number') or sol.get('solution_id'),
                    "solution_array": sol.get('solution_array') or sol.get('solution_hash', 'N/A'),
                    "found_at": sol['found_at'].isoformat() if sol.get('found_at') else None
                })
            
            return {
                "status": "success",
                "data": {
                    "player_name": player_name,
                    "solutions": formatted_solutions,
                    "total_found": len(formatted_solutions)
                }
            }
        finally:
            cursor.close()
            connection.close()
            
    except Exception as e:
        logger.error(f"Error getting player solutions: {e}")
        return {"status": "error", "message": str(e), "data": {"solutions": []}}


@router.get("/players/check/{player_name}")
async def check_player_exists(player_name: str):
    """Check if a player exists in the database"""
    try:
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, name FROM players WHERE LOWER(name) = LOWER(%s)", (player_name,))
            player = cursor.fetchone()
        finally:
            connection.close()
            
            if player:
                return {
                    "status": "success",
                    "message": "Player found",
                    "data": {
                        "exists": True,
                        "player_id": player['id'],
                        "name": player['name']
                    }
                }
            else:
                return {
                    "status": "success", 
                    "message": "Player not found",
                    "data": {
                        "exists": False
                    }
                }
        
    except Exception as e:
        logger.error(f"Check player error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check player")

@router.post("/game/exit", response_model=GameResponse)
async def exit_game(exit_data: GameExitRequest):
    """Handle game exit and save current progress as incomplete"""
    try:
        session_id = exit_data.session_id
        current_board = exit_data.current_board
        hints_used = exit_data.hints_used
        undos_used = exit_data.undos_used
        time_elapsed = exit_data.time_elapsed
        
        # Remove from memory sessions
        if session_id and session_id in game_sessions:
            del game_sessions[session_id]
        
        # Update database record as exited
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            update_query = """
                UPDATE game_sessions 
                SET status = 'exited', 
                    session_end = NOW(),
                    current_board = %s,
                    hints_used = %s,
                    undo_count = %s,
                    completion_time_seconds = %s,
                    game_completed = 0
                WHERE id = %s
            """
            cursor.execute(update_query, (
                json.dumps(current_board) if current_board else None,
                hints_used,
                undos_used, 
                int(time_elapsed),
                session_id
            ))
        finally:
            connection.close()
        
        return GameResponse(
            status="success",
            message="Game exited successfully. Progress saved.",
            data={"session_id": session_id, "status": "exited"}
        )
        
    except Exception as e:
        logger.error(f"Exit game error: {e}")
        return GameResponse(
            status="success",  # Still return success for user experience
            message="Game exited (progress may not be saved)",
            data={}
        )