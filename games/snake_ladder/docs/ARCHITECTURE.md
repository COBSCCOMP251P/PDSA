# Snake and Ladder Game - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Frontend (HTML/CSS/JS)                   │   │
│  │  • Game board visualization                           │   │
│  │  • Player input forms                                 │   │
│  │  • Answer selection UI                                │   │
│  │  • Results display                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │ (JSON)
┌──────────────────────▼──────────────────────────────────────┐
│                   Backend Server (FastAPI)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  API Routes Layer                       │ │
│  │  /init    /submit    /stats    /leaderboard           │ │
│  └───────────────────────┬─────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼─────────────────────────────────┐ │
│  │              Business Logic Layer                       │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │ │
│  │  │ Game Logic   │  │  Pathfinding │  │  Validation  │ │ │
│  │  │              │  │              │  │              │ │ │
│  │  │ • Board Gen  │  │ • BFS Algo   │  │ • Input Val  │ │ │
│  │  │ • Rules      │  │ • DFS Algo   │  │ • Error Hdl  │ │ │
│  │  │ • State Mgmt │  │ • Comparison │  │ • Sanitize   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │ │
│  └───────────────────────┬─────────────────────────────────┘ │
│                          │                                   │
│  ┌───────────────────────▼─────────────────────────────────┐ │
│  │              Database Access Layer                      │ │
│  │  • Connection pooling                                   │ │
│  │  • Query execution                                      │ │
│  │  • Transaction management                               │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ MySQL Protocol
┌──────────────────────▼──────────────────────────────────────┐
│                      MySQL Database                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Players    │  │ GameSessions │  │   Results    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │     SnakeLadderAlgorithmPerformance              │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### Game Initialization Flow
```
Player Input
    ↓
[Validate Input]
    ↓
[Create/Get Player] → Database
    ↓
[Create Session] → Database
    ↓
[Generate Board]
    ↓
[Run BFS Algorithm] → [Calculate Min Moves]
    ↓
[Run DFS Algorithm] → [Calculate Min Moves]
    ↓
[Save Performance] → Database
    ↓
[Generate Choices]
    ↓
[Return to Frontend]
    ↓
Display Board & Choices
```

### Answer Submission Flow
```
Player Answer
    ↓
[Validate Answer]
    ↓
[Check Correctness]
    ↓
[Save Result] → Database
    ↓
[Complete Session] → Database
    ↓
[Get Player Stats] → Database
    ↓
[Return Results]
    ↓
Display Win/Lose
```

## Algorithm Flow

### BFS (Breadth-First Search)
```
Start: Cell 1
Goal: Cell N²

Initialize:
  queue = [(1, 0, [1])]  # (position, moves, path)
  visited = {1}

While queue not empty:
  current, moves, path = dequeue()
  
  For dice in 1..6:
    next = get_next_position(current, dice)
    
    If next == goal:
      Return moves + 1
    
    If next not visited:
      Add next to visited
      Enqueue (next, moves+1, path+[next])

Return -1 (no solution)
```

### DFS with Iterative Deepening
```
Start: Cell 1
Goal: Cell N²

For depth_limit in 0..max_depth:
  result = dfs_limited(1, goal, depth_limit)
  
  If result found:
    Return result

dfs_limited(current, goal, depth):
  If current == goal:
    Return 0
  
  If depth == 0:
    Return None
  
  For dice in 1..6:
    next = get_next_position(current, dice)
    
    If next not in visited:
      result = dfs_limited(next, goal, depth-1)
      
      If result found:
        Return result + 1
  
  Return None
```

## Component Interactions

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend Components                    │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Setup Form  →  Loading  →  Game Board  →  Result       │
│                                                           │
│  • Name input   • Spinner   • Grid view   • Feedback    │
│  • Size select  • Status    • Legends     • Stats       │
│  • Email input              • Choices     • Actions     │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                    API Endpoints                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  POST /init           → Initialize game session          │
│  POST /submit         → Submit player answer             │
│  GET  /stats/:name    → Get player statistics           │
│  GET  /leaderboard    → Get top players                 │
│  GET  /comparison     → Get algorithm metrics           │
│  GET  /health         → Server health check             │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                  Core Algorithms                          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  SnakeLadderBoard    → Board generation & rules          │
│  find_min_moves_bfs  → BFS pathfinding                   │
│  find_min_moves_dfs  → DFS pathfinding                   │
│  validate_answer     → Answer validation                 │
│  SnakeLadderDB       → Database operations               │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────────────────────────────────────────────┐
│                       Players                            │
├─────────────────────────────────────────────────────────┤
│ PK │ player_id      INT AUTO_INCREMENT                  │
│    │ player_name    VARCHAR(100)                        │
│    │ email          VARCHAR(150) UNIQUE                 │
│    │ created_at     TIMESTAMP                           │
└─────┬───────────────────────────────────────────────────┘
      │
      │ 1:N
      │
┌─────▼───────────────────────────────────────────────────┐
│                    GameSessions                          │
├─────────────────────────────────────────────────────────┤
│ PK │ session_id     INT AUTO_INCREMENT                  │
│ FK │ player_id      INT                                 │
│    │ game_type      ENUM('snake_ladder', ...)          │
│    │ started_at     TIMESTAMP                           │
│    │ completed_at   TIMESTAMP                           │
│    │ status         ENUM('active', 'completed', ...)   │
└─────┬───────────────────────────────────────────────────┘
      │
      │ 1:N
      ├─────────────────────────────┐
      │                             │
┌─────▼─────────────────┐  ┌───────▼─────────────────────┐
│  SnakeLadderResults   │  │ SnakeLadderAlgorithm        │
│                       │  │      Performance            │
├───────────────────────┤  ├─────────────────────────────┤
│ PK │ result_id       │  │ PK │ performance_id        │
│ FK │ session_id      │  │ FK │ session_id            │
│    │ player_name     │  │    │ board_size            │
│    │ board_size      │  │    │ algorithm_type        │
│    │ algorithm_type  │  │    │ execution_time_ms     │
│    │ player_answer   │  │    │ minimum_moves         │
│    │ correct_answer  │  │    │ board_config (JSON)   │
│    │ is_correct      │  │    │ recorded_at           │
│    │ execution_time  │  └─────────────────────────────┘
│    │ board_config    │
│    │ submitted_at    │
└───────────────────────┘
```

## Testing Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Test Framework                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Unit Tests                 Integration Tests            │
│  ├─ test_game_logic.py     ├─ test_integration.py       │
│  │  • Board generation     │  • Complete game flow       │
│  │  • Rule validation      │  • API integration          │
│  │  • Edge cases           │  • Database operations      │
│  │                         │  • Error handling           │
│  ├─ test_pathfinding.py    │                            │
│  │  • BFS algorithm        │                            │
│  │  • DFS algorithm        │                            │
│  │  • Performance          │                            │
│  │  • Correctness          │                            │
│  │                         │                            │
│  └─ run_tests.py           └─ Test Runner               │
│     • Test orchestration                                 │
│     • Report generation                                  │
│     • Coverage analysis                                  │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
Input Received
    ↓
[Validation Layer]
    │
    ├─ Valid → Continue Processing
    │
    └─ Invalid → [ValidationError]
                      ↓
                 [Error Handler]
                      ↓
                 Format Response
                      ↓
                 Return to Client
                      ↓
                 Display Error Message
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Production Setup                       │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Web Server (Nginx/Apache)                              │
│      ↓                                                    │
│  ASGI Server (Uvicorn)                                   │
│      ↓                                                    │
│  FastAPI Application                                     │
│      ↓                                                    │
│  Database Connection Pool                                │
│      ↓                                                    │
│  MySQL Database                                          │
│                                                           │
│  Static Files → CDN (optional)                           │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Performance Optimization

```
┌──────────────────────────────────────────────────────────┐
│              Performance Considerations                   │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  1. Algorithm Efficiency                                 │
│     • BFS: O(N² × 6) time, O(N²) space                  │
│     • DFS: O(N² × 6 × d) time, O(d) space               │
│                                                           │
│  2. Database Optimization                                │
│     • Indexed queries                                    │
│     • Connection pooling                                 │
│     • Prepared statements                                │
│                                                           │
│  3. Frontend Optimization                                │
│     • Cached static resources                            │
│     • Minimal DOM manipulation                           │
│     • Responsive design                                  │
│                                                           │
│  4. API Optimization                                     │
│     • Request validation                                 │
│     • Error caching                                      │
│     • Session management                                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Security Layers

```
┌──────────────────────────────────────────────────────────┐
│                    Security Measures                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Input Layer        → Validation & Sanitization          │
│  API Layer          → CORS, Rate Limiting                │
│  Business Logic     → Authorization Checks               │
│  Database Layer     → Parameterized Queries              │
│  Transport Layer    → HTTPS (Production)                 │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

This architecture ensures:
✅ Scalability
✅ Maintainability
✅ Testability
✅ Security
✅ Performance
