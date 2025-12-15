-- Create database and use it.
CREATE DATABASE IF NOT EXISTS tsp_game;
USE tsp_game;

-- Main table for game rounds.
CREATE TABLE IF NOT EXISTS game_rounds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player_name VARCHAR(50) NOT NULL,
    home_city CHAR(1) NOT NULL,
    selected_cities TEXT NOT NULL,
    brute_force_distance FLOAT NOT NULL,
    nearest_neighbor_distance FLOAT NOT NULL,
    dp_distance FLOAT NOT NULL,
    player_distance FLOAT NOT NULL,
    player_score INT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Timing information for each algorithm run.
CREATE TABLE IF NOT EXISTS algorithm_times (
    id INT AUTO_INCREMENT PRIMARY KEY,
    round_id INT NOT NULL,
    brute_force_time FLOAT NOT NULL,
    nearest_neighbor_time FLOAT NOT NULL,
    dp_time FLOAT NOT NULL,
    CONSTRAINT fk_round FOREIGN KEY (round_id) REFERENCES game_rounds(id) ON DELETE CASCADE
);

