"""
Pathfinding Algorithms for Snake and Ladder
Implements BFS and DFS to find minimum number of dice throws
"""

from collections import deque
from typing import List, Tuple, Optional
import time
from .game_logic import SnakeLadderBoard


class PathfindingResult:
    """
    Result object containing algorithm execution details.
    """
    
    def __init__(self, min_moves: int, execution_time_ms: float, algorithm: str, path: Optional[List[int]] = None):
        self.min_moves = min_moves
        self.execution_time_ms = execution_time_ms
        self.algorithm = algorithm
        self.path = path or []
    
    def to_dict(self):
        """Convert result to dictionary."""
        return {
            "min_moves": self.min_moves,
            "execution_time_ms": round(self.execution_time_ms, 3),
            "algorithm": self.algorithm,
            "path": self.path
        }


def find_min_moves_bfs(board: SnakeLadderBoard) -> PathfindingResult:
    """
    Find minimum number of dice throws using Breadth-First Search (BFS).
    
    BFS is optimal for unweighted graphs and guarantees the shortest path.
    It explores all positions reachable in k moves before exploring positions
    reachable in k+1 moves.
    
    Args:
        board: SnakeLadderBoard instance
        
    Returns:
        PathfindingResult containing minimum moves and execution time
    """
    start_time = time.perf_counter()
    
    try:
        # Starting position is cell 1
        start = 1
        target = board.total_cells
        
        # If already at target
        if start == target:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            return PathfindingResult(0, execution_time, "bfs", [start])
        
        # Queue stores tuples of (current_position, number_of_moves, path)
        queue = deque([(start, 0, [start])])
        visited = {start}
        
        while queue:
            current, moves, path = queue.popleft()
            
            # Try all possible dice rolls (1-6)
            for dice in range(1, 7):
                next_pos = board.get_next_position(current, dice)
                
                # Check if we reached the target
                if next_pos == target:
                    end_time = time.perf_counter()
                    execution_time = (end_time - start_time) * 1000
                    final_path = path + [next_pos]
                    return PathfindingResult(moves + 1, execution_time, "bfs", final_path)
                
                # Add to queue if not visited
                if next_pos not in visited and next_pos != current:
                    visited.add(next_pos)
                    queue.append((next_pos, moves + 1, path + [next_pos]))
        
        # If no path found (shouldn't happen in valid Snake and Ladder)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        return PathfindingResult(-1, execution_time, "bfs", [])
    
    except Exception as e:
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        raise Exception(f"BFS algorithm error: {str(e)}")


def find_min_moves_dfs(board: SnakeLadderBoard) -> PathfindingResult:
    """
    Find minimum number of dice throws using Depth-First Search (DFS) with iterative deepening.
    
    Standard DFS doesn't guarantee shortest path, so we use Iterative Deepening DFS (IDDFS)
    which combines DFS's space efficiency with BFS's completeness and optimality.
    
    Args:
        board: SnakeLadderBoard instance
        
    Returns:
        PathfindingResult containing minimum moves and execution time
    """
    start_time = time.perf_counter()
    
    try:
        start = 1
        target = board.total_cells
        
        # If already at target
        if start == target:
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000
            return PathfindingResult(0, execution_time, "dfs", [start])
        
        # Iterative deepening: try depths 0, 1, 2, ...
        max_depth = board.total_cells  # Upper bound
        
        for depth_limit in range(max_depth):
            result = _dfs_limited(board, start, target, depth_limit, [start], set())
            
            if result is not None:
                moves, path = result
                end_time = time.perf_counter()
                execution_time = (end_time - start_time) * 1000
                return PathfindingResult(moves, execution_time, "dfs", path)
        
        # If no path found
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        return PathfindingResult(-1, execution_time, "dfs", [])
    
    except Exception as e:
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000
        raise Exception(f"DFS algorithm error: {str(e)}")


def _dfs_limited(board: SnakeLadderBoard, current: int, target: int, 
                 depth_limit: int, path: List[int], visited: set) -> Optional[Tuple[int, List[int]]]:
    """
    Helper function for depth-limited DFS.
    
    Args:
        board: SnakeLadderBoard instance
        current: Current position
        target: Target position
        depth_limit: Maximum depth to explore
        path: Current path
        visited: Set of visited positions at current depth
        
    Returns:
        Tuple of (moves, path) if target found, None otherwise
    """
    # Base case: reached target
    if current == target:
        return (0, path)
    
    # Base case: depth limit reached
    if depth_limit == 0:
        return None
    
    # Mark as visited for this path
    visited.add(current)
    
    # Try all possible dice rolls
    for dice in range(1, 7):
        next_pos = board.get_next_position(current, dice)
        
        # Skip if already visited in current path (avoid cycles)
        if next_pos in visited or next_pos == current:
            continue
        
        # Recursive call with reduced depth
        result = _dfs_limited(board, next_pos, target, depth_limit - 1, 
                             path + [next_pos], visited.copy())
        
        if result is not None:
            moves, found_path = result
            return (moves + 1, found_path)
    
    return None


def compare_algorithms(board: SnakeLadderBoard) -> Tuple[PathfindingResult, PathfindingResult]:
    """
    Run both BFS and DFS algorithms and compare results.
    
    Args:
        board: SnakeLadderBoard instance
        
    Returns:
        Tuple of (bfs_result, dfs_result)
    """
    bfs_result = find_min_moves_bfs(board)
    dfs_result = find_min_moves_dfs(board)
    
    return bfs_result, dfs_result


def validate_answer(player_answer: int, correct_answer: int) -> bool:
    """
    Validate if player's answer matches the correct answer.
    
    Args:
        player_answer: Player's submitted answer
        correct_answer: Correct minimum number of moves
        
    Returns:
        True if answer is correct, False otherwise
    """
    if not isinstance(player_answer, int):
        raise ValueError("Player answer must be an integer")
    
    if player_answer < 0:
        raise ValueError("Player answer must be non-negative")
    
    return player_answer == correct_answer
