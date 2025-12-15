# Eight Queens Game

## About
This is my implementation of the Eight Queens puzzle for the PDSA coursework. The goal is to place 8 queens on a chessboard so that no two queens can attack each other.

## How It Works
- Queens can attack in rows, columns, and diagonals
- There are exactly 92 valid solutions
- I used backtracking algorithm to find all solutions

## Algorithms Used

### Sequential Solver
- Uses backtracking to find all 92 solutions one by one
- Tries each column in each row
- If a position is safe, places queen and moves to next row
- If stuck, backtracks and tries next column

### Threaded Solver
- Same backtracking logic but runs in parallel
- Each thread starts with queen in different column (0-7)
- Finds solutions faster by using multiple CPU cores
- Results are combined at the end

## Files

```
eight_queens/
├── algorithms/
│   ├── sequential_solver.py   - single threaded solver
│   ├── threaded_solver.py     - multi threaded solver
│   └── validation.py          - validates queen positions
├── api/
│   └── routes.py              - API endpoints
├── frontend/
│   └── index.html             - game interface
├── database/
│   ├── schema.sql             - database tables
│   ├── connection.py          - database connection
│   └── models.py              - database operations
└── tests/
    └── test_solver.py         - unit tests
```

## How to Run

1. Start the server from project root:
```
python -m uvicorn shared.backend.main:app --reload
```

2. Open in browser:
```
http://127.0.0.1:8000/games/eight_queens/frontend/index.html
```

## Database Tables
- `players` - stores player information
- `EightQueensSolutions` - all 92 solutions with MD5 hash
- `game_sessions` - tracks each game played
- `EightQueensResults` - player submissions
- `algorithm_comparisons` - sequential vs threaded timing

## Features
- Register new player or login existing
- Three difficulty levels (Easy, Medium, Hard)
- Click on board to place queens
- Shows conflicts when queens attack each other
- Validates solution against database
- Records time taken for sequential and threaded algorithms
- Tracks if solution was already found by another player

## Algorithm Complexity
- Time: O(N!) - tries all possible arrangements
- Space: O(N) - stores queen positions array

## Testing
Run tests from project root:
```
python -m pytest games/eight_queens/tests/
```