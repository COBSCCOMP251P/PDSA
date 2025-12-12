# Tower of Hanoi - Validation & Exception Handling Quick Reference

## Input Validation Rules

### Player Name
- ✅ Required (cannot be empty or whitespace)
- ✅ Max 100 characters
- ❌ Empty string: `"Player name is required and cannot be empty"`

### Disk Count
- ✅ Range: 1-20
- ❌ Out of range: `"Disk count must be between 1 and 20"`

### Peg Count
- ✅ Valid: 3 or 4
- ❌ Invalid: `"Peg count must be either 3 or 4"`

### Moves
- ✅ Minimum: 1
- ❌ Invalid: `"Move count must be at least 1"`

### Time Taken
- ✅ Non-negative
- ❌ Negative: `"Time taken cannot be negative"`

### Move Format
- ✅ Format: `"X->Y"` (e.g., `"1->3"`)
- ✅ X, Y must be integers
- ✅ X, Y must be within peg range (1 to peg_count)
- ✅ X ≠ Y (source cannot equal destination)

---

## Optimal Moves Formulas

### 3-Peg Tower of Hanoi
```
Optimal Moves = 2^n - 1
```

**Examples:**
- 3 disks: 2³ - 1 = **7 moves**
- 5 disks: 2⁵ - 1 = **31 moves**
- 10 disks: 2¹⁰ - 1 = **1023 moves**

### 4-Peg Tower of Hanoi (Frame-Stewart)
```python
def calculate_4peg_optimal_moves(n):
    dp[1] = 1
    dp[2] = 3
    for i in range(3, n + 1):
        dp[i] = min(2*dp[k] + (2^(i-k) - 1) for k in range(1, i))
    return dp[n]
```

**Examples:**
- 3 disks: **5 moves**
- 5 disks: **13 moves**
- 10 disks: **49 moves** (vs 1023 for 3-peg!)

---

## API Endpoints Quick Reference

### POST /api/leaderboard
**Save game result with validation**

```json
{
    "player_name": "Alice",
    "disk_count": 5,
    "peg_count": 3,
    "moves": 31,
    "time_taken": 45.2
}
```

**Response:**
```json
{
    "status": "success",
    "is_optimal": true,
    "optimal_moves": 31,
    "efficiency": 100.0
}
```

### POST /api/validate
**Validate move sequence**

```json
{
    "n_disks": 3,
    "peg_count": 3,
    "move_sequence": ["1->3", "1->2", "3->2", "1->3", "2->1", "2->3", "1->3"],
    "declared_moves": 7
}
```

### POST /api/benchmark
**Compare algorithm performance**

```json
{
    "n_disks": 5,
    "peg_count": 4
}
```

**Response:**
```json
{
    "success": true,
    "results": [
        {"algorithm": "Frame-Stewart 4-Peg", "moves": 13, "runtime_ms": 0.02},
        {"algorithm": "Dynamic Programming 4-Peg", "moves": 13, "runtime_ms": 0.02}
    ]
}
```

---

## Error Handling

### HTTP Status Codes
- **400**: Validation error (client mistake)
- **500**: Server error (unexpected issue)

### Exception Pattern
```python
try:
    # Validation
    if invalid:
        raise HTTPException(status_code=400, detail="Error message")
    
    # Business logic
    # Database operations
    
except HTTPException as he:
    raise  # Re-raise validation errors
    
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing

### Run Tests
```bash
# All validation tests
pytest tests/test_validation.py -v

# Specific test class
pytest tests/test_validation.py::TestOptimalMoveCalculation -v

# All algorithm tests
pytest tests/test_algorithms.py -v
```

### Test Coverage
- ✅ Input validation (21 tests)
- ✅ Algorithm correctness (22 tests)
- ✅ Optimal move calculation (3 tests)

---

## Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| Player name required | Empty or whitespace name | Provide non-empty name |
| Disk count out of range | n < 1 or n > 20 | Use 1-20 disks |
| Invalid peg count | Not 3 or 4 | Use 3 or 4 pegs |
| Invalid move format | Wrong format | Use "X->Y" format |
| Move count mismatch | Declared ≠ actual | Match declared to sequence length |

---

## Efficiency Calculation

```
Efficiency = (Optimal Moves / Player Moves) × 100%
```

**Ratings:**
- **100%**: Optimal solution! 🎯
- **80-99%**: Excellent 🌟
- **60-79%**: Good ✓
- **<60%**: Room for improvement 📈

---

## Database Fields Saved

```python
{
    "session_id": int,
    "player_id": int,
    "disk_count": int,          # 1-20
    "peg_count": int,           # 3 or 4
    "algorithm": str,           # "3-Peg Classic" or "4-Peg Frame-Stewart"
    "moves": int,               # Player's moves
    "optimal_moves": int,       # Calculated optimal
    "is_optimal": bool,         # moves == optimal_moves
    "time_taken": float,        # Seconds
    "is_correct": bool,         # Always true for completed games
    "efficiency": float,        # Percentage 0-100
    "created_at": datetime
}
```

---

## Key Functions

### Calculate 4-Peg Optimal
```python
from main import calculate_4peg_optimal_moves

optimal = calculate_4peg_optimal_moves(10)
print(optimal)  # 49
```

### Calculate 3-Peg Optimal
```python
optimal = (2 ** n) - 1
```

---

## Quick Checklist for New Features

- [ ] Add input validation with descriptive errors
- [ ] Use try-except with HTTPException
- [ ] Calculate optimal moves correctly (3-peg or 4-peg)
- [ ] Log successes (✓) and errors (❌)
- [ ] Verify database operations succeeded
- [ ] Write tests for new validation rules
- [ ] Update documentation

---

## Support

For detailed information, see:
- **Full Documentation**: `VALIDATION_DOCUMENTATION.md`
- **Algorithm Tests**: `tests/test_algorithms.py`
- **Validation Tests**: `tests/test_validation.py`
- **API Tests**: `tests/test_api.py`
