# talents/talent_utils.py
import logging
from typing import Union
from enum import Enum

logger = logging.getLogger(__name__)

def has_talent(
    talent_string: str,
    talent_index: Union[int, Enum], # Accept index or Enum member
    expected_amount: int,
    mode: str = "at_least",
) -> bool:
    """
    Check if a talent at a specific index in the talent string meets a condition.

    Parameters:
        talent_string (str): The string of allocated talent points (e.g., "5030...").
        talent_index (int or Enum): The zero-based index or Enum member representing the talent.
        expected_amount (int): The amount to compare against.
        mode (str): Condition mode - "at_least", "at_most", "exact", "less_than".

    Returns:
        bool: Whether the condition is met.
    """
    # If Enum member is passed, get its value (which should be the index)
    if hasattr(talent_index, 'value'):
        index = talent_index.value
    else:
        index = int(talent_index) # Assume it's already an int

    if not isinstance(talent_string, str) or index < 0 or index >= len(talent_string):
        logger.error(f"Invalid talent string or index ({index}) for check.")
        return False # Invalid input

    try:
        # Talent points are single digits in the string
        talent_value = int(talent_string[index])
    except (ValueError, IndexError):
        logger.warning(f"Could not read talent value at index {index} from string.")
        return False # Error reading value, treat as condition not met

    if mode == "exact":
        return talent_value == expected_amount
    elif mode == "at_most":
        return talent_value <= expected_amount
    elif mode == "less_than":
        return talent_value < expected_amount
    elif mode == "at_least": # Default case
        return talent_value >= expected_amount
    else:
        logger.warning(f"Unknown mode '{mode}' in has_talent check.")
        return False

