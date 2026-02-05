"""
Shared parsing utilities for time and day strings.

Consolidates duplicate parsing logic from search.py, schedule_builder.py, and ics_export.py.
"""

import re


# Day code mappings
DAY_CODES = {
    "MO": "Monday",
    "TU": "Tuesday",
    "WE": "Wednesday",
    "TH": "Thursday",
    "FR": "Friday",
    "SA": "Saturday",
    "SU": "Sunday",
}

# Reverse mapping (full name to code)
DAY_NAME_TO_CODE = {
    "Monday": "MO",
    "Tuesday": "TU",
    "Wednesday": "WE",
    "Thursday": "TH",
    "Friday": "FR",
    "Saturday": "SA",
    "Sunday": "SU",
}

# iCalendar day codes
ICAL_DAY_MAP = {
    "M": "MO",
    "TU": "TU",
    "W": "WE",
    "TH": "TH",
    "F": "FR",
    "SA": "SA",
    "SU": "SU",
}

# Day code to weekday number (Monday = 0)
DAY_TO_WEEKDAY = {
    "M": 0,
    "TU": 1,
    "W": 2,
    "TH": 3,
    "F": 4,
    "SA": 5,
    "SU": 6,
}

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_time_to_minutes(time_str: str) -> int:
    """
    Convert time string to minutes since midnight.

    Handles formats:
    - "9:30 AM" / "2:30 PM"
    - "9:30" / "14:30" (with or without AM/PM)
    - "1430" (4-digit military time)

    Args:
        time_str: Time string to parse

    Returns:
        Minutes since midnight (0-1439)

    Examples:
        >>> parse_time_to_minutes("9:30 AM")
        570
        >>> parse_time_to_minutes("2:30 PM")
        870
        >>> parse_time_to_minutes("14:30")
        870
    """
    time_str = time_str.strip().upper()

    # Check for AM/PM
    is_pm = "PM" in time_str
    is_am = "AM" in time_str
    time_str = time_str.replace("AM", "").replace("PM", "").strip()

    # Try format with colon (e.g., "9:30")
    if ":" in time_str:
        parts = time_str.split(":")
        h = int(parts[0])
        m = int(parts[1].split()[0])  # Handle trailing whitespace

        # Convert to 24-hour format
        if is_pm and h != 12:
            h += 12
        elif is_am and h == 12:
            h = 0

        return h * 60 + m

    # Try 4-digit format (e.g., "1430")
    if time_str.isdigit():
        if len(time_str) == 4:
            return int(time_str[:2]) * 60 + int(time_str[2:])
        # Assume hours only
        return int(time_str) * 60

    return 0


def parse_time_to_hours_minutes(time_str: str) -> tuple[int, int]:
    """
    Parse time string into (hour, minute) in 24-hour format.

    Args:
        time_str: Time string to parse

    Returns:
        Tuple of (hour, minute) in 24-hour format

    Examples:
        >>> parse_time_to_hours_minutes("9:30 AM")
        (9, 30)
        >>> parse_time_to_hours_minutes("2:30 PM")
        (14, 30)
    """
    minutes = parse_time_to_minutes(time_str)
    return minutes // 60, minutes % 60


def parse_days_to_codes(days_str: str) -> list[str]:
    """
    Parse day string into list of two-letter day codes.

    Examples:
        'MWF' -> ['M', 'W', 'F']
        'TuTh' -> ['TU', 'TH']
        'MoWeFr' -> ['MO', 'WE', 'FR']

    Args:
        days_str: Day string like 'MWF', 'TuTh', 'MoWeFr'

    Returns:
        List of day codes (e.g., ['M', 'W', 'F'] or ['TU', 'TH'])
    """
    result = []
    days_upper = days_str.upper()

    # Check for two-letter codes first
    for two_letter in ["TU", "TH", "SA", "SU", "MO", "WE", "FR"]:
        if two_letter in days_upper:
            result.append(two_letter)
            days_upper = days_upper.replace(two_letter, "", 1)

    # Single letter codes (for format like "MWF")
    for char in days_upper:
        if char == 'M' and 'MO' not in result:
            result.append('M')
        elif char == 'W' and 'WE' not in result:
            result.append('W')
        elif char == 'F' and 'FR' not in result:
            result.append('F')

    return result


def parse_days_to_full_names(days_str: str) -> list[str]:
    """
    Parse day string into list of full day names.

    Examples:
        'MoWeFr' -> ['Monday', 'Wednesday', 'Friday']
        'TuTh' -> ['Tuesday', 'Thursday']
        'MWF' -> ['Monday', 'Wednesday', 'Friday']

    Args:
        days_str: Day string like 'MWF', 'TuTh', 'MoWeFr'

    Returns:
        List of full day names
    """
    codes = parse_days_to_codes(days_str)
    names = []

    for code in codes:
        if code in DAY_CODES:
            names.append(DAY_CODES[code])
        elif code == 'M':
            names.append('Monday')
        elif code == 'W':
            names.append('Wednesday')
        elif code == 'F':
            names.append('Friday')

    return names


def parse_days_to_set(days_str: str) -> set[str]:
    """
    Parse day string into set of day codes for overlap detection.

    Used by search.py for conflict detection.

    Args:
        days_str: Day string like 'MWF' or 'TuTh'

    Returns:
        Set of day codes
    """
    result = set()
    days = days_str.upper()

    # Two-letter codes
    for two_letter in ["TU", "TH", "SA", "SU"]:
        if two_letter in days:
            result.add(two_letter)
            days = days.replace(two_letter, "")

    # Single letter codes
    for char in days:
        if char in "MTWFS":
            result.add(char)

    return result
