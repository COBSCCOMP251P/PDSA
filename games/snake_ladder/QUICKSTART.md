# 🐍 Snake and Ladder Game - Quick Start

## 🚀 Get Started in 5 Minutes

### Prerequisites
- ✅ Python 3.8+
- ✅ MySQL 8.0+
- ✅ Web browser

---

## 📋 Step-by-Step Setup

### 1️⃣ Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### 2️⃣ Setup Database
```sql
-- In MySQL:
CREATE DATABASE pdsa_games;
USE pdsa_games;
SOURCE shared/database/schema.sql;
```

### 3️⃣ Configure Environment
Create `.env` file in project root:
```env
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=pdsa_games
```

### 4️⃣ Run Tests (Optional but Recommended)
```powershell
cd games\snake_ladder\tests
python run_tests.py
```

### 5️⃣ Start Backend Server
```powershell
cd games\snake_ladder
.\start_backend.ps1
```

**OR manually:**
```powershell
cd shared\backend
python main.py
```

### 6️⃣ Open Frontend
```powershell
# In a new terminal:
cd games\snake_ladder
.\start_frontend.ps1
```

**OR open directly:**
Open `games\snake_ladder\frontend\index.html` in your browser

---

## 🎮 How to Play

1. **Enter Your Name** - Type your name in the form
2. **Select Board Size** - Choose between 6×6 and 12×12
3. **Click Start Game** - Board will be generated
4. **View the Board** - See snakes 🐍 and ladders 🪜
5. **Select Your Answer** - Choose from 3 options
6. **Submit** - See if you're correct!
7. **View Stats** - Check your performance and leaderboard

---

## 📊 Game Rules

- 🎯 **Goal**: Find minimum dice throws to reach the end
- 🎲 **Dice**: Each roll gives 1-6
- 🪜 **Ladders**: Jump up to higher cells
- 🐍 **Snakes**: Slide down to lower cells
- 🏁 **Win**: Reach cell N² (last cell)

---

## 🔗 Important URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:8080 | Game interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Interactive docs |
| Health Check | http://localhost:8000/api/health | Server status |

---

## 🧪 Testing

### Run All Tests
```powershell
cd games\snake_ladder\tests
python run_tests.py
```

### Expected Output
```
✅ 70+ tests passed
✅ Game logic verified
✅ Algorithms tested
✅ Integration working
```

---

## 🆘 Quick Troubleshooting

### Backend Won't Start
```powershell
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip list | findstr fastapi

# Check port availability
netstat -ano | findstr :8000
```

### Database Connection Error
```powershell
# Test MySQL connection
mysql -u root -p

# Verify database exists
SHOW DATABASES;
```

### Frontend Can't Connect
1. Ensure backend is running: `http://localhost:8000/api/health`
2. Check browser console for errors (F12)
3. Verify API_BASE_URL in `frontend/script.js`

---

## 📁 Project Structure

```
games/snake_ladder/
├── algorithms/       # Game logic & algorithms
├── api/             # REST API endpoints
├── frontend/        # User interface
├── tests/           # Unit & integration tests
├── start_backend.ps1   # Backend startup script
├── start_frontend.ps1  # Frontend startup script
├── README.md        # Full documentation
└── SETUP.md        # Detailed setup guide
```

---

## ✨ Features

✅ Random board generation  
✅ BFS & DFS algorithms  
✅ Interactive UI  
✅ Player statistics  
✅ Leaderboard  
✅ Performance tracking  
✅ 70+ unit tests  
✅ Exception handling  

---

## 🎯 API Endpoints

### Initialize Game
```
POST /api/snake-ladder/init
Body: {"player_name": "John", "board_size": 8}
```

### Submit Answer
```
POST /api/snake-ladder/submit
Body: {"session_id": "...", "player_answer": 6}
```

### Get Leaderboard
```
GET /api/snake-ladder/leaderboard?limit=10
```

### Get Player Stats
```
GET /api/snake-ladder/stats/{player_name}
```

---

## 📞 Need Help?

1. Check [SETUP.md](SETUP.md) for detailed setup
2. Check [README.md](README.md) for full documentation
3. Review test outputs: `python run_tests.py`
4. Check API docs: http://localhost:8000/docs

---

## 🎓 Algorithms Used

### BFS (Breadth-First Search)
- **Best for**: Finding shortest path
- **Guarantees**: Optimal solution
- **Time**: O(N² × 6)

### DFS (Iterative Deepening)
- **Best for**: Memory efficiency
- **Guarantees**: Optimal solution (with ID)
- **Space**: O(depth)

---

## 🏆 Sample Game Results

```
Board: 8×8 (64 cells)
Ladders: 6
Snakes: 6
Minimum Moves: 7

BFS Time: 1.234 ms
DFS Time: 2.456 ms

Player Answer: 7 ✅ CORRECT!
```

---

## 📝 Quick Commands Cheat Sheet

```powershell
# Install dependencies
pip install -r requirements.txt

# Run tests
cd games\snake_ladder\tests; python run_tests.py

# Start backend
cd shared\backend; python main.py

# Start frontend
cd games\snake_ladder\frontend; python -m http.server 8080

# Create database
mysql -u root -p < shared\database\schema.sql

# Format code
black games/snake_ladder/

# Check imports
pip list
```

---

## 🎉 You're Ready!

Now start playing and see if you can find the optimal path! 🎲🎯

Good luck! 🍀
