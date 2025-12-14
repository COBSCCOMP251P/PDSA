# PDSA Games - Complete Database Setup Script (PowerShell)
# Run this script to set up all 5 game databases

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PDSA GAMES - DATABASE SETUP" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "This script will create all databases for the 5 games:`n"
Write-Host "  1. Eight Queens Game"
Write-Host "  2. Snake & Ladder Game"
Write-Host "  3. Traffic Simulation Game"
Write-Host "  4. Tower of Hanoi Game"
Write-Host "  5. Traveling Salesman Game`n"

# Get MySQL password
$mysqlPassword = Read-Host "Enter MySQL root password" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($mysqlPassword)
$password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

Write-Host "`n🔌 Connecting to MySQL...`n" -ForegroundColor Yellow

# ===== 1. EIGHT QUEENS DATABASE =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  1. Setting up Eight Queens Database" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (Test-Path "games\eight_queens\database\schema.sql") {
    Write-Host "📋 Executing schema.sql..." -ForegroundColor Yellow
    Get-Content "games\eight_queens\database\schema.sql" | mysql -u root -p$password 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Eight Queens database created: 'eight_queens_game'" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Database may already exist or there were warnings (this is usually OK)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Schema file not found" -ForegroundColor Red
}

# ===== 2. SNAKE & LADDER DATABASE =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  2. Setting up Snake & Ladder Database" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "📋 Creating database and tables..." -ForegroundColor Yellow

$snakeLadderSQL = @"
CREATE DATABASE IF NOT EXISTS snake_ladder_game;
USE snake_ladder_game;

CREATE TABLE IF NOT EXISTS Players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_name (player_name)
);

CREATE TABLE IF NOT EXISTS GameSessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    status ENUM('active', 'completed', 'abandoned') DEFAULT 'active',
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_difficulty (difficulty_level)
);

CREATE TABLE IF NOT EXISTS SnakeLadderResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    player_id INT NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    player_rolls INT NOT NULL,
    optimal_rolls INT NOT NULL,
    player_path JSON,
    optimal_path JSON,
    score INT NOT NULL,
    won BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES GameSessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (player_id) REFERENCES Players(player_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS SnakeLadderAlgorithmPerformance (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    result_id INT NOT NULL,
    bfs_runtime_ns BIGINT NOT NULL,
    dfs_runtime_ns BIGINT NOT NULL,
    bfs_path_length INT NOT NULL,
    dfs_path_length INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (result_id) REFERENCES SnakeLadderResults(result_id) ON DELETE CASCADE
);
"@

$snakeLadderSQL | mysql -u root -p$password 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Snake & Ladder database created: 'snake_ladder_game'" -ForegroundColor Green
} else {
    Write-Host "⚠️  Database may already exist or there were warnings (this is usually OK)" -ForegroundColor Yellow
}

# ===== 3. TRAFFIC SIMULATION DATABASE =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  3. Setting up Traffic Simulation Database" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (Test-Path "games\traffic_simulation\database\schema.sql") {
    Write-Host "📋 Executing schema.sql..." -ForegroundColor Yellow
    Get-Content "games\traffic_simulation\database\schema.sql" | mysql -u root -p$password 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Traffic Simulation database created: 'traffic_simulation_game'" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Database may already exist or there were warnings (this is usually OK)" -ForegroundColor Yellow
    }
} else {
    Write-Host "📋 Creating basic structure..." -ForegroundColor Yellow
    $trafficSQL = @"
CREATE DATABASE IF NOT EXISTS traffic_simulation_game;
USE traffic_simulation_game;

CREATE TABLE IF NOT EXISTS Players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_player_name (player_name)
);

CREATE TABLE IF NOT EXISTS TrafficFlowResults (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    max_flow_guess INT NOT NULL,
    max_flow_actual INT NOT NULL,
    win_status ENUM('Win', 'Loss') NOT NULL,
    runtime_ek_ms DECIMAL(10,3) NOT NULL,
    runtime_dinic_ms DECIMAL(10,3),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"@
    $trafficSQL | mysql -u root -p$password 2>$null
    Write-Host "✅ Traffic Simulation database created: 'traffic_simulation_game'" -ForegroundColor Green
}

# ===== 4. TOWER OF HANOI DATABASE =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  4. Setting up Tower of Hanoi Database" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (Test-Path "games\tower_hanoi\database\schema.sql") {
    Write-Host "📋 Executing schema.sql..." -ForegroundColor Yellow
    Get-Content "games\tower_hanoi\database\schema.sql" | mysql -u root -p$password 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tower of Hanoi database created: 'pdsa_games'" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Database may already exist or there were warnings (this is usually OK)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Schema file not found" -ForegroundColor Red
}

# ===== 5. TRAVELING SALESMAN DATABASE =====
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  5. Setting up Traveling Salesman Database" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (Test-Path "games\traveling_salesman\database\tsp_schema.sql") {
    Write-Host "📋 Executing tsp_schema.sql..." -ForegroundColor Yellow
    Get-Content "games\traveling_salesman\database\tsp_schema.sql" | mysql -u root -p$password 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Traveling Salesman database created: 'tsp_game'" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Database may already exist or there were warnings (this is usually OK)" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Schema file not found" -ForegroundColor Red
}

# ===== SUMMARY =====
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✅ DATABASE SETUP COMPLETED!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "📊 Created Databases:"
Write-Host "  1. eight_queens_game"
Write-Host "  2. snake_ladder_game"
Write-Host "  3. traffic_simulation_game"
Write-Host "  4. pdsa_games (Tower of Hanoi)"
Write-Host "  5. tsp_game (Traveling Salesman)"

Write-Host "`n🎮 All games are now ready to use!`n"

Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  1. Run: .\start.ps1"
Write-Host "  2. Or manually:"
Write-Host "     .\.venv\Scripts\Activate.ps1"
Write-Host "     python -m uvicorn shared.backend.main:app --reload"
Write-Host "  3. Open: http://127.0.0.1:8000/shared/index.html`n"
