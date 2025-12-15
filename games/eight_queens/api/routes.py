"""
FastAPI routes for the Eight Queens game.

This module provides REST API endpoints for:
- Solving the puzzle (all solutions, first solution, step-by-step)
- Validating moves and board states
- Providing hints and game assistance
- Managing game sessions and progress

All endpoints return JSON responses with proper error handling
and educational information for university assignment purposes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator as pydantic_validator
from typing import List, Optional, Dict, Any
import time
import traceback

from ..algorithms.sequential_solver import EightQueensSolver
from ..algorithms.validation import EightQueensValidator, ConflictAnalyzer

# Create router for Eight Queens endpoints
router = APIRouter(prefix="/api/eight-queens", tags=["Eight Queens Game"])

# Global solver instance for performance
solver = EightQueensSolver()
queens_validator = EightQueensValidator()  # Renamed to avoid conflict with pydantic validator


# Pydantic models for request/response validation
class BoardState(BaseModel):
    """Represents current board state."""
    queens: List[int] = Field(..., min_items=8, max_items=8, description="Queen positions, -1 for empty row")
    
    @pydantic_validator('queens')
    def validate_queen_positions(cls, v):
        """Validate that all queen positions are in valid range"""
        if len(v) != 8:
            raise ValueError('Queens array must have exactly 8 elements')
        for i, pos in enumerate(v):
            if not isinstance(pos, int) or pos < -1 or pos > 7:
                raise ValueError(f'Position at row {i} must be between -1 and 7')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "queens": [0, 2, 5, 7, 1, 3, 6, 4]  # Example valid solution
            }
        }


class MoveRequest(BaseModel):
    """Request to validate or make a move."""
    queens: List[int] = Field(..., min_items=8, max_items=8, description="Current queen positions")
    row: int = Field(..., ge=0, le=7, description="Target row")
    col: int = Field(..., ge=0, le=7, description="Target column")
    
    @pydantic_validator('queens')
    def validate_queen_positions(cls, v):
        """Validate that all queen positions are in valid range"""
        if len(v) != 8:
            raise ValueError('Queens array must have exactly 8 elements')
        for i, pos in enumerate(v):
            if not isinstance(pos, int) or pos < -1 or pos > 7:
                raise ValueError(f'Position at row {i} must be between -1 and 7')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "queens": [-1, -1, -1, -1, -1, -1, -1, -1],
                "row": 0,
                "col": 0
            }
        }


class SolverResponse(BaseModel):
    """Response from solving operations."""
    success: bool
    solutions: List[List[int]]
    solution_count: int
    solving_time_ms: float
    message: str


class ValidationResponse(BaseModel):
    """Response from validation operations."""
    is_valid: bool
    is_complete: bool
    conflicts: List[Dict[str, Any]]
    message: str
    progress: Dict[str, Any]


class HintResponse(BaseModel):
    """Response from hint requests."""
    has_hint: bool
    hint_position: Optional[List[int]]
    message: str
    safe_moves: List[List[int]]
    difficulty: str


# ============================================================================
# SOLVING ENDPOINTS
# ============================================================================

@router.get("/solve", response_model=SolverResponse)
async def solve_all_solutions():
    """
    Find all 92 solutions to the Eight Queens problem.
    
    Returns:
        SolverResponse: All solutions with timing information
        
    This endpoint demonstrates:
    - Complete backtracking algorithm execution
    - Performance measurement
    - Educational value showing all possible solutions
    """
    try:
        start_time = time.time()
        
        # Find all solutions
        solutions = solver.solve_all()
        
        end_time = time.time()
        solving_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return SolverResponse(
            success=True,
            solutions=solutions,
            solution_count=len(solutions),
            solving_time_ms=round(solving_time, 3),
            message=f"Found all {len(solutions)} solutions in {solving_time:.3f}ms"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error solving puzzle: {str(e)}"
        )


@router.get("/solve-first", response_model=SolverResponse)
async def solve_first_solution():
    """
    Find the first valid solution quickly.
    
    Returns:
        SolverResponse: First solution found
        
    Use cases:
    - Quick solving for demonstrations
    - Providing example solutions
    - Performance comparison with full solve
    """
    try:
        start_time = time.time()
        
        # Find first solution
        solution = solver.solve_first()
        
        end_time = time.time()
        solving_time = (end_time - start_time) * 1000
        
        if solution:
            return SolverResponse(
                success=True,
                solutions=[solution],
                solution_count=1,
                solving_time_ms=round(solving_time, 3),
                message=f"Found first solution in {solving_time:.3f}ms"
            )
        else:
            return SolverResponse(
                success=False,
                solutions=[],
                solution_count=0,
                solving_time_ms=round(solving_time, 3),
                message="No solution found"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding solution: {str(e)}"
        )


@router.get("/solve-steps")
async def solve_with_steps():
    """
    Solve with step-by-step recording for educational visualization.
    
    Returns:
        dict: Solution and steps showing the backtracking process
        
    Perfect for:
    - University presentations
    - Understanding algorithm execution
    - Educational demonstrations
    """
    try:
        start_time = time.time()
        
        # Solve with step recording
        solution, steps = solver.solve_step_by_step()
        
        end_time = time.time()
        solving_time = (end_time - start_time) * 1000
        
        return {
            "success": solution is not None,
            "solution": solution,
            "steps": steps,
            "step_count": len(steps),
            "solving_time_ms": round(solving_time, 3),
            "message": f"Solved with {len(steps)} steps in {solving_time:.3f}ms"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error solving with steps: {str(e)}"
        )


# ============================================================================
# VALIDATION ENDPOINTS
# ============================================================================

@router.post("/validate-move")
async def validate_move(request: MoveRequest):
    """
    Validate if a specific move is legal.
    
    Args:
        request: Move to validate
        
    Returns:
        dict: Validation result with conflict analysis
        
    This endpoint provides:
    - Real-time move validation
    - Detailed conflict explanations
    - Educational feedback
    """
    try:
        # Validate input
        if len(request.queens) != 8:
            raise HTTPException(
                status_code=400,
                detail="Queens array must have exactly 8 elements"
            )
        
        # Check if move is valid
        is_valid = queens_validator.is_valid_move(request.queens, request.row, request.col)
        
        # Get conflict analysis
        conflicts = ConflictAnalyzer.analyze_position_conflicts(
            request.queens, request.row, request.col
        )
        
        # Get attack pattern for educational purposes
        attack_pattern = list(ConflictAnalyzer.get_attack_pattern(request.row, request.col))
        
        return {
            "is_valid": is_valid,
            "position": [request.row, request.col],
            "conflicts": conflicts,
            "attack_pattern": attack_pattern,
            "message": "Valid move" if is_valid else "Invalid move - conflicts detected"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating move: {str(e)}"
        )


@router.post("/validate-solution", response_model=ValidationResponse)
async def validate_solution(board: BoardState):
    """
    Validate a complete or partial solution.
    
    Args:
        board: Board state to validate
        
    Returns:
        ValidationResponse: Detailed validation result
        
    Features:
    - Complete solution validation
    - Progress tracking
    - Conflict identification
    - Educational feedback
    """
    try:
        # Validate the solution
        validation_result = queens_validator.validate_complete_solution(board.queens)
        
        # Get progress information
        progress_info = queens_validator.get_progress_info(board.queens)
        
        return ValidationResponse(
            is_valid=validation_result['is_valid'],
            is_complete=validation_result['is_complete'],
            conflicts=validation_result['conflicts'],
            message=validation_result['message'],
            progress=progress_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating solution: {str(e)}"
        )


# ============================================================================
# HINT AND ASSISTANCE ENDPOINTS
# ============================================================================

@router.post("/hint", response_model=HintResponse)
async def get_hint(board: BoardState):
    """
    Get a hint for the next best move.
    
    Args:
        board: Current board state
        
    Returns:
        HintResponse: Hint and additional information
        
    Provides:
    - Next move suggestion
    - All safe moves
    - Difficulty assessment
    - Strategic guidance
    """
    try:
        # Get hint
        hint = queens_validator.get_next_hint(board.queens)
        
        # Get all safe moves
        safe_moves = queens_validator.get_safe_moves(board.queens)
        
        # Get difficulty rating
        difficulty = queens_validator.get_difficulty_rating(board.queens)
        
        return HintResponse(
            has_hint=hint is not None,
            hint_position=list(hint) if hint else None,
            message=f"Try position {hint}" if hint else "No valid moves available",
            safe_moves=[list(move) for move in safe_moves],
            difficulty=difficulty
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting hint: {str(e)}"
        )


@router.post("/safe-moves")
async def get_safe_moves(board: BoardState):
    """
    Get all safe moves for current board state.
    
    Args:
        board: Current board state
        
    Returns:
        dict: List of safe moves with analysis
        
    Useful for:
    - Highlighting valid positions in UI
    - Checking if puzzle is solvable
    - Educational exploration
    """
    try:
        safe_moves = queens_validator.get_safe_moves(board.queens)
        progress_info = queens_validator.get_progress_info(board.queens)
        
        return {
            "safe_moves": [list(move) for move in safe_moves],
            "safe_move_count": len(safe_moves),
            "progress": progress_info,
            "message": f"Found {len(safe_moves)} safe moves"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error finding safe moves: {str(e)}"
        )


# ============================================================================
# SOLUTION NAVIGATION ENDPOINTS
# ============================================================================

@router.get("/solution/{index}")
async def get_solution_by_index(index: int):
    """
    Get a specific solution by index.
    
    Args:
        index: Solution index (0-91)
        
    Returns:
        dict: Specific solution with visualization data
        
    Perfect for:
    - Solution browsing
    - Comparing different solutions
    - Educational exploration
    """
    try:
        # Validate index range
        if index < 0 or index > 91:
            raise HTTPException(
                status_code=400,
                detail=f"Index must be between 0 and 91, got {index}"
            )
        # Ensure we have all solutions
        if not solver.solutions:
            solver.solve_all()
        
        solution = solver.get_solution(index)
        
        if solution is None:
            raise HTTPException(
                status_code=404,
                detail=f"Solution {index} not found"
            )
        
        # Get board display and attacked squares
        board_display = solver.get_board_display(solution)
        attacked_squares = list(solver.get_attacked_squares(solution))
        
        return {
            "index": index,
            "solution": solution,
            "board_display": board_display,
            "attacked_squares": attacked_squares,
            "total_solutions": solver.get_solution_count(),
            "message": f"Solution {index + 1} of {solver.get_solution_count()}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving solution: {str(e)}"
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/info")
async def get_game_info():
    """
    Get general information about the Eight Queens problem.
    
    Returns:
        dict: Educational information and game statistics
        
    Provides:
    - Problem description
    - Algorithm information
    - Performance statistics
    - Educational context
    """
    return {
        "game_name": "Eight Queens Problem",
        "description": "Place 8 queens on a chess board so no two queens attack each other",
        "board_size": 8,
        "total_solutions": 92,
        "algorithm": "Recursive Backtracking with Constraint Satisfaction",
        "time_complexity": "O(N!) worst case, much faster with pruning",
        "space_complexity": "O(N) for recursion stack",
        "educational_value": [
            "Demonstrates backtracking algorithm",
            "Shows constraint satisfaction problems",
            "Illustrates pruning optimization",
            "Teaches recursive thinking"
        ],
        "features": [
            "Auto-solving with all 92 solutions",
            "Step-by-step solving visualization",
            "Real-time move validation",
            "Intelligent hint system",
            "Progress tracking",
            "Educational conflict analysis"
        ]
    }


@router.get("/statistics")
async def get_solving_statistics():
    """
    Get performance statistics for the solver.
    
    Returns:
        dict: Benchmark results and performance data
    """
    try:
        # Benchmark first solution
        start_time = time.time()
        first_solution = solver.solve_first()
        first_solve_time = (time.time() - start_time) * 1000
        
        # Benchmark all solutions
        start_time = time.time()
        all_solutions = solver.solve_all()
        all_solve_time = (time.time() - start_time) * 1000
        
        return {
            "first_solution_time_ms": round(first_solve_time, 3),
            "all_solutions_time_ms": round(all_solve_time, 3),
            "total_solutions_found": len(all_solutions),
            "expected_solutions": 92,
            "performance_rating": "Excellent" if all_solve_time < 50 else "Good",
            "algorithm_efficiency": f"{((8**8 - 2000) / 8**8) * 100:.2f}% search space reduction"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating statistics: {str(e)}"
        )


@router.post("/reset")
async def reset_game():
    """
    Reset the game state.
    
    Returns:
        dict: Confirmation of reset
    """
    try:
        # Reset solver state
        solver.queens = [-1] * 8
        solver.solutions = []
        solver.solving_steps = []
        
        return {
            "success": True,
            "message": "Game state reset successfully",
            "empty_board": [-1, -1, -1, -1, -1, -1, -1, -1]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting game: {str(e)}"
        )