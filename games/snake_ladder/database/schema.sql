-- Snake and Ladder Game Database Schema
-- Database: snake_game

-- Players table
CREATE TABLE IF NOT EXISTS Players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_name (player_name)
);

-- Game Sessions table
CREATE TABLE IF NOT EXISTS GameSessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    game_type VARCHAR(50) DEFAULT 'snake_ladder',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    INDEX idx_game_type (game_type),
    INDEX idx_status (status)
);

-- Snake Ladder Results table
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
);

-- Algorithm Performance Tracking table
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
);
