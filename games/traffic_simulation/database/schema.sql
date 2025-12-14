-- Traffic Simulation Game Database Schema
-- Database: traffic_simulation_game

-- Players table
CREATE TABLE IF NOT EXISTS Players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_name (player_name)
);

-- Game sessions
CREATE TABLE IF NOT EXISTS GameSessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    INDEX idx_status (status)
);

-- Traffic Flow Results
CREATE TABLE IF NOT EXISTS TrafficFlowResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    player_id INT NULL, 
    player_name VARCHAR(100) NOT NULL,
    -- Game-Specific Input/Output
    player_answer INT NOT NULL,
    max_flow_guess INT NOT NULL,
    correct_answer INT NOT NULL,
    max_flow_actual INT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    win_status ENUM('Win', 'Draw', 'Loss') NOT NULL,
    algorithm_type ENUM('ford_fulkerson', 'edmonds_karp', 'dinic') NOT NULL,
    -- Performance Tracking
    runtime_ek_ms DECIMAL(10,3) NOT NULL,
    max_flow_dinic INT NULL,
    runtime_dinic_ms DECIMAL(10,3) NULL,
    network_snapshot JSON,
    flow_paths JSON NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
    INDEX idx_algorithm_type (algorithm_type)
);

-- Views for backward compatibility
CREATE OR REPLACE VIEW game_rounds AS
SELECT 
    result_id AS round_id, 
    player_name, 
    player_answer AS max_flow_guess,
    correct_answer AS max_flow_actual, 
    win_status, 
    submitted_at AS round_timestamp
FROM TrafficFlowResults;

CREATE OR REPLACE VIEW performance_logs AS
SELECT
    tfr.result_id AS log_id,
    tfr.result_id AS round_id,
    tfr.correct_answer AS max_flow_ek,
    tfr.runtime_ek_ms * 1000000 AS runtime_ek_ns,
    tfr.max_flow_dinic,
    tfr.runtime_dinic_ms * 1000000 AS runtime_dinic_ns,
    tfr.network_snapshot
FROM TrafficFlowResults tfr;

-- Insert sample players
INSERT IGNORE INTO Players (player_name, email) VALUES 
('Test Player 1', 'test1@example.com'),
('Test Player 2', 'test2@example.com'),
('Sohan', 'sohan@university.edu');
