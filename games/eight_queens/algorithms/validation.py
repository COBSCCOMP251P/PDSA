# Eight Queens Validation Module
# Provides move validation and hint functionality

from typing import List, Tuple, Optional, Set
from .sequential_solver import EightQueensSolver


class EightQueensValidator:
    
    def __init__(self):
        self.board_size = 8
        self.solver = EightQueensSolver()
    
    def is_valid_move(self, current_queens: List[int], row: int, col: int) -> bool:
        # check if placing queen at row,col is valid
        
        # check if row already has a queen
        if current_queens[row] != -1:
            return False
        
        # check for conflicts with existing queens
        for existing_row in range(self.board_size):
            existing_col = current_queens[existing_row]
            
            if existing_col == -1:
                continue
            
            # column conflict
            if existing_col == col:
                return False
            
            # diagonal conflict
            if abs(existing_row - row) == abs(existing_col - col):
                return False
        
        return True
    
    def get_safe_moves(self, current_queens: List[int]) -> List[Tuple[int, int]]:
        # get all safe positions for current board
        safe_moves = []
        
        for row in range(self.board_size):
            if current_queens[row] != -1:
                continue
                
            for col in range(self.board_size):
                if self.is_valid_move(current_queens, row, col):
                    safe_moves.append((row, col))
        
        return safe_moves
    
    def get_next_hint(self, current_queens: List[int]) -> Optional[Tuple[int, int]]:
        # provide hint for next best move
        
        # find first empty row
        next_row = -1
        for row in range(self.board_size):
            if current_queens[row] == -1:
                next_row = row
                break
        
        if next_row == -1:
            return None
        
        # try to extend current solution
        temp_queens = current_queens[:]
        self.solver.queens = temp_queens
        
        # find valid move for next row
        for col in range(self.board_size):
            if self.is_valid_move(current_queens, next_row, col):
                temp_queens[next_row] = col
                if self._can_complete_solution(temp_queens, next_row + 1):
                    return (next_row, col)
                temp_queens[next_row] = -1
        
        return None
    
    def _can_complete_solution(self, queens: List[int], start_row: int) -> bool:
        # check if partial solution can be completed
        if start_row == self.board_size:
            return True
        
        for col in range(self.board_size):
            if self._is_safe_for_partial(queens, start_row, col):
                queens[start_row] = col
                if self._can_complete_solution(queens, start_row + 1):
                    return True
                queens[start_row] = -1
        
        return False
    
    def _is_safe_for_partial(self, queens: List[int], row: int, col: int) -> bool:
        # helper to check safety in partial solutions
        for prev_row in range(row):
            prev_col = queens[prev_row]
            if prev_col == -1:
                continue
            
            if prev_col == col or abs(prev_row - row) == abs(prev_col - col):
                return False
        return True
    
    def validate_complete_solution(self, queens: List[int]) -> dict:
        # validate complete solution and return detailed feedback
        result = {
            'is_valid': True,
            'is_complete': True,
            'conflicts': [],
            'message': 'Valid solution!'
        }
        
        # check completeness
        empty_rows = [i for i, pos in enumerate(queens) if pos == -1]
        if empty_rows:
            result['is_complete'] = False
            result['is_valid'] = False
            result['message'] = f'Incomplete solution. Missing queens in rows: {empty_rows}'
            return result
        
        # check for conflicts
        conflicts = []
        for row1 in range(self.board_size):
            col1 = queens[row1]
            for row2 in range(row1 + 1, self.board_size):
                col2 = queens[row2]
                
                # column conflict
                if col1 == col2:
                    conflicts.append({
                        'type': 'column',
                        'position1': (row1, col1),
                        'position2': (row2, col2),
                        'description': f'Queens at ({row1},{col1}) and ({row2},{col2}) are in same column'
                    })
                
                # diagonal conflict
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
        # get current game progress information
        placed_queens = sum(1 for pos in current_queens if pos != -1)
        safe_moves = self.get_safe_moves(current_queens)
        
        # check if solution is still possible
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
        # get game status string
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
        # rate difficulty of current position
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
    # analyzes conflicts and provides feedback
    
    @staticmethod
    def analyze_position_conflicts(queens: List[int], row: int, col: int) -> dict:
        # analyze why a position conflicts with existing queens
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
            
            # column conflict
            if existing_col == col:
                conflicts['has_conflict'] = True
                conflicts['conflict_types'].append('column')
                conflicts['conflicting_queens'].append((existing_row, existing_col))
                conflicts['explanation'] = f'Queen at ({existing_row},{existing_col}) attacks same column'
            
            # diagonal conflict
            elif abs(existing_row - row) == abs(existing_col - col):
                conflicts['has_conflict'] = True
                conflicts['conflict_types'].append('diagonal')
                conflicts['conflicting_queens'].append((existing_row, existing_col))
                
                # determine diagonal direction
                if (existing_row - row) * (existing_col - col) > 0:
                    direction = 'main diagonal (\\'
                else:
                    direction = 'anti-diagonal (/'
                
                conflicts['explanation'] = f'Queen at ({existing_row},{existing_col}) attacks {direction})'
        
        return conflicts
    
    @staticmethod
    def get_attack_pattern(row: int, col: int, board_size: int = 8) -> Set[Tuple[int, int]]:
        # get all squares attacked by queen at given position
        attacked = set()
        
        for i in range(board_size):
            # row and column attacks
            attacked.add((row, i))
            attacked.add((i, col))
            
            # main diagonal attacks
            main_diag_row = row + (i - col)
            main_diag_col = i
            if 0 <= main_diag_row < board_size:
                attacked.add((main_diag_row, main_diag_col))
            
            # anti-diagonal attacks
            anti_diag_row = row - (i - col)
            anti_diag_col = i
            if 0 <= anti_diag_row < board_size:
                attacked.add((anti_diag_row, anti_diag_col))
        
        # remove queen's own position
        attacked.discard((row, col))
        
        return attacked