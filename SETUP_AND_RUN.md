# 🎮 PDSA Algorithm Games - Setup & Run Guide

Complete guide for running all 5 integrated algorithm games.

---

## 🚀 Quick Start (Recommended)

### **Windows PowerShell** (Simplest Method)

```powershell
# Navigate to project directory
cd C:\Users\User\OneDrive\Desktop\PDSA

# Run the unified start script
.\start.ps1
```

**That's it!** The script automatically:
- ✅ Checks MySQL service
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Builds CSS assets
- ✅ Starts FastAPI server

---

## 📋 Prerequisites

### Required Software:
1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **MySQL Server** - Already installed (MySQL80 service)
3. **Node.js** - For CSS building (optional)
4. **Git** - For version control

### Database Credentials:
- **Host**: localhost:3306
- **User**: root
- **Password**: pruthuvide (configured in `.env` file)

---

## 🎯 Access Points After Starting

Once the server is running, access games at:

| Game | URL |
|------|-----|
| 🎮 **Main Menu** | http://127.0.0.1:8000/shared/index.html |
| ♛ **Eight Queens** | http://127.0.0.1:8000/games/eight_queens/frontend/index.html |
| 🐍 **Snake & Ladder** | http://127.0.0.1:8000/games/snake_ladder/frontend/index.html |
| 🚦 **Traffic Simulation** | http://127.0.0.1:8000/games/traffic_simulation/frontend/index.html |
| 🗺️ **Traveling Salesman** | http://127.0.0.1:8000/games/traveling_salesman/src/frontend/index.html |
| 🗼 **Tower of Hanoi** | http://127.0.0.1:8000/games/tower_hanoi/frontend/index.html |
| 📚 **API Docs** | http://127.0.0.1:8000/docs |
| 💚 **Health Check** | http://127.0.0.1:8000/api/health |

---

## 🛠️ Advanced Usage

### Start Script Options:

```powershell
# Quick start (skip dependency checks)
.\start.ps1 -QuickStart

# Reset database and start
.\start.ps1 -ResetDatabase

# Show detailed output
.\start.ps1 -Verbose
```

### Manual Startup (if script fails):

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies manually
pip install fastapi uvicorn[standard] python-dotenv mysql-connector-python

# 3. Build CSS (optional)
npm install
npm run build-css

# 4. Start server
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 🗄️ Database Setup

### Databases Used:
1. **eight_queens_game** - Eight Queens game data
2. **snake_game** - Snake & Ladder game data
3. **traffic_simulation_game** - Traffic simulation data
4. **pdsa_games** - Tower of Hanoi and shared game data

### Manual Database Creation:

```sql
-- Connect to MySQL
mysql -u root -ppruthuvide

-- Create databases (if not exist)
CREATE DATABASE IF NOT EXISTS eight_queens_game;
CREATE DATABASE IF NOT EXISTS snake_game;
CREATE DATABASE IF NOT EXISTS traffic_simulation_game;
CREATE DATABASE IF NOT EXISTS pdsa_games;

-- Verify databases
SHOW DATABASES;
```

### Database Schemas:

All schema files are located in:
- `games/eight_queens/database/schema.sql`
- `games/snake_ladder/` (auto-created by API)
- `games/traffic_simulation/database/schema.sql`
- `games/tower_hanoi/database/schema.sql`

---

## 🐛 Troubleshooting

### Common Issues:

#### **1. Port 8000 Already in Use**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### **2. Virtual Environment Not Working**
```powershell
# Delete and recreate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\start.ps1
```

#### **3. MySQL Connection Failed**
```powershell
# Check MySQL service
Get-Service | Where-Object {$_.Name -like "*mysql*"}

# Start MySQL service if stopped
Start-Service MySQL80

# Test connection
mysql -u root -ppruthuvide -e "SELECT 1;"
```

#### **4. Database Password Error**
```
Error: Access denied for user 'root'@'localhost' (using password: NO)
```
**Fix**: Check `.env` file has correct password:
```env
DB_PASSWORD=pruthuvide
```

#### **5. CSS Not Loading**
```powershell
# Rebuild CSS manually
npm install
npm run build-css
```

---

## 📦 Project Structure

```
PDSA/
├── start.ps1                    # 🚀 Main startup script (USE THIS)
├── .env                         # Database credentials
├── shared/
│   ├── backend/
│   │   └── main.py             # FastAPI main application
│   ├── frontend/
│   │   └── index.html          # Main game menu
│   └── database/
│       └── connection.py       # Shared DB connection
├── games/
│   ├── eight_queens/           # Game 1
│   ├── snake_ladder/           # Game 2
│   ├── traffic_simulation/     # Game 3
│   ├── traveling_salesman/     # Game 4
│   └── tower_hanoi/            # Game 5
└── .venv/                      # Python virtual environment
```

---

## 🔄 For New Team Members

### First Time Setup:

```powershell
# 1. Clone the repository
git clone <repository-url>
cd PDSA

# 2. Checkout the integration branch
git checkout feature/all-games-integration

# 3. Ensure MySQL is running
# Check in Windows Services or run:
Start-Service MySQL80

# 4. Run the start script
.\start.ps1

# 5. Open browser to main menu
# http://127.0.0.1:8000/shared/index.html
```

**That's it!** The script handles everything else automatically.

---

## 📝 Environment Variables (.env file)

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=pruthuvide
DB_NAME=eight_queens_game

# API Configuration
API_HOST=localhost
API_PORT=8000
API_PREFIX=/api

# Development Settings
DEBUG=true
ENVIRONMENT=development
```

---

## 🎓 Development Tips

### Running Individual Games:
All games are integrated into one server. Just navigate to different URLs (see Access Points above).

### Stopping the Server:
Press `Ctrl+C` in the terminal where the server is running.

### Viewing Logs:
Server logs appear in the terminal. Check for:
- ✅ Game routes loaded
- 🔍 Database connections
- ⚠️ Warnings or errors

### API Documentation:
Visit http://127.0.0.1:8000/docs for interactive API documentation.

---

## 🤝 Team Workflow

1. **Pull latest changes**: `git pull origin feature/all-games-integration`
2. **Run start script**: `.\start.ps1`
3. **Test your game**: Navigate to your game's URL
4. **Check database**: Verify data persistence in MySQL
5. **Push changes**: Commit and push to your feature branch

---

## 📞 Support

If you encounter issues:
1. Check this guide's Troubleshooting section
2. Verify all prerequisites are installed
3. Check terminal output for error messages
4. Ensure MySQL service is running
5. Verify port 8000 is not in use

---

## ✅ Quick Checklist

Before running the project:
- [ ] Python 3.8+ installed
- [ ] MySQL service running (MySQL80)
- [ ] Port 8000 available
- [ ] `.env` file contains correct password
- [ ] In project root directory
- [ ] Run `.\start.ps1`
- [ ] Open http://127.0.0.1:8000/shared/index.html

**Done! All 5 games should now be accessible.** 🎉
