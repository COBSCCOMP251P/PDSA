"""
Traffic Simulation Routes - Standalone version without database dependency
Provides API endpoints for the Traffic Flow Max Flow game
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
from typing import List, Dict
from datetime import datetime

# Create router
router = APIRouter()

# Try to import algorithms using importlib to avoid path conflicts
try:
    import os
    import importlib.util
    
    # Get algorithms folder path
    algorithms_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'algorithms')
    
    # Load max_flow_solvers module directly from file
    solvers_spec = importlib.util.spec_from_file_location(
        "max_flow_solvers", 
        os.path.join(algorithms_path, "max_flow_solvers.py")
    )
    solvers_module = importlib.util.module_from_spec(solvers_spec)
    solvers_spec.loader.exec_module(solvers_module)
    
    # Extract functions
    edmonds_karp = solvers_module.edmonds_karp
    dinics_algorithm = solvers_module.dinics_algorithm
    create_random_graph = solvers_module.create_random_graph
    find_min_cut_nodes = solvers_module.find_min_cut_nodes
    SOURCE = solvers_module.SOURCE
    SINK = solvers_module.SINK
    
    ALGORITHMS_AVAILABLE = True
except Exception as e:
    print(f"Traffic Simulation algorithms not available: {e}")
    ALGORITHMS_AVAILABLE = False

# In-memory storage for leaderboard (no database)
leaderboard_data: List[Dict] = []

# Pydantic Models
class MaxFlowInput(BaseModel):
    player_name: str
    max_flow_guess: int

@router.get("/status")
async def get_status():
    """Get game status"""
    return {
        "status": "ok",
        "game": "Traffic Simulation",
        "algorithms_available": ALGORITHMS_AVAILABLE
    }

@router.post("/new-round")
async def run_simulation_round(data: MaxFlowInput):
    """Runs the Max Flow simulation, executes both algorithms, and returns results."""
    
    if not ALGORITHMS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Algorithms not available")
    
    player_name = data.player_name
    max_flow_guess = data.max_flow_guess
    
    # Input Validation
    if max_flow_guess < 1:
        raise HTTPException(status_code=400, detail="Max Flow guess must be at least 1.")
    
    try:
        # 1. Generate Graph
        graph_capacity, cytoscape_elements = create_random_graph()

        # 2. RUN ALGORITHM I: Edmonds-Karp Timing
        start_time_ek = time.perf_counter_ns()
        max_flow_ek, r_graph_ek = edmonds_karp(graph_capacity.copy(), SOURCE, SINK)
        end_time_ek = time.perf_counter_ns()
        runtime_ek_ns = (end_time_ek - start_time_ek)  

        # 3. RUN ALGORITHM II: Dinic's Timing
        start_time_dinic = time.perf_counter_ns()
        max_flow_dinic, r_graph_dinic = dinics_algorithm(graph_capacity.copy(), SOURCE, SINK)
        end_time_dinic = time.perf_counter_ns()
        runtime_dinic_ns = (end_time_dinic - start_time_dinic) 
        
        # 4. Find Min-Cut Nodes (S-set)
        s_side_nodes = find_min_cut_nodes(r_graph_ek, SOURCE)

        # 5. Determine Win Status
        win_status = "Win" if max_flow_guess == max_flow_ek else "Lose"
        
        # 6. Store in leaderboard if correct
        if win_status == "Win":
            leaderboard_data.append({
                "player_name": player_name,
                "runtime_ek_ms": runtime_ek_ns / 1_000_000.0,
                "runtime_dinic_ms": runtime_dinic_ns / 1_000_000.0,
                "max_flow": max_flow_ek,
                "timestamp": datetime.now().isoformat()
            })
            # Keep only top 10
            leaderboard_data.sort(key=lambda x: x["runtime_ek_ms"])
            if len(leaderboard_data) > 10:
                leaderboard_data.pop()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during simulation: {e}")

    # 7. RETURN DATA TO FRONTEND
    runtime_ek_ms_display = runtime_ek_ns / 1_000_000.0
    runtime_dinic_ms_display = runtime_dinic_ns / 1_000_000.0
    
    return {
        'maxFlowEK': max_flow_ek,
        'runtimeEK_ms': f"{runtime_ek_ms_display:.6f}",
        'maxFlowDinic': max_flow_dinic,
        'runtimeDinic_ms': f"{runtime_dinic_ms_display:.6f}",
        'elements': cytoscape_elements,
        'sSideNodes': s_side_nodes,
        'winStatus': win_status,
        'playerName': player_name,
        'playerGuess': max_flow_guess
    }

@router.get("/leaderboard")
async def get_leaderboard():
    """Fetches the top 10 fastest simulation runtimes for correct guesses."""
    return leaderboard_data

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "game": "traffic_simulation"}
