# 🎮 PDSA Games - Complete Setup Instructions for All Team Members

## ✅ Quick Setup (3 Steps)

### Step 1: Clone and Setup Environment
```powershell
# Clone repository
git clone https://github.com/COBSCCOMP251P/PDSA.git
cd PDSA

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install fastapi uvicorn python-dotenv mysql-connector-python pydantic sqlalchemy
npm install
npm run build-css
```

### Step 2: Setup All Databases
```powershell
# Run the database setup script
.\setup_databases.ps1

# It will prompt for MySQL password - enter your MySQL root password
```

### Step 3: Start the Application
```powershell
# Use the startup script (easiest)
.\start.ps1

# Or manually
.\.venv\Scripts\Activate.ps1
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000
```

**That's it! Open http://127.0.0.1:8000/shared/index.html**

---

## 📊 Database Overview

### All 5 Databases Created:

| # | Game | Database Name | Status |
|---|------|---------------|--------|
| 1 | Eight Queens | `eight_queens_game` | ✅ Working with all features |
| 2 | Snake & Ladder | `snake_ladder_game` | ✅ Working |
| 3 | Traffic Simulation | `traffic_simulation_game` | ✅ Working |
| 4 | Tower of Hanoi | `pdsa_games` | ✅ Working |
| 5 | Traveling Salesman | `tsp_game` | ✅ Working |

### Verify Databases Created:
```sql
-- Connect to MySQL
mysql -u root -p

-- List all databases
SHOW DATABASES;

-- You should see:
-- eight_queens_game
-- snake_ladder_game  
-- traffic_simulation_game
-- pdsa_games
-- tsp_game
```

---

## 🔧 Scripts Provided

| Script | Purpose | Usage |
|--------|---------|-------|
| `setup_databases.ps1` | Create all 5 game databases | `.\setup_databases.ps1` |
| `start.ps1` | Start server (handles everything) | `.\start.ps1` |
| `setup_all_databases.py` | Python version (backup) | `python setup_all_databases.py` |

---

## 📁 What Each Team Member Needs

### For ANY Team Member:

1. **Prerequisites:**
   - Python 3.8+
   - MySQL Server installed and running
   - Node.js (for Tailwind CSS)
   - Git

2. **Setup Steps (same for everyone):**
   ```powershell
   # 1. Clone
   git clone https://github.com/COBSCCOMP251P/PDSA.git
   cd PDSA
   
   # 2. Virtual environment
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   
   # 3. Dependencies
   pip install fastapi uvicorn python-dotenv mysql-connector-python pydantic sqlalchemy
   npm install
   
   # 4. Build CSS
   npm run build-css
   
   # 5. Setup databases
   .\setup_databases.ps1
   
   # 6. Start server
   .\start.ps1
   ```

3. **Done!** All 5 games will work on everyone's computer

---

## 🎮 Game Access URLs

After running `.\start.ps1`:

| Game | URL |
|------|-----|
| **Main Menu** | http://127.0.0.1:8000/shared/index.html |
| Eight Queens | http://127.0.0.1:8000/games/eight_queens/frontend/index.html |
| Snake & Ladder | http://127.0.0.1:8000/games/snake_ladder/frontend/index.html |
| Traffic Simulation | http://127.0.0.1:8000/games/traffic_simulation/frontend/traffic.html |
| Tower of Hanoi | http://127.0.0.1:8000/games/tower_hanoi/frontend/index.html |
| Traveling Salesman | http://127.0.0.1:8000/games/traveling_salesman/frontend/index.html |
| **API Docs** | http://127.0.0.1:8000/docs |

---

## 💾 Database Details

### 1. Eight Queens (`eight_queens_game`)

**Tables:**
- `players` - Player information
- `solutions` - All 92 queen placement solutions
- `game_sessions` - Game rounds played
- `eightqueensresults` - Game results and scores
- `difficulty_settings` - Difficulty configurations

**Features:**
- Solution discovery tracking
- Duplicate solution detection
- Auto-reset after all 92 solutions found
- Player ranking system

### 2. Snake & Ladder (`snake_ladder_game`)

**Tables:**
- `Players` - Player profiles
- `GameSessions` - Active game sessions
- `SnakeLadderResults` - Game outcomes
- `SnakeLadderAlgorithmPerformance` - BFS vs DFS metrics

**Features:**
- Pathfinding algorithms (BFS/DFS)
- Performance benchmarking
- Player statistics

### 3. Traffic Simulation (`traffic_simulation_game`)

**Tables:**
- `Players` - Player data
- `GameSessions` - Game sessions
- `TrafficFlowResults` - Max flow results

**Features:**
- Edmonds-Karp algorithm
- Dinic's algorithm
- Performance comparison

### 4. Tower of Hanoi (`pdsa_games`)

**Tables:**
- `players` - Player information
- `rounds` - Game rounds
- `submissions` - Player solutions
- `algorithm_runs` - Algorithm benchmarks

**Features:**
- 3-peg and 4-peg configurations
- Multiple algorithm comparison
- Move validation

### 5. Traveling Salesman (`tsp_game`)

**Tables:**
- `game_rounds` - Game data
- `algorithm_times` - Performance metrics

**Features:**
- Brute Force algorithm
- Nearest Neighbor heuristic
- Dynamic Programming (Held-Karp)

---

## 🚨 Troubleshooting

### Issue: "MySQL connection failed"

**Solution:**
1. Check MySQL is running:
   ```powershell
   # Windows
   services.msc  # Look for MySQL80
   ```

2. Test connection:
   ```powershell
   mysql -u root -p
   ```

3. Verify password when running `setup_databases.ps1`

### Issue: "Module not found"

**Solution:**
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Reinstall packages
pip install fastapi uvicorn python-dotenv mysql-connector-python pydantic sqlalchemy
```

### Issue: "Port 8000 already in use"

**Solution:**
```powershell
# Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### Issue: "CSS not loading"

**Solution:**
```powershell
npm run build-css
```

### Issue: "Database already exists"

**Solution:**
This is OK! The warning means databases are already set up. Games will work fine.

---

## 🎓 For VIVA Preparation

### What to Know About Databases:

**1. Your Game's Schema:**
- Table names and purposes
- Column types and constraints
- Relationships (foreign keys)
- Indexes for performance

**2. Database Operations:**
- How data is inserted (game results)
- How data is queried (leaderboards, statistics)
- How transactions work

**3. SQL Examples:**
```sql
-- See all players
USE eight_queens_game;
SELECT * FROM players;

-- See game results
SELECT * FROM eightqueensresults ORDER BY score DESC LIMIT 10;

-- Check solutions found
SELECT COUNT(*) FROM solutions WHERE is_found = TRUE;
```

### Demo Flow:

1. **Show the game menu** - http://127.0.0.1:8000/shared/index.html
2. **Play your game** - demonstrate features
3. **Show database updates:**
   ```sql
   -- Before playing
   SELECT COUNT(*) FROM eightqueensresults;
   
   -- After playing
   SELECT COUNT(*) FROM eightqueensresults;  -- Number increased!
   
   -- Show the result
   SELECT * FROM eightqueensresults ORDER BY id DESC LIMIT 1;
   ```
4. **Explain your algorithms** - how they work
5. **Show API endpoints** - http://127.0.0.1:8000/docs

---

## ✅ Verification Checklist

Before your VIVA, verify:

- [ ] Virtual environment works
- [ ] All dependencies installed
- [ ] MySQL running
- [ ] All 5 databases created
- [ ] Server starts without errors
- [ ] All 5 games load from menu
- [ ] Your game works completely
- [ ] Database updates when you play
- [ ] Can explain your code
- [ ] Can explain your database schema
- [ ] Can demonstrate live

---

## 📞 Team Communication

### Sharing Your Work:

```bash
# Create your branch
git checkout -b feature/your-game

# Commit your changes
git add games/your_game/
git commit -m "Completed my game features"

# Push to your branch
git push origin feature/your-game
```

### Pulling Team Changes:

```bash
# Update from main
git checkout main
git pull origin main

# Rebuild CSS if needed
npm run build-css

# Restart server
.\start.ps1
```

---

## 🎯 Success Criteria

Your setup is complete when:

1. ✅ You can run `.\start.ps1` without errors
2. ✅ Terminal shows all 5 games loaded
3. ✅ Game menu opens in browser
4. ✅ All 5 games are playable
5. ✅ Databases update when playing
6. ✅ API docs are accessible

---

## 📝 Summary

**For ALL team members to get working:**

```powershell
# 1. Clone
git clone https://github.com/COBSCCOMP251P/PDSA.git
cd PDSA

# 2. Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn python-dotenv mysql-connector-python pydantic sqlalchemy
npm install
npm run build-css

# 3. Create databases
.\setup_databases.ps1  # Enter MySQL password when prompted

# 4. Start
.\start.ps1

# 5. Open browser
http://127.0.0.1:8000/shared/index.html
```

**That's it!** All 5 games with all databases working on everyone's computer! 🎉

---

**Need Help?** Check TEAM_SETUP_GUIDE.md for detailed troubleshooting.
