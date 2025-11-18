def display_board(n, snakes, ladders, player_positions=None):
    """Displays the game board."""
    board_size = n * n
    for i in range(board_size, 0, -n):
        for j in range(n):
            cell = i - j
            if (i // n) % 2 == 0:
                cell = i - (n - 1) + j

            char = " "
            if cell in snakes:
                char = "S"
            elif cell in ladders:
                char = "L"
            
            player_chars = []
            if player_positions:
                for p_idx, p_pos in enumerate(player_positions):
                    if p_pos == cell:
                        player_chars.append(str(p_idx + 1))
            
            if player_chars:
                char = ",".join(player_chars)

            print(f"| {cell:3d} ({char:^3s}) ", end="")
        print("|")
    print("-" * (n * 12))
