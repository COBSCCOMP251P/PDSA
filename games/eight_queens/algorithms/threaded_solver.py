import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple


class ThreadedEightQueensSolver:
    


    """
    Solves 8 Queens using multiple threads.
    
    How it works:
    - Splits the work: each thread starts with queen in different column
    - 8 starting positions = 8 threads can work at same time
    - All threads search their part and combine results at end
    """
    def __init__(self, max_workers=None):
        
        self.board_size = 8
        self.max_workers = max_workers
        self.solutions = []
        self.solutions_lock = threading.Lock() 
        





        """
        Find all 92 solutions using threads.
        
        Steps:
        1. Create 8 threads (one for each starting column)
        2. Each thread finds solutions starting from its column
        3. Combine all results when done
        """
    def solve_all(self):
        self.solutions = []
        
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            
            futures = []
            for first_col in range(self.board_size):
                future = executor.submit(self._solve_from_position, first_col)
                futures.append(future)
            
           
            for future in as_completed(futures):
                thread_solutions = future.result()
                with self.solutions_lock:
                    self.solutions.extend(thread_solutions)
        
        return self.solutions
    



        """
        Find just the first solution (whichever thread finds it first).
        Returns None if no solution found.
        """
    def solve_first(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for first_col in range(self.board_size):
                future = executor.submit(self._solve_first_from_position, first_col)
                futures.append(future)
            
            
            for future in as_completed(futures):
                solution = future.result()
                if solution is not None:
                    for f in futures:
                        f.cancel()
                    return solution
        
        return None



        """
        Thread work: find all solutions starting with queen at column first_col.
        Each thread runs this independently.
        """
    def _solve_from_position(self, first_col: int) -> List[List[int]]:
        solutions = []
        queens = [-1] * self.board_size
        queens[0] = first_col 
        
        self._backtrack_all_solutions(1, queens, solutions)
        
        return solutions





    """Thread work: find first solution from this starting column."""    
    def _solve_first_from_position(self, first_col: int) -> List[int]:
    
        queens = [-1] * self.board_size
        queens[0] = first_col
        
        if self._backtrack_first_solution(1, queens):
            return queens[:]
        return None
    



        """
        Backtracking to find all solutions.
        Same logic as sequential, but runs in separate thread.
        """   
    def _backtrack_all_solutions(self, row: int, queens: List[int], solutions: List[List[int]]):
        
        if row == self.board_size:
            
            solutions.append(queens[:])
            return
        
        
        for col in range(self.board_size):
            if self._is_safe(row, col, queens):
                queens[row] = col
                self._backtrack_all_solutions(row + 1, queens, solutions)
                queens[row] = -1  
    






        """Backtracking to find first solution only."""
    def _backtrack_first_solution(self, row: int, queens: List[int]) -> bool:
        if row == self.board_size:
            return True
        
        for col in range(self.board_size):
            if self._is_safe(row, col, queens):
                queens[row] = col
                if self._backtrack_first_solution(row + 1, queens):
                    return True
                queens[row] = -1
        
        return False






        """
        Check if position is safe (no conflicts).
        Same logic as sequential solver.
        """     
    def _is_safe(self, row: int, col: int, queens: List[int]) -> bool:
        for prev_row in range(row):
            prev_col = queens[prev_row]
            
            if prev_col == -1:
                continue
            
            
            if prev_col == col:
                return False
            
            
            row_diff = row - prev_row
            col_diff = abs(col - prev_col)
            
            if row_diff == col_diff:
                return False
        
        return True




        """Return how many solutions found."""    
    def get_solution_count(self) -> int:
        return len(self.solutions)




        """Check if a solution is valid."""    
    def validate_solution(self, queens: List[int]) -> bool:
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




# Performance comparison helper (optional - for testing)
def compare_performance():
    """
    Compare sequential vs threaded performance.
    
    This is useful for:
    - Assignment demonstrations
    - Performance analysis
    - Understanding threading benefits
    """
    import time
    
    # Import sequential solver
    from sequential_solver import EightQueensSolver
    
    # Test Sequential
    print("Testing Sequential Solver...")
    sequential_solver = EightQueensSolver()
    start = time.perf_counter()
    sequential_solutions = sequential_solver.solve_all()
    sequential_time = time.perf_counter() - start
    print(f"Sequential: Found {len(sequential_solutions)} solutions in {sequential_time:.4f} seconds")
    
    # Test Threaded
    print("\nTesting Threaded Solver...")
    threaded_solver = ThreadedEightQueensSolver()
    start = time.perf_counter()
    threaded_solutions = threaded_solver.solve_all()
    threaded_time = time.perf_counter() - start
    print(f"Threaded: Found {len(threaded_solutions)} solutions in {threaded_time:.4f} seconds")
    
    # Calculate speedup
    speedup = sequential_time / threaded_time if threaded_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x faster")
    print(f"Performance Improvement: {((speedup - 1) * 100):.1f}%")


if __name__ == "__main__":
    # Quick test
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
