import sys
from database import setup_database

def main():
    """Main function to run the game."""
    setup_database()

    if len(sys.argv) > 1 and sys.argv[1] == 'cli':
        from game import play_cli_game
        while True:
            print("\n--- Snake and Ladder Game (CLI) ---")
            play_cli_game()
            play_again = input("\nPlay another round? (yes/no): ").lower()
            if play_again != 'yes':
                break
    else:
        from gui import GameGUI
        app = GameGUI()
        app.mainloop()

if __name__ == "__main__":
    main()
