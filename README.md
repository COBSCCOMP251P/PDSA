# PDSA Interactive Algorithm Game Collection

## Quick Start for Team Members

### 1. Clone and Setup
```bash
git clone https://github.com/COBSCCOMP251P/PDSA.git
cd PDSA
```

### 2. Create Your Game Branch
```bash
# Replace with your assigned game
git checkout -b feature/eight-queens-[your-name]
git checkout -b feature/snake-ladder-[your-name]
git checkout -b feature/traffic-simulation-[your-name]
git checkout -b feature/traveling-salesman-[your-name]
git checkout -b feature/tower-hanoi-[your-name]
```

### 3. Setup Development Environment

#### Python Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Frontend Setup (Tailwind CSS)
```bash
# Install Node.js dependencies
npm install

# Build Tailwind CSS (run this when you modify styles)
npm run build-css

# Watch for changes during development
npm run watch-css
```

#### Database Setup
```bash
# Install MySQL (if not installed)
# Create database
mysql -u root -p
CREATE DATABASE pdsa_games;

# Run database schema
mysql -u root -p pdsa_games < shared/database/schema.sql
```

### 4. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
DATABASE_HOST=localhost
DATABASE_USER=root
DATABASE_PASSWORD=your_password
DATABASE_NAME=pdsa_games
```

### 5. Start Development
```bash
# Start backend server
cd shared/backend
uvicorn main:app --reload --port 8000

# Open frontend
# Open shared/frontend/index.html in browser
# Or use live server extension in VS Code
```

## Project Structure

```
PDSA/
├── games/                     # Individual game modules
│   ├── eight_queens/         #  Member 5
│   ├── snake_ladder/         #  Member 1  
│   ├── traffic_simulation/   #  Member 2
│   ├── traveling_salesman/   #  Member 3
│   └── tower_hanoi/          #  Member 4
│
├── shared/                   # Common components
│   ├── frontend/            # Main menu & shared UI
│   ├── backend/             # FastAPI application
│   └── database/            # Database schema & connection
│
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
└── .env.example           # Environment template
```

## Game Assignments

| Game | Member | Branch | API Route |
|------|--------|--------|-----------|
| Eight Queens | Member 5 | `feature/eight-queens-[name]` | `/api/queens/` |
| Snake & Ladder | Member 1 | `feature/snake-ladder-[name]` | `/api/snake-ladder/` |
| Traffic Simulation | Member 2 | `feature/traffic-simulation-[name]` | `/api/traffic/` |
| Traveling Salesman | Member 3 | `feature/traveling-salesman-[name]` | `/api/tsp/` |
| Tower of Hanoi | Member 4 | `feature/tower-hanoi-[name]` | `/api/hanoi/` |

## Your Development Workflow

### 1. Work in Your Game Module
```bash
# Example for Eight Queens
cd games/eight_queens/

# Your files:
algorithms/sequential_solver.py
algorithms/threaded_solver.py  
frontend/queens.html
frontend/queens.js
api/queens_routes.py
database/queens_schema.sql
tests/test_queens.py
docs/algorithm_analysis.md
```

### 2. Test Your Work
```bash
# Run your algorithm tests
python games/eight_queens/tests/test_sequential.py

# Test your API endpoints
python games/eight_queens/api/queens_routes.py

# View your frontend
open games/eight_queens/frontend/queens.html
```

### 3. Regular Commits
```bash
git add games/eight_queens/
git commit -m "feat(queens): implement sequential backtracking algorithm"
git push origin feature/eight-queens-[your-name]
```

### 4. Integration to Main
```bash
# When ready, create Pull Request
# Team lead will review and merge
# Update main menu to include your game
```

## Testing Your Setup

### 1. Backend Test
```bash
cd shared/backend
python main.py
# Should see: "FastAPI app running on http://localhost:8000"
```

### 2. Frontend Test
```bash
# Open shared/frontend/index.html
# Should see main menu with game options
```

### 3. Database Test
```bash
python shared/database/connection.py
# Should see: "Database connection successful"
```
