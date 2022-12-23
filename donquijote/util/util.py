import re


def int_cast(input):
    """
    Attempts to cast the input to an integer. If the input cannot be cast to an integer, returns None.

    Args:
        input (any): The input to be cast to an integer.

    Returns:
        int: The input as an integer if it can be cast, None otherwise.
    """
    try:
        return int(input)
    except ValueError:
        return None


def time_cast(input):
    """
    Attempts to cast the input to a time string in the format 'HH:MM'.
    If the input is not in the correct format or is an invalid time, returns None.

    Args:
        input (str): The input to be cast to a time string.

    Returns:
        str: The input as a time string if it is in the correct format and is a valid time, None otherwise.
    """
    time_regex = re.compile(r"^\d\d:\d\d$")

    if time_regex.match(input):
        if 24 >= int(input[:2]) >= 0 and 59 >= int(input[-2:]) >= 0:
            return input

    return None
