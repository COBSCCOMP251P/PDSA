"""
Traveling Salesman Game API Routes
Integrates with main PDSA backend
"""

from fastapi import APIRouter, HTTPException, status
import random
import sys
import os
from pathlib import Path

# Optional database imports
try:
    from fastapi import Depends
    from sqlalchemy.orm import Session
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Load algorithms by directly executing the Python files
game_root = Path(__file__).parent.parent
algorithms_path = game_root / "src" / "backend" / "algorithms"

try:
    # Execute the algorithm files and extract functions
    import itertools
    import time
    from typing import List, Tuple
    
    # ===== BASE FUNCTIONS (from base.py) =====
    CITIES = [chr(code) for code in range(ord("A"), ord("J") + 1)]
    
    def city_to_index(city: str) -> int:
        return CITIES.index(city)
    
    def compute_route_distance(route: List[str], matrix: List[List[float]]) -> float:
        distance = 0.0
        for current, nxt in zip(route, route[1:]):
            distance += float(matrix[city_to_index(current)][city_to_index(nxt)])
        return round(distance, 1)
    
    # ===== GENERATORS (from generators.py) =====
    def generate_distance_matrix() -> List[List[float]]:
        matrix = [[0.0 for _ in range(10)] for _ in range(10)]
        for i in range(10):
            for j in range(i + 1, 10):
                value = round(random.uniform(50, 100), 1)
                matrix[i][j] = value
                matrix[j][i] = value
        return matrix
    
    # ===== BRUTE FORCE (from brute_force.py) =====
    def brute_force_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
        start_time = time.perf_counter()
        best_route: List[str] = []
        best_distance = float("inf")
        for perm in itertools.permutations(selected_cities):
            route = [home_city, *perm, home_city]
            distance = compute_route_distance(route, matrix)
            if distance < best_distance:
                best_distance = distance
                best_route = list(route)
        elapsed = time.perf_counter() - start_time
        return best_route, round(best_distance, 1), elapsed
    
    # ===== NEAREST NEIGHBOR (from nearest_neighbor.py) =====
    def nearest_neighbor_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
        start_time = time.perf_counter()
        unvisited = set(selected_cities)
        route = [home_city]
        while unvisited:
            current = route[-1]
            current_idx = city_to_index(current)
            nearest = min(unvisited, key=lambda c: matrix[current_idx][city_to_index(c)])
            route.append(nearest)
            unvisited.remove(nearest)
        route.append(home_city)
        distance = compute_route_distance(route, matrix)
        elapsed = time.perf_counter() - start_time
        return route, round(distance, 1), elapsed
    
    # ===== DYNAMIC PROGRAMMING (from dynamic_programming.py) =====
    def dynamic_programming_tsp(home_city: str, selected_cities: List[str], matrix: List[List[float]]) -> Tuple[List[str], float, float]:
        start_time = time.perf_counter()
        n = len(selected_cities)
        if n == 0:
            return [home_city, home_city], 0.0, 0.0
        
        cities_list = [home_city] + selected_cities
        indices = [city_to_index(c) for c in cities_list]
        INF = float("inf")
        dp = [[INF] * n for _ in range(1 << n)]
        parent = [[None] * n for _ in range(1 << n)]
        
        for i in range(n):
            dp[1 << i][i] = matrix[indices[0]][indices[i + 1]]
        
        for mask in range(1 << n):
            for last in range(n):
                if not (mask & (1 << last)) or dp[mask][last] == INF:
                    continue
                for nxt in range(n):
                    if mask & (1 << nxt):
                        continue
                    new_mask = mask | (1 << nxt)
                    new_cost = dp[mask][last] + matrix[indices[last + 1]][indices[nxt + 1]]
                    if new_cost < dp[new_mask][nxt]:
                        dp[new_mask][nxt] = new_cost
                        parent[new_mask][nxt] = last
        
        full_mask = (1 << n) - 1
        best_cost = INF
        best_last = -1
        for last in range(n):
            cost = dp[full_mask][last] + matrix[indices[last + 1]][indices[0]]
            if cost < best_cost:
                best_cost = cost
                best_last = last
        
        route = [home_city]
        if best_last != -1:
            path = []
            mask = full_mask
            current = best_last
            while current is not None:
                path.append(selected_cities[current])
                prev = parent[mask][current]
                if prev is not None:
                    mask ^= (1 << current)
                current = prev
            route.extend(reversed(path))
        route.append(home_city)
        
        distance = compute_route_distance(route, matrix)
        elapsed = time.perf_counter() - start_time
        return route, round(distance, 1), elapsed
    
    # Import pydantic schemas from backend
    backend_path = game_root / "src" / "backend"
    sys.path.insert(0, str(backend_path))
    import schemas
    
    # Try to load database support (optional)
    DATABASE_AVAILABLE = False
    try:
        from fastapi import Depends
        from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Float, func, create_engine
        from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
        
        # Database configuration
        DATABASE_URL = os.getenv(
            "TSP_DATABASE_URL",
            "mysql+mysqlconnector://root:pruthuvide@localhost:3306/tsp_game"
        )
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()
        
        # Define models inline
        class GameRound(Base):
            __tablename__ = "game_rounds"
            id = Column(Integer, primary_key=True, index=True)
            player_name = Column(String(50), nullable=False)
            home_city = Column(String(1), nullable=False)
            selected_cities = Column(Text, nullable=False)
            brute_force_distance = Column(Float, nullable=False)
            nearest_neighbor_distance = Column(Float, nullable=False)
            dp_distance = Column(Float, nullable=False)
            player_distance = Column(Float, nullable=False)
            player_score = Column(Integer, nullable=False)
            timestamp = Column(DateTime, server_default=func.now())
            algorithm_times = relationship("AlgorithmTime", back_populates="game_round", cascade="all, delete-orphan")
        
        class AlgorithmTime(Base):
            __tablename__ = "algorithm_times"
            id = Column(Integer, primary_key=True, index=True)
            round_id = Column(Integer, ForeignKey("game_rounds.id", ondelete="CASCADE"), nullable=False)
            brute_force_time = Column(Float, nullable=False)
            nearest_neighbor_time = Column(Float, nullable=False)
            dp_time = Column(Float, nullable=False)
            game_round = relationship("GameRound", back_populates="algorithm_times")
        
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        DATABASE_AVAILABLE = True
        print("✅ TSP database models loaded successfully")
    except Exception as db_error:
        print(f"⚠️ Database not available: {db_error}")
        DATABASE_AVAILABLE = False
    
    ALGORITHMS_AVAILABLE = True
    print("✅ TSP algorithms loaded successfully (inline)")
except Exception as e:
    print(f"⚠️ TSP algorithms not fully available: {e}")
    import traceback
    traceback.print_exc()
    ALGORITHMS_AVAILABLE = False

# Create router
router = APIRouter()

# Endpoints
@router.get("/status")
async def get_status():
    """Check TSP game status"""
    return {
        "game": "traveling_salesman",
        "status": "operational" if ALGORITHMS_AVAILABLE else "limited",
        "algorithms_available": ALGORITHMS_AVAILABLE
    }

if ALGORITHMS_AVAILABLE:
    @router.post("/generate-matrix", response_model=schemas.MatrixResponse, status_code=status.HTTP_200_OK)
    def generate_matrix_endpoint() -> schemas.MatrixResponse:
        """Generate a symmetric distance matrix and random home city."""
        matrix = generate_distance_matrix()
        home_city = CITIES[random.randint(0, 9)]
        return schemas.MatrixResponse(home_city=home_city, distance_matrix=matrix)

    @router.post(
        "/calculate-player-route",
        response_model=schemas.CalculatePlayerRouteResponse,
        status_code=status.HTTP_200_OK,
    )
    def calculate_player_route(payload: schemas.CalculatePlayerRouteRequest) -> schemas.CalculatePlayerRouteResponse:
        """Calculate the distance of the player's chosen route."""
        route = [payload.home_city, *payload.player_order, payload.home_city]
        distance = compute_route_distance(route, payload.distance_matrix)
        return schemas.CalculatePlayerRouteResponse(route=route, distance=distance)

    @router.post("/solve-tsp", response_model=schemas.SolveTspResponse, status_code=status.HTTP_200_OK)
    def solve_tsp(payload: schemas.SolveTspRequest) -> schemas.SolveTspResponse:
        """Run brute force, nearest neighbor, and DP algorithms."""
        if not payload.selected_cities:
            raise HTTPException(status_code=400, detail="At least one city must be selected.")
        brute_route, brute_distance, brute_time = brute_force_tsp(
            payload.home_city, payload.selected_cities, payload.distance_matrix
        )
        nn_route, nn_distance, nn_time = nearest_neighbor_tsp(
            payload.home_city, payload.selected_cities, payload.distance_matrix
        )
        dp_route, dp_distance, dp_time = dynamic_programming_tsp(
            payload.home_city, payload.selected_cities, payload.distance_matrix
        )
        return schemas.SolveTspResponse(
            brute_force=schemas.AlgorithmResult(route=brute_route, distance=brute_distance, time_seconds=brute_time),
            nearest_neighbor=schemas.AlgorithmResult(route=nn_route, distance=nn_distance, time_seconds=nn_time),
            dynamic_programming=schemas.AlgorithmResult(route=dp_route, distance=dp_distance, time_seconds=dp_time),
        )

    if DATABASE_AVAILABLE:
        @router.post("/save-result", response_model=schemas.SaveResultResponse, status_code=status.HTTP_201_CREATED)
        def save_result(payload: schemas.SaveResultRequest, db: Session = Depends(get_db)) -> schemas.SaveResultResponse:
            """Persist a completed game round and its timings."""
            try:
                game_round = GameRound(
                    player_name=payload.player_name,
                    home_city=payload.home_city,
                    selected_cities=",".join(payload.selected_cities),
                    brute_force_distance=payload.brute_force_distance,
                    nearest_neighbor_distance=payload.nearest_neighbor_distance,
                    dp_distance=payload.dp_distance,
                    player_distance=payload.player_distance,
                    player_score=payload.score,
                )
                db.add(game_round)
                db.flush()

                timing = AlgorithmTime(
                    round_id=game_round.id,
                    brute_force_time=payload.algorithm_times.brute_force_time,
                    nearest_neighbor_time=payload.algorithm_times.nearest_neighbor_time,
                    dp_time=payload.algorithm_times.dp_time,
                )
                db.add(timing)
                db.commit()
            except Exception as exc:
                db.rollback()
                raise HTTPException(status_code=500, detail=f"Failed to save result: {exc}")
            return schemas.SaveResultResponse(message="Result saved successfully.")
    else:
        @router.post("/save-result")
        def save_result():
            """Database not available - results not saved"""
            return {"message": "Database not configured - result not saved"}

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "game": "traveling_salesman",
        "algorithms_available": ALGORITHMS_AVAILABLE
    }
