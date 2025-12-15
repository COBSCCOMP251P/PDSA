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
    Calculate optimal number of moves for 4-peg Tower of Hanoi.
    Uses optimal mathematical formula to find minimum moves.
    
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
    algorithm_type: Optional[str] = None
    disk_count: Optional[int] = None
    peg_count: Optional[int] = None
    best_time_ms: Optional[float] = None
    avg_time_ms: Optional[float] = None


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
            'database': os.getenv('DATABASE_NAME', 'pdsa_games'),
            'autocommit': True,
            'raise_on_warnings': True
        }
        # Only add password if it's set (empty string causes auth issues)
        password = os.getenv('DATABASE_PASSWORD', '')
        if password:
            self.config['password'] = password
            
        self.db_available = False
        self.in_memory_storage = {
            'rounds': {},
            'submissions': {},
            'algorithm_runs': {},
            'leaderboard': {},
            'players': {},
            'sessions': {},
            'next_id': {'rounds': 1, 'submissions': 1, 'algorithm_runs': 1, 'players': 1, 'sessions': 1}
        }
    
    def get_connection(self):
        """Get a database connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            self.db_available = True
            return connection
        except Error as e:
            self.db_available = False
            return None
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a database query"""
        connection = self.get_connection()
        
        # Use in-memory storage if database is unavailable
        if not connection:
            return self._execute_in_memory(query, params, fetch)
        
        try:
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
            # Fall back to in-memory storage on error
            return self._execute_in_memory(query, params, fetch)
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def _execute_in_memory(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute query using in-memory storage"""
        query_upper = query.strip().upper()
        
        # Handle INSERT queries
        if query_upper.startswith('INSERT INTO ROUNDS'):
            round_id = self.in_memory_storage['next_id']['rounds']
            self.in_memory_storage['rounds'][round_id] = {
                'round_id': round_id,
                'id': round_id,
                'n_disks': params[0],
                'peg_count': params[1],
                'source': params[2],
                'destination': params[3],
                'started_at': datetime.now()
            }
            self.in_memory_storage['next_id']['rounds'] += 1
            return round_id
        
        # Handle INSERT into Players
        elif query_upper.startswith('INSERT INTO PLAYERS'):
            player_id = self.in_memory_storage['next_id']['players']
            player_name = params[0] if params else 'Anonymous'
            self.in_memory_storage['players'][player_id] = {
                'player_id': player_id,
                'player_name': player_name,
                'created_at': params[1] if len(params) > 1 else datetime.now()
            }
            self.in_memory_storage['next_id']['players'] += 1
            return player_id
        
        # Handle INSERT into gamesessions
        elif query_upper.startswith('INSERT INTO GAMESESSIONS'):
            session_id = self.in_memory_storage['next_id']['sessions']
            self.in_memory_storage['sessions'][session_id] = {
                'session_id': session_id,
                'player_id': params[0] if params else 0,
                'game_type': params[1] if len(params) > 1 else 'tower_hanoi',
                'started_at': params[2] if len(params) > 2 else datetime.now(),
                'status': params[3] if len(params) > 3 else 'active'
            }
            self.in_memory_storage['next_id']['sessions'] += 1
            return session_id
        
        # Handle INSERT into HanoiResults (leaderboard)
        elif query_upper.startswith('INSERT INTO HANOIRESULTS'):
            result_id = len(self.in_memory_storage['leaderboard']) + 1
            self.in_memory_storage['leaderboard'][result_id] = {
                'result_id': result_id,
                'session_id': params[0] if params else 0,
                'player_name': params[1] if len(params) > 1 else 'Anonymous',
                'disk_count': params[2] if len(params) > 2 else 0,
                'peg_count': params[3] if len(params) > 3 else 3,
                'player_moves': params[5] if len(params) > 5 else 0,
                'correct_moves': params[6] if len(params) > 6 else 0,
                'is_correct': params[7] if len(params) > 7 else 0,
                'submitted_at': datetime.now()
            }
            return result_id
        
        # Handle SELECT queries for Players
        elif 'FROM PLAYERS' in query_upper and 'WHERE PLAYER_NAME' in query_upper:
            if fetch:
                player_name = params[0] if params else None
                matching_players = [p for p in self.in_memory_storage['players'].values() 
                                  if p['player_name'] == player_name]
                return matching_players
        
        # Handle SELECT queries for gamesessions
        elif 'FROM GAMESESSIONS' in query_upper:
            if fetch:
                player_id = params[0] if params else None
                matching_sessions = [s for s in self.in_memory_storage['sessions'].values() 
                                    if s['player_id'] == player_id and s['status'] == 'active']
                return sorted(matching_sessions, key=lambda x: x['started_at'], reverse=True)[:1]
        
        # Handle SELECT queries for rounds
        elif 'FROM ROUNDS' in query_upper and 'WHERE ROUND_ID' in query_upper:
            if fetch:
                round_id = params[0] if params else None
                round_data = self.in_memory_storage['rounds'].get(round_id)
                return [round_data] if round_data else []
        
        # Handle SELECT queries for leaderboard
        elif 'FROM HANOIRESULTS' in query_upper:
            if fetch:
                # Return aggregated leaderboard data
                leaderboard_data = []
                player_stats = {}
                
                for result in self.in_memory_storage['leaderboard'].values():
                    name = result['player_name']
                    if name not in player_stats:
                        player_stats[name] = {
                            'name': name,
                            'total_submissions': 0,
                            'correct_submissions': 0,
                            'best_moves': None,
                            'avg_moves': None,
                            'total_correct_moves': 0,
                            'last_submission': None
                        }
                    
                    stats = player_stats[name]
                    stats['total_submissions'] += 1
                    if result.get('is_correct'):
                        stats['correct_submissions'] += 1
                        moves = result.get('player_moves', 0)
                        if stats['best_moves'] is None or moves < stats['best_moves']:
                            stats['best_moves'] = moves
                        stats['total_correct_moves'] += moves
                    
                    if stats['last_submission'] is None or result['submitted_at'] > stats['last_submission']:
                        stats['last_submission'] = result['submitted_at']
                
                # Calculate average moves for each player
                for stats in player_stats.values():
                    if stats['correct_submissions'] > 0:
                        stats['avg_moves'] = round(stats['total_correct_moves'] / stats['correct_submissions'], 2)
                    # Remove the helper field
                    stats.pop('total_correct_moves', None)
                
                return list(player_stats.values())
        
        # Handle other queries - return empty or default values
        elif fetch:
            return []
        
        return None
    
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
            MAX(hr.submitted_at) as last_submission,
            hr.algorithm_type,
            hr.disk_count,
            hr.peg_count,
            ROUND(MIN(CASE WHEN hr.is_correct = 1 THEN hr.execution_time_ms ELSE NULL END), 2) as best_time_ms,
            ROUND(AVG(CASE WHEN hr.is_correct = 1 THEN hr.execution_time_ms ELSE NULL END), 2) as avg_time_ms
        FROM HanoiResults hr
        WHERE hr.submitted_at >= '1970-01-01 00:00:01'
        GROUP BY hr.player_name, hr.algorithm_type, hr.disk_count, hr.peg_count
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
        # For 4-peg: Use optimal 4-peg algorithm
        if game_result.peg_count == 3:
            optimal_moves = (2 ** game_result.disk_count) - 1
            algorithm_name = "3-Peg Classic"
        else:  # 4-peg
            # Calculate optimal moves for 4-peg
            optimal_moves = calculate_4peg_optimal_moves(game_result.disk_count)
            algorithm_name = "4-Peg Optimal"
        
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
async def run_benchmark(data: dict, db: DatabaseManager = Depends(get_db_manager)):
    """
    Analyze actual gameplay benchmarks from database.
    Returns real performance statistics from stored gameplay data.
    """
    import time
    from collections import defaultdict
    
    try:
        # ===== FETCH ACTUAL DATA FROM DATABASE =====
        query = """
            SELECT 
                disk_count,
                peg_count,
                player_moves,
                correct_moves,
                execution_time_ms,
                is_correct,
                algorithm_type,
                submitted_at
            FROM HanoiResults
            ORDER BY submitted_at DESC
            LIMIT 100
        """
        
        gameplay_data = db.execute_query(query, fetch=True)
        
        if not gameplay_data or len(gameplay_data) == 0:
            # If no data, return empty results
            return {
                'success': True,
                'message': 'No gameplay data available yet. Play some games first!',
                'results': [],
                'statistics': {}
            }
        
        # ===== ANALYZE DATA BY CONFIGURATION =====
        stats_by_config = defaultdict(lambda: {
            'total_games': 0,
            'avg_moves': 0,
            'min_moves': float('inf'),
            'max_moves': 0,
            'avg_time_ms': 0,
            'optimal_moves': 0,
            'total_moves': 0,
            'total_time': 0
        })
        
        for record in gameplay_data:
            # Handle both dict and tuple formats
            if isinstance(record, dict):
                disk_count = record.get('disk_count', 0)
                peg_count = record.get('peg_count', 0)
                player_moves = record.get('player_moves', 0)
                execution_time_ms = record.get('execution_time_ms', 0)
                correct_moves = record.get('correct_moves', 0)
            else:
                continue  # Skip non-dict records
            
            if disk_count == 0 or peg_count == 0:
                continue  # Skip invalid records
            
            key = f"{disk_count}_disks_{peg_count}_pegs"
            stats = stats_by_config[key]
            
            stats['total_games'] += 1
            stats['total_moves'] += player_moves
            stats['total_time'] += execution_time_ms
            stats['min_moves'] = min(stats['min_moves'], player_moves)
            stats['max_moves'] = max(stats['max_moves'], player_moves)
            stats['optimal_moves'] = correct_moves
            stats['disk_count'] = disk_count
            stats['peg_count'] = peg_count
        
        # Calculate averages
        for key, stats in stats_by_config.items():
            if stats['total_games'] > 0:
                stats['avg_moves'] = round(stats['total_moves'] / stats['total_games'], 2)
                stats['avg_time_ms'] = round(stats['total_time'] / stats['total_games'], 2)
        
        # ===== FORMAT RESULTS FOR UI =====
        results = []
        for key, stats in sorted(stats_by_config.items()):
            algorithm_name = f"{stats['disk_count']} Disks, {stats['peg_count']} Pegs"
            
            results.append({
                'algorithm': algorithm_name,
                'runtime_ms': stats['avg_time_ms'],
                'moves': stats['avg_moves'],
                'optimal': stats['optimal_moves'],
                'games_played': stats['total_games'],
                'min_moves': stats['min_moves'],
                'max_moves': stats['max_moves'],
                'from_database': True
            })
        
        # Get input parameters for filtering (optional)
        n_disks = data.get('n_disks', None)
        peg_count = data.get('peg_count', None)
        
        # Filter results if parameters provided
        if n_disks or peg_count:
            filtered_results = []
            for result in results:
                match = True
                if n_disks and result.get('algorithm', '').find(f"{n_disks} Disks") == -1:
                    match = False
                if peg_count and result.get('algorithm', '').find(f"{peg_count} Pegs") == -1:
                    match = False
                if match:
                    filtered_results.append(result)
            results = filtered_results
        
        # ===== CALCULATE OVERALL STATISTICS =====
        total_games = sum(r['games_played'] for r in results)
        
        statistics = {
            'total_games_analyzed': total_games,
            'configurations': len(results),
            'data_source': 'database',
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Benchmark analysis complete! Analyzed {total_games} games across {len(results)} configurations")
        
        return {
            'success': True,
            'message': f'Analyzed {total_games} real gameplay sessions from database',
            'results': results,
            'statistics': statistics
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


def hanoi_4peg_optimal(n, source='A', dest='D', aux1='B', aux2='C'):
    """Optimal algorithm for 4-peg Tower of Hanoi"""
    moves = []
    memo = {}
    
    def optimal_k(n):
        """Find optimal split point for 4-peg algorithm"""
        if n <= 2:
            return 1
        if n in memo:
            return memo[n]
        
        best_k = 1
        min_moves = float('inf')
        
        for k in range(1, n):
            # Approximate optimal moves
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
    """Helper function for 3-peg Tower of Hanoi within 4-peg algorithm"""
    if n == 1:
        moves_list.append(f"{src}->{dst}")
        return
    hanoi_3peg_helper(n - 1, src, aux, dst, moves_list)
    moves_list.append(f"{src}->{dst}")
    hanoi_3peg_helper(n - 1, aux, dst, src, moves_list)

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


# ===== NEW GAMEPLAY API ENDPOINTS =====

class GameplayRequest(BaseModel):
    """Request model for saving gameplay session"""
    player_name: str
    algorithm_name: str
    disk_count: int
    peg_count: int
    move_count: int
    algorithm_execution_time_ms: float
    gameplay_time_ms: int
    generated_sequence: List[str]
    is_auto_completed: bool = False


class GameplayResponse(BaseModel):
    """Response model for gameplay session"""
    id: int
    player_name: str
    algorithm_name: str
    disk_count: int
    peg_count: int
    move_count: int
    algorithm_execution_time_ms: float
    gameplay_time_ms: int
    generated_sequence: List[str]
    is_auto_completed: bool
    created_at: datetime


class AutoCompleteRequest(BaseModel):
    """Request model for auto-complete game"""
    disk_count: int
    peg_count: int
    algorithm_name: str


class AutoCompleteResponse(BaseModel):
    """Response model for auto-complete solution"""
    algorithm_name: str
    disk_count: int
    peg_count: int
    move_count: int
    execution_time_ms: float
    move_sequence: List[str]


@app.post("/api/gameplay/save", response_model=GameplayResponse)
async def save_gameplay_session(
    gameplay: GameplayRequest,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Save a gameplay session to the database.
    Stores player name, algorithm details, execution time, gameplay time, and move sequence.
    """
    try:
        # Validate input
        if not gameplay.player_name or not gameplay.player_name.strip():
            raise HTTPException(status_code=400, detail="Player name is required")
        
        if gameplay.disk_count < 3 or gameplay.disk_count > 10:
            raise HTTPException(status_code=400, detail="Disk count must be between 3 and 10")
        
        if gameplay.peg_count not in [3, 4]:
            raise HTTPException(status_code=400, detail="Peg count must be 3 or 4")
        
        if gameplay.move_count < 1:
            raise HTTPException(status_code=400, detail="Move count must be at least 1")
        
        # Calculate optimal moves
        if gameplay.peg_count == 3:
            optimal_moves = (2 ** gameplay.disk_count) - 1
        else:  # 4 pegs
            optimal_moves = calculate_4peg_optimal_moves(gameplay.disk_count)
        
        # Auto-detect algorithm type based on move efficiency
        # If player made near-optimal moves (within 20%), classify as recursive (efficient/optimal approach)
        # Otherwise, classify as iterative (trial-and-error approach)
        move_efficiency = optimal_moves / gameplay.move_count if gameplay.move_count > 0 else 0
        
        if gameplay.peg_count == 3:
            if move_efficiency >= 0.8:  # Within 20% of optimal
                algorithm_type = "recursive_3peg"
            else:
                algorithm_type = "iterative_3peg"
        else:  # 4 pegs
            if move_efficiency >= 0.8:  # Within 20% of optimal
                algorithm_type = "recursive_4peg"
            else:
                algorithm_type = "iterative_4peg"
        
        correct_moves = optimal_moves
        
        # Check if solution is correct (player completed the puzzle)
        is_correct = True  # Since they completed the game
        
        # Insert directly into HanoiResults - single table storage
        insert_query = """
            INSERT INTO HanoiResults 
            (session_id, player_name, disk_count, peg_count, algorithm_type, 
             player_moves, correct_moves, is_correct, execution_time_ms, submitted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        result = db.execute_query(
            insert_query,
            (
                None,  # session_id is now nullable, not using GameSessions table
                gameplay.player_name,
                gameplay.disk_count,
                gameplay.peg_count,
                algorithm_type,
                gameplay.move_count,
                correct_moves,
                is_correct,
                gameplay.algorithm_execution_time_ms
            )
        )
        
        # Get the inserted record
        result_id = result
        
        select_query = "SELECT * FROM HanoiResults WHERE result_id = %s"
        result_data = db.execute_query(select_query, (result_id,), fetch=True)
        
        if not result_data:
            raise HTTPException(status_code=500, detail="Failed to retrieve saved session")
        
        saved_result = result_data[0]
        
        return GameplayResponse(
            id=saved_result['result_id'],
            player_name=saved_result['player_name'],
            algorithm_name=gameplay.algorithm_name,  # Return original name
            disk_count=saved_result['disk_count'],
            peg_count=saved_result['peg_count'],
            move_count=saved_result['player_moves'],
            algorithm_execution_time_ms=float(saved_result['execution_time_ms']),
            gameplay_time_ms=0,  # Not stored in HanoiResults
            generated_sequence=[],  # Not stored in HanoiResults
            is_auto_completed=gameplay.is_auto_completed,
            created_at=saved_result['submitted_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving gameplay session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save gameplay session: {str(e)}")


@app.post("/api/gameplay/auto-complete", response_model=AutoCompleteResponse)
async def auto_complete_game(
    request: AutoCompleteRequest,
    runner: AlgorithmRunner = Depends(get_algorithm_runner)
):
    """
    Auto-complete a Tower of Hanoi game using the specified algorithm.
    Returns the complete solution sequence with execution time.
    """
    try:
        # Validate input
        if request.disk_count < 3 or request.disk_count > 10:
            raise HTTPException(status_code=400, detail="Disk count must be between 3 and 10")
        
        if request.peg_count not in [3, 4]:
            raise HTTPException(status_code=400, detail="Peg count must be 3 or 4")
        
        # Get the algorithm
        try:
            algorithm = runner.get_algorithm_by_name(request.algorithm_name)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid algorithm name: {request.algorithm_name}")
        
        # Solve the problem
        if request.peg_count == 3:
            result = algorithm.solve(request.disk_count, 'A', 'C', ['B'])
        else:  # 4 pegs
            result = algorithm.solve(request.disk_count, 'A', 'D', ['B', 'C'])
        
        return AutoCompleteResponse(
            algorithm_name=result.algorithm_name,
            disk_count=request.disk_count,
            peg_count=request.peg_count,
            move_count=result.moves,
            execution_time_ms=result.runtime_ms,
            move_sequence=result.sequence
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in auto-complete: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to auto-complete: {str(e)}")


@app.get("/api/algorithms/list")
async def list_algorithms(peg_count: Optional[int] = None):
    """
    List available algorithms.
    
    Args:
        peg_count: Filter by peg count (3 or 4). If None, returns all algorithms.
    
    Returns:
        Dictionary with algorithm lists by peg count
    """
    algorithms = {
        "3_peg": [
            {"name": "Recursive 3-Peg", "description": "Classic recursive solution"},
            {"name": "Iterative 3-Peg", "description": "Stack-based iterative solution"}
        ],
        "4_peg": [
            {"name": "Recursive 4-Peg", "description": "Optimal recursive algorithm"},
            {"name": "Iterative 4-Peg", "description": "Stack-based iterative algorithm"}
        ]
    }
    
    if peg_count == 3:
        return {"algorithms": algorithms["3_peg"]}
    elif peg_count == 4:
        return {"algorithms": algorithms["4_peg"]}
    else:
        return algorithms


@app.get("/api/gameplay/history")
async def get_gameplay_history(
    player_name: Optional[str] = None,
    limit: int = 50,
    db: DatabaseManager = Depends(get_db_manager)
):
    """
    Get gameplay session history.
    
    Args:
        player_name: Filter by player name (optional)
        limit: Maximum number of records to return
    
    Returns:
        List of gameplay sessions
    """
    try:
        if player_name:
            query = """
                SELECT * FROM gameplay_sessions 
                WHERE player_name = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            results = db.execute_query(query, (player_name, limit), fetch=True)
        else:
            query = """
                SELECT * FROM gameplay_sessions 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            results = db.execute_query(query, (limit,), fetch=True)
        
        return {
            "sessions": [
                {
                    "id": row['id'],
                    "player_name": row['player_name'],
                    "algorithm_name": row['algorithm_name'],
                    "disk_count": row['disk_count'],
                    "peg_count": row['peg_count'],
                    "move_count": row['move_count'],
                    "algorithm_execution_time_ms": float(row['algorithm_execution_time_ms']),
                    "gameplay_time_ms": row['gameplay_time_ms'],
                    "is_auto_completed": bool(row['is_auto_completed']),
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None
                }
                for row in results
            ]
        }
        
    except Exception as e:
        print(f"Error fetching gameplay history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")


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