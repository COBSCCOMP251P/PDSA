# Traveling Salesman API

The FastAPI backend is implemented in `backend/main.py`. Key routes:
- `POST /generate-matrix` — random matrix + home city.
- `POST /calculate-player-route` — distance for a player-provided order.
- `POST /solve-tsp` — brute force, nearest neighbor, and DP outputs with timings.
- `POST /save-result` — store results in MySQL (`tsp_game` DB).
- `GET /health` — simple readiness check.

Enable the API with: `uvicorn backend.main:app --reload --port 8000` after installing requirements and configuring `TSP_DATABASE_URL`.
