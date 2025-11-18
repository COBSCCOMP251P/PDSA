import sqlite3

def setup_database():
    """Sets up the database and creates the games and player_stats tables if they don't exist."""
    conn = sqlite3.connect('snake_and_ladder.db')
    c = conn.cursor()

    # Create games table
    c.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            winner_name TEXT,
            min_throws_bfs INTEGER,
            time_taken_bfs REAL,
            min_throws_dijkstra INTEGER,
            time_taken_dijkstra REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create player_stats table
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            player_name TEXT NOT NULL,
            throws INTEGER NOT NULL,
            final_position INTEGER NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games (id)
        )
    ''')
    conn.commit()
    conn.close()

def save_game_and_player_stats(winner_name, min_throws_bfs, time_taken_bfs, min_throws_dijkstra, time_taken_dijkstra, player_stats):
    """Saves a game and its player stats to the database."""
    conn = sqlite3.connect('snake_and_ladder.db')
    c = conn.cursor()
    
    # Insert into games table
    c.execute('''
        INSERT INTO games (winner_name, min_throws_bfs, time_taken_bfs, min_throws_dijkstra, time_taken_dijkstra)
        VALUES (?, ?, ?, ?, ?)
    ''', (winner_name, min_throws_bfs, time_taken_bfs, min_throws_dijkstra, time_taken_dijkstra))
    
    game_id = c.lastrowid
    
    # Insert into player_stats table
    for stats in player_stats:
        c.execute('''
            INSERT INTO player_stats (game_id, player_name, throws, final_position)
            VALUES (?, ?, ?, ?)
        ''', (game_id, stats['player_name'], stats['throws'], stats['final_position']))
        
    conn.commit()
    conn.close()
