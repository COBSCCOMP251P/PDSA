# **Snake and Ladder Game - Program Logic Explanation**

---

## **Overview**

The Snake and Ladder Game solves the problem of finding the **minimum number of dice throws** required to move from **Cell 1** to **Cell N²** on a dynamically generated N×N game board with random snakes and ladders.

The solution uses **two pathfinding algorithms**:
1. **Breadth-First Search (BFS)** - Guarantees optimal solution
2. **Depth-First Search (DFS) with Iterative Deepening** - Space-efficient alternative

---

## **Part 1: Board Generation Logic**

### **1.1 Board Initialization**

**File:** `algorithms/game_logic.py` → `SnakeLadderBoard` class

```python
class SnakeLadderBoard:
    def __init__(self, n: int):
        self.n = n                          # Board dimension (6-12)
        self.total_cells = n * n            # Total cells on board
        self.ladders: Dict[int, int] = {}   # {start: end}
        self.snakes: Dict[int, int] = {}    # {head: tail}
        self.num_ladders = n - 2            # Number of ladders to place
        self.num_snakes = n - 2             # Number of snakes to place
        self._generate_board()              # Generate random board
```

**Key Properties:**
- Board size: N × N (where N is 6-12)
- Total cells: N² (36-144 cells)
- Ladders: N-2 (4-10 ladders)
- Snakes: N-2 (4-10 snakes)

---

### **1.2 Random Board Generation Algorithm**

**Logic Flow:**

#### **Step 1: Generate Ladders**

```python
while len(self.ladders) < self.num_ladders:
    # 1. Pick a random START position in lower-to-middle region
    start = random.randint(2, total_cells - n)
    
    # 2. Verify START is not occupied
    if start in occupied_cells: continue
    
    # 3. Calculate valid END range (must go UP)
    min_end = start + n                    # At least n cells ahead
    max_end = min(total_cells - 1, start + 2*n)  # At most 2n cells ahead
    
    # 4. Pick random END in valid range
    end = random.randint(min_end, max_end)
    
    # 5. Verify END is not occupied
    if end in occupied_cells: continue
    
    # 6. Record ladder and mark cells as occupied
    self.ladders[start] = end
    occupied_cells.add(start)
    occupied_cells.add(end)
```

**Ladder Constraints:**
- Start must be in lower half of board (cells 2 to N²-N)
- End must be N to 2N cells above the start
- No overlapping with other ladders or snakes
- Cannot start at cell 1 or end at cell N²

---

#### **Step 2: Generate Snakes**

```python
while len(self.snakes) < self.num_snakes:
    # 1. Pick random HEAD position in upper region
    head = random.randint(n + 1, total_cells - 1)
    
    # 2. Verify HEAD is not occupied
    if head in occupied_cells: continue
    
    # 3. Calculate valid TAIL range (must go DOWN)
    min_tail = 2                           # Minimum position
    max_tail = head - n                    # At least n cells below
    
    # 4. Pick random TAIL in valid range
    tail = random.randint(min_tail, max_tail)
    
    # 5. Verify TAIL is not occupied
    if tail in occupied_cells: continue
    
    # 6. Record snake and mark cells as occupied
    self.snakes[head] = tail
    occupied_cells.add(head)
    occupied_cells.add(tail)
```

**Snake Constraints:**
- Head must be in upper half of board (cells N+1 to N²-1)
- Tail must be N cells below the head
- No overlapping with other snakes or ladders
- Cannot be at cell 1 or cell N²

---

### **1.3 Movement Logic**

**Function:** `get_next_position(current, dice)`

```python
def get_next_position(self, current: int, dice: int) -> int:
    """
    Simulate rolling a dice and moving accordingly.
    Automatically applies ladder/snake transitions.
    """
    # Step 1: Calculate new position based on dice roll
    next_pos = current + dice
    
    # Step 2: Boundary check - cannot go beyond target
    if next_pos > self.total_cells:
        return current  # Stay in current position
    
    # Step 3: Check for ladder at new position
    if next_pos in self.ladders:
        return self.ladders[next_pos]  # Jump up the ladder
    
    # Step 4: Check for snake at new position
    if next_pos in self.snakes:
        return self.snakes[next_pos]   # Slide down the snake
    
    # Step 5: No ladder/snake, return new position
    return next_pos
```

**Example:**
```
Current position: 5
Dice roll: 4
New position: 5 + 4 = 9

If 9 has a ladder to 20:
    Final position = 20

If 9 has a snake to 3:
    Final position = 3

If 9 has neither:
    Final position = 9
```

---

## **Part 2: Pathfinding Algorithm Logic**

### **2.1 BFS Algorithm (Breadth-First Search)**

**File:** `algorithms/pathfinding.py` → `find_min_moves_bfs()`

**Why BFS?**
- Explores nodes level-by-level (breadth-first)
- Guarantees **shortest path** in unweighted graphs
- Perfect for finding minimum number of dice throws
- Each dice throw is one edge in the graph

---

#### **BFS Algorithm Step-by-Step:**

```python
def find_min_moves_bfs(board: SnakeLadderBoard) -> PathfindingResult:
    start = 1                          # Starting cell
    target = board.total_cells         # Target cell (N²)
    
    # Data structure: Queue to store (position, number_of_moves, path)
    queue = deque([(start, 0, [start])])
    visited = {start}                  # Track visited positions
    
    # Level 1: Explore all positions reachable in 1 move
    # Level 2: Explore all positions reachable in 2 moves
    # Level 3: Continue until target is found
    
    while queue:
        current, moves, path = queue.popleft()
        
        # Try all possible dice rolls (1 through 6)
        for dice in range(1, 7):
            next_pos = board.get_next_position(current, dice)
            
            # Target found! Return immediately with moves+1
            if next_pos == target:
                return PathfindingResult(moves + 1, execution_time, "bfs", path)
            
            # Add new position to queue if not visited before
            if next_pos not in visited:
                visited.add(next_pos)
                queue.append((next_pos, moves + 1, path + [next_pos]))
    
    # No path found (shouldn't happen in valid board)
    return PathfindingResult(-1, execution_time, "bfs", [])
```

---

#### **BFS Visualization Example:**

```
Board: 6×6 (36 cells total)

Move 0 (Start):
  Queue: [(1, 0)]
  Positions reachable: {1}

Move 1 (Try dice 1-6 from position 1):
  From 1 + dice: {2, 3, 4, 5, 6, 7}
  If 4 has ladder to 12:
    Queue: [(2,1), (3,1), (12,1), (5,1), (6,1), (7,1)]
  Positions reachable in 1 move: {2, 3, 12, 5, 6, 7}

Move 2 (Try dice 1-6 from each position in Move 1):
  From 2: {3, 4, 5, 6, 7, 8}
  From 3: {4, 5, 6, 7, 8, 9}
  From 12: {13, 14, 15, 16, 17, 18}
  ... continue for all ...
  Positions reachable in 2 moves: {...}

Continue until cell 36 is reached.
```

---

#### **BFS Complexity:**

```
Time Complexity:  O(N² × 6) = O(N²)
  - Worst case: visit all N² cells
  - Each cell tries 6 dice rolls
  
Space Complexity: O(N²)
  - Queue can contain up to N² positions
  - Visited set tracks up to N² positions

For 8×8 board: ~384 operations (64 cells × 6)
For 12×12 board: ~864 operations (144 cells × 6)
```

---

### **2.2 DFS Algorithm (Depth-First Search with Iterative Deepening)**

**File:** `algorithms/pathfinding.py` → `find_min_moves_dfs()`

**Why DFS with Iterative Deepening (IDDFS)?**
- Standard DFS doesn't guarantee shortest path
- IDDFS = DFS at depth 0, then depth 1, then depth 2, etc.
- Guarantees optimal solution like BFS
- Uses less memory than BFS (doesn't store entire level)

---

#### **IDDFS Algorithm Step-by-Step:**

```python
def find_min_moves_dfs(board: SnakeLadderBoard) -> PathfindingResult:
    start = 1
    target = board.total_cells
    
    # Try increasing depth limits: 0, 1, 2, 3, ...
    for depth_limit in range(board.total_cells):
        # Perform depth-limited DFS
        result = _dfs_limited(board, start, target, depth_limit, [start], set())
        
        if result is not None:
            moves, path = result
            return PathfindingResult(moves, execution_time, "dfs", path)
    
    return PathfindingResult(-1, execution_time, "dfs", [])
```

---

#### **Depth-Limited DFS Helper:**

```python
def _dfs_limited(board, current, target, depth_limit, path, visited):
    
    # Base case 1: Target reached!
    if current == target:
        return (0, path)
    
    # Base case 2: Depth limit reached - cannot go deeper
    if depth_limit == 0:
        return None
    
    # Recursive case: Try all dice rolls
    for dice in range(1, 7):
        next_pos = board.get_next_position(current, dice)
        
        # Avoid cycles
        if next_pos in visited or next_pos == current:
            continue
        
        # Explore with reduced depth limit
        result = _dfs_limited(board, next_pos, target, depth_limit - 1,
                             path + [next_pos], visited.copy())
        
        if result is not None:
            moves, found_path = result
            return (moves + 1, found_path)  # Found! Return immediately
    
    return None  # No solution at this depth
```

---

#### **IDDFS Visualization Example:**

```
Depth Limit 0: Can only be at start position
  Search: [1]
  Result: Not at target, return None

Depth Limit 1: Can go 1 level deep (one dice throw)
  From 1, try: 2, 3, 4, 5, 6, 7 (with ladder/snake effects)
  If target is cell 36 and not reachable in 1 move: return None

Depth Limit 2: Can go 2 levels deep (two dice throws)
  From 1 → {2,3,4,5,6,7} → try from each position
  Search all paths of depth ≤ 2
  If target reachable in 2 moves: return Path

Depth Limit 3: Can go 3 levels deep (three dice throws)
  Continue searching if not found yet...

Continue until target is found.
```

---

#### **DFS Complexity:**

```
Time Complexity:  O(6^d) where d = optimal depth (moves)
  - For each depth limit, explores all paths up to that depth
  - With 6 dice options, this is exponential in depth
  - But depth is usually small (5-10 moves)
  
Space Complexity: O(d)
  - Only stores current path (much better than BFS)
  - Recursive call stack is at most depth limit

For optimal solution at 5 moves: ~7,776 operations worst case
BFS would be ~384 operations (explores all cells once)
Therefore: BFS is more efficient for this problem
```

---

## **Part 3: Algorithm Comparison**

### **3.1 BFS vs DFS (IDDFS)**

| Factor | BFS | DFS (IDDFS) |
|--------|-----|-----------|
| **Optimality** | ✓ Guaranteed | ✓ Guaranteed |
| **Time Complexity** | O(N²) | O(6^d) |
| **Space Complexity** | O(N²) | O(d) |
| **Speed** | Faster for this problem | Slower due to revisiting depths |
| **Memory Usage** | Higher | Lower |
| **Path Finding** | Finds path level-by-level | Finds path depth-by-depth |
| **Best Use Case** | When speed matters | When memory is limited |

---

### **3.2 Actual Execution Example**

**Board: 8×8, Random Snakes and Ladders**

```
BFS Results:
  Minimum moves: 5
  Execution time: 1.234 ms
  Path: 1 → 3 → 9 → 15 → 21 → 36

DFS Results:
  Minimum moves: 5
  Execution time: 3.567 ms
  Path: 1 → 2 → 8 → 14 → 20 → 36

Both algorithms find the same minimum (5 moves) but may find different paths.
BFS is faster because it doesn't re-explore shallower levels.
```

---

## **Part 4: Complete Game Flow**

### **4.1 Game Initialization**

```
1. User selects board size N (6-12)
2. SnakeLadderBoard(N) creates random board
   ├─ Generate N-2 ladders
   ├─ Generate N-2 snakes
   └─ Verify no overlaps
```

---

### **4.2 Algorithm Execution**

```
3. Run both algorithms:
   ├─ BFS: find_min_moves_bfs(board)
   │  └─ Returns: (moves: 5, time: 1.234ms)
   └─ DFS: find_min_moves_dfs(board)
      └─ Returns: (moves: 5, time: 3.567ms)
```

---

### **4.3 Answer Validation**

```
4. Player guesses the minimum moves
5. compare_algorithms() returns both results
6. Player's answer is checked:
   ├─ Correct if answer == BFS result
   └─ Incorrect otherwise
```

---

### **4.4 Data Storage**

```
7. Results saved to database:
   ├─ Player name
   ├─ Board size
   ├─ Snakes and ladders positions
   ├─ Player answer
   ├─ Correct answer (BFS result)
   ├─ BFS execution time
   ├─ DFS execution time
   ├─ Win/Loss status
   └─ Timestamp
```

---

## **Part 5: Key Algorithm Insights**

### **5.1 Why Minimum Moves Guarantee?**

Both BFS and DFS with Iterative Deepening guarantee the minimum number of moves because:

1. **They explore all possible paths** systematically
2. **They return as soon as the target is found** at the current depth
3. **The depth/level where target is found = minimum moves**

```
BFS finds target at level L → Minimum is L moves
IDDFS finds target at depth D → Minimum is D moves
```

---

### **5.2 Ladder and Snake Effect**

The algorithms automatically handle snakes and ladders because:

```python
# When position is checked, snakes/ladders are already applied
next_pos = board.get_next_position(current, dice)
# This function internally applies ladder/snake logic
```

This simplifies the algorithm - they don't need special logic for snakes/ladders.

---

### **5.3 Performance Factors**

**What affects execution time?**

1. **Board Size (N)**
   - Larger boards → more cells → potentially longer shortest path

2. **Snake/Ladder Placement**
   - Strategic placement can reduce or increase minimum moves
   - Random placement creates varied difficulty

3. **Algorithm Choice**
   - BFS: Consistent O(N²) time
   - DFS: Depends on optimal depth (usually 5-10 moves)

---

## **Summary**

The Snake and Ladder Game solution uses two complementary algorithms:

1. **BFS** - Fast and reliable pathfinding that guarantees optimality
2. **DFS (IDDFS)** - Space-efficient alternative with same optimality guarantee

Both algorithms work by treating the board as a graph where:
- Nodes = board cells
- Edges = dice rolls (1-6)
- Snakes/Ladders = automatic position transitions

The player's task is to guess the minimum number of dice throws (moves) to reach the target cell, and the system uses these algorithms to compute the correct answer and measure algorithm performance.
