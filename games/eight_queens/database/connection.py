import mysql.connector
from mysql.connector import pooling, Error
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration management"""
    
    def __init__(self):
        """Initialize database configuration from environment variables"""
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.database = os.getenv('DB_NAME', 'eight_queens_game')
        self.username = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.pool_name = 'eight_queens_pool'
        self.pool_size = int(os.getenv('DB_POOL_SIZE', 5))
        
    def get_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary"""
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.username,
            'password': self.password,
            'pool_name': self.pool_name,
            'pool_size': self.pool_size,
            'autocommit': True,
            'use_unicode': True,
            'charset': 'utf8mb4'
        }

class DatabaseManager:
    """
    Manages database connections and operations for Eight Queens Game
    Implements connection pooling for better performance
    """
    
    def __init__(self):
        """Initialize database manager with connection pooling"""
        self.config = DatabaseConfig()
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize MySQL connection pool"""
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                **self.config.get_config()
            )
            logger.info(f"Database connection pool initialized successfully")
            
            # Test connection
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
                
        except Error as e:
            logger.error(f"Error initializing database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting database connections from pool
        Automatically handles connection cleanup
        """
        connection = None
        try:
            connection = self.connection_pool.get_connection()
            yield connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Dict]:
        """
        Execute SELECT query and return results as list of dictionaries
        
        Args:
            query: SQL SELECT query
            params: Query parameters
            
        Returns:
            List of dictionaries representing rows
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                cursor.close()
                return results
        except Error as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute INSERT, UPDATE, or DELETE query
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, params or ())
                affected_rows = cursor.rowcount
                connection.commit()
                cursor.close()
                return affected_rows
        except Error as e:
            logger.error(f"Update execution error: {e}")
            raise
    
    def execute_procedure(self, procedure_name: str, params: Tuple = ()) -> List[Dict]:
        """
        Execute stored procedure and return results
        
        Args:
            procedure_name: Name of stored procedure
            params: Procedure parameters
            
        Returns:
            List of dictionaries representing results
        """
        try:
            with self.get_connection() as connection:
                cursor = connection.cursor(dictionary=True)
                cursor.callproc(procedure_name, params)
                
                # Get all result sets
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                
                connection.commit()
                cursor.close()
                return results
        except Error as e:
            logger.error(f"Procedure execution error: {e}")
            raise

class EightQueensDatabase:
    """
    High-level database operations for Eight Queens Game
    Implements all coursework requirements
    """
    
    def __init__(self):
        """Initialize Eight Queens database operations"""
        self.db = DatabaseManager()
    
    # =============================================
    # PLAYER MANAGEMENT
    # =============================================
    
    def register_player(self, name: str, email: str = None) -> Dict[str, Any]:
        """
        Register new player in database
        
        Args:
            name: Player name
            email: Player email (optional)
            
        Returns:
            Dictionary with player_id and status
        """
        try:
            results = self.db.execute_procedure('RegisterPlayer', (name, email))
            return results[0] if results else {'player_id': 0, 'status': 'ERROR'}
        except Exception as e:
            logger.error(f"Player registration error: {e}")
            return {'player_id': 0, 'status': 'ERROR', 'error': str(e)}
    
    def get_player_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get player information by name"""
        query = "SELECT * FROM players WHERE name = %s"
        results = self.db.execute_query(query, (name,))
        return results[0] if results else None
    
    def get_player_statistics(self, player_id: int) -> Dict[str, Any]:
        """Get comprehensive player statistics"""
        query = "SELECT * FROM player_statistics WHERE id = %s"
        results = self.db.execute_query(query, (player_id,))
        return results[0] if results else {}
    
    # =============================================
    # SOLUTION MANAGEMENT
    # =============================================
    
    def submit_solution(self, player_id: int, solution: List[int], 
                       algorithm_type: str, execution_time_ms: float) -> Dict[str, Any]:
        """
        Submit player solution and check for duplicates
        Implements university requirement for duplicate prevention
        
        Args:
            player_id: Player ID
            solution: Solution array [0,4,7,5,2,6,1,3]
            algorithm_type: 'sequential' or 'threaded'
            execution_time_ms: Algorithm execution time
            
        Returns:
            Dictionary with submission status
        """
        try:
            # Convert solution to string format
            solution_string = ''.join(map(str, solution))
            
            results = self.db.execute_procedure(
                'SubmitSolution',
                (player_id, solution_string, algorithm_type, execution_time_ms)
            )
            
            return results[0] if results else {'status': 'ERROR'}
            
        except Exception as e:
            logger.error(f"Solution submission error: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def get_discovered_solutions(self) -> List[Dict[str, Any]]:
        """Get all discovered solutions with discovery information"""
        query = "SELECT * FROM solution_discovery_status ORDER BY solution_number"
        return self.db.execute_query(query)
    
    def get_undiscovered_solutions_count(self) -> int:
        """Get count of undiscovered solutions"""
        query = """
        SELECT COUNT(*) as count 
        FROM solutions s 
        LEFT JOIN discovered_solutions ds ON s.id = ds.solution_id 
        WHERE ds.id IS NULL
        """
        results = self.db.execute_query(query)
        return results[0]['count'] if results else 92
    
    def check_and_reset_discoveries(self) -> Dict[str, Any]:
        """
        Check if all solutions discovered and reset if needed
        Implements university requirement for solution reset
        """
        try:
            results = self.db.execute_procedure('CheckAndResetDiscoveries')
            return results[0] if results else {'status': 'ERROR'}
        except Exception as e:
            logger.error(f"Discovery reset check error: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    # =============================================
    # GAME SESSION MANAGEMENT
    # =============================================
    
    def start_game_session(self, player_id: int, algorithm_type: str) -> int:
        """
        Start new game session
        
        Args:
            player_id: Player ID
            algorithm_type: 'sequential' or 'threaded'
            
        Returns:
            Session ID
        """
        query = """
        INSERT INTO game_sessions (player_id, algorithm_type, execution_time_ms)
        VALUES (%s, %s, 0)
        """
        
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute(query, (player_id, algorithm_type))
                session_id = cursor.lastrowid
                connection.commit()
                cursor.close()
                return session_id
        except Exception as e:
            logger.error(f"Session start error: {e}")
            return 0
    
    def end_game_session(self, session_id: int, execution_time_ms: float,
                        solutions_found: int = 0, solutions_attempted: int = 0,
                        duplicate_attempts: int = 0, thread_count: int = None) -> bool:
        """
        End game session with performance data
        Implements university requirement for timing data storage
        """
        query = """
        UPDATE game_sessions SET
            session_end = NOW(),
            execution_time_ms = %s,
            total_solutions_found = %s,
            solutions_attempted = %s,
            duplicate_attempts = %s,
            thread_count = %s,
            game_completed = TRUE
        WHERE id = %s
        """
        
        try:
            affected = self.db.execute_update(
                query,
                (execution_time_ms, solutions_found, solutions_attempted,
                 duplicate_attempts, thread_count, session_id)
            )
            return affected > 0
        except Exception as e:
            logger.error(f"Session end error: {e}")
            return False
    
    # =============================================
    # PERFORMANCE ANALYSIS
    # =============================================
    
    def get_algorithm_performance(self) -> List[Dict[str, Any]]:
        """
        Get performance comparison between sequential and threaded algorithms
        Required for university coursework analysis
        """
        query = "SELECT * FROM algorithm_performance"
        return self.db.execute_query(query)
    
    def get_player_performance_history(self, player_id: int, limit: int = 15) -> List[Dict[str, Any]]:
        """
        Get player's performance history for last N sessions
        Required for coursework: 15 game rounds analysis
        """
        query = """
        SELECT 
            algorithm_type,
            execution_time_ms,
            total_solutions_found,
            thread_count,
            session_start,
            game_completed
        FROM game_sessions 
        WHERE player_id = %s 
        ORDER BY session_start DESC 
        LIMIT %s
        """
        return self.db.execute_query(query, (player_id, limit))
    
    def get_performance_charts_data(self, player_id: int = None) -> Dict[str, Any]:
        """
        Get data for performance charts required in coursework
        Returns data suitable for creating comparison charts
        """
        base_query = """
        SELECT 
            algorithm_type,
            execution_time_ms,
            total_solutions_found,
            session_start,
            thread_count
        FROM game_sessions 
        WHERE game_completed = TRUE
        """
        
        params = ()
        if player_id:
            base_query += " AND player_id = %s"
            params = (player_id,)
        
        base_query += " ORDER BY session_start DESC LIMIT 30"
        
        sessions = self.db.execute_query(base_query, params)
        
        # Organize data for charting
        sequential_times = []
        threaded_times = []
        
        for session in sessions:
            if session['algorithm_type'] == 'sequential':
                sequential_times.append(session['execution_time_ms'])
            else:
                threaded_times.append(session['execution_time_ms'])
        
        return {
            'sequential_times': sequential_times,
            'threaded_times': threaded_times,
            'all_sessions': sessions
        }
    
    # =============================================
    # DATABASE UTILITIES
    # =============================================
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.db.get_connection() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring"""
        queries = {
            'total_players': "SELECT COUNT(*) as count FROM players",
            'total_sessions': "SELECT COUNT(*) as count FROM game_sessions",
            'discovered_solutions': "SELECT COUNT(*) as count FROM discovered_solutions",
            'total_solutions': "SELECT COUNT(*) as count FROM solutions"
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                result = self.db.execute_query(query)
                stats[key] = result[0]['count'] if result else 0
            except Exception as e:
                logger.error(f"Error getting {key}: {e}")
                stats[key] = 0
        
        return stats

# Global database instance
db_instance = None

def get_database() -> EightQueensDatabase:
    """
    Get global database instance (singleton pattern)
    Ensures single database connection pool across application
    """
    global db_instance
    if db_instance is None:
        db_instance = EightQueensDatabase()
    return db_instance

def initialize_database():
    """Initialize database connection on application startup"""
    global db_instance
    db_instance = EightQueensDatabase()
    logger.info("Database initialized successfully")
    return db_instance