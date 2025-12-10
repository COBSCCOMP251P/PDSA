# Traveling Salesman Game

Vanilla JS + Tailwind frontend with a FastAPI backend and MySQL storage for a student-friendly Traveling Salesman Problem game.

## What’s Inside
- `frontend/` — static HTML/JS/CSS pages for home, game board, and results.
- `backend/` — FastAPI app with TSP algorithms, validation, and DB persistence.
- `database/` — MySQL schema for `tsp_game` with game rounds and algorithm times.
- `requirements.txt` — Python dependencies for the backend.

## Quickstart
1) Install Python deps: `pip install -r requirements.txt`
2) Create MySQL DB: run `database/tsp_schema.sql` in your MySQL client.
3) Configure DB URL: export `TSP_DATABASE_URL=mysql+mysqlconnector://user:pass@localhost:3306/tsp_game`
4) Run API: `uvicorn backend.main:app --reload --port 8000`
5) Open `frontend/index.html` in your browser (or serve the folder statically).

## Gameplay Flow
1) Home page: enter optional player name and continue.
2) Game page: pick cities (A–J), generate matrix, set visit order, compute your route.
3) Results page: compare against brute force, nearest neighbor, and DP; save to DB.

## Notes
- CORS is open for easy local testing.
- Score formula: `max(10, int((optimal_distance / player_distance) * 100))`.
- Matrix is always 10×10, symmetric, 50–100 weights, and zero diagonal.
