"""
Tower of Hanoi Move Validation System
Validates player move sequences against game rules and checks completion
"""

from typing import List, Dict, Tuple, Optional
import re


class GameState:
    """Represents the current state of the Tower of Hanoi game"""
    
    def __init__(self, n_disks: int, peg_count: int, source: str = 'A', destination: str = 'D'):
        self.n_disks = n_disks
        self.peg_count = peg_count
        self.source = source
        self.destination = destination
        
        # Initialize pegs - source has all disks (largest=n to smallest=1)
        self.pegs = {}
        valid_pegs = ['A', 'B', 'C'] if peg_count == 3 else ['A', 'B', 'C', 'D']
        
        for peg in valid_pegs:
            self.pegs[peg] = []
        
        # Place all disks on source peg (largest at bottom)
        self.pegs[source] = list(range(n_disks, 0, -1))
        
        self.valid_pegs = set(valid_pegs)
        self.move_count = 0
    
    def copy(self) -> 'GameState':
        """Create a deep copy of the game state"""
        new_state = GameState(self.n_disks, self.peg_count, self.source, self.destination)
        new_state.pegs = {peg: stack.copy() for peg, stack in self.pegs.items()}
        new_state.move_count = self.move_count
        return new_state
    
    def get_top_disk(self, peg: str) -> Optional[int]:
        """Get the top disk of a peg (None if empty)"""
        if peg not in self.pegs or not self.pegs[peg]:
            return None
        return self.pegs[peg][-1]
    
    def is_complete(self) -> bool:
        """Check if all disks are on the destination peg in correct order"""
        dest_stack = self.pegs[self.destination]
        if len(dest_stack) != self.n_disks:
            return False
        
        # Check if disks are in correct order (largest at bottom)
        expected = list(range(self.n_disks, 0, -1))
        return dest_stack == expected
    
    def get_state_string(self) -> str:
        """Get a string representation of the current state"""
        state_parts = []
        for peg in sorted(self.pegs.keys()):
            stack = self.pegs[peg]
            stack_str = str(stack) if stack else "[]"
            state_parts.append(f"{peg}: {stack_str}")
        return " | ".join(state_parts)


class ValidationError:
    """Represents a validation error with details"""
    
    def __init__(self, move_index: int, move: str, error_type: str, message: str, state: GameState = None):
        self.move_index = move_index
        self.move = move
        self.error_type = error_type
        self.message = message
        self.state = state
    
    def to_dict(self) -> Dict:
        return {
            'move_index': self.move_index,
            'move': self.move,
            'error_type': self.error_type,
            'message': self.message,
            'state': self.state.get_state_string() if self.state else None
        }


class MoveValidator:
    """Validates Tower of Hanoi move sequences"""
    
    # Move format pattern: X->Y where X and Y are single characters
    MOVE_PATTERN = re.compile(r'^([A-Z])->([A-Z])$')
    
    def __init__(self):
        self.error_types = {
            'INVALID_FORMAT': 'Invalid move format',
            'INVALID_PEG': 'Invalid peg label',
            'SAME_PEG': 'Source and destination are the same',
            'EMPTY_SOURCE': 'Source peg is empty',
            'LARGER_ON_SMALLER': 'Cannot place larger disk on smaller disk',
            'INCOMPLETE_SOLUTION': 'Solution does not complete the puzzle',
            'SEQUENCE_TOO_SHORT': 'Move sequence is too short',
            'SEQUENCE_TOO_LONG': 'Move sequence is suspiciously long'
        }
    
    def validate_move_format(self, move: str) -> Tuple[bool, Optional[str], Optional[Tuple[str, str]]]:
        """
        Validate the format of a single move
        
        Returns:
            (is_valid, error_message, (source_peg, dest_peg))
        """
        if not isinstance(move, str):
            return False, "Move must be a string", None
        
        move = move.strip()
        match = self.MOVE_PATTERN.match(move)
        
        if not match:
            return False, f"Invalid move format: '{move}'. Expected format: 'X->Y'", None
        
        source, dest = match.groups()
        
        if source == dest:
            return False, f"Source and destination cannot be the same: '{move}'", None
        
        return True, None, (source, dest)
    
    def validate_move_sequence(self, moves: List[str], initial_state: GameState) -> Tuple[bool, List[ValidationError], GameState]:
        """
        Validate a complete move sequence
        
        Args:
            moves: List of move strings
            initial_state: Starting game state
        
        Returns:
            (is_valid, validation_errors, final_state)
        """
        errors = []
        state = initial_state.copy()
        
        # Basic sequence validation
        if not moves:
            error = ValidationError(
                move_index=0,
                move="",
                error_type='SEQUENCE_TOO_SHORT',
                message="Move sequence cannot be empty"
            )
            return False, [error], state
        
        # Check for reasonable sequence length (exponential upper bound)
        max_reasonable_moves = 2 ** (initial_state.n_disks + 2)
        if len(moves) > max_reasonable_moves:
            error = ValidationError(
                move_index=len(moves),
                move="",
                error_type='SEQUENCE_TOO_LONG',
                message=f"Move sequence too long: {len(moves)} moves (max reasonable: {max_reasonable_moves})"
            )
            errors.append(error)
        
        # Validate each move
        for i, move in enumerate(moves):
            # Validate move format
            is_valid_format, format_error, peg_pair = self.validate_move_format(move)
            
            if not is_valid_format:
                error = ValidationError(
                    move_index=i + 1,
                    move=move,
                    error_type='INVALID_FORMAT',
                    message=format_error,
                    state=state
                )
                errors.append(error)
                continue
            
            source_peg, dest_peg = peg_pair
            
            # Validate peg labels
            if source_peg not in state.valid_pegs:
                error = ValidationError(
                    move_index=i + 1,
                    move=move,
                    error_type='INVALID_PEG',
                    message=f"Invalid source peg '{source_peg}'. Valid pegs: {sorted(state.valid_pegs)}",
                    state=state
                )
                errors.append(error)
                continue
            
            if dest_peg not in state.valid_pegs:
                error = ValidationError(
                    move_index=i + 1,
                    move=move,
                    error_type='INVALID_PEG',
                    message=f"Invalid destination peg '{dest_peg}'. Valid pegs: {sorted(state.valid_pegs)}",
                    state=state
                )
                errors.append(error)
                continue
            
            # Validate move legality
            move_error = self._validate_single_move(i + 1, move, source_peg, dest_peg, state)
            if move_error:
                errors.append(move_error)
                continue
            
            # Execute the move if valid
            self._execute_move(source_peg, dest_peg, state)
        
        # Check if puzzle is completed
        if not errors and not state.is_complete():
            error = ValidationError(
                move_index=len(moves),
                move="",
                error_type='INCOMPLETE_SOLUTION',
                message=f"Puzzle not completed. Final state: {state.get_state_string()}",
                state=state
            )
            errors.append(error)
        
        return len(errors) == 0, errors, state
    
    def _validate_single_move(self, move_index: int, move: str, source: str, dest: str, state: GameState) -> Optional[ValidationError]:
        """Validate a single move against current game state"""
        
        # Check if source peg has disks
        top_disk = state.get_top_disk(source)
        if top_disk is None:
            return ValidationError(
                move_index=move_index,
                move=move,
                error_type='EMPTY_SOURCE',
                message=f"Cannot move from empty peg '{source}'",
                state=state
            )
        
        # Check if move violates the "larger on smaller" rule
        dest_top_disk = state.get_top_disk(dest)
        if dest_top_disk is not None and top_disk > dest_top_disk:
            return ValidationError(
                move_index=move_index,
                move=move,
                error_type='LARGER_ON_SMALLER',
                message=f"Cannot place disk {top_disk} on smaller disk {dest_top_disk} (peg {dest})",
                state=state
            )
        
        return None
    
    def _execute_move(self, source: str, dest: str, state: GameState):
        """Execute a validated move on the game state"""
        disk = state.pegs[source].pop()
        state.pegs[dest].append(disk)
        state.move_count += 1
    
    def get_detailed_error_report(self, errors: List[ValidationError]) -> str:
        """Generate a detailed human-readable error report"""
        if not errors:
            return "✅ All moves are valid!"
        
        report = f"❌ Found {len(errors)} validation error(s):\n\n"
        
        for i, error in enumerate(errors, 1):
            report += f"{i}. Move #{error.move_index}"
            if error.move:
                report += f" ('{error.move}')"
            report += f": {error.message}\n"
            
            if error.state:
                report += f"   State before move: {error.state.get_state_string()}\n"
            report += "\n"
        
        return report.strip()
    
    def validate_declared_moves(self, declared: int, actual: int, tolerance: int = 0) -> Tuple[bool, str]:
        """
        Validate declared move count against actual moves
        
        Args:
            declared: Player's declared number of moves
            actual: Actual number of moves in sequence
            tolerance: Allowed difference (for flexibility)
        
        Returns:
            (is_valid, message)
        """
        if declared < 0:
            return False, "Declared move count cannot be negative"
        
        if abs(declared - actual) <= tolerance:
            return True, "Declared move count matches actual moves"
        
        return False, f"Declared {declared} moves but sequence has {actual} moves (difference: {abs(declared - actual)})"


class GameValidator:
    """Main validator class that combines all validation logic"""
    
    def __init__(self):
        self.move_validator = MoveValidator()
    
    def validate_submission(self, 
                          n_disks: int, 
                          peg_count: int, 
                          move_sequence: List[str], 
                          declared_moves: int = None,
                          source: str = 'A', 
                          destination: str = None) -> Dict:
        """
        Validate a complete game submission
        
        Args:
            n_disks: Number of disks in the game
            peg_count: Number of pegs (3 or 4)
            move_sequence: List of move strings
            declared_moves: Player's declared number of moves
            source: Source peg label
            destination: Destination peg label
        
        Returns:
            Dictionary with validation results
        """
        # Set default destination based on peg count
        if destination is None:
            destination = 'D' if peg_count == 4 else 'C'
        
        # Create initial game state
        initial_state = GameState(n_disks, peg_count, source, destination)
        
        # Validate move sequence
        is_valid, errors, final_state = self.move_validator.validate_move_sequence(move_sequence, initial_state)
        
        # Validate declared moves if provided
        declared_valid = True
        declared_message = ""
        
        if declared_moves is not None:
            declared_valid, declared_message = self.move_validator.validate_declared_moves(
                declared_moves, len(move_sequence)
            )
        
        # Overall validation result
        overall_valid = is_valid and declared_valid
        
        return {
            'is_valid': overall_valid,
            'move_sequence_valid': is_valid,
            'declared_moves_valid': declared_valid,
            'declared_moves_message': declared_message,
            'total_moves': len(move_sequence),
            'puzzle_completed': final_state.is_complete() if is_valid else False,
            'errors': [error.to_dict() for error in errors],
            'error_count': len(errors),
            'detailed_report': self.move_validator.get_detailed_error_report(errors),
            'final_state': final_state.get_state_string(),
            'initial_state': initial_state.get_state_string()
        }


# Convenience functions for external use
def validate_tower_of_hanoi_solution(n_disks: int, 
                                    peg_count: int, 
                                    moves: List[str], 
                                    declared_moves: int = None,
                                    source: str = 'A',
                                    destination: str = None) -> Dict:
    """
    Validate a Tower of Hanoi solution
    
    Args:
        n_disks: Number of disks
        peg_count: Number of pegs (3 or 4)  
        moves: List of move strings in format "X->Y"
        declared_moves: Optional declared number of moves
    
    Returns:
        Validation result dictionary
    """
    validator = GameValidator()
    return validator.validate_submission(n_disks, peg_count, moves, declared_moves, source, destination)


def parse_move_sequence(move_string: str) -> List[str]:
    """
    Parse a move sequence from various string formats
    
    Supports:
    - Comma-separated: "A->B, A->C, B->C"
    - Space-separated: "A->B A->C B->C"
    - Newline-separated: "A->B\nA->C\nB->C"
    """
    if not move_string:
        return []
    
    # Replace common separators with commas
    move_string = move_string.replace('\n', ',').replace('\r', ',').replace(';', ',')
    
    # Split by comma and clean up
    moves = [move.strip() for move in move_string.split(',')]
    
    # If no commas found, try splitting by spaces
    if len(moves) == 1 and ' ' in moves[0]:
        moves = moves[0].split()
    
    # Filter out empty moves
    return [move for move in moves if move]


if __name__ == "__main__":
    # Example usage and testing
    print("🔍 Tower of Hanoi Move Validator Testing")
    print("=" * 50)
    
    # Test case 1: Valid 3-disk solution
    print("\n✅ Test 1: Valid 3-disk, 3-peg solution")
    moves_valid = ["A->C", "A->B", "C->B", "A->C", "B->A", "B->C", "A->C"]
    result = validate_tower_of_hanoi_solution(3, 3, moves_valid, 7)
    print(f"Valid: {result['is_valid']}")
    print(f"Completed: {result['puzzle_completed']}")
    
    # Test case 2: Invalid move (larger on smaller)
    print("\n❌ Test 2: Invalid move sequence")
    moves_invalid = ["A->B", "A->C", "A->B"]  # This will try to put larger disk on smaller
    result = validate_tower_of_hanoi_solution(3, 3, moves_invalid)
    print(f"Valid: {result['is_valid']}")
    print(f"Errors: {result['error_count']}")
    if result['errors']:
        print(f"First error: {result['errors'][0]['message']}")
    
    # Test case 3: String parsing
    print("\n📝 Test 3: String parsing")
    move_string = "A->C, A->B, C->B, A->C, B->A, B->C, A->C"
    parsed_moves = parse_move_sequence(move_string)
    print(f"Parsed moves: {parsed_moves}")
    result = validate_tower_of_hanoi_solution(3, 3, parsed_moves)
    print(f"Valid: {result['is_valid']}")