"""
Database Setup Script for Snake and Ladder Game
Run this script to create the database and tables
"""

import mysql.connector
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.backend.config import DATABASE_CONFIG

def setup_database():
    """Create database and tables for the Snake and Ladder game"""
    
    print("🔧 Setting up database...")
    
    # Connect without specifying database (to create it)
    connection_config = DATABASE_CONFIG.copy()
    database_name = connection_config.pop('database')
    
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**connection_config)
        cursor = conn.cursor()
        
        # Create database
        print(f"📦 Creating database '{database_name}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        print(f"✅ Database '{database_name}' created/verified")
        
        # Use the database
        cursor.execute(f"USE {database_name}")
        
        # Create Players table
        print("📋 Creating Players table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Players (
                player_id INT AUTO_INCREMENT PRIMARY KEY,
                player_name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_player_name (player_name)
            )
        """)
        print("✅ Players table created")
        
        # Create GameSessions table
        print("📋 Creating GameSessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS GameSessions (
                session_id INT AUTO_INCREMENT PRIMARY KEY,
                player_id INT NOT NULL,
                game_type ENUM('eight_queens', 'snake_ladder', 'traffic_simulation', 
                              'traveling_salesman', 'tower_hanoi') NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
                FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
                INDEX idx_game_type (game_type),
                INDEX idx_status (status)
            )
        """)
        print("✅ GameSessions table created")
        
        # Create SnakeLadderResults table
        print("📋 Creating SnakeLadderResults table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SnakeLadderResults (
                result_id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                player_name VARCHAR(100) NOT NULL,
                board_size INT NOT NULL,
                algorithm_type ENUM('bfs', 'dfs') NOT NULL,
                player_answer INT NOT NULL,
                correct_answer INT NOT NULL,
                is_correct BOOLEAN NOT NULL,
                execution_time_ms DECIMAL(10,3) NOT NULL,
                board_config JSON,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
                INDEX idx_board_size (board_size),
                INDEX idx_algorithm_type (algorithm_type)
            )
        """)
        print("✅ SnakeLadderResults table created")
        
        # Create SnakeLadderAlgorithmPerformance table
        print("📋 Creating SnakeLadderAlgorithmPerformance table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS SnakeLadderAlgorithmPerformance (
                performance_id INT AUTO_INCREMENT PRIMARY KEY,
                session_id INT NOT NULL,
                board_size INT NOT NULL,
                algorithm_type ENUM('bfs', 'dfs') NOT NULL,
                execution_time_ms DECIMAL(10,3) NOT NULL,
                minimum_moves INT NOT NULL,
                board_config JSON,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
                INDEX idx_algorithm_type (algorithm_type),
                INDEX idx_board_size (board_size)
            )
        """)
        print("✅ SnakeLadderAlgorithmPerformance table created")
        
        conn.commit()
        
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n📊 Tables in database:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database setup complete!")
        print(f"🎮 You can now start the game!")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")
        print("\n🔍 Troubleshooting tips:")
        print("   1. Make sure MySQL server is running")
        print("   2. Check your MySQL credentials in shared/backend/config.py")
        print(f"   3. Current config: host={connection_config.get('host')}, "
              f"user={connection_config.get('user')}, port={connection_config.get('port')}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🐍 Snake and Ladder Game - Database Setup")
    print("=" * 60)
    print()
    
    success = setup_database()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Setup successful! You can now run the game.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Setup failed. Please fix the errors and try again.")
        print("=" * 60)
        sys.exit(1)
