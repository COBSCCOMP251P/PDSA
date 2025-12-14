# 🎮 PDSA Games - Team Setup Guide

## Quick Start for Team Members

This guide will help all 5 team members set up and run all games on their computers.

---

## 📋 Prerequisites

Before starting, make sure you have:

1. **Python 3.8+** installed
   - Check: `python --version`
   - Download: https://www.python.org/downloads/

2. **MySQL Server** installed and running
   - Check: `mysql --version`
   - Download: https://dev.mysql.com/downloads/mysql/

3. **Node.js** (for Tailwind CSS)
   - Check: `node --version`
   - Download: https://nodejs.org/

4. **Git** installed
   - Check: `git --version`

---

## 🚀 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/COBSCCOMP251P/PDSA.git
cd PDSA
```

### Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
pip install fastapi uvicorn python-dotenv mysql-connector-python pydantic sqlalchemy
```

### Step 4: Install Node Dependencies

```bash
npm install
```

### Step 5: Configure Database Password

1. Open `setup_all_databases.py`
2. Find line 13:
   ```python
   'password': 'pruthuvide',  # Change this to your MySQL password
   ```
3. Change `'pruthuvide'` to **YOUR MySQL root password**

### Step 6: Run Database Setup

```bash
python setup_all_databases.py
```

Expected output:
```
✅ Eight Queens database created: 'eight_queens_game'
✅ Snake & Ladder database created: 'snake_ladder_game'
✅ Traffic Simulation database created: 'traffic_simulation_game'
✅ Tower of Hanoi database created: 'pdsa_games'
✅ Traveling Salesman database created: 'tsp_game'
```

### Step 7: Build Frontend CSS

```bash
npm run build-css
```

### Step 8: Start the Server

```bash
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
✅ Eight Queens routes loaded (original + simple gaming)
✅ Snake Ladder routes loaded
✅ Traffic Simulation routes loaded
✅ Traveling Salesman routes loaded
✅ Tower of Hanoi routes loaded
```

### Step 9: Open in Browser

Navigate to: **http://127.0.0.1:8000/shared/index.html**

---

## 🎯 Quick Commands Reference

### Start Everything (After Initial Setup)

**Windows PowerShell:**
```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Start server
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Mac/Linux:**
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Start server
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Use the Startup Script (Easiest)

**Windows:**
```powershell
.\start.ps1
```

This script does everything automatically!

---

## 📊 Database Information

### All 5 Game Databases

| Game | Database Name | Tables |
|------|---------------|--------|
| Eight Queens | `eight_queens_game` | players, solutions, game_sessions, eightqueensresults |
| Snake & Ladder | `snake_ladder_game` | Players, GameSessions, SnakeLadderResults, SnakeLadderAlgorithmPerformance |
| Traffic Simulation | `traffic_simulation_game` | Players, GameSessions, TrafficFlowResults |
| Tower of Hanoi | `pdsa_games` | players, rounds, submissions, algorithm_runs |
| Traveling Salesman | `tsp_game` | game_rounds, algorithm_times |

### MySQL Access

```bash
# Connect to MySQL
mysql -u root -p

# Show all databases
SHOW DATABASES;

# Use a specific database
USE eight_queens_game;

# Show tables
SHOW TABLES;

# View data
SELECT * FROM players;
```

---

## 🔧 Troubleshooting

### Issue: "Module not found"

**Solution:**
```bash
# Make sure virtual environment is activated
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Mac/Linux

# Reinstall dependencies
pip install fastapi uvicorn python-dotenv mysql-connector-python
```

### Issue: "Database connection failed"

**Solution:**
1. Check MySQL is running:
   ```bash
   # Windows
   services.msc  # Look for MySQL80
   
   # Mac
   brew services list
   ```

2. Verify password in `setup_all_databases.py`

3. Test connection:
   ```bash
   mysql -u root -p
   ```

### Issue: "Port 8000 is already in use"

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux
lsof -i :8000
kill -9 <process_id>
```

### Issue: CSS not loading

**Solution:**
```bash
npm run build-css
```

---

## 🎮 Game URLs

After starting the server:

| Game | URL |
|------|-----|
| **Game Menu** | http://127.0.0.1:8000/shared/index.html |
| Eight Queens | http://127.0.0.1:8000/games/eight_queens/frontend/index.html |
| Snake & Ladder | http://127.0.0.1:8000/games/snake_ladder/frontend/index.html |
| Traffic Simulation | http://127.0.0.1:8000/games/traffic_simulation/frontend/traffic.html |
| Tower of Hanoi | http://127.0.0.1:8000/games/tower_hanoi/frontend/index.html |
| Traveling Salesman | http://127.0.0.1:8000/games/traveling_salesman/frontend/index.html |
| **API Documentation** | http://127.0.0.1:8000/docs |

---

## 📁 Project Structure

```
PDSA/
├── games/                    # All 5 games
│   ├── eight_queens/         # Your game
│   ├── snake_ladder/         # Team member 2
│   ├── traffic_simulation/   # Team member 3
│   ├── tower_hanoi/          # Team member 4
│   └── traveling_salesman/   # Team member 5
├── shared/                   # Common code
│   ├── backend/              # FastAPI server
│   │   └── main.py           # Main entry point
│   ├── frontend/             # Game menu
│   │   └── index.html        # Main menu page
│   └── database/             # Shared database utilities
├── .venv/                    # Virtual environment (create this)
├── setup_all_databases.py    # Database setup script
├── start.ps1                 # Windows startup script
└── package.json              # Node dependencies
```

---

## 👥 Team Member Workflow

### For Team Member Working on Their Game

1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Work on your game folder only:**
   ```
   games/your_game/
   ```

3. **Test your changes:**
   ```bash
   # Start server
   python -m uvicorn shared.backend.main:app --reload
   
   # Open your game
   http://127.0.0.1:8000/games/your_game/frontend/index.html
   ```

4. **Commit your changes:**
   ```bash
   git add games/your_game/
   git commit -m "Updated my game feature"
   git push origin your-branch
   ```

### Sharing Work with Team

1. Each member creates their own branch:
   ```bash
   git checkout -b feature/your-game-name
   ```

2. Push to their branch:
   ```bash
   git push origin feature/your-game-name
   ```

3. Team lead merges all branches into main

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Virtual environment activates without errors
- [ ] `pip list` shows fastapi, uvicorn, mysql-connector-python
- [ ] MySQL is running (`mysql -u root -p` works)
- [ ] All 5 databases created (check with `SHOW DATABASES;`)
- [ ] Server starts without errors
- [ ] See "✅" for all 5 games in terminal
- [ ] Game menu loads at http://127.0.0.1:8000/shared/index.html
- [ ] Each game opens from the menu
- [ ] API docs accessible at http://127.0.0.1:8000/docs

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the terminal output** for specific error messages
2. **Verify all prerequisites** are installed
3. **Ask team members** who got it working
4. **Check the troubleshooting section** above

---

## 📝 Important Notes

- **Always activate virtual environment** before running Python commands
- **MySQL password** must match in `setup_all_databases.py`
- **Don't edit other members' game folders** to avoid conflicts
- **Test your game** before pushing to repository
- **Use the startup script** (`start.ps1`) for easiest setup

---

## 🎓 For VIVA Preparation

Make sure you understand:

1. **Your game's database schema** - which tables, columns, relationships
2. **Your game's API endpoints** - what they do, inputs, outputs
3. **Your game's algorithms** - how they work, time complexity
4. **How to start the application** - full process from scratch
5. **How to demonstrate your game** - gameplay, features, database interaction

Good luck with your presentation! 🚀
