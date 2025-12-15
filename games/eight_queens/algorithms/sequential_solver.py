# Eight Queens Solver - Sequential Algorithm
# Uses backtracking to find all 92 solutions

class EightQueensSolver:
    
    def __init__(self):
        # initialize board size and arrays
        self.board_size = 8
        self.queens = [-1] * self.board_size
        self.solutions = []
        self.solving_steps = []
    
    def solve_all(self):
        # find all 92 solutions
        self.solutions = []
        self.queens = [-1] * self.board_size
        self._backtrack_all_solutions(0)
        return self.solutions
    
    def solve_first(self):
        # find only the first solution
        self.queens = [-1] * self.board_size
        if self._backtrack_first_solution(0):
            return self.queens[:]
        return None
    
    def solve_step_by_step(self):
        # solve and record each step for visualization
        self.solving_steps = []
        self.queens = [-1] * self.board_size
        
        if self._backtrack_with_steps(0):
            return self.queens[:], self.solving_steps
        return None, self.solving_steps
    
    def _backtrack_all_solutions(self, row):
        # backtracking to find all solutions
        
        # if all 8 queens placed, save solution
        if row == self.board_size:
            self.solutions.append(self.queens[:])
            return
        
        # try each column in current row
        for col in range(self.board_size):
            if self._is_safe_placement(row, col):
                self.queens[row] = col
                self._backtrack_all_solutions(row + 1)
                self.queens[row] = -1
    
    def _backtrack_first_solution(self, row):
        # find first solution and stop
        if row == self.board_size:
            return True
        
        for col in range(self.board_size):
            if self._is_safe_placement(row, col):
                self.queens[row] = col
                if self._backtrack_first_solution(row + 1):
                    return True
                self.queens[row] = -1
        
        return False
    
    def _backtrack_with_steps(self, row):
        # backtracking with step recording for visualization
        
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
            # record trying this position
            self.solving_steps.append({
                'row': row,
                'col': col,
                'queens': self.queens[:],
                'action': 'trying_position',
                'message': f'Trying position ({row}, {col})'
            })
            
            if self._is_safe_placement(row, col):
                self.queens[row] = col
                # record queen placed
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'queens': self.queens[:],
                    'action': 'placed_queen',
                    'message': f'Placed queen at ({row}, {col}) - safe position'
                })
                
                if self._backtrack_with_steps(row + 1):
                    return True
                
                # backtrack
                self.queens[row] = -1
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'queens': self.queens[:],
                    'action': 'backtrack',
                    'message': f'Backtracking from ({row}, {col}) - no solution in this path'
                })
            else:
                # record conflict
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'queens': self.queens[:],
                    'action': 'conflict_detected',
                    'message': f'Position ({row}, {col}) conflicts with existing queen'
                })
        
        return False
    
    def _is_safe_placement(self, row, col):
        # check if queen can be placed safely at this position
        
        for prev_row in range(row):
            prev_col = self.queens[prev_row]
            
            if prev_col == -1:
                continue
            
            # check same column
            if prev_col == col:
                return False
            
            # check diagonal
            if abs(prev_row - row) == abs(prev_col - col):
                return False
        
        return True
    
    def get_board_display(self, solution=None):
        # convert queens array to 8x8 board display
        queens_to_use = solution if solution else self.queens
        board = [['.' for _ in range(self.board_size)] for _ in range(self.board_size)]
        
        for row in range(self.board_size):
            col = queens_to_use[row]
            if col != -1:
                board[row][col] = 'Q'
        
        return board
    
    def get_attacked_squares(self, solution=None):
        # get all squares attacked by current queens
        queens_to_use = solution if solution else self.queens
        attacked = set()
        
        for row in range(self.board_size):
            col = queens_to_use[row]
            if col == -1:
                continue
            
            # mark all attacked squares
            for i in range(self.board_size):
                attacked.add((row, i))
                attacked.add((i, col))
                
                # diagonal attacks
                diag_row, diag_col = row + (i - row), col + (i - row)
                if 0 <= diag_row < self.board_size and 0 <= diag_col < self.board_size:
                    attacked.add((diag_row, diag_col))
                
                diag_row, diag_col = row + (i - row), col - (i - row)
                if 0 <= diag_row < self.board_size and 0 <= diag_col < self.board_size:
                    attacked.add((diag_row, diag_col))
        
        return attacked
    
    def is_complete_solution(self, solution=None):
        # check if solution is valid and complete
        queens_to_use = solution if solution else self.queens
        
        # check all queens placed
        if any(pos == -1 for pos in queens_to_use):
            return False
        
        # check no conflicts
        for row in range(self.board_size):
            for other_row in range(row + 1, self.board_size):
                col = queens_to_use[row]
                other_col = queens_to_use[other_row]
                
                if col == other_col:
                    return False
                if abs(row - other_row) == abs(col - other_col):
                    return False
        
        return True
    
    def get_solution_count(self):
        # return number of solutions found
        return len(self.solutions)
    
    def get_solution(self, index):
        # get solution by index
        if 0 <= index < len(self.solutions):
            return self.solutions[index]
        return None
