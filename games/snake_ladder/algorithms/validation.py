"""
Input Validation and Exception Handling Module
Centralized validation and error handling for Snake and Ladder game
"""

from typing import Any, Optional
import re


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class GameError(Exception):
    """Custom exception for game-related errors."""
    pass


class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass


def validate_board_size_strict(board_size: Any) -> int:
    """
    Strictly validate board size input.
    
    Args:
        board_size: Board size to validate
        
    Returns:
        Validated board size as integer
        
    Raises:
        ValidationError: If validation fails
    """
    # Check type
    if not isinstance(board_size, (int, str)):
        raise ValidationError(
            f"Board size must be an integer or numeric string, got {type(board_size).__name__}"
        )
    
    # Convert to int if string
    try:
        size = int(board_size)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid board size format: {board_size}") from e
    
    # Check range
    if size < 6:
        raise ValidationError(
            f"Board size {size} is too small. Minimum size is 6."
        )
    
    if size > 12:
        raise ValidationError(
            f"Board size {size} is too large. Maximum size is 12."
        )
    
    return size


def validate_player_name(name: Any, min_length: int = 1, max_length: int = 100) -> str:
    """
    Validate player name input.
    
    Args:
        name: Player name to validate
        min_length: Minimum name length
        max_length: Maximum name length
        
    Returns:
        Validated and sanitized player name
        
    Raises:
        ValidationError: If validation fails
    """
    # Check type
    if not isinstance(name, str):
        raise ValidationError(
            f"Player name must be a string, got {type(name).__name__}"
        )
    
    # Strip whitespace
    name = name.strip()
    
    # Check emptiness
    if not name:
        raise ValidationError("Player name cannot be empty")
    
    # Check length
    if len(name) < min_length:
        raise ValidationError(
            f"Player name must be at least {min_length} characters long"
        )
    
    if len(name) > max_length:
        raise ValidationError(
            f"Player name must not exceed {max_length} characters"
        )
    
    # Check for invalid characters (optional - allow most Unicode)
    # Remove control characters
    if any(ord(char) < 32 for char in name):
        raise ValidationError(
            "Player name contains invalid control characters"
        )
    
    return name


def validate_email(email: Optional[str]) -> Optional[str]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate (can be None)
        
    Returns:
        Validated email or None
        
    Raises:
        ValidationError: If email format is invalid
    """
    if email is None or email == "":
        return None
    
    if not isinstance(email, str):
        raise ValidationError(
            f"Email must be a string, got {type(email).__name__}"
        )
    
    email = email.strip()
    
    if not email:
        return None
    
    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValidationError(
            f"Invalid email format: {email}"
        )
    
    if len(email) > 150:
        raise ValidationError(
            "Email address is too long (max 150 characters)"
        )
    
    return email


def validate_player_answer(answer: Any, min_value: int = 0) -> int:
    """
    Validate player's answer input.
    
    Args:
        answer: Player's answer to validate
        min_value: Minimum valid answer value
        
    Returns:
        Validated answer as integer
        
    Raises:
        ValidationError: If validation fails
    """
    # Check type
    if not isinstance(answer, (int, str)):
        raise ValidationError(
            f"Answer must be an integer or numeric string, got {type(answer).__name__}"
        )
    
    # Convert to int if string
    try:
        answer_int = int(answer)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid answer format: {answer}") from e
    
    # Check range
    if answer_int < min_value:
        raise ValidationError(
            f"Answer must be at least {min_value}, got {answer_int}"
        )
    
    # Sanity check - answer shouldn't be absurdly large
    if answer_int > 1000:
        raise ValidationError(
            f"Answer {answer_int} is unreasonably large"
        )
    
    return answer_int


def validate_session_id(session_id: Any) -> str:
    """
    Validate session ID format.
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        Validated session ID
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(session_id, str):
        raise ValidationError(
            f"Session ID must be a string, got {type(session_id).__name__}"
        )
    
    session_id = session_id.strip()
    
    if not session_id:
        raise ValidationError("Session ID cannot be empty")
    
    # Check format (should start with "session_")
    if not session_id.startswith("session_"):
        raise ValidationError(
            f"Invalid session ID format: {session_id}"
        )
    
    # Check length
    if len(session_id) > 100:
        raise ValidationError(
            "Session ID is too long"
        )
    
    return session_id


def validate_limit(limit: Any, min_limit: int = 1, max_limit: int = 100) -> int:
    """
    Validate limit parameter for pagination.
    
    Args:
        limit: Limit value to validate
        min_limit: Minimum valid limit
        max_limit: Maximum valid limit
        
    Returns:
        Validated limit as integer
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        limit_int = int(limit)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid limit format: {limit}") from e
    
    if limit_int < min_limit:
        raise ValidationError(
            f"Limit must be at least {min_limit}, got {limit_int}"
        )
    
    if limit_int > max_limit:
        raise ValidationError(
            f"Limit must not exceed {max_limit}, got {limit_int}"
        )
    
    return limit_int


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer with default fallback.
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize string input for safe storage.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Trim whitespace
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def handle_exception(e: Exception, context: str = "") -> dict:
    """
    Handle exceptions and return formatted error response.
    
    Args:
        e: Exception to handle
        context: Context information about where error occurred
        
    Returns:
        Dictionary with error details
    """
    error_type = type(e).__name__
    error_message = str(e)
    
    if context:
        full_message = f"{context}: {error_message}"
    else:
        full_message = error_message
    
    return {
        "error": True,
        "error_type": error_type,
        "message": full_message,
        "details": error_message
    }


# Exception handler decorators
def validate_inputs(func):
    """
    Decorator to automatically validate function inputs.
    Catches ValidationError and returns formatted error.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            return handle_exception(e, f"Validation error in {func.__name__}")
    return wrapper


def handle_errors(func):
    """
    Decorator to handle general errors in functions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return handle_exception(e, f"Error in {func.__name__}")
    return wrapper


# Validation summary
def validate_game_init_request(player_name: str, board_size: int, 
                               email: Optional[str] = None) -> dict:
    """
    Validate all inputs for game initialization.
    
    Args:
        player_name: Player's name
        board_size: Board size
        email: Player's email (optional)
        
    Returns:
        Dictionary with validation results
        
    Raises:
        ValidationError: If any validation fails
    """
    errors = []
    validated = {}
    
    try:
        validated['player_name'] = validate_player_name(player_name)
    except ValidationError as e:
        errors.append(str(e))
    
    try:
        validated['board_size'] = validate_board_size_strict(board_size)
    except ValidationError as e:
        errors.append(str(e))
    
    try:
        validated['email'] = validate_email(email)
    except ValidationError as e:
        errors.append(str(e))
    
    if errors:
        raise ValidationError("; ".join(errors))
    
    return validated


def validate_submit_answer_request(session_id: str, player_answer: int) -> dict:
    """
    Validate all inputs for answer submission.
    
    Args:
        session_id: Game session ID
        player_answer: Player's answer
        
    Returns:
        Dictionary with validation results
        
    Raises:
        ValidationError: If any validation fails
    """
    errors = []
    validated = {}
    
    try:
        validated['session_id'] = validate_session_id(session_id)
    except ValidationError as e:
        errors.append(str(e))
    
    try:
        validated['player_answer'] = validate_player_answer(player_answer)
    except ValidationError as e:
        errors.append(str(e))
    
    if errors:
        raise ValidationError("; ".join(errors))
    
    return validated
