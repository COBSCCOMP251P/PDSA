# How to Run PDSA Eight Queens Game

## 🚀 Quick Start (Choose ONE method)

### Method 1: Double-Click (Easiest)
1. Open the `PDSA` folder
2. Double-click `run.bat`
3. Wait for server to start
4. Open browser: http://127.0.0.1:8000/games/eight_queens/frontend/index.html

### Method 2: PowerShell Command
```powershell
cd C:\Users\User\OneDrive\Desktop\PDSA
.\run.ps1
```

### Method 3: Manual Commands (if above don't work)
```powershell
cd C:\Users\User\OneDrive\Desktop\PDSA
.\.venv\Scripts\Activate.ps1
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8000
```

---

## 📋 Requirements (Must be installed)

| Software | Required | Check Command |
|----------|----------|---------------|
| Python 3.8+ | ✅ | `python --version` |
| MySQL | ✅ | `mysql --version` |
| Node.js | Optional | `node --version` |

---

## 🔗 URLs (After server starts)

| Page | URL |
|------|-----|
| **Game** | http://127.0.0.1:8000/games/eight_queens/frontend/index.html |
| **API Docs** | http://127.0.0.1:8000/docs |
| **Health Check** | http://127.0.0.1:8000/api/health |

---

## ❌ Common Problems & Solutions

### Problem: "python not found"
**Solution:** Install Python from https://python.org and add to PATH

### Problem: "Module not found"
**Solution:** Run these commands:
```powershell
cd C:\Users\User\OneDrive\Desktop\PDSA
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn python-dotenv mysql-connector-python
```

### Problem: "Port 8000 already in use"
**Solution:** Close VS Code or other programs, or use different port:
```powershell
python -m uvicorn shared.backend.main:app --reload --host 127.0.0.1 --port 8001
```

### Problem: "MySQL connection failed"
**Solution:** 
1. Make sure MySQL is running (check Windows Services)
2. Check password in `.env` file is correct: `DB_PASSWORD=pruthuvide`

---

## 🛑 To Stop Server
Press `Ctrl + C` in the terminal

---

## 📁 File Explanation

| File | Purpose |
|------|---------|
| `run.bat` | Double-click to start (Windows) |
| `run.ps1` | PowerShell start script |
| `start.ps1` | Full setup script (complex) |
| `.venv/` | Python virtual environment |
| `shared/backend/main.py` | Main server file |
| `games/eight_queens/` | Game files |
