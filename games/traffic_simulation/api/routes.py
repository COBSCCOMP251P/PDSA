"""
Traffic Simulation Routes - Database-connected version
Provides API endpoints for the Traffic Flow Max Flow game with MySQL integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import json
from typing import List, Dict
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create router
router = APIRouter()

# Database configuration for traffic_simulation_game
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'pruthuvide'),
    'database': 'traffic_simulation_game'  # Specific database for traffic simulation
}

# Database helper functions
def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e}")

def ensure_player(player_name: str, conn):
    """Ensure player exists in Players table, create if not"""
    cursor = conn.cursor()
    try:
        # Check if player exists
        cursor.execute("SELECT player_id FROM Players WHERE player_name = %s", (player_name,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        
        # Create new player
        cursor.execute(
            "INSERT INTO Players (player_name, email) VALUES (%s, %s)",
            (player_name, f"{player_name.lower().replace(' ', '')}@traffic.game")
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()

def create_game_session(player_id: int, conn):
    """Create a new game session"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO GameSessions (player_id, status) VALUES (%s, 'active')",
            (player_id,)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()

def save_traffic_result(session_id, player_id, player_name, player_guess, actual_flow, 
                       win_status, runtime_ek_ns, max_flow_dinic, runtime_dinic_ns, 
                       graph_data, conn):
    """Save traffic flow result to database"""
    cursor = conn.cursor()
    try:
        # Convert nanoseconds to milliseconds
        runtime_ek_ms = runtime_ek_ns / 1_000_000.0
        runtime_dinic_ms = runtime_dinic_ns / 1_000_000.0 if runtime_dinic_ns else None
        
        cursor.execute("""
            INSERT INTO TrafficFlowResults (
                session_id, player_id, player_name, player_answer, max_flow_guess,
                correct_answer, max_flow_actual, is_correct, win_status, algorithm_type,
                runtime_ek_ms, max_flow_dinic, runtime_dinic_ms, network_snapshot
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            session_id, player_id, player_name, player_guess, player_guess,
            actual_flow, actual_flow, player_guess == actual_flow, win_status,
            'edmonds_karp', runtime_ek_ms, max_flow_dinic, runtime_dinic_ms,
            json.dumps(graph_data)
        ))
        conn.commit()
        
        # Update session status
        cursor.execute(
            "UPDATE GameSessions SET status = 'completed', completed_at = NOW() WHERE session_id = %s",
            (session_id,)
        )
        conn.commit()
        
        return cursor.lastrowid
    finally:
        cursor.close()

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
    convert_cytoscape_to_capacity_matrix = solvers_module.convert_cytoscape_to_capacity_matrix
    SOURCE = solvers_module.SOURCE
    SINK = solvers_module.SINK
    
    ALGORITHMS_AVAILABLE = True
except Exception as e:
    print(f"Traffic Simulation algorithms not available: {e}")
    ALGORITHMS_AVAILABLE = False

# Pydantic Models
class MaxFlowInput(BaseModel):
    player_name: str
    max_flow_guess: int

class GraphInput(BaseModel):
    player_name: str
    max_flow_guess: int
    graph_elements: List

@router.get("/status")
async def get_status():
    """Get game status"""
    return {
        "status": "ok",
        "game": "Traffic Simulation",
        "algorithms_available": ALGORITHMS_AVAILABLE
    }

@router.get("/generate-graph")
async def generate_graph():
    """Generate a new random graph for the game"""
    if not ALGORITHMS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Algorithms not available")
    
    try:
        # Generate a new random graph
        graph_capacity, cytoscape_elements = create_random_graph()
        
        return {
            'elements': cytoscape_elements,
            'graph_capacity': graph_capacity
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating graph: {e}")

@router.post("/run-simulation")
async def run_simulation(data: GraphInput):
    """Runs the Max Flow simulation using a pre-generated graph."""
    
    if not ALGORITHMS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Algorithms not available")
    
    player_name = data.player_name
    max_flow_guess = data.max_flow_guess
    graph_elements = data.graph_elements
    
    # Input Validation
    if max_flow_guess < 1:
        raise HTTPException(status_code=400, detail="Max Flow guess must be at least 1.")
    
    try:
        # Convert Cytoscape elements to capacity matrix
        graph_capacity = convert_cytoscape_to_capacity_matrix(graph_elements)
        
        # Run Edmonds-Karp Algorithm
        start_time_ek = time.perf_counter_ns()
        max_flow_ek, r_graph_ek = edmonds_karp(graph_capacity.copy(), SOURCE, SINK)
        end_time_ek = time.perf_counter_ns()
        runtime_ek_ns = (end_time_ek - start_time_ek)
        
        # Run Dinic's Algorithm
        start_time_dinic = time.perf_counter_ns()
        max_flow_dinic, r_graph_dinic = dinics_algorithm(graph_capacity.copy(), SOURCE, SINK)
        end_time_dinic = time.perf_counter_ns()
        runtime_dinic_ns = (end_time_dinic - start_time_dinic)
        
        # Find Min-Cut Nodes
        s_side_nodes = find_min_cut_nodes(r_graph_ek, SOURCE)
        
        # Determine Win Status
        win_status = "Win" if max_flow_guess == max_flow_ek else "Loss"
        
        # Try to save to database (optional)
        try:
            conn = get_db_connection()
            try:
                player_id = ensure_player(player_name, conn)
                session_id = create_game_session(player_id, conn)
                save_traffic_result(
                    session_id=session_id,
                    player_id=player_id,
                    player_name=player_name,
                    player_guess=max_flow_guess,
                    actual_flow=max_flow_ek,
                    win_status=win_status,
                    runtime_ek_ns=runtime_ek_ns,
                    max_flow_dinic=max_flow_dinic,
                    runtime_dinic_ns=runtime_dinic_ns,
                    graph_data=graph_capacity,
                    conn=conn
                )
            finally:
                conn.close()
        except Exception as db_error:
            print(f"Database save error (continuing without save): {db_error}")
        
        # Return results
        runtime_ek_ms_display = runtime_ek_ns / 1_000_000.0
        runtime_dinic_ms_display = runtime_dinic_ns / 1_000_000.0
        
        return {
            'maxFlowEK': max_flow_ek,
            'runtimeEK_ms': f"{runtime_ek_ms_display:.6f}",
            'maxFlowDinic': max_flow_dinic,
            'runtimeDinic_ms': f"{runtime_dinic_ms_display:.6f}",
            'sSideNodes': s_side_nodes,
            'winStatus': win_status,
            'playerName': player_name,
            'playerGuess': max_flow_guess
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during simulation: {e}")

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
        win_status = "Win" if max_flow_guess == max_flow_ek else "Loss"
        
        # 6. Save to Database
        try:
            conn = get_db_connection()
            try:
                # Ensure player exists
                player_id = ensure_player(player_name, conn)
                
                # Create game session
                session_id = create_game_session(player_id, conn)
                
                # Save game result
                save_traffic_result(
                    session_id=session_id,
                    player_id=player_id,
                    player_name=player_name,
                    player_guess=max_flow_guess,
                    actual_flow=max_flow_ek,
                    win_status=win_status,
                    runtime_ek_ns=runtime_ek_ns,
                    max_flow_dinic=max_flow_dinic,
                    runtime_dinic_ns=runtime_dinic_ns,
                    graph_data=graph_capacity,
                    conn=conn
                )
            finally:
                conn.close()
        except Exception as db_error:
            print(f"Database save error (continuing without save): {db_error}")
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
    """Fetches the top 10 fastest simulation runtimes for correct guesses (Win status)."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT 
                    player_name,
                    runtime_ek_ms,
                    runtime_dinic_ms,
                    max_flow_actual as max_flow,
                    submitted_at as timestamp
                FROM TrafficFlowResults
                WHERE win_status = 'Win'
                ORDER BY runtime_ek_ms ASC
                LIMIT 10
            """)
            results = cursor.fetchall()
            
            # Convert datetime to string and add runtime_ms for frontend
            for result in results:
                if result['timestamp']:
                    result['timestamp'] = result['timestamp'].isoformat()
                # Add runtime_ms for frontend compatibility
                result['runtime_ms'] = result.get('runtime_ek_ms', 0)
            
            return results if results else []
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Leaderboard fetch error: {e}")
        # Return sample data when database is not available
        return [
            {"player_name": "Sample Pilot", "runtime_ms": 0.42, "runtime_ek_ms": 0.42, "runtime_dinic_ms": 0.35, "max_flow": 45, "timestamp": "2024-12-14T10:30:00"},
            {"player_name": "Demo User", "runtime_ms": 0.48, "runtime_ek_ms": 0.48, "runtime_dinic_ms": 0.40, "max_flow": 42, "timestamp": "2024-12-14T09:15:00"}
        ]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "game": "traffic_simulation", "database": "traffic_simulation_game"}
