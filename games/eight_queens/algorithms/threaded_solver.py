# Eight Queens Solver - Threaded Algorithm
# Uses multiple threads to find all 92 solutions faster

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple


class ThreadedEightQueensSolver:
    
    def __init__(self, max_workers=None):
        # initialize solver with thread pool
        self.board_size = 8
        self.max_workers = max_workers
        self.solutions = []
        self.solutions_lock = threading.Lock()
    
    def solve_all(self):
        # find all solutions using multiple threads
        self.solutions = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # create thread for each starting column
            futures = []
            for first_col in range(self.board_size):
                future = executor.submit(self._solve_from_position, first_col)
                futures.append(future)
            
            # collect results from all threads
            for future in as_completed(futures):
                thread_solutions = future.result()
                with self.solutions_lock:
                    self.solutions.extend(thread_solutions)
        
        return self.solutions
    
    def solve_first(self):
        # find first solution using threads
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for first_col in range(self.board_size):
                future = executor.submit(self._solve_first_from_position, first_col)
                futures.append(future)
            
            # return first solution found
            for future in as_completed(futures):
                solution = future.result()
                if solution is not None:
                    for f in futures:
                        f.cancel()
                    return solution
        
        return None
    
    def _solve_from_position(self, first_col: int) -> List[List[int]]:
        # thread work - find solutions starting from first_col
        solutions = []
        queens = [-1] * self.board_size
        queens[0] = first_col
        
        self._backtrack_all_solutions(1, queens, solutions)
        
        return solutions
    
    def _solve_first_from_position(self, first_col: int) -> List[int]:
        # thread work - find first solution from this column
        queens = [-1] * self.board_size
        queens[0] = first_col
        
        if self._backtrack_first_solution(1, queens):
            return queens[:]
        return None
    
    def _backtrack_all_solutions(self, row: int, queens: List[int], solutions: List[List[int]]):
        # backtracking to find all solutions
        
        if row == self.board_size:
            solutions.append(queens[:])
            return
        
        for col in range(self.board_size):
            if self._is_safe(row, col, queens):
                queens[row] = col
                self._backtrack_all_solutions(row + 1, queens, solutions)
                queens[row] = -1
    
    def _backtrack_first_solution(self, row: int, queens: List[int]) -> bool:
        # backtracking to find first solution only
        if row == self.board_size:
            return True
        
        for col in range(self.board_size):
            if self._is_safe(row, col, queens):
                queens[row] = col
                if self._backtrack_first_solution(row + 1, queens):
                    return True
                queens[row] = -1
        
        return False
    
    def _is_safe(self, row: int, col: int, queens: List[int]) -> bool:
        # check if queen can be placed safely
        for prev_row in range(row):
            prev_col = queens[prev_row]
            
            if prev_col == -1:
                continue
            
            # check same column
            if prev_col == col:
                return False
            
            # check diagonal
            row_diff = row - prev_row
            col_diff = abs(col - prev_col)
            
            if row_diff == col_diff:
                return False
        
        return True
    
    def get_solution_count(self) -> int:
        # return number of solutions found
        return len(self.solutions)
    
    def validate_solution(self, queens: List[int]) -> bool:
        # check if a solution is valid
        if len(queens) != self.board_size:
            return False
        
        for row in range(self.board_size):
            col = queens[row]
            
            if col < 0 or col >= self.board_size:
                return False
            
            for prev_row in range(row):
                if not self._is_safe(row, col, queens[:row+1]):
                    return False
        
        return True


# performance comparison function
def compare_performance():
    import time
    from sequential_solver import EightQueensSolver
    
    # test sequential
    print("Testing Sequential Solver...")
    sequential_solver = EightQueensSolver()
    start = time.perf_counter()
    sequential_solutions = sequential_solver.solve_all()
    sequential_time = time.perf_counter() - start
    print(f"Sequential: Found {len(sequential_solutions)} solutions in {sequential_time:.4f} seconds")
    
    # test threaded
    print("\nTesting Threaded Solver...")
    threaded_solver = ThreadedEightQueensSolver()
    start = time.perf_counter()
    threaded_solutions = threaded_solver.solve_all()
    threaded_time = time.perf_counter() - start
    print(f"Threaded: Found {len(threaded_solutions)} solutions in {threaded_time:.4f} seconds")
    
    # calculate speedup
    speedup = sequential_time / threaded_time if threaded_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x faster")
    print(f"Performance Improvement: {((speedup - 1) * 100):.1f}%")


if __name__ == "__main__":
    # quick test
    print("Eight Queens - Threaded Solver")
    print("=" * 50)
    
    solver = ThreadedEightQueensSolver()
    
    print("\nFinding all solutions using multi-threading...")
    import time
    start = time.perf_counter()
    solutions = solver.solve_all()
    elapsed = time.perf_counter() - start
    
    print(f"Found {len(solutions)} solutions in {elapsed:.4f} seconds")
    print(f"First solution: {solutions[0]}")
    
    print("\n" + "=" * 50)
    print("Run compare_performance() for detailed comparison with sequential solver")
