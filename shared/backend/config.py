"""
PDSA Games Configuration
Environment and database configuration settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "pruthuvide"),
    "database": os.getenv("DB_NAME", "pdsa_games"),
    "charset": "utf8mb4",
    "autocommit": True
}

# API Configuration
API_CONFIG = {
    "host": os.getenv("API_HOST", "localhost"),
    "port": int(os.getenv("API_PORT", 8000)),
    "prefix": os.getenv("API_PREFIX", "/api"),
    "debug": os.getenv("DEBUG", "true").lower() == "true"
}

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "pdsa-games-secret-key-change-in-production")

# Logging Configuration
LOG_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# Game-specific configurations
GAME_CONFIG = {
    "eight_queens": {
        "board_size": 8,
        "max_solutions": 92,
        "thread_count": 4
    },
    "snake_ladder": {
        "min_board_size": 6,
        "max_board_size": 12,
        "dice_faces": 6
    },
    "traffic_simulation": {
        "min_capacity": 5,
        "max_capacity": 15,
        "nodes": ["A", "B", "C", "D", "E", "F", "G", "H", "T"]
    },
    "traveling_salesman": {
        "cities": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        "min_distance": 50,
        "max_distance": 100
    },
    "tower_hanoi": {
        "min_disks": 5,
        "max_disks": 10,
        "min_pegs": 3,
        "max_pegs": 4
    }
}