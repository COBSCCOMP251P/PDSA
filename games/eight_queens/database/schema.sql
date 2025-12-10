-- Eight Queens Game - MySQL Database Schema
-- Author: PDSA Course Project
-- Date: November 24, 2025
-- Purpose: Store player data, solutions, and game performance metrics

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS eight_queens_game;
USE eight_queens_game;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS game_sessions;
DROP TABLE IF EXISTS discovered_solutions;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS solutions;

-- =============================================
-- 1. PLAYERS TABLE
-- Store player information and registration
-- =============================================
CREATE TABLE players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    total_games_played INT DEFAULT 0,
    total_solutions_found INT DEFAULT 0,
    
    -- Indexes for performance
    INDEX idx_name (name),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
);

-- =============================================
-- 2. SOLUTIONS TABLE
-- Store all 92 possible Eight Queens solutions
-- =============================================
CREATE TABLE solutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solution_number INT UNIQUE NOT NULL, -- 1 to 92
    solution_array JSON NOT NULL, -- [0,4,7,5,2,6,1,3] format
    solution_string VARCHAR(16) NOT NULL, -- "04752613" format for quick lookup
    symmetry_group INT, -- Group solutions by rotational/mirror symmetry
    is_fundamental BOOLEAN DEFAULT FALSE, -- True for 12 fundamental solutions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_solution_number (solution_number),
    INDEX idx_solution_string (solution_string),
    INDEX idx_symmetry_group (symmetry_group)
);

-- =============================================
-- 3. DISCOVERED_SOLUTIONS TABLE  
-- Track which solutions have been found by players
-- Implements duplicate prevention requirement
-- =============================================
CREATE TABLE discovered_solutions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    solution_id INT NOT NULL,
    discovered_by_player_id INT NOT NULL,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    algorithm_type ENUM('sequential', 'threaded') NOT NULL,
    execution_time_ms DECIMAL(10,3) NOT NULL, -- Milliseconds with 3 decimal precision
    
    -- Foreign keys
    FOREIGN KEY (solution_id) REFERENCES solutions(id) ON DELETE CASCADE,
    FOREIGN KEY (discovered_by_player_id) REFERENCES players(id) ON DELETE CASCADE,
    
    -- Prevent duplicate discoveries of same solution
    UNIQUE KEY unique_solution_discovery (solution_id),
    
    -- Indexes for performance
    INDEX idx_discovered_by (discovered_by_player_id),
    INDEX idx_discovered_at (discovered_at),
    INDEX idx_algorithm_type (algorithm_type)
);

-- =============================================
-- ALGORITHM COMPARISONS TABLE (NEW)
-- Track BOTH algorithm timings for each game round
-- Required for PDSA: 15 Game Rounds timing chart
-- =============================================
CREATE TABLE IF NOT EXISTS algorithm_comparisons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sequential_time_ms DECIMAL(10,3) NOT NULL,
    threaded_time_ms DECIMAL(10,3) NOT NULL,
    speedup_factor DECIMAL(5,2),
    solutions_count INT DEFAULT 92,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_created_at (created_at)
);

-- =============================================
-- 4. GAME_SESSIONS TABLE
-- Record individual game rounds and performance data
-- Required for coursework: "record time taken for each algorithm"
-- =============================================
CREATE TABLE game_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    algorithm_type ENUM('sequential', 'threaded') NOT NULL,
    
    -- Performance metrics - BOTH algorithms (PDSA Requirement)
    total_solutions_found INT DEFAULT 0,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    sequential_time_ms DECIMAL(10,3) NULL,      -- Time for sequential algorithm
    threaded_time_ms DECIMAL(10,3) NULL,        -- Time for threaded algorithm  
    speedup_factor DECIMAL(5,2) NULL,           -- Speedup ratio (sequential/threaded)
    memory_usage_mb DECIMAL(8,2), -- Optional: memory usage tracking
    cpu_usage_percent DECIMAL(5,2), -- Optional: CPU usage tracking
    
    -- Threading specific metrics
    thread_count INT NULL, -- Number of threads used (for threaded algorithm)
    parallel_efficiency DECIMAL(5,2), -- Speed-up ratio for threading
    
    -- Game state
    game_completed BOOLEAN DEFAULT FALSE,
    solutions_attempted INT DEFAULT 0,
    duplicate_attempts INT DEFAULT 0, -- How many duplicate solutions were attempted
    
    -- Session metadata
    user_agent TEXT, -- Browser/system info
    ip_address VARCHAR(45), -- IPv4 or IPv6
    
    -- Foreign keys
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_player_sessions (player_id),
    INDEX idx_session_date (session_start),
    INDEX idx_algorithm_type (algorithm_type),
    INDEX idx_execution_time (execution_time_ms)
);

-- =============================================
-- VIEWS FOR EASY DATA ACCESS
-- =============================================

-- View: Player Statistics
CREATE VIEW player_statistics AS
SELECT 
    p.id,
    p.name,
    p.total_games_played,
    p.total_solutions_found,
    COUNT(DISTINCT ds.solution_id) as unique_solutions_discovered,
    AVG(gs.execution_time_ms) as avg_execution_time_ms,
    MIN(gs.execution_time_ms) as best_time_ms,
    MAX(gs.execution_time_ms) as worst_time_ms,
    p.created_at,
    p.last_played
FROM players p
LEFT JOIN discovered_solutions ds ON p.id = ds.discovered_by_player_id
LEFT JOIN game_sessions gs ON p.id = gs.player_id
GROUP BY p.id, p.name, p.total_games_played, p.total_solutions_found, p.created_at, p.last_played;

-- View: Solution Discovery Status
CREATE VIEW solution_discovery_status AS
SELECT 
    s.solution_number,
    s.solution_string,
    s.is_fundamental,
    CASE 
        WHEN ds.id IS NOT NULL THEN 'DISCOVERED'
        ELSE 'UNDISCOVERED'
    END as discovery_status,
    p.name as discovered_by_player,
    ds.discovered_at,
    ds.algorithm_type,
    ds.execution_time_ms
FROM solutions s
LEFT JOIN discovered_solutions ds ON s.id = ds.solution_id
LEFT JOIN players p ON ds.discovered_by_player_id = p.id
ORDER BY s.solution_number;

-- View: Algorithm Performance Comparison
CREATE VIEW algorithm_performance AS
SELECT 
    algorithm_type,
    COUNT(*) as total_sessions,
    AVG(execution_time_ms) as avg_execution_time,
    MIN(execution_time_ms) as min_execution_time,
    MAX(execution_time_ms) as max_execution_time,
    STDDEV(execution_time_ms) as stddev_execution_time,
    AVG(total_solutions_found) as avg_solutions_per_session,
    AVG(CASE WHEN algorithm_type = 'threaded' THEN parallel_efficiency END) as avg_parallel_efficiency
FROM game_sessions
GROUP BY algorithm_type;

-- =============================================
-- STORED PROCEDURES FOR GAME LOGIC
-- =============================================

-- Procedure: Register new player
DELIMITER //
CREATE PROCEDURE RegisterPlayer(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(255)
)
BEGIN
    DECLARE player_exists INT DEFAULT 0;
    
    -- Check if player already exists
    SELECT COUNT(*) INTO player_exists 
    FROM players 
    WHERE email = p_email OR name = p_name;
    
    IF player_exists = 0 THEN
        INSERT INTO players (name, email) VALUES (p_name, p_email);
        SELECT LAST_INSERT_ID() as player_id, 'SUCCESS' as status;
    ELSE
        SELECT 0 as player_id, 'PLAYER_EXISTS' as status;
    END IF;
END//

-- Procedure: Submit solution and check for duplicates
CREATE PROCEDURE SubmitSolution(
    IN p_player_id INT,
    IN p_solution_string VARCHAR(16),
    IN p_algorithm_type ENUM('sequential', 'threaded'),
    IN p_execution_time_ms DECIMAL(10,3)
)
BEGIN
    DECLARE solution_id_val INT DEFAULT 0;
    DECLARE already_discovered INT DEFAULT 0;
    DECLARE discovered_by_player VARCHAR(100);
    
    -- Find solution ID
    SELECT id INTO solution_id_val 
    FROM solutions 
    WHERE solution_string = p_solution_string;
    
    IF solution_id_val > 0 THEN
        -- Check if already discovered
        SELECT COUNT(*), p.name INTO already_discovered, discovered_by_player
        FROM discovered_solutions ds
        JOIN players p ON ds.discovered_by_player_id = p.id
        WHERE ds.solution_id = solution_id_val;
        
        IF already_discovered = 0 THEN
            -- New discovery!
            INSERT INTO discovered_solutions 
            (solution_id, discovered_by_player_id, algorithm_type, execution_time_ms)
            VALUES (solution_id_val, p_player_id, p_algorithm_type, p_execution_time_ms);
            
            -- Update player statistics
            UPDATE players 
            SET total_solutions_found = total_solutions_found + 1 
            WHERE id = p_player_id;
            
            SELECT 'NEW_DISCOVERY' as status, solution_id_val as solution_id;
        ELSE
            -- Already discovered
            SELECT 'ALREADY_DISCOVERED' as status, 
                   discovered_by_player as discovered_by,
                   solution_id_val as solution_id;
        END IF;
    ELSE
        SELECT 'INVALID_SOLUTION' as status, 0 as solution_id;
    END IF;
END//

-- Procedure: Check if all solutions discovered and reset if needed
CREATE PROCEDURE CheckAndResetDiscoveries()
BEGIN
    DECLARE total_discovered INT DEFAULT 0;
    
    SELECT COUNT(*) INTO total_discovered FROM discovered_solutions;
    
    IF total_discovered >= 92 THEN
        -- All solutions found! Reset for new game cycle
        DELETE FROM discovered_solutions;
        UPDATE players SET total_solutions_found = 0;
        SELECT 'RESET_COMPLETE' as status, 'All 92 solutions discovered! Game reset for new cycle.' as message;
    ELSE
        SELECT 'CONTINUE' as status, 
               CONCAT(total_discovered, ' of 92 solutions discovered.') as message,
               (92 - total_discovered) as remaining_solutions;
    END IF;
END//

DELIMITER ;

-- =============================================
-- INITIAL DATA: INSERT ALL 92 SOLUTIONS
-- =============================================

-- Insert all 92 Eight Queens solutions
-- Note: This is a sample of the first 10 solutions. 
-- In production, you would insert all 92 solutions.
INSERT INTO solutions (solution_number, solution_array, solution_string, symmetry_group, is_fundamental) VALUES
(1, '[0,4,7,5,2,6,1,3]', '04752613', 1, true),
(2, '[0,5,7,2,6,3,1,4]', '05726314', 2, true),
(3, '[0,6,3,5,7,1,4,2]', '06357142', 3, true),
(4, '[0,6,4,7,1,3,5,2]', '06471352', 4, true),
(5, '[1,3,5,7,2,0,6,4]', '13572064', 5, true),
(6, '[1,4,6,0,2,7,5,3]', '14602753', 6, true),
(7, '[1,4,6,3,0,7,5,2]', '14630752', 7, true),
(8, '[1,5,0,6,3,7,2,4]', '15063724', 8, true),
(9, '[1,5,7,2,0,3,6,4]', '15720364', 9, true),
(10, '[1,6,2,5,7,4,0,3]', '16257403', 10, true);

-- Note: In a complete implementation, you would insert all 92 solutions
-- This can be done programmatically or by importing a complete data file

-- =============================================
-- INDEXES FOR OPTIMIZATION
-- =============================================

-- Additional composite indexes for common queries
CREATE INDEX idx_player_algorithm_performance ON game_sessions(player_id, algorithm_type, execution_time_ms);
CREATE INDEX idx_discovery_timeline ON discovered_solutions(discovered_at, algorithm_type);
CREATE INDEX idx_solution_lookup ON solutions(solution_string, solution_number);

-- =============================================
-- SAMPLE TRIGGERS FOR DATA INTEGRITY
-- =============================================

-- Trigger: Update player stats when game session ends
DELIMITER //
CREATE TRIGGER update_player_stats_after_session
AFTER INSERT ON game_sessions
FOR EACH ROW
BEGIN
    UPDATE players 
    SET total_games_played = total_games_played + 1,
        last_played = NEW.session_start
    WHERE id = NEW.player_id;
END//
DELIMITER ;

-- =============================================
-- GRANT PERMISSIONS (Adjust based on your setup)
-- =============================================

-- Create application user with limited permissions
-- CREATE USER 'eight_queens_app'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE ON eight_queens_game.* TO 'eight_queens_app'@'localhost';
-- FLUSH PRIVILEGES;

-- =============================================
-- VERIFICATION QUERIES
-- =============================================

-- Verify table creation
SELECT 'Database schema created successfully!' as status;
SELECT TABLE_NAME, TABLE_ROWS 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'eight_queens_game';

-- Show sample data
SELECT * FROM solutions LIMIT 5;
SELECT * FROM solution_discovery_status LIMIT 5;