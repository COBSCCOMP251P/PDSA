"""
Database Models and Utilities for Snake and Ladder Game
"""

from typing import Dict, List, Optional, Tuple
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime


class DatabaseConnection:
    """
    Database connection manager for Snake and Ladder game.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize database connection.
        
        Args:
            config: Database configuration dictionary
        """
        self.config = config
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            raise Exception(f"Database connection error: {str(e)}")
    
    def disconnect(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


class SnakeLadderDB:
    """
    Database operations for Snake and Ladder game.
    """
    
    def __init__(self, db_config: Dict):
        """
        Initialize database handler.
        
        Args:
            db_config: Database configuration dictionary
        """
        self.db_config = db_config
    
    def create_or_get_player(self, player_name: str, email: Optional[str] = None) -> int:
        """
        Create a new player or get existing player ID.
        
        Args:
            player_name: Player's name
            email: Player's email (optional)
            
        Returns:
            Player ID
        """
        with DatabaseConnection(self.db_config) as db:
            # Check if player exists
            if email:
                query = "SELECT player_id FROM Players WHERE email = %s"
                db.cursor.execute(query, (email,))
            else:
                query = "SELECT player_id FROM Players WHERE player_name = %s ORDER BY created_at DESC LIMIT 1"
                db.cursor.execute(query, (player_name,))
            
            result = db.cursor.fetchone()
            
            if result:
                return result['player_id']
            
            # Create new player
            insert_query = "INSERT INTO Players (player_name, email) VALUES (%s, %s)"
            db.cursor.execute(insert_query, (player_name, email))
            db.connection.commit()
            
            return db.cursor.lastrowid
    
    def create_game_session(self, player_id: int) -> int:
        """
        Create a new game session.
        
        Args:
            player_id: Player's ID
            
        Returns:
            Session ID
        """
        with DatabaseConnection(self.db_config) as db:
            query = """
                INSERT INTO GameSessions (player_id, game_type, status)
                VALUES (%s, 'snake_ladder', 'active')
            """
            db.cursor.execute(query, (player_id,))
            db.connection.commit()
            
            return db.cursor.lastrowid
    
    def complete_game_session(self, session_id: int):
        """
        Mark a game session as completed.
        
        Args:
            session_id: Session ID
        """
        with DatabaseConnection(self.db_config) as db:
            query = """
                UPDATE GameSessions 
                SET status = 'completed', completed_at = NOW()
                WHERE session_id = %s
            """
            db.cursor.execute(query, (session_id,))
            db.connection.commit()
    
    def save_game_result(self, session_id: int, player_name: str, board_size: int,
                        algorithm_type: str, player_answer: int, correct_answer: int,
                        is_correct: bool, execution_time_ms: float, 
                        board_config: Dict) -> int:
        """
        Save game result to database.
        
        Args:
            session_id: Game session ID
            player_name: Player's name
            board_size: Size of the board
            algorithm_type: Algorithm used ('bfs' or 'dfs')
            player_answer: Player's submitted answer
            correct_answer: Correct answer
            is_correct: Whether player's answer is correct
            execution_time_ms: Algorithm execution time in milliseconds
            board_config: Board configuration as dictionary
            
        Returns:
            Result ID
        """
        with DatabaseConnection(self.db_config) as db:
            query = """
                INSERT INTO SnakeLadderResults 
                (session_id, player_name, board_size, algorithm_type, player_answer, 
                 correct_answer, is_correct, execution_time_ms, board_config)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            board_json = json.dumps(board_config)
            
            db.cursor.execute(query, (
                session_id, player_name, board_size, algorithm_type,
                player_answer, correct_answer, is_correct, execution_time_ms,
                board_json
            ))
            db.connection.commit()
            
            return db.cursor.lastrowid
    
    def save_algorithm_performance(self, session_id: int, board_size: int,
                                   algorithm_type: str, execution_time_ms: float,
                                   minimum_moves: int, board_config: Dict) -> int:
        """
        Save algorithm performance metrics.
        
        Args:
            session_id: Game session ID
            board_size: Size of the board
            algorithm_type: Algorithm used ('bfs' or 'dfs')
            execution_time_ms: Algorithm execution time in milliseconds
            minimum_moves: Minimum number of moves found
            board_config: Board configuration as dictionary
            
        Returns:
            Performance record ID
        """
        with DatabaseConnection(self.db_config) as db:
            query = """
                INSERT INTO SnakeLadderAlgorithmPerformance
                (session_id, board_size, algorithm_type, execution_time_ms, 
                 minimum_moves, board_config)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            board_json = json.dumps(board_config)
            
            db.cursor.execute(query, (
                session_id, board_size, algorithm_type, execution_time_ms,
                minimum_moves, board_json
            ))
            db.connection.commit()
            
            return db.cursor.lastrowid
    
    def get_player_stats(self, player_name: str) -> Dict:
        """
        Get player statistics.
        
        Args:
            player_name: Player's name
            
        Returns:
            Dictionary containing player statistics
        """
        with DatabaseConnection(self.db_config) as db:
            query = """
                SELECT 
                    COUNT(*) as total_games,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                    AVG(execution_time_ms) as avg_execution_time,
                    MIN(board_size) as min_board_size,
                    MAX(board_size) as max_board_size
                FROM SnakeLadderResults
                WHERE player_name = %s
            """
            
            db.cursor.execute(query, (player_name,))
            result = db.cursor.fetchone()
            
            if result and result['total_games'] > 0:
                return {
                    'total_games': result['total_games'],
                    'correct_answers': result['correct_answers'],
                    'accuracy': round((result['correct_answers'] / result['total_games']) * 100, 2),
                    'avg_execution_time': round(float(result['avg_execution_time']) if result['avg_execution_time'] else 0.0, 3),
                    'min_board_size': result['min_board_size'],
                    'max_board_size': result['max_board_size']
                }
            
            return {
                'total_games': 0,
                'correct_answers': 0,
                'accuracy': 0.0,
                'avg_execution_time': 0.0,
                'min_board_size': 0,
                'max_board_size': 0
            }
    
    def get_algorithm_comparison(self, board_size: Optional[int] = None) -> Dict:
        """
        Compare algorithm performance.
        
        Args:
            board_size: Optional board size to filter by
            
        Returns:
            Dictionary containing algorithm comparison data
        """
        with DatabaseConnection(self.db_config) as db:
            if board_size:
                query = """
                    SELECT 
                        algorithm_type,
                        COUNT(*) as executions,
                        AVG(execution_time_ms) as avg_time,
                        MIN(execution_time_ms) as min_time,
                        MAX(execution_time_ms) as max_time,
                        AVG(minimum_moves) as avg_moves
                    FROM SnakeLadderAlgorithmPerformance
                    WHERE board_size = %s
                    GROUP BY algorithm_type
                """
                db.cursor.execute(query, (board_size,))
            else:
                query = """
                    SELECT 
                        algorithm_type,
                        COUNT(*) as executions,
                        AVG(execution_time_ms) as avg_time,
                        MIN(execution_time_ms) as min_time,
                        MAX(execution_time_ms) as max_time,
                        AVG(minimum_moves) as avg_moves
                    FROM SnakeLadderAlgorithmPerformance
                    GROUP BY algorithm_type
                """
                db.cursor.execute(query)
            
            results = db.cursor.fetchall()
            
            comparison = {}
            for row in results:
                comparison[row['algorithm_type']] = {
                    'executions': row['executions'],
                    'avg_time': round(row['avg_time'], 3),
                    'min_time': round(row['min_time'], 3),
                    'max_time': round(row['max_time'], 3),
                    'avg_moves': round(row['avg_moves'], 2)
                }
            
            return comparison
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """
        Get top players leaderboard.
        
        Args:
            limit: Number of top players to return
            
        Returns:
            List of player statistics
        """
        with DatabaseConnection(self.db_config) as db:
            query = """
                SELECT 
                    player_name,
                    COUNT(*) as total_games,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
                    ROUND((SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) as accuracy,
                    MAX(submitted_at) as last_played
                FROM SnakeLadderResults
                GROUP BY player_name
                HAVING total_games >= 1
                ORDER BY correct_answers DESC, accuracy DESC, total_games DESC
                LIMIT %s
            """
            
            db.cursor.execute(query, (limit,))
            results = db.cursor.fetchall()
            
            leaderboard = []
            for idx, row in enumerate(results, 1):
                leaderboard.append({
                    'rank': idx,
                    'player_name': row['player_name'],
                    'total_games': row['total_games'],
                    'correct_answers': row['correct_answers'],
                    'accuracy': row['accuracy'],
                    'last_played': row['last_played'].isoformat() if row['last_played'] else None
                })
            
            return leaderboard
