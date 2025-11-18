import random
import time
from algorithms import bfs, dijkstra
from database import save_game_and_player_stats

class Game:
    def __init__(self, n, num_players=1):
        self.n = n
        self.board_size = n * n
        self.num_players = num_players
        self.snakes, self.ladders = self._setup_board()
        self.player_positions = [1] * num_players
        self.current_player = 0
        self.throws = [0] * num_players

        start_time_bfs = time.time()
        self.min_throws_bfs = bfs(self.n, self.snakes, self.ladders)
        self.time_taken_bfs = time.time() - start_time_bfs

        start_time_dijkstra = time.time()
        self.min_throws_dijkstra = dijkstra(self.n, self.snakes, self.ladders)
        self.time_taken_dijkstra = time.time() - start_time_dijkstra

    def _setup_board(self):
        """Sets up the board with random snakes and ladders."""
        snakes = {}
        ladders = {}
        
        num_snakes_and_ladders = self.n - 2
        
        # Generate snakes
        for _ in range(num_snakes_and_ladders):
            while True:
                start = random.randint(2, self.board_size - 1)
                end = random.randint(1, start - 1)
                if start not in snakes and start not in ladders and start != end:
                    snakes[start] = end
                    break

        # Generate ladders
        for _ in range(num_snakes_and_ladders):
            while True:
                start = random.randint(2, self.board_size - 1)
                end = random.randint(start + 1, self.board_size)
                if start not in snakes and start not in ladders and start != end:
                    ladders[start] = end
                    break
                    
        return snakes, ladders

    def roll_dice(self):
        """Rolls the dice and returns a number between 1 and 6."""
        self.throws[self.current_player] += 1
        return random.randint(1, 6)

    def move_player(self, dice_roll):
        """Moves the current player according to the dice roll."""
        current_position = self.player_positions[self.current_player]
        new_position = current_position + dice_roll
        
        if new_position > self.board_size:
            return current_position # Stay in the same position if the roll is too high

        if new_position in self.ladders:
            new_position = self.ladders[new_position]
        elif new_position in self.snakes:
            new_position = self.snakes[new_position]
            
        self.player_positions[self.current_player] = new_position
        return new_position

    def check_win(self):
        """Checks if the current player has won the game."""
        return self.player_positions[self.current_player] == self.board_size

    def next_player(self):
        """Switches to the next player."""
        self.current_player = (self.current_player + 1) % self.num_players

    def save_result(self, winner_name):
        """Saves the game result to the database."""
        player_stats = []
        for i in range(self.num_players):
            if i == self.current_player:
                name = winner_name
            else:
                name = f"Player {i + 1}"
            
            stats = {
                'player_name': name,
                'throws': self.throws[i],
                'final_position': self.player_positions[i]
            }
            player_stats.append(stats)

        save_game_and_player_stats(
            winner_name=winner_name,
            min_throws_bfs=self.min_throws_bfs,
            time_taken_bfs=self.time_taken_bfs,
            min_throws_dijkstra=self.min_throws_dijkstra,
            time_taken_dijkstra=self.time_taken_dijkstra,
            player_stats=player_stats
        )