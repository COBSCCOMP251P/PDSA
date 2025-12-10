# Snake and Ladder Game Module

## Overview
The Snake and Ladder Game is an interactive problem-solving game that challenges players to find the minimum number of dice throws required to reach the end of a Snake and Ladder board. The game uses two different pathfinding algorithms (BFS and DFS) to compute the optimal solution.

## Features
- **Dynamic Board Generation**: Randomly generates Snake and Ladder boards of size N×N (6 ≤ N ≤ 12)
- **Dual Algorithm Approach**: Uses both BFS and DFS algorithms to find the minimum dice throws
- **Interactive UI**: HTML/CSS/JS frontend with visual board representation
- **Performance Tracking**: Records and compares algorithm execution times
- **Player Statistics**: Tracks player performance and maintains a leaderboard
- **Database Integration**: MySQL database for storing game results and statistics

## Technology Stack
- **Backend**: Python with FastAPI
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MySQL
- **Algorithms**: BFS (Breadth-First Search) and DFS (Depth-First Search)

## Game Rules
1. Board is N×N with cells numbered from 1 to N²
2. Start from cell 1, goal is to reach cell N²
3. Each move is a dice roll (1-6)
4. Landing on a ladder base → climb to its top
5. Landing on a snake head → slide to its tail
6. Number of ladders = N - 2
7. Number of snakes = N - 2
8. Snakes and ladders are randomly positioned each game

## Directory Structure
```
snake_ladder/
├── algorithms/
│   ├── __init__.py
│   ├── game_logic.py      # Board generation and game rules
│   ├── pathfinding.py     # BFS and DFS implementations
│   └── database.py        # Database operations
├── api/
│   ├── __init__.py
│   └── routes.py          # FastAPI endpoints
├── frontend/
│   ├── index.html         # Main game interface
│   ├── styles.css         # Styling
│   └── script.js          # Frontend logic
├── tests/
│   ├── test_game_logic.py      # Game logic tests
│   ├── test_pathfinding.py     # Algorithm tests
│   ├── test_integration.py     # Integration tests
│   └── run_tests.py            # Test runner
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Node.js (optional, for frontend development)

### Setup Steps

1. **Clone the repository**:
```bash
cd d:\PDSA\CW\git game\PDSA
```

2. **Create virtual environment** (recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure database**:
   - Create MySQL database: `pdsa_games`
   - Run schema: `shared/database/schema.sql`
   - Update database credentials in `.env` file

5. **Create .env file** (in project root):
```env
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=pdsa_games
API_HOST=localhost
API_PORT=8000
DEBUG=true
```

## Running the Application

### Start Backend Server
```bash
cd shared/backend
python main.py
```
The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Access Frontend
Open `games/snake_ladder/frontend/index.html` in a web browser, or serve it with:
```bash
# Using Python's built-in server
cd games/snake_ladder/frontend
python -m http.server 8080
```
Then navigate to: `http://localhost:8080`

## Running Tests

### Run All Tests
```bash
cd games/snake_ladder/tests
python run_tests.py
```

### Run Specific Test Suite
```bash
# Game logic tests only
python run_tests.py game_logic

# Pathfinding algorithm tests only
python run_tests.py pathfinding

# Integration tests only
python run_tests.py integration
```

### Run Individual Test Files
```bash
python test_game_logic.py
python test_pathfinding.py
python test_integration.py
```

## API Endpoints

### Initialize Game
```
POST /api/snake-ladder/init
Content-Type: application/json

{
  "player_name": "John Doe",
  "board_size": 8,
  "email": "john@example.com"  // optional
}

Response: {
  "session_id": "session_123",
  "board_config": {...},
  "answer_choices": [5, 7, 6],
  "message": "Game initialized successfully!"
}
```

### Submit Answer
```
POST /api/snake-ladder/submit
Content-Type: application/json

{
  "session_id": "session_123",
  "player_answer": 6
}

Response: {
  "is_correct": true,
  "correct_answer": 6,
  "player_answer": 6,
  "bfs_result": {...},
  "dfs_result": {...},
  "message": "Congratulations!",
  "player_stats": {...}
}
```

### Get Player Statistics
```
GET /api/snake-ladder/stats/{player_name}

Response: {
  "player_name": "John Doe",
  "stats": {
    "total_games": 10,
    "correct_answers": 7,
    "accuracy": 70.0,
    "avg_execution_time": 1.234
  }
}
```

### Get Leaderboard
```
GET /api/snake-ladder/leaderboard?limit=10

Response: {
  "leaderboard": [
    {
      "rank": 1,
      "player_name": "John Doe",
      "total_games": 10,
      "correct_answers": 9,
      "accuracy": 90.0
    },
    ...
  ]
}
```

### Get Algorithm Comparison
```
GET /api/snake-ladder/algorithm-comparison?board_size=8

Response: {
  "comparison": {
    "bfs": {
      "executions": 50,
      "avg_time": 1.234,
      "min_time": 0.5,
      "max_time": 3.0,
      "avg_moves": 6.2
    },
    "dfs": {
      "executions": 50,
      "avg_time": 2.345,
      ...
    }
  },
  "board_size": 8
}
```

## Algorithms

### BFS (Breadth-First Search)
- **Purpose**: Find shortest path (minimum dice throws)
- **Time Complexity**: O(N² × 6) where N is board size
- **Space Complexity**: O(N²)
- **Guarantees**: Optimal solution (shortest path)
- **Implementation**: Uses queue to explore moves level by level

### DFS (Depth-First Search) with Iterative Deepening
- **Purpose**: Find shortest path using depth-limited search
- **Time Complexity**: O(N² × 6 × d) where d is depth
- **Space Complexity**: O(d) - more memory efficient
- **Guarantees**: Optimal solution (with iterative deepening)
- **Implementation**: Recursive depth-limited search with increasing limits

## Database Schema

### SnakeLadderResults Table
Stores game results for each player submission:
- `result_id`: Primary key
- `session_id`: Game session reference
- `player_name`: Player's name
- `board_size`: Size of the board
- `algorithm_type`: 'bfs' or 'dfs'
- `player_answer`: Player's submitted answer
- `correct_answer`: Correct minimum moves
- `is_correct`: Whether answer was correct
- `execution_time_ms`: Algorithm execution time
- `board_config`: JSON of board configuration
- `submitted_at`: Timestamp

### SnakeLadderAlgorithmPerformance Table
Tracks algorithm performance metrics:
- `performance_id`: Primary key
- `session_id`: Game session reference
- `board_size`: Size of the board
- `algorithm_type`: 'bfs' or 'dfs'
- `execution_time_ms`: Execution time
- `minimum_moves`: Minimum moves found
- `board_config`: JSON of board configuration
- `recorded_at`: Timestamp

## Validation & Exception Handling

### Input Validation
- **Board Size**: Must be integer between 6 and 12
- **Player Name**: Non-empty, max 100 characters
- **Email**: Valid email format (optional)
- **Player Answer**: Non-negative integer

### Exception Handling
- **ValueError**: Invalid input parameters
- **HTTPException**: API errors with appropriate status codes
- **Database Errors**: Connection and query failures
- **Algorithm Errors**: Wrapped with context information

### Error Responses
All API errors return structured responses:
```json
{
  "detail": "Error description"
}
```

## Frontend Features

### Game Board Visualization
- Grid layout matching board size
- Color-coded cells:
  - 🎯 Green: Start (cell 1)
  - 🏁 Orange: End (cell N²)
  - 🪜 Blue: Ladder positions
  - 🐍 Yellow: Snake positions

### User Interface Components
1. **Setup Form**: Player info and board size selection
2. **Game Board**: Visual representation with legend
3. **Answer Selection**: Multiple choice (3 options)
4. **Result Display**: Win/lose feedback with statistics
5. **Leaderboard**: Top players ranking

### Interactive Elements
- Hover effects on board cells
- Animated transitions between sections
- Real-time validation feedback
- Responsive design for mobile devices

## Performance Benchmarks

### Average Execution Times (milliseconds)
| Board Size | BFS  | DFS  |
|------------|------|------|
| 6×6        | 0.5  | 1.2  |
| 8×8        | 1.2  | 2.8  |
| 10×10      | 3.5  | 7.2  |
| 12×12      | 8.0  | 15.5 |

*Note: Times vary based on board configuration*

## Testing Coverage

### Test Categories
1. **Unit Tests**: 50+ test cases
   - Board generation
   - Game rules
   - Algorithm correctness
   - Validation functions

2. **Integration Tests**: 20+ test cases
   - Complete game flow
   - Board persistence
   - Algorithm consistency
   - Error handling

3. **Performance Tests**
   - Algorithm speed benchmarks
   - Memory usage validation

## Troubleshooting

### Common Issues

**Database Connection Error**
```
Solution: Check MySQL service is running and credentials in .env are correct
```

**Import Errors**
```
Solution: Ensure all dependencies are installed: pip install -r requirements.txt
```

**API Not Starting**
```
Solution: Check if port 8000 is available or change API_PORT in .env
```

**Frontend Can't Connect to API**
```
Solution: Update API_BASE_URL in frontend/script.js to match your backend URL
```

## Contributing
This is a coursework project. For questions or improvements, contact the development team.

## License
See LICENSE file in project root.

## Authors
PDSA Coursework Team - Member 1 (Snake and Ladder Game)

## Acknowledgments
- FastAPI documentation and community
- Algorithm design patterns from PDSA course materials
- Game concept: Traditional Snake and Ladder board game
