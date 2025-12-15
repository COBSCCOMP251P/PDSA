"""
Snake and Ladder Game Logic
Handles board generation, game rules, and board state management
"""

import random
from typing import Dict, List, Tuple, Optional
import json


class SnakeLadderBoard:
    """
    Represents a Snake and Ladder game board with random snakes and ladders.
    """
    
    def __init__(self, n: int):
        """
        Initialize a Snake and Ladder board of size N×N.
        
        Args:
            n: Board size (between 6 and 12)
            
        Raises:
            ValueError: If n is not between 6 and 12
        """
        if not 6 <= n <= 12:
            raise ValueError("Board size must be between 6 and 12")
        
        self.n = n
        self.total_cells = n * n
        self.ladders: Dict[int, int] = {}  # {start: end}
        self.snakes: Dict[int, int] = {}   # {head: tail}
        self.num_ladders = n - 2
        self.num_snakes = n - 2
        
        # Generate random snakes and ladders
        self._generate_board()
    
    def _generate_board(self):
        """
        Generate random positions for snakes and ladders.
        Ensures:
        - Ladders go up (start < end)
        - Snakes go down (head > tail)
        - No overlapping start positions
        - First and last cells are free
        """
        occupied_cells = {1, self.total_cells}
        
        # Generate ladders
        attempts = 0
        max_attempts = 1000
        
        while len(self.ladders) < self.num_ladders and attempts < max_attempts:
            attempts += 1
            
            # Ladder start should be in lower half to middle of board
            start = random.randint(2, self.total_cells - self.n)
            
            if start in occupied_cells or start in self.ladders or start in self.snakes:
                continue
            
            # Ladder end should be at least n cells ahead but not exceed total
            min_end = start + self.n
            max_end = min(self.total_cells - 1, start + (2 * self.n))
            
            if min_end > max_end:
                continue
            
            end = random.randint(min_end, max_end)
            
            if end in occupied_cells or end in self.ladders.values() or end in self.snakes.values():
                continue
            
            self.ladders[start] = end
            occupied_cells.add(start)
            occupied_cells.add(end)
        
        # Generate snakes
        attempts = 0
        while len(self.snakes) < self.num_snakes and attempts < max_attempts:
            attempts += 1
            
            # Snake head should be in upper half of board
            head = random.randint(self.n + 1, self.total_cells - 1)
            
            if head in occupied_cells or head in self.ladders or head in self.snakes:
                continue
            
            # Snake tail should be at least n cells below
            min_tail = 2
            max_tail = head - self.n
            
            if max_tail < min_tail:
                continue
            
            tail = random.randint(min_tail, max_tail)
            
            if tail in occupied_cells or tail in self.ladders.values() or tail in self.snakes.values():
                continue
            
            self.snakes[head] = tail
            occupied_cells.add(head)
            occupied_cells.add(tail)
    
    def get_next_position(self, current: int, dice: int) -> int:
        """
        Get the next position after rolling the dice.
        Handles snake and ladder transitions.
        
        Args:
            current: Current cell position (0-indexed internally, but 1-indexed in logic)
            dice: Dice roll value (1-6)
            
        Returns:
            Next position after applying dice roll and snake/ladder rules
        """
        next_pos = current + dice
        
        # Can't go beyond the last cell
        if next_pos > self.total_cells:
            return current
        
        # Check for ladder
        if next_pos in self.ladders:
            return self.ladders[next_pos]
        
        # Check for snake
        if next_pos in self.snakes:
            return self.snakes[next_pos]
        
        return next_pos
    
    def get_all_possible_moves(self, current: int) -> List[int]:
        """
        Get all possible next positions from current position.
        
        Args:
            current: Current cell position
            
        Returns:
            List of possible next positions after rolling dice (1-6)
        """
        possible_moves = []
        for dice in range(1, 7):
            next_pos = self.get_next_position(current, dice)
            if next_pos != current or next_pos == self.total_cells:
                possible_moves.append(next_pos)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_moves = []
        for move in possible_moves:
            if move not in seen:
                seen.add(move)
                unique_moves.append(move)
        
        return unique_moves
    
    def to_dict(self) -> Dict:
        """
        Convert board configuration to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the board
        """
        return {
            "board_size": self.n,
            "total_cells": self.total_cells,
            "ladders": self.ladders,
            "snakes": self.snakes,
            "num_ladders": self.num_ladders,
            "num_snakes": self.num_snakes
        }
    
    def to_json(self) -> str:
        """
        Convert board configuration to JSON string.
        
        Returns:
            JSON string representation of the board
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SnakeLadderBoard':
        """
        Create a board from dictionary data.
        
        Args:
            data: Dictionary containing board configuration
            
        Returns:
            SnakeLadderBoard instance
        """
        board = cls.__new__(cls)
        board.n = data["board_size"]
        board.total_cells = data["total_cells"]
        board.ladders = {int(k): int(v) for k, v in data["ladders"].items()}
        board.snakes = {int(k): int(v) for k, v in data["snakes"].items()}
        board.num_ladders = data["num_ladders"]
        board.num_snakes = data["num_snakes"]
        return board
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SnakeLadderBoard':
        """
        Create a board from JSON string.
        
        Args:
            json_str: JSON string containing board configuration
            
        Returns:
            SnakeLadderBoard instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def __repr__(self) -> str:
        """String representation of the board."""
        return (f"SnakeLadderBoard(size={self.n}x{self.n}, "
                f"ladders={len(self.ladders)}, snakes={len(self.snakes)})")


def validate_board_size(n: int) -> None:
    """
    Validate board size input.
    
    Args:
        n: Board size to validate
        
    Raises:
        ValueError: If board size is invalid
    """
    if not isinstance(n, int):
        raise ValueError("Board size must be an integer")
    
    if not 6 <= n <= 12:
        raise ValueError("Board size must be between 6 and 12")


def generate_answer_choices(correct_answer: int) -> List[int]:
    """
    Generate 3 answer choices including the correct answer.
    
    Args:
        correct_answer: The correct minimum number of dice throws
        
    Returns:
        List of 3 answer choices in random order
    """
    choices = [correct_answer]
    
    # Generate two wrong answers
    # One slightly higher, one slightly lower
    lower_bound = max(1, correct_answer - 3)
    upper_bound = correct_answer + 5
    
    wrong_answers = []
    attempts = 0
    max_attempts = 50
    
    while len(wrong_answers) < 2 and attempts < max_attempts:
        attempts += 1
        wrong = random.randint(lower_bound, upper_bound)
        if wrong != correct_answer and wrong not in wrong_answers:
            wrong_answers.append(wrong)
    
    # If we couldn't generate enough wrong answers, use simple offsets
    if len(wrong_answers) < 2:
        if correct_answer > 1:
            wrong_answers.append(correct_answer - 1)
        if len(wrong_answers) < 2:
            wrong_answers.append(correct_answer + 2)
    
    choices.extend(wrong_answers[:2])
    random.shuffle(choices)
    
    return choices
