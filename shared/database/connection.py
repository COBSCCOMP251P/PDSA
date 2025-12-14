"""
Database Connection Module
Provides MySQL connection functionality for all games
"""

import mysql.connector
from mysql.connector import Error
import logging
from ..backend.config import DATABASE_CONFIG
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DATABASE_CONFIG)
            if self.connection.is_connected():
                logger.info("✅ Database connection successful")
                return True
        except Error as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("🔌 Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
                
            cursor.close()
            return result
            
        except Error as e:
            logger.error(f"Query execution failed: {e}")
            return None
    
    def execute_many(self, query, params_list):
        """Execute query with multiple parameter sets"""
        try:
            cursor = self.connection.cursor()
            cursor.executemany(query, params_list)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logger.error(f"Batch execution failed: {e}")
            return False

# Global database instance
db = DatabaseConnection()

def get_db_connection():
    """Get database connection instance"""
    if not db.connection or not db.connection.is_connected():
        db.connect()
    return db

def init_database():
    """Initialize database connection and verify tables"""
    if db.connect():
        # Test query
        result = db.execute_query("SELECT 1 as test")
        if result:
            logger.info("📊 Database initialization successful")
            return True
    return False

# --- TRAFFIC SIMULATION SPECIFIC FUNCTIONS ---

def get_player_id_and_insert_if_missing(player_name: str) -> int:
    """Finds player ID by name or creates a new entry in the Players table."""
    conn = get_db_connection()
    
    # 1. Check if player exists
    query_select = "SELECT player_id FROM Players WHERE player_name = %s"
    result = conn.execute_query(query_select, (player_name,))
    
    if result:
        return result[0]['player_id']
        
    # 2. If not, insert new player
    query_insert = "INSERT INTO Players (player_name) VALUES (%s)"
    player_id = conn.execute_query(query_insert, (player_name,))
    
    if not player_id:
        raise mysql.connector.Error("Failed to insert new player.")
    
    return player_id

def create_new_game_session(player_id: int) -> int:
    """Creates a new entry in the shared GameSessions table for traffic_simulation."""
    conn = get_db_connection()
    
    query = """
    INSERT INTO GameSessions (player_id, game_type, status)
    VALUES (%s, 'traffic_simulation', 'active')
    """
    session_id = conn.execute_query(query, (player_id,))
    
    if not session_id:
        raise mysql.connector.Error("Failed to create new game session.")
    
    return session_id

def log_traffic_flow_result(
    player_name: str,
    max_flow_guess: int,
    max_flow_actual: int,
    runtime_ek_ns: int,
    max_flow_dinic: int,
    runtime_dinic_ns: int,
    graph_capacity: dict
) -> tuple[int, str]:
    """
    Logs all simulation data into the single TrafficFlowResults table.
    
    Returns: (result_id, win_status)
    """
    
    # 1. Pre-calculations and Conversions
    player_id = get_player_id_and_insert_if_missing(player_name)
    session_id = create_new_game_session(player_id)
    
    # Determine Win Status
    if max_flow_guess == max_flow_actual:
        win_status = 'Win'
        is_correct = True
    # elif abs(max_flow_guess - max_flow_actual) <= 1: # Example: allow a small tolerance for "Draw"
    #     win_status = 'Draw'
    #     is_correct = False 
    else:
        win_status = 'Loss'
        is_correct = False
        
    # Convert nanoseconds to milliseconds (DECIMAL(10,3) in DB)
    runtime_ek_ms = runtime_ek_ns / 1_000_000.0
    runtime_dinic_ms = runtime_dinic_ns / 1_000_000.0
    
    # JSON serialization
    network_snapshot_json = json.dumps(graph_capacity)
    flow_paths_json = json.dumps([]) # <--- NEW: Placeholder for the 'flow_paths' column
    
    conn = get_db_connection()
    
    # NOTE: INSERT query now includes 'flow_paths'
    query = """
    INSERT INTO TrafficFlowResults (
        session_id, player_id, player_name, player_answer, max_flow_guess, correct_answer, 
        max_flow_actual, is_correct, win_status, algorithm_type,
        runtime_ek_ms, max_flow_dinic, runtime_dinic_ms, network_snapshot, flow_paths
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s,
        %s, %s, %s, %s, %s
    )
    """
    params = (
        session_id,
        player_id, # <-- player_id is needed for GameSessions and for this insert if schema requires it
        player_name, 
        max_flow_guess,  # player_answer
        max_flow_guess, # max_flow_guess
        max_flow_actual, # correct_answer
        max_flow_actual, # max_flow_actual
        is_correct,
        win_status,
        'Edmonds Karp / Dinics',   # algorithm_type is set statically to 'edmonds_karp' for the performance benchmark
        runtime_ek_ms,
        max_flow_dinic,
        runtime_dinic_ms,
        network_snapshot_json, # Stored as JSON string
        flow_paths_json            #Placeholder value for flow_paths
    )
    
    try:
        result_id = conn.execute_query(query, params)
        
        # Mark session as completed
        conn.execute_query("UPDATE GameSessions SET completed_at = NOW(), status = 'completed' WHERE session_id = %s", (session_id,))
        
        if not result_id:
            raise mysql.connector.Error("Failed to log traffic flow result: No rows inserted.")
            
        return result_id, win_status
    except mysql.connector.Error as e:
        logger.error(f"FATAL DB INSERT ERROR: {e}")
        # The exception will be caught by the FastAPI router and converted to a 500 error.
        raise # Re-raise the error to ensure the transaction is rolled back by the database.

def get_top_leaderboard_scores(limit: int = 10) -> list[dict]:
    """
    Fetches leaderboard data (top N fastest runtimes from successful rounds).
    The fastest runtime (smallest runtime_ek_ms) for a 'Win' is used for ranking.
    """
    conn = get_db_connection()
    
    query = f"""
    SELECT
        tfr.player_name,
        tfr.runtime_ek_ms
    FROM TrafficFlowResults tfr
    WHERE tfr.win_status = 'Win'
    ORDER BY tfr.runtime_ek_ms ASC
    LIMIT %s
    """
    
    # Note: execute_query returns results as a list of dictionaries if successful
    leaderboard_data = conn.execute_query(query, (limit,))
    
    # Rename column to match frontend expectation (runtime_ms)
    formatted_data = []
    if leaderboard_data:
        for row in leaderboard_data:
            formatted_data.append({
                'player_name': row['player_name'],
                'runtime_ms': row['runtime_ek_ms'] 
            })
            
    return formatted_data

if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    if init_database():
        print("✅ Database connection test passed")
        db.disconnect()
    else:
        print("❌ Database connection test failed")
        print("Make sure MySQL is running and credentials are correct in .env file")