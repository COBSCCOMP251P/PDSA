from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import json
import mysql.connector

# NOTE: Adjusted imports to reflect the consolidated database logging function:
# We are replacing log_game_round and log_performance_data with log_traffic_flow_result.

# For Algorithms: (Path: PDSA/games/traffic_simulation/algorithms/...)
from ..algorithms.max_flow_solvers import (
    edmonds_karp, dinics_algorithm, create_random_graph, 
    SOURCE, SINK, find_min_cut_nodes
)

# For Database Functions: (Path: PDSA/shared/database/connection.py)
from shared.database.connection import log_traffic_flow_result, get_top_leaderboard_scores

# Initialize the FastAPI router for this game
router = APIRouter()

# Pydantic Schema for Input Validation
class MaxFlowInput(BaseModel):
    player_name: str
    max_flow_guess: int

@router.post("/new-round")
async def run_simulation_round_fastapi(data: MaxFlowInput):
    """Runs the Max Flow simulation, executes both algorithms, logs performance, 
    and returns data for the Min-Cut visualization."""
    
    player_name = data.player_name
    max_flow_guess = data.max_flow_guess
    
    # Input Validation
    if max_flow_guess < 1:
        raise HTTPException(status_code=400, detail="Max Flow guess must be at least 1.")
    
    try:
        # 1. Generate Graph
        graph_capacity, cytoscape_elements = create_random_graph()

        # 2. RUN ALGORITHM I: Edmonds-Karp Timing (using nanoseconds)
        start_time_ek = time.perf_counter_ns()  # Start Time
        max_flow_ek, r_graph_ek = edmonds_karp(graph_capacity.copy(), SOURCE, SINK)
        end_time_ek = time.perf_counter_ns()    # End Time
        runtime_ek_ns = (end_time_ek - start_time_ek)  

        # 3. RUN ALGORITHM II: Dinic's Timing
        start_time_dinic = time.perf_counter_ns()    # Start Time
        max_flow_dinic, r_graph_dinic = dinics_algorithm(graph_capacity.copy(), SOURCE, SINK)
        end_time_dinic = time.perf_counter_ns()     # End Time
        runtime_dinic_ns = (end_time_dinic - start_time_dinic) 
        
        # 4. Find Min-Cut Nodes (S-set)
        s_side_nodes = find_min_cut_nodes(r_graph_ek, SOURCE)

        # 5. LOG RESULTS to Database (Using the consolidated function)
        # We pass all necessary data to log_traffic_flow_result, which handles 
        # session creation, result logging, and win status determination.
        result_id, win_status = log_traffic_flow_result(
            player_name=player_name, 
            max_flow_guess=max_flow_guess, 
            max_flow_actual=max_flow_ek, 
            runtime_ek_ns=runtime_ek_ns,
            max_flow_dinic=max_flow_dinic,
            runtime_dinic_ns=runtime_dinic_ns,
            graph_capacity=graph_capacity
        )
        
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Database service unavailable: {e}")
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database logging failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error during simulation: {e}")

    # 6. RETURN DATA TO FRONTEND (Convert to MS for Display)
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
    """Fetches the top 10 fastest simulation runtimes for correct guesses (Win status)."""
    try:
        # get_top_leaderboard_scores queries the TrafficFlowResults table/view.
        leaderboard_data = get_top_leaderboard_scores(limit=10)
        
        return leaderboard_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error fetching leaderboard: {e}")
    