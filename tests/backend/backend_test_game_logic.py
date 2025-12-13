import pytest

from games.snake_ladder.algorithms.game_logic import SnakeLadderBoard


def make_deterministic_board():
    board = SnakeLadderBoard(6)
    board.ladders = {2: 14, 7: 19}
    board.snakes = {22: 5, 24: 12}
    return board


def test_board_initialization_constraints():
    with pytest.raises(ValueError):
        SnakeLadderBoard(5)
    with pytest.raises(ValueError):
        SnakeLadderBoard(13)


def test_to_dict_structure():
    board = make_deterministic_board()
    data = board.to_dict()
    assert data["board_size"] == 6
    assert data["total_cells"] == 36
    assert isinstance(data["ladders"], dict)
    assert isinstance(data["snakes"], dict)


def test_get_next_position_basic_move():
    board = make_deterministic_board()
    assert board.get_next_position(1, 3) == 4


def test_get_next_position_ladder():
    board = make_deterministic_board()
    assert board.get_next_position(1, 1) == 14


def test_get_next_position_snake():
    board = make_deterministic_board()
    assert board.get_next_position(20, 2) == 5


def test_get_next_position_bounds():
    board = make_deterministic_board()
    assert board.get_next_position(35, 2) == 35


def test_get_all_possible_moves_contains_unique_positions():
    board = make_deterministic_board()
    moves = board.get_all_possible_moves(1)
    assert len(moves) > 0
    assert len(moves) == len(set(moves))
