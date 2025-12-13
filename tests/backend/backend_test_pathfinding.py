from games.snake_ladder.algorithms.game_logic import SnakeLadderBoard
from games.snake_ladder.algorithms.pathfinding import find_min_moves_bfs, find_min_moves_dfs


def make_small_board():
    board = SnakeLadderBoard(6)
    board.ladders = {3: 15, 8: 20}
    board.snakes = {28: 10}
    return board


def test_bfs_min_moves_and_path():
    board = make_small_board()
    result = find_min_moves_bfs(board)
    assert result.algorithm == "bfs"
    assert result.min_moves > 0
    assert isinstance(result.path, list)
    assert result.path[0] == 1
    assert result.path[-1] == board.total_cells


def test_dfs_min_moves_and_path():
    board = make_small_board()
    result = find_min_moves_dfs(board)
    assert result.algorithm == "dfs"
    assert result.min_moves > 0
    assert isinstance(result.path, list)
    assert result.path[0] == 1
    assert result.path[-1] == board.total_cells
