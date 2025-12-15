# PDSA Games - Team Setup Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Clone/Download the Project
```bash
git clone <repository-url>
cd PDSA
```

### Step 2: Run Setup Script
```powershell
# Right-click on team_setup.ps1 -> "Run with PowerShell"
# OR open PowerShell and run:
.\team_setup.ps1
```

The script will ask for your **MySQL password** and set everything up automatically.

### Step 3: Play!
Open browser: http://127.0.0.1:8000/shared/index.html

---

## 📋 Prerequisites

Before running setup, ensure you have:

| Software | Download Link | Required |
|----------|---------------|----------|
| Python 3.10+ | https://www.python.org/downloads/ | ✅ Yes |
| MySQL 8.0+ | https://dev.mysql.com/downloads/installer/ | ✅ Yes |
| Node.js 18+ | https://nodejs.org/ | ⚠️ Optional |

### Python Installation Tips:
- ✅ Check "Add Python to PATH" during installation
- ✅ Check "Install pip" option

### MySQL Installation Tips:
- Remember your root password!
- Default port is 3306

---

## 🔧 Manual Setup (If Script Fails)

### 1. Create .env File
Copy `.env.example` to `.env` and edit:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=YOUR_PASSWORD_HERE
```

### 2. Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install fastapi uvicorn python-dotenv mysql-connector-python pydantic sqlalchemy
```

### 4. Create Databases
```sql
-- Run in MySQL:
CREATE DATABASE IF NOT EXISTS eight_queens_game;
CREATE DATABASE IF NOT EXISTS snake_game;
CREATE DATABASE IF NOT EXISTS traffic_simulation_game;
CREATE DATABASE IF NOT EXISTS tsp_game;
CREATE DATABASE IF NOT EXISTS pdsa_games;
```

### 5. Start Server
```powershell
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🎮 Game URLs

| Game | URL |
|------|-----|
| Game Menu | http://127.0.0.1:8000/shared/index.html |
| Eight Queens | http://127.0.0.1:8000/games/eight_queens/frontend/index.html |
| Snake & Ladder | http://127.0.0.1:8000/games/snake_ladder/frontend/index.html |
| Traffic Simulation | http://127.0.0.1:8000/games/traffic_simulation/frontend/traffic.html |
| Traveling Salesman | http://127.0.0.1:8000/games/traveling_salesman/src/frontend/index.html |
| Tower of Hanoi | http://127.0.0.1:8000/games/tower_hanoi/frontend/index.html |

---

## 🐛 Troubleshooting

### "Access denied for user 'root'@'localhost'"
- Check your MySQL password in `.env` file
- Make sure MySQL service is running

### "Port 8000 already in use"
```powershell
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### "Module not found"
```powershell
# Make sure virtual environment is active
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### "Python not recognized"
- Reinstall Python with "Add to PATH" checked
- Or add Python to PATH manually

---

## 📁 Project Structure

```
PDSA/
├── .env                 # Your local config (DO NOT COMMIT)
├── .env.example         # Template for .env
├── team_setup.ps1       # Universal setup script
├── games/               # All 5 games
│   ├── eight_queens/
│   ├── snake_ladder/
│   ├── traffic_simulation/
│   ├── traveling_salesman/
│   └── tower_hanoi/
└── shared/              # Common code
    ├── backend/         # FastAPI server
    ├── database/        # Shared schema
    └── frontend/        # Game menu
```

---

## 👥 Team Databases

Each game uses its own database:

| Game | Database Name |
|------|---------------|
| Eight Queens | eight_queens_game |
| Snake & Ladder | snake_game |
| Traffic Simulation | traffic_simulation_game |
| Traveling Salesman | tsp_game |
| Tower of Hanoi | pdsa_games |

---

## ❓ Need Help?

1. Check the console/terminal for error messages
2. Make sure MySQL is running: `net start MySQL80`
3. Verify `.env` has correct password
4. Try running `.\team_setup.ps1` again
