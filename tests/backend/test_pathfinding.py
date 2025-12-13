from games.snake_ladder.algorithms.game_logic import SnakeLadderBoard
from games.snake_ladder.algorithms.pathfinding import find_min_moves_bfs, find_min_moves_dfs


def make_small_board():
    board = SnakeLadderBoard(6)
    # Deterministic ladders/snakes to make path predictable
    # Aim: help reach 36 quickly but include a snake to test algorithm
    board.ladders = {3: 15, 8: 20}
    board.snakes = {28: 10}
    return board


def test_bfs_min_moves_and_path():
    board = make_small_board()
    result = find_min_moves_bfs(board)
    assert result.algorithm == "bfs"
    assert result.min_moves > 0
    assert isinstance(result.path, list)
    # Path must start at 1 and end at total_cells
    assert result.path[0] == 1
    assert result.path[-1] == board.total_cells


def test_dfs_min_moves_and_path():
    board = make_small_board()
    result = find_min_moves_dfs(board)
    assert result.algorithm == "dfs"
    assert result.min_moves > 0
    assert isinstance(result.path, list)
    # Path must start at 1 and end at total_cells
    assert result.path[0] == 1
    assert result.path[-1] == board.total_cells
