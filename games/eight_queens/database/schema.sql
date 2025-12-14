-- =============================================
-- Eight Queens Game - Complete Database Schema
-- Based on actual queries in simple_gaming_routes.py
-- =============================================
-- SAFE TO RUN MULTIPLE TIMES (uses IF NOT EXISTS / INSERT IGNORE)
-- Usage: mysql -u root -p < schema.sql
-- =============================================

-- CREATE DATABASE
CREATE DATABASE IF NOT EXISTS eight_queens_game;
USE eight_queens_game;

-- =============================================
-- 1. PLAYERS TABLE (No email - only username)
-- =============================================
CREATE TABLE IF NOT EXISTS players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    total_games_played INT DEFAULT 0,
    total_solutions_found INT DEFAULT 0,
    highest_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played TIMESTAMP NULL,
    INDEX idx_player_name (name)
);

-- =============================================
-- 2. EightQueensSolutions TABLE (with solution_hash)
-- This is what the code actually queries!
-- =============================================
CREATE TABLE IF NOT EXISTS EightQueensSolutions (
    solution_id INT AUTO_INCREMENT PRIMARY KEY,
    solution_array JSON NOT NULL,
    solution_hash VARCHAR(64) NOT NULL UNIQUE,
    is_found BOOLEAN DEFAULT FALSE,
    found_by_player_id INT NULL,
    found_at TIMESTAMP NULL,
    INDEX idx_solution_hash (solution_hash),
    INDEX idx_is_found (is_found)
);

-- =============================================
-- 3. GAME_SESSIONS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS game_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    score INT DEFAULT 0,
    hints_used INT DEFAULT 0,
    undo_count INT DEFAULT 0,
    is_completed TINYINT(1) DEFAULT 0,
    result ENUM('win', 'loss', 'abandoned') NULL,
    solution_type ENUM('new', 'duplicate') NULL,
    completion_time_seconds INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'in_progress',
    sequential_time_ms DECIMAL(10,3) NULL,
    threaded_time_ms DECIMAL(10,3) NULL,
    speedup_factor DECIMAL(5,2) NULL,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    INDEX idx_player_sessions (player_id),
    INDEX idx_session_date (session_start),
    INDEX idx_status (status)
);

-- =============================================
-- 4. EightQueensResults TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS EightQueensResults (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NULL,
    player_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    solution_id INT NULL,
    solution_submitted JSON NULL,
    is_correct TINYINT(1) DEFAULT 0,
    is_duplicate TINYINT(1) DEFAULT 0,
    previous_finder_name VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player (player_id),
    INDEX idx_session (session_id),
    INDEX idx_solution (solution_id)
);

-- =============================================
-- 5. ALGORITHM_COMPARISONS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS algorithm_comparisons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sequential_time_ms DECIMAL(10,3) NOT NULL,
    threaded_time_ms DECIMAL(10,3) NOT NULL,
    speedup_factor DECIMAL(5,2) NOT NULL,
    solutions_count INT DEFAULT 92,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);

-- =============================================
-- 6. DIFFICULTY_SETTINGS TABLE
-- =============================================
CREATE TABLE IF NOT EXISTS difficulty_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    difficulty ENUM('easy', 'medium', 'hard') NOT NULL UNIQUE,
    max_hints INT NOT NULL,
    time_limit_seconds INT NULL,
    undo_allowed TINYINT(1) DEFAULT 1,
    max_undos INT NULL,
    visual_hints TINYINT(1) DEFAULT 1,
    conflict_checking TINYINT(1) DEFAULT 1,
    starting_queens INT DEFAULT 0,
    base_score INT DEFAULT 100,
    time_bonus_multiplier DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 7. VIEW: solutions (alias for EightQueensSolutions)
-- Required for backward compatibility with some queries
-- =============================================
DROP VIEW IF EXISTS solutions;
CREATE VIEW solutions AS 
SELECT 
    solution_id as id, 
    solution_id, 
    solution_array, 
    solution_hash, 
    is_found, 
    found_by_player_id, 
    found_at 
FROM EightQueensSolutions;

-- =============================================
-- INSERT DIFFICULTY SETTINGS (IGNORE DUPLICATES)
-- =============================================
INSERT IGNORE INTO difficulty_settings (difficulty, max_hints, time_limit_seconds, undo_allowed, max_undos, visual_hints, conflict_checking, starting_queens, base_score) VALUES
('easy', 999, NULL, 1, NULL, 1, 1, 2, 50),
('medium', 3, 1800, 1, NULL, 1, 1, 0, 100),
('hard', 1, 600, 0, 0, 0, 0, 0, 200);

-- =============================================
-- INSERT ALL 92 SOLUTIONS (IGNORE DUPLICATES)
-- The hash is MD5 of JSON array like "[0, 4, 7, 5, 2, 6, 1, 3]"
-- =============================================
INSERT IGNORE INTO EightQueensSolutions (solution_array, solution_hash) VALUES
('[0,4,7,5,2,6,1,3]', MD5('[0, 4, 7, 5, 2, 6, 1, 3]')),
('[0,5,7,2,6,3,1,4]', MD5('[0, 5, 7, 2, 6, 3, 1, 4]')),
('[0,6,3,5,7,1,4,2]', MD5('[0, 6, 3, 5, 7, 1, 4, 2]')),
('[0,6,4,7,1,3,5,2]', MD5('[0, 6, 4, 7, 1, 3, 5, 2]')),
('[1,3,5,7,2,0,6,4]', MD5('[1, 3, 5, 7, 2, 0, 6, 4]')),
('[1,4,6,0,2,7,5,3]', MD5('[1, 4, 6, 0, 2, 7, 5, 3]')),
('[1,4,6,3,0,7,5,2]', MD5('[1, 4, 6, 3, 0, 7, 5, 2]')),
('[1,5,0,6,3,7,2,4]', MD5('[1, 5, 0, 6, 3, 7, 2, 4]')),
('[1,5,7,2,0,3,6,4]', MD5('[1, 5, 7, 2, 0, 3, 6, 4]')),
('[1,6,2,5,7,4,0,3]', MD5('[1, 6, 2, 5, 7, 4, 0, 3]')),
('[1,6,4,7,0,3,5,2]', MD5('[1, 6, 4, 7, 0, 3, 5, 2]')),
('[1,7,5,0,2,4,6,3]', MD5('[1, 7, 5, 0, 2, 4, 6, 3]')),
('[2,0,6,4,7,1,3,5]', MD5('[2, 0, 6, 4, 7, 1, 3, 5]')),
('[2,4,1,7,0,6,3,5]', MD5('[2, 4, 1, 7, 0, 6, 3, 5]')),
('[2,4,1,7,5,3,6,0]', MD5('[2, 4, 1, 7, 5, 3, 6, 0]')),
('[2,4,6,0,3,1,7,5]', MD5('[2, 4, 6, 0, 3, 1, 7, 5]')),
('[2,4,7,3,0,6,1,5]', MD5('[2, 4, 7, 3, 0, 6, 1, 5]')),
('[2,5,1,4,7,0,6,3]', MD5('[2, 5, 1, 4, 7, 0, 6, 3]')),
('[2,5,1,6,0,3,7,4]', MD5('[2, 5, 1, 6, 0, 3, 7, 4]')),
('[2,5,1,6,4,0,7,3]', MD5('[2, 5, 1, 6, 4, 0, 7, 3]')),
('[2,5,3,0,7,4,6,1]', MD5('[2, 5, 3, 0, 7, 4, 6, 1]')),
('[2,5,3,1,7,4,6,0]', MD5('[2, 5, 3, 1, 7, 4, 6, 0]')),
('[2,5,7,0,3,6,4,1]', MD5('[2, 5, 7, 0, 3, 6, 4, 1]')),
('[2,5,7,0,4,6,1,3]', MD5('[2, 5, 7, 0, 4, 6, 1, 3]')),
('[2,5,7,1,3,0,6,4]', MD5('[2, 5, 7, 1, 3, 0, 6, 4]')),
('[2,6,1,7,4,0,3,5]', MD5('[2, 6, 1, 7, 4, 0, 3, 5]')),
('[2,6,1,7,5,3,0,4]', MD5('[2, 6, 1, 7, 5, 3, 0, 4]')),
('[2,7,3,6,0,5,1,4]', MD5('[2, 7, 3, 6, 0, 5, 1, 4]')),
('[3,0,4,7,1,6,2,5]', MD5('[3, 0, 4, 7, 1, 6, 2, 5]')),
('[3,0,4,7,5,2,6,1]', MD5('[3, 0, 4, 7, 5, 2, 6, 1]')),
('[3,1,4,7,5,0,2,6]', MD5('[3, 1, 4, 7, 5, 0, 2, 6]')),
('[3,1,6,2,5,7,0,4]', MD5('[3, 1, 6, 2, 5, 7, 0, 4]')),
('[3,1,6,2,5,7,4,0]', MD5('[3, 1, 6, 2, 5, 7, 4, 0]')),
('[3,1,6,4,0,7,5,2]', MD5('[3, 1, 6, 4, 0, 7, 5, 2]')),
('[3,1,7,4,6,0,2,5]', MD5('[3, 1, 7, 4, 6, 0, 2, 5]')),
('[3,1,7,5,0,2,4,6]', MD5('[3, 1, 7, 5, 0, 2, 4, 6]')),
('[3,5,0,4,1,7,2,6]', MD5('[3, 5, 0, 4, 1, 7, 2, 6]')),
('[3,5,7,1,6,0,2,4]', MD5('[3, 5, 7, 1, 6, 0, 2, 4]')),
('[3,5,7,2,0,6,4,1]', MD5('[3, 5, 7, 2, 0, 6, 4, 1]')),
('[3,6,0,7,4,1,5,2]', MD5('[3, 6, 0, 7, 4, 1, 5, 2]')),
('[3,6,2,7,1,4,0,5]', MD5('[3, 6, 2, 7, 1, 4, 0, 5]')),
('[3,6,4,1,5,0,2,7]', MD5('[3, 6, 4, 1, 5, 0, 2, 7]')),
('[3,6,4,2,0,5,7,1]', MD5('[3, 6, 4, 2, 0, 5, 7, 1]')),
('[3,7,0,2,5,1,6,4]', MD5('[3, 7, 0, 2, 5, 1, 6, 4]')),
('[3,7,0,4,6,1,5,2]', MD5('[3, 7, 0, 4, 6, 1, 5, 2]')),
('[3,7,4,2,0,6,1,5]', MD5('[3, 7, 4, 2, 0, 6, 1, 5]')),
('[4,0,3,5,7,1,6,2]', MD5('[4, 0, 3, 5, 7, 1, 6, 2]')),
('[4,0,7,3,1,6,2,5]', MD5('[4, 0, 7, 3, 1, 6, 2, 5]')),
('[4,0,7,5,2,6,1,3]', MD5('[4, 0, 7, 5, 2, 6, 1, 3]')),
('[4,1,3,5,7,2,0,6]', MD5('[4, 1, 3, 5, 7, 2, 0, 6]')),
('[4,1,3,6,2,7,5,0]', MD5('[4, 1, 3, 6, 2, 7, 5, 0]')),
('[4,1,5,0,6,3,7,2]', MD5('[4, 1, 5, 0, 6, 3, 7, 2]')),
('[4,1,7,0,3,6,2,5]', MD5('[4, 1, 7, 0, 3, 6, 2, 5]')),
('[4,2,0,5,7,1,3,6]', MD5('[4, 2, 0, 5, 7, 1, 3, 6]')),
('[4,2,0,6,1,7,5,3]', MD5('[4, 2, 0, 6, 1, 7, 5, 3]')),
('[4,2,7,3,6,0,5,1]', MD5('[4, 2, 7, 3, 6, 0, 5, 1]')),
('[4,6,0,2,7,5,3,1]', MD5('[4, 6, 0, 2, 7, 5, 3, 1]')),
('[4,6,0,3,1,7,5,2]', MD5('[4, 6, 0, 3, 1, 7, 5, 2]')),
('[4,6,1,3,7,0,2,5]', MD5('[4, 6, 1, 3, 7, 0, 2, 5]')),
('[4,6,1,5,2,0,3,7]', MD5('[4, 6, 1, 5, 2, 0, 3, 7]')),
('[4,6,1,5,2,0,7,3]', MD5('[4, 6, 1, 5, 2, 0, 7, 3]')),
('[4,6,3,0,2,7,5,1]', MD5('[4, 6, 3, 0, 2, 7, 5, 1]')),
('[4,7,3,0,2,5,1,6]', MD5('[4, 7, 3, 0, 2, 5, 1, 6]')),
('[4,7,3,0,6,1,5,2]', MD5('[4, 7, 3, 0, 6, 1, 5, 2]')),
('[5,0,4,1,7,2,6,3]', MD5('[5, 0, 4, 1, 7, 2, 6, 3]')),
('[5,1,6,0,2,4,7,3]', MD5('[5, 1, 6, 0, 2, 4, 7, 3]')),
('[5,1,6,0,3,7,4,2]', MD5('[5, 1, 6, 0, 3, 7, 4, 2]')),
('[5,2,0,6,4,7,1,3]', MD5('[5, 2, 0, 6, 4, 7, 1, 3]')),
('[5,2,0,7,3,1,6,4]', MD5('[5, 2, 0, 7, 3, 1, 6, 4]')),
('[5,2,0,7,4,1,3,6]', MD5('[5, 2, 0, 7, 4, 1, 3, 6]')),
('[5,2,4,6,0,3,1,7]', MD5('[5, 2, 4, 6, 0, 3, 1, 7]')),
('[5,2,4,7,0,3,1,6]', MD5('[5, 2, 4, 7, 0, 3, 1, 6]')),
('[5,2,6,1,3,7,0,4]', MD5('[5, 2, 6, 1, 3, 7, 0, 4]')),
('[5,2,6,1,7,4,0,3]', MD5('[5, 2, 6, 1, 7, 4, 0, 3]')),
('[5,2,6,3,0,7,1,4]', MD5('[5, 2, 6, 3, 0, 7, 1, 4]')),
('[5,3,0,4,7,1,6,2]', MD5('[5, 3, 0, 4, 7, 1, 6, 2]')),
('[5,3,1,7,4,6,0,2]', MD5('[5, 3, 1, 7, 4, 6, 0, 2]')),
('[5,3,6,0,2,4,1,7]', MD5('[5, 3, 6, 0, 2, 4, 1, 7]')),
('[5,3,6,0,7,1,4,2]', MD5('[5, 3, 6, 0, 7, 1, 4, 2]')),
('[5,7,1,3,0,6,4,2]', MD5('[5, 7, 1, 3, 0, 6, 4, 2]')),
('[6,0,2,7,5,3,1,4]', MD5('[6, 0, 2, 7, 5, 3, 1, 4]')),
('[6,1,3,0,7,4,2,5]', MD5('[6, 1, 3, 0, 7, 4, 2, 5]')),
('[6,1,5,2,0,3,7,4]', MD5('[6, 1, 5, 2, 0, 3, 7, 4]')),
('[6,2,0,5,7,4,1,3]', MD5('[6, 2, 0, 5, 7, 4, 1, 3]')),
('[6,2,7,1,4,0,5,3]', MD5('[6, 2, 7, 1, 4, 0, 5, 3]')),
('[6,3,1,4,7,0,2,5]', MD5('[6, 3, 1, 4, 7, 0, 2, 5]')),
('[6,3,1,7,5,0,2,4]', MD5('[6, 3, 1, 7, 5, 0, 2, 4]')),
('[6,4,2,0,5,7,1,3]', MD5('[6, 4, 2, 0, 5, 7, 1, 3]')),
('[7,1,3,0,6,4,2,5]', MD5('[7, 1, 3, 0, 6, 4, 2, 5]')),
('[7,1,4,2,0,6,3,5]', MD5('[7, 1, 4, 2, 0, 6, 3, 5]')),
('[7,2,0,5,1,4,6,3]', MD5('[7, 2, 0, 5, 1, 4, 6, 3]')),
('[7,3,0,2,5,1,6,4]', MD5('[7, 3, 0, 2, 5, 1, 6, 4]'));

-- =============================================
-- VERIFICATION
-- =============================================
SELECT 'Eight Queens database setup complete!' AS Status;
SELECT COUNT(*) AS total_solutions FROM EightQueensSolutions;
SELECT COUNT(*) AS difficulty_levels FROM difficulty_settings;
