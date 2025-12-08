from typing import List, Tuple, Optional, Set
from .sequential_solver import EightQueensSolver


class EightQueensValidator:
    """
    Provides validation and hint functionality for the Eight Queens game.
    
    This class contains utility functions that help with:
    - Validating user moves
    - Checking partial solutions
    - Providing hints for next moves
    - Analyzing board states
    """
    
    def __init__(self):
        self.board_size = 8
        self.solver = EightQueensSolver()
    
    def is_valid_move(self, current_queens: List[int], row: int, col: int) -> bool:
        """
        Check if placing a queen at (row, col) is valid given current board state.
        
        Args:
            current_queens (List[int]): Current queen positions (-1 for empty)
            row (int): Target row (0-7)
            col (int): Target column (0-7)
            
        Returns:
            bool: True if move is valid, False if conflicts exist
            
        This function is used when:
        - User clicks on a square to place a queen
        - Providing real-time feedback in the UI
        - Validating user input before accepting the move
        """
        # Check if row already has a queen
        if current_queens[row] != -1:
            return False
        
        # Check for conflicts with existing queens
        for existing_row in range(self.board_size):
            existing_col = current_queens[existing_row]
            
            # Skip empty rows
            if existing_col == -1:
                continue
            
            # Column conflict
            if existing_col == col:
                return False
            
            # Diagonal conflict
            if abs(existing_row - row) == abs(existing_col - col):
                return False
        
        return True
    
    def get_safe_moves(self, current_queens: List[int]) -> List[Tuple[int, int]]:
        """
        Get all safe moves (positions) for the current board state.
        
        Args:
            current_queens (List[int]): Current queen positions
            
        Returns:
            List[Tuple[int, int]]: List of (row, col) tuples for safe moves
            
        Use cases:
        - Highlighting safe squares in green
        - Providing multiple move options to user
        - Checking if puzzle is still solvable
        """
        safe_moves = []
        
        for row in range(self.board_size):
            # Skip rows that already have queens
            if current_queens[row] != -1:
                continue
                
            for col in range(self.board_size):
                if self.is_valid_move(current_queens, row, col):
                    safe_moves.append((row, col))
        
        return safe_moves
    
    def get_next_hint(self, current_queens: List[int]) -> Optional[Tuple[int, int]]:
        """
        Provide a hint for the next best move.
        
        Args:
            current_queens (List[int]): Current board state
            
        Returns:
            Optional[Tuple[int, int]]: Next move suggestion or None if no solution
            
        Algorithm:
        1. Find the first empty row
        2. Use solver to find a valid continuation
        3. Return the next move from that solution
        """
        # Find first empty row
        next_row = -1
        for row in range(self.board_size):
            if current_queens[row] == -1:
                next_row = row
                break
        
        if next_row == -1:
            # Board is full
            return None
        
        # Try to extend current partial solution
        temp_queens = current_queens[:]
        self.solver.queens = temp_queens
        
        # Find a valid move for the next row
        for col in range(self.board_size):
            if self.is_valid_move(current_queens, next_row, col):
                # Test if this move leads to a solution
                temp_queens[next_row] = col
                if self._can_complete_solution(temp_queens, next_row + 1):
                    return (next_row, col)
                temp_queens[next_row] = -1
        
        return None  # No valid continuation found
    
    def _can_complete_solution(self, queens: List[int], start_row: int) -> bool:
        """
        Check if partial solution can be completed.
        
        Args:
            queens (List[int]): Partial solution
            start_row (int): Row to start checking from
            
        Returns:
            bool: True if solution can be completed
        """
        if start_row == self.board_size:
            return True  # All queens placed
        
        for col in range(self.board_size):
            if self._is_safe_for_partial(queens, start_row, col):
                queens[start_row] = col
                if self._can_complete_solution(queens, start_row + 1):
                    return True
                queens[start_row] = -1
        
        return False
    
    def _is_safe_for_partial(self, queens: List[int], row: int, col: int) -> bool:
        """Helper function for checking safety in partial solutions."""
        for prev_row in range(row):
            prev_col = queens[prev_row]
            if prev_col == -1:
                continue
            
            if prev_col == col or abs(prev_row - row) == abs(prev_col - col):
                return False
        return True
    
    def validate_complete_solution(self, queens: List[int]) -> dict:
        """
        Validate a complete solution and provide detailed feedback.
        
        Args:
            queens (List[int]): Complete solution to validate
            
        Returns:
            dict: Validation result with details
            
        Return format:
        {
            'is_valid': bool,
            'is_complete': bool,
            'conflicts': List[dict],  # Details of any conflicts found
            'message': str
        }
        """
        result = {
            'is_valid': True,
            'is_complete': True,
            'conflicts': [],
            'message': 'Valid solution!'
        }
        
        # Check completeness
        empty_rows = [i for i, pos in enumerate(queens) if pos == -1]
        if empty_rows:
            result['is_complete'] = False
            result['is_valid'] = False
            result['message'] = f'Incomplete solution. Missing queens in rows: {empty_rows}'
            return result
        
        # Check for conflicts
        conflicts = []
        for row1 in range(self.board_size):
            col1 = queens[row1]
            for row2 in range(row1 + 1, self.board_size):
                col2 = queens[row2]
                
                # Column conflict
                if col1 == col2:
                    conflicts.append({
                        'type': 'column',
                        'position1': (row1, col1),
                        'position2': (row2, col2),
                        'description': f'Queens at ({row1},{col1}) and ({row2},{col2}) are in same column'
                    })
                
                # Diagonal conflict
                elif abs(row1 - row2) == abs(col1 - col2):
                    conflicts.append({
                        'type': 'diagonal',
                        'position1': (row1, col1),
                        'position2': (row2, col2),
                        'description': f'Queens at ({row1},{col1}) and ({row2},{col2}) are on same diagonal'
                    })
        
        if conflicts:
            result['is_valid'] = False
            result['conflicts'] = conflicts
            result['message'] = f'Solution has {len(conflicts)} conflict(s)'
        
        return result
    
    def get_progress_info(self, current_queens: List[int]) -> dict:
        """
        Get information about current progress.
        
        Args:
            current_queens (List[int]): Current board state
            
        Returns:
            dict: Progress information
            
        Information includes:
        - Number of queens placed
        - Number of safe moves remaining
        - Whether solution is still possible
        - Completion percentage
        """
        placed_queens = sum(1 for pos in current_queens if pos != -1)
        safe_moves = self.get_safe_moves(current_queens)
        
        # Check if current state can lead to a solution
        can_solve = len(safe_moves) > 0 or placed_queens == 8
        if placed_queens < 8 and len(safe_moves) == 0:
            can_solve = False
        
        progress = {
            'queens_placed': placed_queens,
            'queens_remaining': 8 - placed_queens,
            'safe_moves_count': len(safe_moves),
            'safe_moves': safe_moves,
            'can_solve': can_solve,
            'progress_percentage': (placed_queens / 8) * 100,
            'status': self._get_game_status(placed_queens, safe_moves, can_solve)
        }
        
        return progress
    
    def _get_game_status(self, placed: int, safe_moves: List, can_solve: bool) -> str:
        """Get human-readable game status."""
        if placed == 8:
            return 'completed'
        elif not can_solve:
            return 'stuck'
        elif len(safe_moves) == 1:
            return 'forced_move'
        elif len(safe_moves) <= 3:
            return 'limited_options'
        else:
            return 'in_progress'
    
    def get_difficulty_rating(self, current_queens: List[int]) -> str:
        """
        Rate the difficulty of current position.
        
        Args:
            current_queens (List[int]): Current board state
            
        Returns:
            str: Difficulty rating ('easy', 'medium', 'hard', 'expert')
        """
        safe_moves = len(self.get_safe_moves(current_queens))
        placed = sum(1 for pos in current_queens if pos != -1)
        
        if placed <= 2:
            return 'easy'
        elif safe_moves >= 5:
            return 'easy'
        elif safe_moves >= 3:
            return 'medium'
        elif safe_moves >= 1:
            return 'hard'
        else:
            return 'expert'


class ConflictAnalyzer:
    """
    Analyzes conflicts and provides educational insights.
    
    This class helps users understand WHY certain moves are invalid
    and provides educational value for learning the game.
    """
    
    @staticmethod
    def analyze_position_conflicts(queens: List[int], row: int, col: int) -> dict:
        """
        Analyze why a specific position conflicts with existing queens.
        
        Args:
            queens (List[int]): Current board state
            row (int): Target row
            col (int): Target column
            
        Returns:
            dict: Detailed conflict analysis
        """
        conflicts = {
            'has_conflict': False,
            'conflict_types': [],
            'conflicting_queens': [],
            'explanation': ''
        }
        
        for existing_row in range(len(queens)):
            existing_col = queens[existing_row]
            
            if existing_col == -1:
                continue
            
            # Column conflict
            if existing_col == col:
                conflicts['has_conflict'] = True
                conflicts['conflict_types'].append('column')
                conflicts['conflicting_queens'].append((existing_row, existing_col))
                conflicts['explanation'] = f'Queen at ({existing_row},{existing_col}) attacks same column'
            
            # Diagonal conflict
            elif abs(existing_row - row) == abs(existing_col - col):
                conflicts['has_conflict'] = True
                conflicts['conflict_types'].append('diagonal')
                conflicts['conflicting_queens'].append((existing_row, existing_col))
                
                # Determine diagonal direction
                if (existing_row - row) * (existing_col - col) > 0:
                    direction = 'main diagonal (\\'
                else:
                    direction = 'anti-diagonal (/'
                
                conflicts['explanation'] = f'Queen at ({existing_row},{existing_col}) attacks {direction})'
        
        return conflicts
    
    @staticmethod
    def get_attack_pattern(row: int, col: int, board_size: int = 8) -> Set[Tuple[int, int]]:
        """
        Get all squares attacked by a queen at given position.
        
        Args:
            row (int): Queen row position
            col (int): Queen column position
            board_size (int): Size of the board (default 8)
            
        Returns:
            Set[Tuple[int, int]]: Set of attacked square coordinates
        """
        attacked = set()
        
        for i in range(board_size):
            # Row attacks
            attacked.add((row, i))
            # Column attacks
            attacked.add((i, col))
            
            # Main diagonal attacks (top-left to bottom-right)
            main_diag_row = row + (i - col)
            main_diag_col = i
            if 0 <= main_diag_row < board_size:
                attacked.add((main_diag_row, main_diag_col))
            
            # Anti-diagonal attacks (top-right to bottom-left)
            anti_diag_row = row - (i - col)
            anti_diag_col = i
            if 0 <= anti_diag_row < board_size:
                attacked.add((anti_diag_row, anti_diag_col))
        
        # Remove the queen's own position
        attacked.discard((row, col))
        
        return attacked