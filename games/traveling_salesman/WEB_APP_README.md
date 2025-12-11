# TSP Game Web App (Vanilla + FastAPI)

Student-friendly Traveling Salesman Problem game with a Tailwind-powered frontend and FastAPI backend.

## Run the Backend
1. `pip install -r requirements.txt`
2. Create MySQL DB using `database/tsp_schema.sql`.
3. Set `TSP_DATABASE_URL` (e.g. `mysql+mysqlconnector://user:pass@localhost:3306/tsp_game`).
4. Start API: `uvicorn backend.main:app --reload --port 8000`

## Use the Frontend
- Open `frontend/index.html` directly or serve the `frontend/` folder.
- Flow: Home → Game (generate matrix, pick cities, arrange order) → Results → Save.

## Key Endpoints
- `POST /generate-matrix` — random symmetric matrix + home city.
- `POST /calculate-player-route` — distance for player order.
- `POST /solve-tsp` — brute force, nearest neighbor, DP results + times.
- `POST /save-result` — persist round and algorithm times.

## Notes
- Matrix: 10×10, distances 50–100, symmetric, zero diagonal.
- Score: `max(10, int((optimal_distance / player_distance) * 100))`.
- CORS enabled for easy local testing.

