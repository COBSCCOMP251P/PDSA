"""
FastAPI Backend for Tower of Hanoi Interactive Game
Provides REST API endpoints for game management, player submissions, and algorithm benchmarking
"""

import os
import random
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import mysql.connector
from mysql.connector import Error
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from algorithms import AlgorithmRunner, solve_tower_of_hanoi
from validator import GameValidator, parse_move_sequence


# ===== HELPER FUNCTIONS =====
def calculate_4peg_optimal_moves(n: int) -> int:
    """
    Calculate optimal number of moves for 4-peg Tower of Hanoi using Frame-Stewart algorithm.
    Uses dynamic programming approach to find minimum moves.
    
    Args:
        n: Number of disks
    
    Returns:
        Minimum number of moves needed
    
    Time Complexity: O(n²)
    Space Complexity: O(n)
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 3
    
    # DP array to store minimum moves for each disk count
    dp = [0] * (n + 1)
    dp[1] = 1  # Base case: 1 disk requires 1 move
    dp[2] = 3  # Base case: 2 disks requires 3 moves
    
    # For each disk count from 3 to n
    for i in range(3, n + 1):
        dp[i] = float('inf')
        
        # Try splitting at different positions k (1 to i-1)
        # Move k disks to auxiliary peg, move remaining i-k disks to destination (3-peg style),
        # then move k disks from auxiliary to destination
        for k in range(1, i):
            moves = 2 * dp[k] + (2 ** (i - k) - 1)
            dp[i] = min(dp[i], moves)
    
    return dp[n]


# Pydantic Models for API
class CreateRoundRequest(BaseModel):
    """Request model for creating a new round"""
    n_disks: Optional[int] = None  # Number of disks (3-7). If not provided, randomly chosen.
    peg_count: int  # Number of pegs (3 or 4)


class SubmissionRequest(BaseModel):
    """Request model for submitting a solution"""
    player_name: str  # Player name
    declared_moves: int  # Declared number of moves
    move_sequence: List[str]  # List of moves in format 'X->Y'


class RoundResponse(BaseModel):
    """Response model for round information"""
    id: int
    n_disks: int
    peg_count: int
    source: str
    destination: str
    started_at: datetime


class SubmissionResponse(BaseModel):
    """Response model for submission validation"""
    correct: bool
    errors: Optional[List[Dict[str, Any]]] = None
    saved_submission_id: Optional[int] = None
    validation_details: Dict[str, Any]
    player_id: int


class AlgorithmRunResponse(BaseModel):
    """Response model for algorithm run results"""
    id: int
    algorithm_name: str
    peg_count: int
    computed_moves: int
    runtime_ms: float
    run_at: datetime


class LeaderboardEntry(BaseModel):
    """Response model for leaderboard entries"""
    name: str
    total_submissions: int
    correct_submissions: int
    best_moves: Optional[int]
    avg_moves: Optional[float]
    last_submission: Optional[datetime]


class GameResult(BaseModel):
    """Request model for submitting game results"""
    player_name: str
    disk_count: int
    peg_count: int = 3  # Default to 3 pegs for backward compatibility
    moves: int
    time_taken: float  # in seconds (can have decimal places)
    is_optimal: bool = False


# Database Connection Manager
class DatabaseManager:
    """Manages MySQL database connections and operations"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DATABASE_HOST', 'localhost'),
            'port': int(os.getenv('DATABASE_PORT', '3306')),
            'user': os.getenv('DATABASE_USER', 'root'),
            'password': os.getenv('DATABASE_PASSWORD', ''),
            'database': os.getenv('DATABASE_NAME', 'pdsa_games'),
            'autocommit': True,
            'raise_on_warnings': True
        }
    
    def get_connection(self):
        """Get a database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a database query"""
        connection = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute(query, params or ())
            
            if fetch:
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    connection.commit()
                    return cursor.lastrowid
            
            # Commit for INSERT, UPDATE, DELETE operations
            if not query.strip().upper().startswith('SELECT'):
                connection.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            if connection:
                connection.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_transaction(self, queries: List[tuple]):
        """Execute multiple queries in a transaction"""
        connection = None
        try:
            connection = self.get_connection()
            connection.autocommit = False
            cursor = connection.cursor(dictionary=True)
            
            results = []
            for query, params in queries:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('INSERT'):
                    results.append(cursor.lastrowid)
                else:
                    results.append(cursor.fetchall() if query.strip().upper().startswith('SELECT') else cursor.rowcount)
            
            connection.commit()
            return results
            
        except Error as e:
            if connection:
                connection.rollback()
            raise HTTPException(status_code=500, detail=f"Transaction error: {e}")
        finally:
            if connection and connection.is_connected():
                connection.close()


# Global instances
db_manager = DatabaseManager()
algorithm_runner = AlgorithmRunner()
game_validator = GameValidator()


# Dependency injection
def get_db_manager():
    """Dependency for database manager"""
    return db_manager


def get_algorithm_runner():
    """Dependency for algorithm runner"""
    return algorithm_runner


def get_game_validator():
    """Dependency for game validator"""
    return game_validator


# Background task for running algorithms
async def run_algorithms_for_round(round_id: int, n_disks: int, peg_count: int):
    """Background task to run all algorithms for a round"""
    try:
        # Run all appropriate algorithms
        results = solve_tower_of_hanoi(n_disks, peg_count)
        
        # Store results in database
        queries = []
        for result in results:
            query = """
                INSERT INTO algorithm_runs (round_id, algorithm_name, peg_count, computed_moves, runtime_ms)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                round_id,
                result.algorithm_name,
                peg_count,
                result.moves,
                result.runtime_ms
            )
            queries.append((query, params))
        
        db_manager.execute_transaction(queries)
        print(f"✅ Algorithm runs completed for round {round_id}")
        
    except Exception as e:
        print(f"❌ Error running algorithms for round {round_id}: {e}")


# FastAPI App Configuration
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("🚀 Starting Tower of Hanoi API server...")
    
    # Test database connection
    try:
        db_manager.execute_query("SELECT 1", fetch=True)
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Tower of Hanoi API server...")


app = FastAPI(
    title="Tower of Hanoi Interactive Game API",
    description="REST API for Tower of Hanoi game with algorithm benchmarking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Endpoints

@app.post("/api/rounds", response_model=RoundResponse)
async def create_round(
    request: CreateRoundRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseManager = Depends(get_db_manager)
):
    """Create a new Tower of Hanoi round"""
    
    # Generate random disk count if not provided (3-7 range)
    n_disks = request.n_disks or random.randint(3, 7)
    
    # Insert round into database
    query = """
        INSERT INTO rounds (n_disks, peg_count, source, destination)
        VALUES (%s, %s, %s, %s)
    """
    params = (n_disks, request.peg_count, 'A', 'D')
    
    round_id = db.execute_query(query, params)
    
    # Start algorithm benchmarking in background
    background_tasks.add_task(run_algorithms_for_round, round_id, n_disks, request.peg_count)
    
    # Fetch and return the created round
    round_data = db.execute_query(
        "SELECT * FROM rounds WHERE round_id = %s",
        (round_id,),
        fetch=True
    )[0]
    
    # Map round_id to id for response model
    round_data['id'] = round_data['round_id']
    
    return RoundResponse(**round_data)


@app.get("/api/rounds/{round_id}", response_model=RoundResponse)
async def get_round(round_id: int, db: DatabaseManager = Depends(get_db_manager)):
    """Get details of a specific round"""
    
    query = "SELECT * FROM rounds WHERE round_id = %s"
    results = db.execute_query(query, (round_id,), fetch=True)
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Round {round_id} not found")
    
    # Map round_id to id for response model
    round_data = results[0]
    round_data['id'] = round_data['round_id']
    
    return RoundResponse(**round_data)


@app.post("/api/rounds/{round_id}/submit", response_model=SubmissionResponse)
async def submit_solution(
    round_id: int,
    submission: SubmissionRequest,
    db: DatabaseManager = Depends(get_db_manager),
    validator: GameValidator = Depends(get_game_validator)
):
    """Submit a solution for validation and scoring"""
    
    # Get round details
    round_query = "SELECT * FROM rounds WHERE round_id = %s"
    round_results = db.execute_query(round_query, (round_id,), fetch=True)
    
    if not round_results:
        raise HTTPException(status_code=404, detail=f"Round {round_id} not found")
    
    round_data = round_results[0]
    
    # Get or create player
    player_query = "SELECT player_id FROM Players WHERE player_name = %s"
    player_results = db.execute_query(player_query, (submission.player_name,), fetch=True)
    
    if player_results:
        player_id = player_results[0]['player_id']
    else:
        # Create new player
        insert_player_query = "INSERT INTO Players (player_name) VALUES (%s)"
        player_id = db.execute_query(insert_player_query, (submission.player_name,))
    
    # Validate the submission
    validation_result = validator.validate_submission(
        n_disks=round_data['n_disks'],
        peg_count=round_data['peg_count'],
        move_sequence=submission.move_sequence,
        declared_moves=submission.declared_moves,
        source=round_data['source'],
        destination=round_data['destination']
    )
    
    # Store submission in database
    submission_query = """
        INSERT INTO submissions (round_id, player_id, declared_moves, move_sequence, is_correct, validation_error)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    validation_error = None if validation_result['is_valid'] else validation_result['detailed_report']
    move_sequence_str = ','.join(submission.move_sequence)
    
    submission_params = (
        round_id,
        player_id,
        submission.declared_moves,
        move_sequence_str,
        validation_result['is_valid'],
        validation_error
    )
    
    submission_id = db.execute_query(submission_query, submission_params)
    
    return SubmissionResponse(
        correct=validation_result['is_valid'],
        errors=validation_result['errors'] if not validation_result['is_valid'] else None,
        saved_submission_id=submission_id if validation_result['is_valid'] else None,
        validation_details=validation_result,
        player_id=player_id
    )


@app.get("/api/rounds/{round_id}/algorithm-runs", response_model=List[AlgorithmRunResponse])
async def get_algorithm_runs(round_id: int, db: DatabaseManager = Depends(get_db_manager)):
    """Get algorithm benchmark results for a round"""
    
    query = """
        SELECT run_id as id, algorithm_name, peg_count, computed_moves, runtime_ms, run_at
        FROM algorithm_runs 
        WHERE round_id = %s
        ORDER BY runtime_ms ASC
    """
    
    results = db.execute_query(query, (round_id,), fetch=True)
    
    return [AlgorithmRunResponse(**result) for result in results]


@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10, db: DatabaseManager = Depends(get_db_manager)):
    """Get the leaderboard of top players"""
    
    query = """
        SELECT 
            hr.player_name as name,
            COUNT(hr.result_id) as total_submissions,
            SUM(CASE WHEN hr.is_correct = 1 THEN 1 ELSE 0 END) as correct_submissions,
            MIN(CASE WHEN hr.is_correct = 1 THEN hr.player_moves ELSE NULL END) as best_moves,
            ROUND(AVG(CASE WHEN hr.is_correct = 1 THEN hr.player_moves ELSE NULL END), 2) as avg_moves,
            MAX(hr.submitted_at) as last_submission
        FROM HanoiResults hr
        WHERE hr.submitted_at >= '1970-01-01 00:00:01'
        GROUP BY hr.player_name
        HAVING total_submissions > 0
        ORDER BY correct_submissions DESC, best_moves ASC, avg_moves ASC
        LIMIT %s
    """
    
    results = db.execute_query(query, (limit,), fetch=True)
    
    return [LeaderboardEntry(**result) for result in results]


@app.post("/api/leaderboard")
async def save_game_result(
    game_result: GameResult,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Save a completed game result to the HanoiResults table.
    Validates input, calculates optimal moves for both 3-peg and 4-peg solutions,
    and saves player name along with correct response.
    """
    
    try:
        # ===== INPUT VALIDATION =====
        if not game_result.player_name or not game_result.player_name.strip():
            raise HTTPException(
                status_code=400, 
                detail="Player name is required and cannot be empty"
            )
        
        if len(game_result.player_name) > 100:
            raise HTTPException(
                status_code=400,
                detail="Player name must be 100 characters or less"
            )
        
        if game_result.disk_count < 1 or game_result.disk_count > 20:
            raise HTTPException(
                status_code=400,
                detail="Disk count must be between 1 and 20"
            )
        
        if game_result.peg_count not in [3, 4]:
            raise HTTPException(
                status_code=400,
                detail="Peg count must be either 3 or 4"
            )
        
        if game_result.moves < 1:
            raise HTTPException(
                status_code=400,
                detail="Move count must be at least 1"
            )
        
        if game_result.time_taken < 0:
            raise HTTPException(
                status_code=400,
                detail="Time taken cannot be negative"
            )
        
        print(f"✓ Validation passed - Saving game result: {game_result}")
        
        # ===== CALCULATE OPTIMAL MOVES =====
        # For 3-peg: Use classic formula 2^n - 1
        # For 4-peg: Use Frame-Stewart algorithm (DP optimal)
        if game_result.peg_count == 3:
            optimal_moves = (2 ** game_result.disk_count) - 1
            algorithm_name = "3-Peg Classic"
        else:  # 4-peg
            # Calculate optimal moves using Frame-Stewart/Dynamic Programming
            optimal_moves = calculate_4peg_optimal_moves(game_result.disk_count)
            algorithm_name = "4-Peg Frame-Stewart"
        
        print(f"✓ Optimal moves for {game_result.disk_count} disks, {game_result.peg_count} pegs: {optimal_moves}")
        
        current_time = datetime.now()
        
        # Determine if solution is correct
        # Player is correct if they completed the puzzle (moved all disks)
        is_correct = True
        
        # Determine if solution is optimal
        is_optimal = game_result.moves == optimal_moves
        
        # Calculate efficiency percentage
        efficiency = min(optimal_moves / game_result.moves * 100, 100.0) if game_result.moves > 0 else 0
        
        # Step 1: Find or create player
        player_query = "SELECT player_id FROM Players WHERE player_name = %s"
        player_result = db.execute_query(player_query, (game_result.player_name,), fetch=True)
        
        if player_result:
            player_id = player_result[0]['player_id']
            print(f"Found existing player: {player_id}")
        else:
            # Create new player
            create_player_query = "INSERT INTO Players (player_name, created_at) VALUES (%s, %s)"
            db.execute_query(create_player_query, (game_result.player_name, current_time))
            # Get the new player_id
            player_result = db.execute_query(player_query, (game_result.player_name,), fetch=True)
            player_id = player_result[0]['player_id']
            print(f"Created new player: {player_id}")
        
        # Step 2: Find or create active game session
        session_query = """
            SELECT session_id FROM gamesessions 
            WHERE player_id = %s AND game_type = 'tower_hanoi' AND status = 'active'
            ORDER BY started_at DESC LIMIT 1
        """
        session_result = db.execute_query(session_query, (player_id,), fetch=True)
        
        if session_result:
            session_id = session_result[0]['session_id']
            print(f"Found existing session: {session_id}")
        else:
            # Create new game session
            create_session_query = """
                INSERT INTO gamesessions (player_id, game_type, started_at, status) 
                VALUES (%s, 'tower_hanoi', %s, 'active')
            """
            db.execute_query(create_session_query, (player_id, current_time))
            # Get the new session_id
            session_result = db.execute_query(session_query, (player_id,), fetch=True)
            session_id = session_result[0]['session_id']
            print(f"Created new session: {session_id}")
        
        # Step 3: Insert game result into HanoiResults
        insert_query = """
            INSERT INTO HanoiResults 
            (session_id, player_name, disk_count, peg_count, algorithm_type, 
             player_moves, correct_moves, is_correct, execution_time_ms, submitted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Determine algorithm type based on peg count
        algorithm_type = 'recursive_3peg' if game_result.peg_count == 3 else 'recursive_4peg'
        
        params = (
            session_id,
            game_result.player_name,
            game_result.disk_count,
            game_result.peg_count,  # Use actual peg_count from request
            algorithm_type,  # Set algorithm based on peg count
            game_result.moves,
            optimal_moves,
            is_correct,
            game_result.time_taken * 1000,  # Convert to milliseconds
            current_time
        )
        
        result = db.execute_query(insert_query, params)
        print(f"Query result: {result}")
        
        # Calculate efficiency for response
        efficiency = min(optimal_moves / game_result.moves, 1.0) if game_result.moves > 0 else 0
        
        return {
            "success": True,
            "message": "Game result saved successfully to HanoiResults",
            "efficiency": round(efficiency * 100, 1),
            "optimal_moves": optimal_moves,
            "player_moves": game_result.moves,
            "is_optimal": game_result.moves == optimal_moves,
            "session_id": session_id,
            "player_id": player_id
        }
        
    except Exception as e:
        print(f"Error saving game result: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save game result: {str(e)}")


@app.get("/api/stats/algorithms")
async def get_algorithm_stats(db: DatabaseManager = Depends(get_db_manager)):
    """Get comprehensive algorithm performance statistics"""
    
    query = """
        SELECT 
            algorithm_name,
            peg_count,
            COUNT(*) as run_count,
            AVG(computed_moves) as avg_moves,
            MIN(computed_moves) as min_moves,
            MAX(computed_moves) as max_moves,
            AVG(runtime_ms) as avg_runtime_ms,
            MIN(runtime_ms) as min_runtime_ms,
            MAX(runtime_ms) as max_runtime_ms
        FROM algorithm_runs
        GROUP BY algorithm_name, peg_count
        ORDER BY peg_count, avg_moves ASC
    """
    
    results = db.execute_query(query, fetch=True)
    
    return results


@app.get("/api/stats/rounds")
async def get_round_stats(db: DatabaseManager = Depends(get_db_manager)):
    """Get statistics about rounds and submissions"""
    
    query = """
        SELECT 
            r.n_disks,
            r.peg_count,
            COUNT(r.round_id) as total_rounds,
            COUNT(s.submission_id) as total_submissions,
            COUNT(CASE WHEN s.correct THEN 1 END) as correct_submissions,
            AVG(CASE WHEN s.correct THEN s.declared_moves END) as avg_winning_moves,
            MIN(CASE WHEN s.correct THEN s.declared_moves END) as best_winning_moves
        FROM rounds r
        LEFT JOIN submissions s ON r.round_id = s.round_id
        GROUP BY r.n_disks, r.peg_count
        ORDER BY r.n_disks, r.peg_count
    """
    
    results = db.execute_query(query, fetch=True)
    
    return results


class ValidateRequest(BaseModel):
    """Request model for move validation"""
    n_disks: int
    peg_count: int
    move_sequence: List[str]
    declared_moves: Optional[int] = None


@app.post("/api/validate")
async def validate_moves(
    request: ValidateRequest,
    validator: GameValidator = Depends(get_game_validator)
):
    """
    Validate a move sequence without saving to database.
    Validates input parameters, move sequence format, and solution correctness.
    """
    
    try:
        # ===== INPUT VALIDATION =====
        if request.n_disks < 1 or request.n_disks > 20:
            raise HTTPException(
                status_code=400, 
                detail="Disk count must be between 1 and 20"
            )
        
        if request.peg_count not in [3, 4]:
            raise HTTPException(
                status_code=400, 
                detail="Peg count must be either 3 or 4"
            )
        
        if not request.move_sequence or len(request.move_sequence) == 0:
            raise HTTPException(
                status_code=400,
                detail="Move sequence cannot be empty"
            )
        
        if request.declared_moves < 1:
            raise HTTPException(
                status_code=400,
                detail="Declared moves must be at least 1"
            )
        
        if request.declared_moves != len(request.move_sequence):
            raise HTTPException(
                status_code=400,
                detail=f"Declared moves ({request.declared_moves}) does not match actual move sequence length ({len(request.move_sequence)})"
            )
        
        # ===== VALIDATE MOVE FORMAT =====
        for i, move in enumerate(request.move_sequence):
            if not isinstance(move, str) or '->' not in move:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid move format at position {i}: '{move}'. Expected format 'X->Y'"
                )
            
            parts = move.split('->')
            if len(parts) != 2:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid move format at position {i}: '{move}'. Expected format 'X->Y'"
                )
            
            try:
                source = int(parts[0])
                dest = int(parts[1])
                
                if source < 1 or source > request.peg_count:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid source peg {source} in move {i}. Must be between 1 and {request.peg_count}"
                    )
                
                if dest < 1 or dest > request.peg_count:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid destination peg {dest} in move {i}. Must be between 1 and {request.peg_count}"
                    )
                
                if source == dest:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid move at position {i}: source and destination cannot be the same ({source})"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid peg numbers in move {i}: '{move}'. Pegs must be integers"
                )
        
        print(f"✓ Validation request - Disks: {request.n_disks}, Pegs: {request.peg_count}, Moves: {len(request.move_sequence)}")
        
        # ===== VALIDATE SOLUTION =====
        validation_result = validator.validate_submission(
            n_disks=request.n_disks,
            peg_count=request.peg_count,
            move_sequence=request.move_sequence,
            declared_moves=request.declared_moves
        )
        
        print(f"✓ Validation result: {validation_result}")
        
        return validation_result
        
    except HTTPException as he:
        # Re-raise HTTP exceptions (validation errors)
        print(f"❌ Validation error: {he.detail}")
        raise
        
    except Exception as e:
        print(f"❌ Error validating moves: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate moves: {str(e)}"
        )


@app.get("/api/health")
async def health_check(db_manager: DatabaseManager = Depends(get_db_manager)):
    """Health check endpoint"""
    try:
        # Test database connection
        db_manager.execute_query("SELECT 1", fetch=True)
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}
        )


@app.post("/api/benchmark")
async def run_benchmark(data: dict):
    """
    Run algorithm benchmarks and return execution times.
    Compares 3-peg (recursive/iterative) and 4-peg (Frame-Stewart/DP) algorithms.
    """
    import time
    
    try:
        # ===== INPUT VALIDATION =====
        n_disks = data.get('n_disks', 5)
        peg_count = data.get('peg_count', 3)
        
        if not isinstance(n_disks, int):
            raise HTTPException(
                status_code=400, 
                detail="n_disks must be an integer"
            )
        
        if not isinstance(peg_count, int):
            raise HTTPException(
                status_code=400,
                detail="peg_count must be an integer"
            )
        
        if n_disks < 1 or n_disks > 20:
            raise HTTPException(
                status_code=400, 
                detail="n_disks must be between 1 and 20"
            )
        
        if peg_count not in [3, 4]:
            raise HTTPException(
                status_code=400, 
                detail="peg_count must be 3 or 4"
            )
        
        print(f"✓ Running benchmark - Disks: {n_disks}, Pegs: {peg_count}")
        
        results = []
        
        # ===== RUN ALGORITHMS =====
        if peg_count == 3:
            # Run 3-peg algorithms
            
            # Recursive 3-Peg
            print(f"  - Testing Recursive 3-Peg...")
            start_time = time.perf_counter()
            recursive_moves = hanoi_3peg_recursive(n_disks)
            end_time = time.perf_counter()
            runtime_ms = (end_time - start_time) * 1000
            
            results.append({
                'algorithm': 'Recursive 3-Peg',
                'runtime_ms': round(runtime_ms, 4),
                'moves': len(recursive_moves),
                'optimal': True
            })
            print(f"    ✓ Completed in {runtime_ms:.4f}ms, {len(recursive_moves)} moves")
            
            # Iterative 3-Peg
            print(f"  - Testing Iterative 3-Peg...")
            start_time = time.perf_counter()
            iterative_moves = hanoi_3peg_iterative(n_disks)
            end_time = time.perf_counter()
            runtime_ms = (end_time - start_time) * 1000
            
            results.append({
                'algorithm': 'Iterative 3-Peg',
                'runtime_ms': round(runtime_ms, 4),
                'moves': len(iterative_moves),
                'optimal': True
            })
            print(f"    ✓ Completed in {runtime_ms:.4f}ms, {len(iterative_moves)} moves")
            
        else:  # peg_count == 4
            # Run 4-peg algorithms
            
            # Frame-Stewart 4-Peg
            print(f"  - Testing Frame-Stewart 4-Peg...")
            start_time = time.perf_counter()
            frame_stewart_moves = hanoi_4peg_frame_stewart(n_disks)
            end_time = time.perf_counter()
            runtime_ms = (end_time - start_time) * 1000
            
            results.append({
                'algorithm': 'Frame-Stewart 4-Peg',
                'runtime_ms': round(runtime_ms, 4),
                'moves': len(frame_stewart_moves),
                'optimal': True
            })
            print(f"    ✓ Completed in {runtime_ms:.4f}ms, {len(frame_stewart_moves)} moves")
            
            # Dynamic Programming 4-Peg
            print(f"  - Testing DP 4-Peg...")
            start_time = time.perf_counter()
            dp_moves = hanoi_4peg_dp(n_disks)
            end_time = time.perf_counter()
            runtime_ms = (end_time - start_time) * 1000
            
            results.append({
                'algorithm': 'Dynamic Programming 4-Peg',
                'runtime_ms': round(runtime_ms, 4),
                'moves': len(dp_moves),
                'optimal': True
            })
            print(f"    ✓ Completed in {runtime_ms:.4f}ms, {len(dp_moves)} moves")
        
        print(f"✅ Benchmark completed successfully!")
        
        return {
            'success': True,
            'n_disks': n_disks,
            'peg_count': peg_count,
            'results': results
        }
        
    except HTTPException as he:
        # Re-raise HTTP exceptions (validation errors)
        print(f"❌ HTTP Exception: {he.detail}")
        raise
        
    except Exception as e:
        print(f"❌ Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run benchmark: {str(e)}"
        )


# ===== ALGORITHM IMPLEMENTATIONS =====

def hanoi_3peg_recursive(n, source='A', dest='C', aux='B'):
    """Classic recursive Tower of Hanoi algorithm for 3 pegs"""
    moves = []
    
    def move_disks(n, src, dst, aux):
        if n == 1:
            moves.append(f"{src}->{dst}")
            return
        move_disks(n - 1, src, aux, dst)
        moves.append(f"{src}->{dst}")
        move_disks(n - 1, aux, dst, src)
    
    move_disks(n, source, dest, aux)
    return moves


def hanoi_3peg_iterative(n, source='A', dest='C', aux='B'):
    """Iterative Tower of Hanoi algorithm for 3 pegs using stack"""
    moves = []
    stack = [(n, source, dest, aux)]
    
    while stack:
        disks, src, dst, aux = stack.pop()
        
        if disks == 1:
            moves.append(f"{src}->{dst}")
        else:
            stack.append((disks - 1, aux, dst, src))
            stack.append((1, src, dst, aux))
            stack.append((disks - 1, src, aux, dst))
    
    return moves


def hanoi_4peg_frame_stewart(n, source='A', dest='D', aux1='B', aux2='C'):
    """Frame-Stewart algorithm for 4-peg Tower of Hanoi"""
    moves = []
    memo = {}
    
    def optimal_k(n):
        """Find optimal split point using Frame-Stewart formula"""
        if n <= 2:
            return 1
        if n in memo:
            return memo[n]
        
        best_k = 1
        min_moves = float('inf')
        
        for k in range(1, n):
            # Approximate Frame-Stewart moves
            moves_k = 2 * optimal_k(k) if k > 1 else 2
            moves_remaining = (2 ** (n - k)) - 1
            total = moves_k + moves_remaining
            
            if total < min_moves:
                min_moves = total
                best_k = k
        
        memo[n] = best_k
        return best_k
    
    def move_tower(n, src, dst, a1, a2):
        if n == 0:
            return
        if n == 1:
            moves.append(f"{src}->{dst}")
            return
        
        k = optimal_k(n)
        
        # Move top k disks to auxiliary using all 4 pegs
        move_tower(k, src, a1, a2, dst)
        
        # Move remaining n-k disks using 3 pegs (classical)
        hanoi_3peg_helper(n - k, src, dst, a2, moves)
        
        # Move k disks from auxiliary to destination
        move_tower(k, a1, dst, src, a2)
    
    move_tower(n, source, dest, aux1, aux2)
    return moves


def hanoi_3peg_helper(n, src, dst, aux, moves_list):
    """Helper function for 3-peg Tower of Hanoi within Frame-Stewart"""
    if n == 1:
        moves_list.append(f"{src}->{dst}")
        return
    hanoi_3peg_helper(n - 1, src, aux, dst, moves_list)
    moves_list.append(f"{src}->{dst}")
    hanoi_3peg_helper(n - 1, aux, dst, src, moves_list)


def hanoi_4peg_dp(n, source='A', dest='D', aux1='B', aux2='C'):
    """
    Dynamic Programming approach for 4-peg Tower of Hanoi
    Uses bottom-up DP table to find optimal k-split and generates move sequence
    """
    moves = []
    
    # Build DP table for minimum moves
    dp = [0] * (n + 1)
    optimal_k = [0] * (n + 1)
    
    # Base cases
    dp[0] = 0
    dp[1] = 1
    
    # Fill DP table bottom-up
    for i in range(2, n + 1):
        min_moves = float('inf')
        best_k = 1
        
        for k in range(1, i):
            # Moves: k disks to aux (4-peg) + (i-k) disks to dest (3-peg) + k disks aux to dest (4-peg)
            moves_needed = 2 * dp[k] + ((1 << (i - k)) - 1)  # 2^(i-k) - 1
            
            if moves_needed < min_moves:
                min_moves = moves_needed
                best_k = k
        
        dp[i] = min_moves
        optimal_k[i] = best_k
    
    def solve_with_dp(n_disks, src, dst, a1, a2):
        """Recursively solve using precomputed optimal splits"""
        if n_disks == 0:
            return
        
        if n_disks == 1:
            moves.append(f"{src}->{dst}")
            return
        
        # Use precomputed optimal k
        k = optimal_k[n_disks]
        
        # Step 1: Move top k disks to first auxiliary peg using all 4 pegs
        solve_with_dp(k, src, a1, a2, dst)
        
        # Step 2: Move bottom (n-k) disks to destination using 3 pegs (classical Hanoi)
        def move_3peg_classical(m, s, d, aux):
            if m == 0:
                return
            if m == 1:
                moves.append(f"{s}->{d}")
                return
            move_3peg_classical(m - 1, s, aux, d)
            moves.append(f"{s}->{d}")
            move_3peg_classical(m - 1, aux, d, s)
        
        move_3peg_classical(n_disks - k, src, dst, a2)
        
        # Step 3: Move k disks from auxiliary to destination using all 4 pegs
        solve_with_dp(k, a1, dst, src, a2)
    
    # Execute the solution
    solve_with_dp(n, source, dest, aux1, aux2)
    return moves


# Error Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "ValueError"}
    )


@app.exception_handler(mysql.connector.Error)
async def database_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred", "type": "DatabaseError"}
    )


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
        log_level="info"
    )