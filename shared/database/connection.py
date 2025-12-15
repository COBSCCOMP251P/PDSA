"""
Database Connection Module
Provides MySQL connection functionality for all games
"""

import mysql.connector
from mysql.connector import Error
import logging
from config import DATABASE_CONFIG

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
            elif query.strip().upper().startswith('INSERT'):
                self.connection.commit()
                result = cursor.lastrowid  # Return last inserted ID for INSERT queries
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

if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    if init_database():
        print("✅ Database connection test passed")
        db.disconnect()
    else:
        print("❌ Database connection test failed")
        print("Make sure MySQL is running and credentials are correct in .env file")