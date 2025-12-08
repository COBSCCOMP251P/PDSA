-- PDSA Interactive Games Database Schema
-- Complete database structure for all games

-- Create database (run manually)
-- CREATE DATABASE pdsa_games;
-- USE pdsa_games;

-- Players table (shared across all games)
CREATE TABLE IF NOT EXISTS Players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_name (player_name)
);

-- Game sessions (shared tracking)
CREATE TABLE IF NOT EXISTS GameSessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    game_type ENUM('eight_queens', 'snake_ladder', 'traffic_simulation', 'traveling_salesman', 'tower_hanoi') NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    INDEX idx_game_type (game_type),
    INDEX idx_status (status)
);

-- Eight Queens Solutions Master Table (All 92 solutions)
CREATE TABLE IF NOT EXISTS EightQueensSolutions (
    solution_id INT AUTO_INCREMENT PRIMARY KEY,
    solution_array JSON NOT NULL, -- e.g., [0,4,7,5,2,6,1,3]
    solution_hash VARCHAR(64) UNIQUE NOT NULL, -- MD5 hash for quick lookup
    is_found BOOLEAN DEFAULT FALSE, -- Has any player found this solution?
    found_by_player_id INT NULL, -- Which player found it
    found_at TIMESTAMP NULL, -- When was it found
    algorithm_used ENUM('sequential', 'threaded') DEFAULT 'sequential',
    FOREIGN KEY (found_by_player_id) REFERENCES Players(player_id) ON DELETE SET NULL,
    INDEX idx_solution_hash (solution_hash),
    INDEX idx_is_found (is_found)
);

-- Eight Queens Player Submissions (Each player's attempts)
CREATE TABLE IF NOT EXISTS EightQueensResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    player_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    solution_id INT NULL, -- Links to the solution they found
    solution_submitted JSON NOT NULL, -- What they submitted
    algorithm_type ENUM('sequential', 'threaded') NOT NULL,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    is_duplicate BOOLEAN DEFAULT FALSE, -- Was this solution already found?
    previous_finder_name VARCHAR(100) NULL, -- Who found it before
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (solution_id) REFERENCES EightQueensSolutions(solution_id) ON DELETE SET NULL,
    INDEX idx_algorithm_type (algorithm_type),
    INDEX idx_is_duplicate (is_duplicate),
    INDEX idx_submitted_at (submitted_at)
);

-- Snake and Ladder Results (Member 1)
CREATE TABLE IF NOT EXISTS SnakeLadderResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    board_size INT NOT NULL,
    algorithm_type ENUM('bfs', 'dynamic_programming') NOT NULL,
    player_answer INT NOT NULL,
    correct_answer INT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    board_config JSON, -- Store ladder/snake positions
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
    INDEX idx_board_size (board_size),
    INDEX idx_algorithm_type (algorithm_type)
);

-- Traffic Simulation Results (Member 2)
CREATE TABLE IF NOT EXISTS TrafficFlowResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    algorithm_type ENUM('ford_fulkerson', 'edmonds_karp') NOT NULL,
    player_answer INT NOT NULL,
    correct_answer INT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    network_config JSON, -- Store capacity configuration
    flow_paths JSON, -- Store flow paths found
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
    INDEX idx_algorithm_type (algorithm_type)
);

-- Traveling Salesman Results (Member 3)
CREATE TABLE IF NOT EXISTS TSPResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    home_city CHAR(1) NOT NULL,
    selected_cities JSON NOT NULL,
    algorithm_type ENUM('brute_force', 'genetic', 'held_karp') NOT NULL,
    player_route JSON,
    correct_route JSON,
    player_distance DECIMAL(8,2),
    correct_distance DECIMAL(8,2),
    is_correct BOOLEAN NOT NULL,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    distance_matrix JSON, -- Store city distances
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
    INDEX idx_algorithm_type (algorithm_type),
    INDEX idx_home_city (home_city)
);

-- Tower of Hanoi Results (Member 4)
CREATE TABLE IF NOT EXISTS HanoiResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    disk_count INT NOT NULL,
    peg_count INT NOT NULL,
    algorithm_type ENUM('recursive_3peg', 'iterative_3peg', 'recursive_4peg', 'frame_stewart') NOT NULL,
    player_moves INT,
    correct_moves INT,
    player_sequence JSON,
    correct_sequence JSON,
    is_correct BOOLEAN NOT NULL,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
    INDEX idx_disk_count (disk_count),
    INDEX idx_peg_count (peg_count),
    INDEX idx_algorithm_type (algorithm_type)
);

-- Algorithm Performance Tracking (Shared)
CREATE TABLE IF NOT EXISTS AlgorithmPerformance (
    perf_id INT AUTO_INCREMENT PRIMARY KEY,
    game_type ENUM('eight_queens', 'snake_ladder', 'traffic_simulation', 'traveling_salesman', 'tower_hanoi') NOT NULL,
    algorithm_name VARCHAR(50) NOT NULL,
    input_size INT,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    memory_usage_mb DECIMAL(8,2),
    cpu_usage_percent DECIMAL(5,2),
    success_rate DECIMAL(5,2) DEFAULT 100.00,
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_game_algorithm (game_type, algorithm_name),
    INDEX idx_execution_time (execution_time_ms)
);

-- Game Leaderboards (Shared)
CREATE TABLE IF NOT EXISTS GameLeaderboards (
    leaderboard_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    game_type ENUM('eight_queens', 'snake_ladder', 'traffic_simulation', 'traveling_salesman', 'tower_hanoi') NOT NULL,
    score DECIMAL(10,2) NOT NULL,
    rank_position INT,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    UNIQUE KEY unique_player_game (player_id, game_type),
    INDEX idx_game_rank (game_type, rank_position)
);

-- Insert sample data for testing
INSERT IGNORE INTO Players (player_name, email) VALUES 
('Test Player 1', 'test1@example.com'),
('Test Player 2', 'test2@example.com'),
('Team Member 1', 'member1@university.edu'),
('Team Member 2', 'member2@university.edu'),
('Team Member 3', 'member3@university.edu'),
('Team Member 4', 'member4@university.edu'),
('Team Member 5', 'member5@university.edu');

-- Create views for easy reporting

-- Performance Summary View
CREATE OR REPLACE VIEW PerformanceSummary AS
SELECT 
    game_type,
    algorithm_name,
    COUNT(*) as test_runs,
    AVG(execution_time_ms) as avg_execution_time,
    MIN(execution_time_ms) as min_execution_time,
    MAX(execution_time_ms) as max_execution_time,
    AVG(memory_usage_mb) as avg_memory_usage
FROM AlgorithmPerformance
GROUP BY game_type, algorithm_name
ORDER BY game_type, avg_execution_time;

-- Player Statistics View
CREATE OR REPLACE VIEW PlayerStatistics AS
SELECT 
    p.player_name,
    COUNT(gs.session_id) as total_sessions,
    COUNT(CASE WHEN gs.status = 'completed' THEN 1 END) as completed_sessions,
    COUNT(DISTINCT gs.game_type) as games_played,
    MAX(gs.completed_at) as last_played
FROM Players p
LEFT JOIN GameSessions gs ON p.player_id = gs.player_id
GROUP BY p.player_id, p.player_name
ORDER BY total_sessions DESC;