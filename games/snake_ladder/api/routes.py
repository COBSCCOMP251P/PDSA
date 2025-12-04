"""
FastAPI Routes for Snake and Ladder Game
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.game_logic import SnakeLadderBoard, validate_board_size, generate_answer_choices
from algorithms.pathfinding import find_min_moves_bfs, find_min_moves_dfs, validate_answer, compare_algorithms
from algorithms.database import SnakeLadderDB

# Import shared configuration
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'shared', 'backend'))
from config import DATABASE_CONFIG

# Initialize router
router = APIRouter(prefix="/snake-ladder", tags=["Snake and Ladder"])

# Initialize database handler
db_handler = SnakeLadderDB(DATABASE_CONFIG)

# Global storage for active game sessions (in production, use Redis or similar)
active_games: Dict[str, Dict] = {}


# Pydantic Models
class InitGameRequest(BaseModel):
    """Request model for initializing a new game."""
    player_name: str = Field(..., min_length=1, max_length=100, description="Player's name")
    board_size: int = Field(..., ge=6, le=12, description="Board size (6-12)")
    email: Optional[str] = Field(None, max_length=150, description="Player's email (optional)")
    
    @validator('player_name')
    def validate_player_name(cls, v):
        if not v.strip():
            raise ValueError("Player name cannot be empty")
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError("Invalid email format")
        return v


class InitGameResponse(BaseModel):
    """Response model for game initialization."""
    session_id: str
    board_config: Dict
    answer_choices: List[int]
    message: str


class SubmitAnswerRequest(BaseModel):
    """Request model for submitting an answer."""
    session_id: str = Field(..., description="Game session ID")
    player_answer: int = Field(..., ge=0, description="Player's answer (minimum dice throws)")
    
    @validator('player_answer')
    def validate_answer(cls, v):
        if v < 0:
            raise ValueError("Answer must be non-negative")
        return v


class SubmitAnswerResponse(BaseModel):
    """Response model for answer submission."""
    is_correct: bool
    correct_answer: int
    player_answer: int
    bfs_result: Dict
    dfs_result: Dict
    message: str
    player_stats: Optional[Dict] = None


class PlayerStatsResponse(BaseModel):
    """Response model for player statistics."""
    player_name: str
    stats: Dict


class LeaderboardResponse(BaseModel):
    """Response model for leaderboard."""
    leaderboard: List[Dict]


class AlgorithmComparisonResponse(BaseModel):
    """Response model for algorithm comparison."""
    comparison: Dict
    board_size: Optional[int] = None


# API Endpoints

@router.post("/init", response_model=InitGameResponse, status_code=status.HTTP_201_CREATED)
async def initialize_game(request: InitGameRequest):
    """
    Initialize a new Snake and Ladder game.
    
    Creates a new game session with a random board configuration,
    calculates the minimum moves using both BFS and DFS algorithms,
    and generates answer choices for the player.
    """
    try:
        # Validate board size
        validate_board_size(request.board_size)
        
        # Create or get player
        player_id = db_handler.create_or_get_player(request.player_name, request.email)
        
        # Create game session
        session_id = db_handler.create_game_session(player_id)
        session_key = f"session_{session_id}"
        
        # Generate board
        board = SnakeLadderBoard(request.board_size)
        
        # Calculate minimum moves using both algorithms
        bfs_result = find_min_moves_bfs(board)
        dfs_result = find_min_moves_dfs(board)
        
        # Use BFS result as the correct answer (BFS guarantees shortest path)
        correct_answer = bfs_result.min_moves
        
        # Generate answer choices
        answer_choices = generate_answer_choices(correct_answer)
        
        # Save algorithm performance to database
        db_handler.save_algorithm_performance(
            session_id, board.n, "bfs", 
            bfs_result.execution_time_ms, bfs_result.min_moves, board.to_dict()
        )
        db_handler.save_algorithm_performance(
            session_id, board.n, "dfs",
            dfs_result.execution_time_ms, dfs_result.min_moves, board.to_dict()
        )
        
        # Store game state
        active_games[session_key] = {
            "session_id": session_id,
            "player_id": player_id,
            "player_name": request.player_name,
            "board": board,
            "bfs_result": bfs_result,
            "dfs_result": dfs_result,
            "correct_answer": correct_answer,
            "answer_choices": answer_choices
        }
        
        return InitGameResponse(
            session_id=session_key,
            board_config=board.to_dict(),
            answer_choices=answer_choices,
            message=f"Game initialized successfully! Board size: {board.n}x{board.n}"
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                          detail=f"Failed to initialize game: {str(e)}")


@router.post("/submit", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """
    Submit player's answer and check if it's correct.
    
    Validates the answer, saves the result to database, and returns
    detailed feedback including algorithm performance metrics.
    """
    try:
        session_key = request.session_id
        
        # Check if session exists
        if session_key not in active_games:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                              detail="Game session not found or expired")
        
        game_state = active_games[session_key]
        
        # Validate answer
        is_correct = validate_answer(request.player_answer, game_state["correct_answer"])
        
        # Save result to database
        db_handler.save_game_result(
            session_id=game_state["session_id"],
            player_name=game_state["player_name"],
            board_size=game_state["board"].n,
            algorithm_type="bfs",  # Primary algorithm
            player_answer=request.player_answer,
            correct_answer=game_state["correct_answer"],
            is_correct=is_correct,
            execution_time_ms=game_state["bfs_result"].execution_time_ms,
            board_config=game_state["board"].to_dict()
        )
        
        # Complete game session
        db_handler.complete_game_session(game_state["session_id"])
        
        # Get updated player stats
        player_stats = db_handler.get_player_stats(game_state["player_name"])
        
        # Prepare response message
        if is_correct:
            message = "🎉 Congratulations! Your answer is correct!"
        else:
            message = f"❌ Incorrect. The correct answer is {game_state['correct_answer']} moves."
        
        response = SubmitAnswerResponse(
            is_correct=is_correct,
            correct_answer=game_state["correct_answer"],
            player_answer=request.player_answer,
            bfs_result=game_state["bfs_result"].to_dict(),
            dfs_result=game_state["dfs_result"].to_dict(),
            message=message,
            player_stats=player_stats
        )
        
        # Clean up session
        del active_games[session_key]
        
        return response
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail=f"Failed to submit answer: {str(e)}")


@router.get("/stats/{player_name}", response_model=PlayerStatsResponse)
async def get_player_stats(player_name: str):
    """
    Get statistics for a specific player.
    
    Returns total games played, correct answers, accuracy, and other metrics.
    """
    try:
        stats = db_handler.get_player_stats(player_name)
        
        return PlayerStatsResponse(
            player_name=player_name,
            stats=stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail=f"Failed to retrieve player stats: {str(e)}")


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(limit: int = 10):
    """
    Get the top players leaderboard.
    
    Returns rankings based on correct answers and accuracy.
    """
    try:
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        leaderboard = db_handler.get_leaderboard(limit)
        
        return LeaderboardResponse(leaderboard=leaderboard)
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail=f"Failed to retrieve leaderboard: {str(e)}")


@router.get("/algorithm-comparison", response_model=AlgorithmComparisonResponse)
async def get_algorithm_comparison(board_size: Optional[int] = None):
    """
    Compare BFS and DFS algorithm performance.
    
    Optionally filter by board size to see performance on specific board dimensions.
    """
    try:
        if board_size is not None:
            validate_board_size(board_size)
        
        comparison = db_handler.get_algorithm_comparison(board_size)
        
        return AlgorithmComparisonResponse(
            comparison=comparison,
            board_size=board_size
        )
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                          detail=f"Failed to retrieve algorithm comparison: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Snake and Ladder API",
        "active_sessions": len(active_games)
    }
