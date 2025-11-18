from game_logic import Game
from utils import display_board

def get_board_size():
    """Gets the board size from the user."""
    while True:
        try:
            n = int(input("Enter the size of the board (N x N, where 6 <= N <= 12): "))
            if 6 <= n <= 12:
                return n
            else:
                print("Invalid input. Please enter a number between 6 and 12.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_num_players():
    """Gets the number of players from the user."""
    while True:
        try:
            num_players = int(input("Enter the number of players (1-4): "))
            if 1 <= num_players <= 4:
                return num_players
            else:
                print("Invalid input. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def play_cli_game():
    """Main game loop for the CLI version."""
    n = get_board_size()
    num_players = get_num_players()

    if num_players == 1:
        play_cli_game_with_ai(n)
        return

    game = Game(n, num_players)
    
    while not game.check_win():
        display_board(game.n, game.snakes, game.ladders, game.player_positions)
        
        player = game.current_player + 1
        print(f"\nPlayer {player}'s turn.")
        print(f"Player positions: {game.player_positions}")
        print(f"Throws for Player {player}: {game.throws[game.current_player]}")
        
        input(f"Player {player}, press Enter to roll the dice...")
        
        dice_roll = game.roll_dice()
        print(f"Player {player} rolled a {dice_roll}")
        
        game.move_player(dice_roll)
        print(f"Player {player} is now at position {game.player_positions[game.current_player]}")

        if game.check_win():
            winner = game.current_player + 1
            print(f"\nCongratulations Player {winner}! You won in {game.throws[game.current_player]} throws.")
            player_name = input(f"Enter Player {winner}'s name: ")
            if player_name:
                game.save_result(player_name)
                print("Your result has been saved.")
            break
        
        game.next_player()

def play_cli_game_with_ai(n):
    """Game loop for playing against an AI."""
    game = Game(n, 2)  # 1 human vs 1 AI
    
    while not game.check_win():
        display_board(game.n, game.snakes, game.ladders, game.player_positions)
        
        player = game.current_player + 1
        print(f"\nPlayer positions: {game.player_positions}")

        if game.current_player == 0:  # Human player
            print(f"Your turn (Player 1).")
            print(f"Throws: {game.throws[game.current_player]}")
            input("Press Enter to roll the dice...")
            dice_roll = game.roll_dice()
            print(f"You rolled a {dice_roll}")
            game.move_player(dice_roll)
            print(f"You are now at position {game.player_positions[game.current_player]}")
        else:  # AI player
            print(f"AI's turn (Player 2).")
            print(f"Throws: {game.throws[game.current_player]}")
            print("AI is thinking...")
            import time
            time.sleep(1)
            dice_roll = game.roll_dice()
            print(f"AI rolled a {dice_roll}")
            game.move_player(dice_roll)
            print(f"AI is now at position {game.player_positions[game.current_player]}")

        if game.check_win():
            winner = game.current_player + 1
            if winner == 1:
                print(f"\nCongratulations! You won in {game.throws[game.current_player]} throws.")
                player_name = input(f"Enter your name: ")
                if player_name:
                    game.save_result(player_name)
                    print("Your result has been saved.")
            else:
                print(f"\nThe AI won in {game.throws[game.current_player]} throws. Better luck next time!")
            break
        
        game.next_player()
