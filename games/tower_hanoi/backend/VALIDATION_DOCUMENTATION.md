# Tower of Hanoi - Validation & Exception Handling Documentation

## Overview
This document describes the comprehensive validation and exception handling features implemented in the Tower of Hanoi game backend to ensure data integrity, proper error handling, and accurate optimal move calculations for both 3-peg and 4-peg solutions.

---

## 1. Input Validation

### 1.1 Leaderboard Endpoint (`/api/leaderboard`)

#### Player Name Validation
- **Required**: Player name cannot be empty or whitespace-only
- **Length**: Maximum 100 characters
- **Error Messages**:
  - Empty name: `"Player name is required and cannot be empty"`
  - Too long: `"Player name must be 100 characters or less"`

#### Disk Count Validation
- **Range**: 1 to 20 disks
- **Type**: Must be an integer
- **Error Message**: `"Disk count must be between 1 and 20"`

#### Peg Count Validation
- **Valid Values**: 3 or 4 pegs only
- **Error Message**: `"Peg count must be either 3 or 4"`

#### Moves Validation
- **Minimum**: At least 1 move
- **Error Message**: `"Move count must be at least 1"`

#### Time Validation
- **Constraint**: Cannot be negative
- **Error Message**: `"Time taken cannot be negative"`

### 1.2 Validate Endpoint (`/api/validate`)

#### Basic Validation
- Disk count: 1-20
- Peg count: 3 or 4
- Move sequence: Cannot be empty
- Declared moves: Must match actual move sequence length

#### Move Format Validation
Each move is validated for:
1. **Format**: Must be in format `"X->Y"` where X and Y are integers
2. **Peg Range**: Source and destination pegs must be within valid range (1 to peg_count)
3. **Different Pegs**: Source and destination cannot be the same
4. **Numeric Values**: Both source and destination must be parseable as integers

**Error Examples**:
```
"Invalid move format at position 0: '1-3'. Expected format 'X->Y'"
"Invalid source peg 5 in move 2. Must be between 1 and 3"
"Invalid move at position 1: source and destination cannot be the same (2)"
```

#### Move Sequence Validation
The validator checks:
- All moves follow valid Tower of Hanoi rules
- No illegal moves (larger disk on smaller disk)
- Solution correctly moves all disks to destination
- Move count matches declared moves

### 1.3 Benchmark Endpoint (`/api/benchmark`)

#### Input Validation
- **n_disks**: 1-20, must be integer
- **peg_count**: 3 or 4, must be integer

#### Type Checking
```python
if not isinstance(n_disks, int):
    raise HTTPException(status_code=400, detail="n_disks must be an integer")
```

---

## 2. Optimal Move Calculations

### 2.1 3-Peg Optimal Moves

For 3-peg Tower of Hanoi, the optimal number of moves is given by the classic formula:

**Formula**: `Optimal Moves = 2^n - 1`

Where `n` is the number of disks.

**Examples**:
| Disks | Calculation | Optimal Moves |
|-------|-------------|---------------|
| 1     | 2^1 - 1     | 1             |
| 2     | 2^2 - 1     | 3             |
| 3     | 2^3 - 1     | 7             |
| 5     | 2^5 - 1     | 31            |
| 10    | 2^10 - 1    | 1023          |

**Implementation**:
```python
if game_result.peg_count == 3:
    optimal_moves = (2 ** game_result.disk_count) - 1
    algorithm_name = "3-Peg Classic"
```

### 2.2 4-Peg Optimal Moves (Frame-Stewart Algorithm)

For 4-peg Tower of Hanoi, we use the **Frame-Stewart algorithm** with dynamic programming to find the optimal solution.

#### Algorithm Description

The Frame-Stewart algorithm works by:
1. Splitting the stack of n disks into two parts: k disks and (n-k) disks
2. Moving k disks to an auxiliary peg using all 4 pegs
3. Moving remaining (n-k) disks to destination using 3 pegs (classic method)
4. Moving k disks from auxiliary to destination using all 4 pegs
5. Finding the optimal split point k that minimizes total moves

#### Mathematical Formula

```
T(n, 4) = min{2 * T(k, 4) + 2^(n-k) - 1} for all k from 1 to n-1
```

Where:
- `T(n, 4)` = minimum moves for n disks with 4 pegs
- `T(k, 4)` = minimum moves for k disks with 4 pegs
- `2^(n-k) - 1` = moves for (n-k) disks using 3-peg method

#### Implementation

```python
def calculate_4peg_optimal_moves(n: int) -> int:
    """
    Calculate optimal number of moves for 4-peg Tower of Hanoi 
    using Frame-Stewart algorithm.
    
    Time Complexity: O(n²)
    Space Complexity: O(n)
    """
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if n == 2:
        return 3
    
    # DP array to store minimum moves for each disk count
    dp = [0] * (n + 1)
    dp[1] = 1  # Base case: 1 disk requires 1 move
    dp[2] = 3  # Base case: 2 disks requires 3 moves
    
    # For each disk count from 3 to n
    for i in range(3, n + 1):
        dp[i] = float('inf')
        
        # Try splitting at different positions k (1 to i-1)
        for k in range(1, i):
            moves = 2 * dp[k] + (2 ** (i - k) - 1)
            dp[i] = min(dp[i], moves)
    
    return dp[n]
```

#### Optimal Moves Table

| Disks | 3-Peg Optimal | 4-Peg Optimal | Improvement |
|-------|---------------|---------------|-------------|
| 1     | 1             | 1             | 0%          |
| 2     | 3             | 3             | 0%          |
| 3     | 7             | 5             | 28.6%       |
| 5     | 31            | 13            | 58.1%       |
| 10    | 1023          | 49            | 95.2%       |
| 15    | 32767         | 129           | 99.6%       |
| 20    | 1048575       | 289           | 99.97%      |

**Key Insight**: The 4-peg solution becomes dramatically more efficient as the number of disks increases, reducing moves by over 99% for large problems.

### 2.3 Efficiency Calculation

The system calculates efficiency as a percentage:

```python
efficiency = min(optimal_moves / game_result.moves * 100, 100.0)
```

This gives players feedback on how close they were to the optimal solution:
- **100%**: Player achieved optimal solution
- **80-99%**: Very good solution
- **60-79%**: Good solution  
- **<60%**: Room for improvement

---

## 3. Exception Handling

### 3.1 Exception Hierarchy

The system uses a three-tier exception handling approach:

```python
try:
    # Validation checks (raise HTTPException with 400)
    # Business logic
    # Database operations
except HTTPException as he:
    # Re-raise validation errors
    raise
except Exception as e:
    # Catch unexpected errors, log, and return 500
    print(f"❌ Error: {e}")
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=f"Error message: {str(e)}")
```

### 3.2 Error Types and Status Codes

#### 400 Bad Request
Used for **validation errors** - client sent invalid data:
- Empty player name
- Invalid disk count or peg count
- Malformed move sequences
- Type mismatches

#### 500 Internal Server Error
Used for **unexpected server errors**:
- Database connection failures
- Algorithm execution errors
- Unexpected runtime exceptions

### 3.3 Database Exception Handling

#### Player Creation
```python
# Check if player exists
player_result = await db.execute_query(player_check_query, (game_result.player_name,))

if not player_result or len(player_result) == 0:
    # Create new player
    await db.execute_query(create_player_query, (game_result.player_name,))
    
    # Verify creation succeeded
    player_result = await db.execute_query(player_check_query, (game_result.player_name,))
    if not player_result or len(player_result) == 0:
        raise HTTPException(
            status_code=500, 
            detail="Failed to create player record"
        )
```

#### Session Management
```python
# Create game session
await db.execute_query(create_session_query, (player_id, current_time))

# Verify session creation
session_result = await db.execute_query(session_query, (player_id,))

if not session_result or len(session_result) == 0:
    raise HTTPException(
        status_code=500, 
        detail="Failed to create game session"
    )
```

### 3.4 Logging and Debugging

The system provides comprehensive logging for troubleshooting:

```python
# Success logging with ✓
print(f"✓ Validation passed - Saving game result: {game_result}")
print(f"✓ Optimal moves for {disk_count} disks, {peg_count} pegs: {optimal_moves}")
print(f"✓ Found existing player with ID: {player_id}")

# Completion logging with ✅
print(f"✅ Game result saved successfully!")

# Error logging with ❌
print(f"❌ HTTP Exception: {he.detail}")
print(f"❌ Error saving game result: {e}")
```

---

## 4. API Response Structure

### 4.1 Success Response (Leaderboard)

```json
{
    "status": "success",
    "message": "Game result saved successfully",
    "player_id": 123,
    "session_id": 456,
    "is_correct": true,
    "is_optimal": false,
    "optimal_moves": 31,
    "efficiency": 83.3
}
```

### 4.2 Success Response (Benchmark)

```json
{
    "success": true,
    "n_disks": 5,
    "peg_count": 4,
    "results": [
        {
            "algorithm": "Frame-Stewart 4-Peg",
            "runtime_ms": 0.0234,
            "moves": 13,
            "optimal": true
        },
        {
            "algorithm": "Dynamic Programming 4-Peg",
            "runtime_ms": 0.0189,
            "moves": 13,
            "optimal": true
        }
    ]
}
```

### 4.3 Error Response

```json
{
    "detail": "Player name is required and cannot be empty"
}
```

---

## 5. Testing

### 5.1 Test Coverage

The system includes comprehensive tests in `tests/test_validation.py`:

#### Validation Tests
- `TestLeaderboardValidation` (9 tests)
  - Empty/whitespace player names
  - Player name length limits
  - Disk count boundaries
  - Invalid peg counts
  - Negative values

- `TestValidateEndpointValidation` (7 tests)
  - Move format validation
  - Invalid peg numbers
  - Same source/destination
  - Declared moves mismatch

- `TestBenchmarkValidation` (5 tests)
  - Type checking
  - Range validation
  - Valid executions

#### Algorithm Tests
- `TestOptimalMoveCalculation` (3 tests)
  - 3-peg optimal calculation
  - 4-peg optimal calculation
  - Comparison verification

### 5.2 Running Tests

```bash
# Run all validation tests
python3 -m pytest tests/test_validation.py -v

# Run specific test class
python3 -m pytest tests/test_validation.py::TestOptimalMoveCalculation -v

# Run with coverage
python3 -m pytest tests/test_validation.py --cov=main
```

---

## 6. Database Schema Alignment

The validation ensures data saved to database matches schema:

```sql
CREATE TABLE HanoiResults (
    session_id INT,
    player_id INT,
    disk_count INT,           -- Validated: 1-20
    peg_count INT,            -- Validated: 3 or 4
    algorithm VARCHAR(50),    -- "3-Peg Classic" or "4-Peg Frame-Stewart"
    moves INT,                -- Player's actual moves
    optimal_moves INT,        -- Calculated optimal moves
    is_optimal BOOLEAN,       -- TRUE if moves == optimal_moves
    time_taken FLOAT,         -- Cannot be negative
    is_correct BOOLEAN,       -- TRUE for completed games
    efficiency FLOAT,         -- Percentage (0-100)
    created_at DATETIME
);
```

---

## 7. Usage Examples

### Example 1: Valid 3-Peg Submission

```python
POST /api/leaderboard
{
    "player_name": "Alice",
    "disk_count": 5,
    "peg_count": 3,
    "moves": 31,
    "time_taken": 45.2
}
```

**Response**:
```json
{
    "status": "success",
    "is_optimal": true,
    "optimal_moves": 31,
    "efficiency": 100.0
}
```

### Example 2: Valid 4-Peg Submission

```python
POST /api/leaderboard
{
    "player_name": "Bob",
    "disk_count": 10,
    "peg_count": 4,
    "moves": 55,
    "time_taken": 120.5
}
```

**Response**:
```json
{
    "status": "success",
    "is_optimal": false,
    "optimal_moves": 49,
    "efficiency": 89.1
}
```

### Example 3: Invalid Input

```python
POST /api/leaderboard
{
    "player_name": "",
    "disk_count": 25,
    "peg_count": 5,
    "moves": -5,
    "time_taken": -10
}
```

**Response** (400 Bad Request):
```json
{
    "detail": "Player name is required and cannot be empty"
}
```

---

## 8. Key Features Summary

### ✅ Comprehensive Input Validation
- All user inputs validated before processing
- Clear, descriptive error messages
- Type checking and range validation

### ✅ Accurate Optimal Move Calculation
- 3-peg: Classic formula `2^n - 1`
- 4-peg: Frame-Stewart algorithm with DP
- Proven correctness with test cases

### ✅ Robust Exception Handling
- Three-tier error handling
- Proper HTTP status codes
- Detailed logging for debugging

### ✅ Database Integrity
- Transaction safety with commit/rollback
- Verification of create operations
- Proper error propagation

### ✅ Efficiency Feedback
- Real-time efficiency calculation
- Comparison with optimal solution
- Separate tracking for 3-peg and 4-peg

---

## 9. Conclusion

The Tower of Hanoi backend now features:

1. **Complete validation** of all user inputs
2. **Accurate optimal move calculations** for both 3-peg and 4-peg solutions
3. **Comprehensive exception handling** with proper error messages
4. **Database integrity** with transaction management
5. **Detailed logging** for monitoring and debugging
6. **Extensive test coverage** to ensure reliability

This ensures that player names, game results, and validations are properly handled and saved to the database with full data integrity and error resilience.
