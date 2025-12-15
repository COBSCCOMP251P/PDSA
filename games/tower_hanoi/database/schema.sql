-- Tower of Hanoi Database Schema
-- Creates the database and all required tables

CREATE DATABASE IF NOT EXISTS pdsa_games;
USE pdsa_games;

-- Players table to store player information
CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name),
    INDEX idx_created_at (created_at)
);

-- Rounds table to store game round metadata
CREATE TABLE rounds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    n_disks INT NOT NULL CHECK (n_disks BETWEEN 5 AND 10),
    peg_count INT NOT NULL CHECK (peg_count IN (3, 4)),
    source CHAR(1) DEFAULT 'A',
    destination CHAR(1) DEFAULT 'D',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_n_disks (n_disks),
    INDEX idx_peg_count (peg_count),
    INDEX idx_started_at (started_at)
);

-- Submissions table to store player move submissions
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_id INT NOT NULL,
    player_id INT,
    declared_moves INT,
    move_sequence TEXT,
    is_correct BOOLEAN DEFAULT FALSE,
    validation_error TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (round_id) REFERENCES rounds(id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE SET NULL,
    INDEX idx_round_id (round_id),
    INDEX idx_player_id (player_id),
    INDEX idx_is_correct (is_correct),
    INDEX idx_submitted_at (submitted_at)
);


-- Gameplay sessions table to store individual game play sessions
CREATE TABLE gameplay_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    algorithm_name VARCHAR(100) NOT NULL,
    disk_count INT NOT NULL CHECK (disk_count BETWEEN 3 AND 10),
    peg_count INT NOT NULL CHECK (peg_count IN (3, 4)),
    move_count INT NOT NULL,
    algorithm_execution_time_ms DECIMAL(12, 3) NOT NULL,
    gameplay_time_ms INT NOT NULL,
    generated_sequence TEXT NOT NULL,
    is_auto_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_name (player_name),
    INDEX idx_algorithm_name (algorithm_name),
    INDEX idx_disk_count (disk_count),
    INDEX idx_peg_count (peg_count),
    INDEX idx_created_at (created_at)
);

-- Create a view for leaderboard with player stats
CREATE VIEW leaderboard AS
SELECT 
    p.name,
    COUNT(s.id) as total_submissions,
    COUNT(CASE WHEN s.is_correct THEN 1 END) as correct_submissions,
    MIN(CASE WHEN s.is_correct THEN s.declared_moves END) as best_moves,
    AVG(CASE WHEN s.is_correct THEN s.declared_moves END) as avg_moves,
    MAX(s.submitted_at) as last_submission
FROM players p
LEFT JOIN submissions s ON p.id = s.player_id
GROUP BY p.id, p.name
HAVING correct_submissions > 0
ORDER BY best_moves ASC, avg_moves ASC, last_submission DESC;

-- Create indexes for better performance
CREATE INDEX idx_submissions_correct_moves ON submissions(is_correct, declared_moves);
CREATE INDEX idx_algorithm_runs_perf ON algorithm_runs(algorithm_name, peg_count, computed_moves, runtime_ms);