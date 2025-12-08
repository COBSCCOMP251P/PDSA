class EightQueensSolver:
    """
    Solves 8 Queens using backtracking.
    queens[row] = column tells us where each queen is placed.
    Example: queens[0] = 3 means queen in row 0 is at column 3.
    """
    
    def __init__(self):
        """Set up empty board."""
        self.board_size = 8
        self.queens = [-1] * self.board_size  # -1 means no queen in that row
        self.solutions = []
        self.solving_steps = []  # for showing how algorithm works
    
    def solve_all(self):
        """Find all 92 solutions. Returns list of all valid queen placements."""
        self.solutions = []
        self.queens = [-1] * self.board_size
        self._backtrack_all_solutions(0)
        return self.solutions
    
    def solve_first(self):
        """Find just the first solution (faster). Good for hints or quick checks."""
        self.queens = [-1] * self.board_size
        if self._backtrack_first_solution(0):
            return self.queens[:]
        return None
    
    def solve_step_by_step(self):
        """Solve and record each step for visualization."""
        self.solving_steps = []
        self.queens = [-1] * self.board_size
        
        if self._backtrack_with_steps(0):
            return self.queens[:], self.solving_steps
        return None, self.solving_steps
    
    def _backtrack_all_solutions(self, row):
        """
        Main backtracking logic to find ALL solutions.
        
        How it works:
        1. If we placed queens in all 8 rows -> save solution
        2. Try each column in current row
        3. If safe, place queen and go to next row
        4. After trying, remove queen (backtrack) and try next column
        """
        # Base case: all 8 queens placed successfully
        if row == self.board_size:
            self.solutions.append(self.queens[:])
            return
        
        # Try each column in this row
        for col in range(self.board_size):
            if self._is_safe_placement(row, col):
                self.queens[row] = col  # place queen
                self._backtrack_all_solutions(row + 1)  # try next row
                self.queens[row] = -1  # remove queen (backtrack)
    
    def _backtrack_first_solution(self, row):
        """Find first solution only - stops when found."""
        if row == self.board_size:
            return True  # found a solution!
        
        for col in range(self.board_size):
            if self._is_safe_placement(row, col):
                self.queens[row] = col
                if self._backtrack_first_solution(row + 1):
                    return True  # solution found, stop searching
                self.queens[row] = -1  # backtrack
        
        return False  # no solution in this path
    
    def _backtrack_with_steps(self, row):
        """Same as backtracking but records each step for visualization."""
        # Record: starting to work on this row
        self.solving_steps.append({
            'row': row,
            'queens': self.queens[:],
            'action': 'trying_row',
            'message': f'Trying to place queen in row {row}'
        })
        
        if row == self.board_size:
            self.solving_steps.append({
                'row': row,
                'queens': self.queens[:],
                'action': 'solution_found',
                'message': 'Solution found! All queens placed safely.'
            })
            return True
        
        for col in range(self.board_size):
            # Record: trying this position
            self.solving_steps.append({
                'row': row,
                'col': col,
                'queens': self.queens[:],
                'action': 'trying_position',
                'message': f'Trying position ({row}, {col})'
            })
            
            if self._is_safe_placement(row, col):
                self.queens[row] = col
                # Record: placed queen here
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'queens': self.queens[:],
                    'action': 'placed_queen',
                    'message': f'Placed queen at ({row}, {col}) - safe position'
                })
                
                if self._backtrack_with_steps(row + 1):
                    return True
                
                # Backtrack
                self.queens[row] = -1
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'queens': self.queens[:],
                    'action': 'backtrack',
                    'message': f'Backtracking from ({row}, {col}) - no solution in this path'
                })
            else:
                # Record: conflict found
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'queens': self.queens[:],
                    'action': 'conflict_detected',
                    'message': f'Position ({row}, {col}) conflicts with existing queen'
                })
        
        return False
    
    def _is_safe_placement(self, row, col):
        """
        Check if we can place queen at (row, col) safely.
        
        We check against all queens in previous rows:
        - Same column? -> conflict
        - Same diagonal? -> conflict (when row diff == col diff)
        """
        for prev_row in range(row):
            prev_col = self.queens[prev_row]
            
            if prev_col == -1:
                continue  # no queen in this row yet
            
            # Same column = conflict
            if prev_col == col:
                return False
            
            # Same diagonal = conflict
            if abs(prev_row - row) == abs(prev_col - col):
                return False
        
        return True  # no conflicts found
    
    def get_board_display(self, solution=None):
        """Convert queens array to 8x8 board. Returns grid with 'Q' for queens, '.' for empty."""
        queens_to_use = solution if solution else self.queens
        board = [['.' for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        for row in range(self.board_size):
            col = queens_to_use[row]
            if col != -1:
                board[row][col] = 'Q'
        
        return board
    
    def get_attacked_squares(self, solution=None):
        """Get all squares that current queens can attack."""
        queens_to_use = solution if solution else self.queens
        attacked = set()
        
        for row in range(self.board_size):
            col = queens_to_use[row]
            if col == -1:
                continue
            
            # Mark all squares this queen attacks
            for i in range(self.board_size):
                attacked.add((row, i))  # row attacks
                attacked.add((i, col))  # column attacks
                
                # diagonal attacks (both directions)
                diag_row, diag_col = row + (i - row), col + (i - row)
                if 0 <= diag_row < self.board_size and 0 <= diag_col < self.board_size:
                    attacked.add((diag_row, diag_col))
                
                diag_row, diag_col = row + (i - row), col - (i - row)
                if 0 <= diag_row < self.board_size and 0 <= diag_col < self.board_size:
                    attacked.add((diag_row, diag_col))
        
        return attacked
    
    def is_complete_solution(self, solution=None):
        """Check if board has valid complete solution. All 8 queens placed with no conflicts = True."""
        queens_to_use = solution if solution else self.queens
        
        # Check all queens are placed
        if any(pos == -1 for pos in queens_to_use):
            return False
        
        # Check no conflicts between any two queens
        for row in range(self.board_size):
            for other_row in range(row + 1, self.board_size):
                col = queens_to_use[row]
                other_col = queens_to_use[other_row]
                
                if col == other_col:  # same column
                    return False
                if abs(row - other_row) == abs(col - other_col):  # same diagonal
                    return False
        
        return True
    
    def get_solution_count(self):
        """Return how many solutions we found (should be 92)."""
        return len(self.solutions)
    
    def get_solution(self, index):
        """Get solution by index (0-91)."""
        if 0 <= index < len(self.solutions):
            return self.solutions[index]
        return None
