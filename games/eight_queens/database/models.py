"""
Database models and data classes for Eight Queens Game
Provides Pydantic models for type safety and validation

Author: PDSA Course Project
Date: November 24, 2025
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AlgorithmType(str, Enum):
    """Enumeration for algorithm types"""
    SEQUENTIAL = "sequential"
    THREADED = "threaded"

class SolutionStatus(str, Enum):
    """Enumeration for solution submission status"""
    NEW_DISCOVERY = "NEW_DISCOVERY"
    ALREADY_DISCOVERED = "ALREADY_DISCOVERED" 
    INVALID_SOLUTION = "INVALID_SOLUTION"
    ERROR = "ERROR"

class PlayerRegistrationStatus(str, Enum):
    """Enumeration for player registration status"""
    SUCCESS = "SUCCESS"
    PLAYER_EXISTS = "PLAYER_EXISTS"
    ERROR = "ERROR"

# ==============================================
# REQUEST MODELS
# ==============================================

class PlayerRegistration(BaseModel):
    """Model for player registration request"""
    name: str = Field(..., min_length=1, max_length=100, description="Player name")
    email: Optional[str] = Field(None, max_length=255, description="Player email (optional)")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Player name cannot be empty')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v

class SolutionSubmission(BaseModel):
    """Model for solution submission request"""
    player_id: int = Field(..., gt=0, description="Player ID")
    solution: List[int] = Field(..., min_items=8, max_items=8, description="8-Queens solution array")
    algorithm_type: AlgorithmType = Field(..., description="Algorithm used")
    execution_time_ms: float = Field(..., ge=0, description="Algorithm execution time in milliseconds")
    
    @validator('solution')
    def validate_solution(cls, v):
        if len(v) != 8:
            raise ValueError('Solution must have exactly 8 queens')
        if not all(0 <= pos <= 7 for pos in v):
            raise ValueError('All queen positions must be between 0 and 7')
        if len(set(v)) != 8:
            raise ValueError('All queens must be in different columns')
        return v

class GameSessionStart(BaseModel):
    """Model for starting a game session"""
    player_id: int = Field(..., gt=0, description="Player ID")
    algorithm_type: AlgorithmType = Field(..., description="Algorithm to use")

class GameSessionEnd(BaseModel):
    """Model for ending a game session"""
    session_id: int = Field(..., gt=0, description="Game session ID")
    execution_time_ms: float = Field(..., ge=0, description="Total execution time")
    solutions_found: int = Field(0, ge=0, description="Number of solutions found")
    solutions_attempted: int = Field(0, ge=0, description="Number of solutions attempted")
    duplicate_attempts: int = Field(0, ge=0, description="Number of duplicate solution attempts")
    thread_count: Optional[int] = Field(None, gt=0, description="Number of threads used (for threaded algorithm)")

# ==============================================
# RESPONSE MODELS
# ==============================================

class PlayerInfo(BaseModel):
    """Model for player information response"""
    id: int
    name: str
    email: Optional[str]
    created_at: datetime
    last_played: datetime
    total_games_played: int
    total_solutions_found: int

class PlayerStatistics(BaseModel):
    """Model for comprehensive player statistics"""
    id: int
    name: str
    total_games_played: int
    total_solutions_found: int
    unique_solutions_discovered: int
    avg_execution_time_ms: Optional[float]
    best_time_ms: Optional[float]
    worst_time_ms: Optional[float]
    created_at: datetime
    last_played: datetime

class SolutionInfo(BaseModel):
    """Model for solution information"""
    solution_number: int
    solution_array: List[int]
    solution_string: str
    is_fundamental: bool
    discovery_status: str
    discovered_by_player: Optional[str]
    discovered_at: Optional[datetime]
    algorithm_type: Optional[AlgorithmType]
    execution_time_ms: Optional[float]

class AlgorithmPerformance(BaseModel):
    """Model for algorithm performance comparison"""
    algorithm_type: AlgorithmType
    total_sessions: int
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    stddev_execution_time: Optional[float]
    avg_solutions_per_session: float
    avg_parallel_efficiency: Optional[float]

class GameSession(BaseModel):
    """Model for game session information"""
    id: int
    player_id: int
    session_start: datetime
    session_end: Optional[datetime]
    algorithm_type: AlgorithmType
    execution_time_ms: float
    total_solutions_found: int
    solutions_attempted: int
    duplicate_attempts: int
    thread_count: Optional[int]
    game_completed: bool

# ==============================================
# API RESPONSE MODELS
# ==============================================

class ApiResponse(BaseModel):
    """Base model for API responses"""
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PlayerRegistrationResponse(ApiResponse):
    """Response model for player registration"""
    player_id: Optional[int] = None
    registration_status: PlayerRegistrationStatus

class SolutionSubmissionResponse(ApiResponse):
    """Response model for solution submission"""
    submission_status: SolutionStatus
    solution_id: Optional[int] = None
    discovered_by: Optional[str] = None
    is_new_discovery: bool = False
    remaining_solutions: Optional[int] = None

class GameSessionResponse(ApiResponse):
    """Response model for game session operations"""
    session_id: Optional[int] = None
    session_data: Optional[GameSession] = None

class PerformanceAnalysisResponse(ApiResponse):
    """Response model for performance analysis"""
    sequential_performance: Optional[AlgorithmPerformance] = None
    threaded_performance: Optional[AlgorithmPerformance] = None
    comparison_data: Optional[Dict[str, Any]] = None

class DatabaseStatsResponse(ApiResponse):
    """Response model for database statistics"""
    total_players: int
    total_sessions: int
    discovered_solutions: int
    total_solutions: int
    discovery_percentage: float

# ==============================================
# CHART DATA MODELS
# ==============================================

class ChartDataPoint(BaseModel):
    """Model for individual chart data point"""
    timestamp: datetime
    value: float
    algorithm_type: AlgorithmType
    additional_info: Optional[Dict[str, Any]] = None

class PerformanceChartData(BaseModel):
    """Model for performance chart data"""
    sequential_times: List[float]
    threaded_times: List[float]
    labels: List[str]
    sequential_avg: float
    threaded_avg: float
    speedup_ratio: Optional[float] = None

class DiscoveryProgressData(BaseModel):
    """Model for solution discovery progress"""
    total_solutions: int = 92
    discovered_solutions: int
    remaining_solutions: int
    discovery_percentage: float
    recent_discoveries: List[SolutionInfo]

# ==============================================
# VALIDATION UTILITIES
# ==============================================

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_solution_array(solution: List[int]) -> bool:
    """
    Validate if solution array represents a valid 8-Queens solution
    
    Args:
        solution: List of 8 integers representing queen positions
        
    Returns:
        True if valid, False otherwise
    """
    if len(solution) != 8:
        return False
    
    if not all(0 <= pos <= 7 for pos in solution):
        return False
    
    # Check for conflicts
    for i in range(8):
        for j in range(i + 1, 8):
            # Same column
            if solution[i] == solution[j]:
                return False
            
            # Same diagonal
            if abs(solution[i] - solution[j]) == abs(i - j):
                return False
    
    return True

def solution_to_string(solution: List[int]) -> str:
    """Convert solution array to string format"""
    return ''.join(map(str, solution))

def string_to_solution(solution_string: str) -> List[int]:
    """Convert string format to solution array"""
    try:
        return [int(char) for char in solution_string]
    except (ValueError, TypeError):
        raise ValidationError("Invalid solution string format")

# ==============================================
# DATABASE MAPPING UTILITIES
# ==============================================

def map_database_row_to_model(row: Dict[str, Any], model_class):
    """
    Map database row dictionary to Pydantic model
    Handles datetime conversion and null values
    """
    try:
        # Handle datetime fields
        for key, value in row.items():
            if isinstance(value, datetime):
                row[key] = value
            elif value is None:
                continue
        
        return model_class(**row)
    except Exception as e:
        raise ValidationError(f"Failed to map database row to {model_class.__name__}: {e}")

def model_to_database_dict(model: BaseModel) -> Dict[str, Any]:
    """
    Convert Pydantic model to dictionary suitable for database operations
    """
    data = model.dict()
    
    # Convert enums to string values
    for key, value in data.items():
        if isinstance(value, Enum):
            data[key] = value.value
    
    return data