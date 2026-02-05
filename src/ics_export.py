"""
ICS calendar export for course schedules.

Generates valid iCalendar (.ics) files with recurring events
for course meeting times throughout the semester.
"""

from datetime import datetime, timedelta
from uuid import uuid4

from src.models import Course, Meeting
from src.config import SEMESTER_DATES, DEFAULT_SEMESTER
from src.utils.parsing import parse_days_to_codes, parse_time_to_hours_minutes, ICAL_DAY_MAP, DAY_TO_WEEKDAY


def get_first_occurrence(semester_start: datetime, day_code: str) -> datetime:
    """Get the first occurrence of a weekday on or after semester start."""
    target_weekday = DAY_TO_WEEKDAY.get(day_code, 0)
    days_ahead = target_weekday - semester_start.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return semester_start + timedelta(days=days_ahead)


def format_datetime(dt: datetime) -> str:
    """Format datetime for iCalendar (YYYYMMDDTHHMMSS)."""
    return dt.strftime("%Y%m%dT%H%M%S")


def format_date(dt: datetime) -> str:
    """Format date for iCalendar UNTIL clause (YYYYMMDD)."""
    return dt.strftime("%Y%m%d")


def escape_ics_text(text: str) -> str:
    """Escape special characters for iCalendar text fields."""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text


def generate_vevent(
    course: Course,
    meeting: Meeting,
    day_code: str,
    semester_dates,
) -> str:
    """Generate a VEVENT for a single meeting day of a course."""
    start_hour, start_minute = parse_time_to_hours_minutes(meeting.start_time)
    end_hour, end_minute = parse_time_to_hours_minutes(meeting.end_time)
    
    # Get first occurrence of this day in the semester
    first_date = get_first_occurrence(semester_dates.start, day_code)
    
    # Create start and end datetimes
    dtstart = first_date.replace(hour=start_hour, minute=start_minute, second=0)
    dtend = first_date.replace(hour=end_hour, minute=end_minute, second=0)
    
    # iCalendar day code for RRULE
    ical_day = ICAL_DAY_MAP.get(day_code, "MO")
    
    # Build VEVENT
    uid = f"{course.id}-{day_code}-{uuid4().hex[:8]}@bu-courses"
    summary = escape_ics_text(f"{course.code}: {course.title}")
    location = escape_ics_text(meeting.location) if meeting.location else ""
    description = escape_ics_text(
        f"Section: {course.section}\\n"
        f"Professor: {course.professor}\\n"
        f"Credits: {course.credits}"
    )
    
    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{format_datetime(datetime.now())}",
        f"DTSTART:{format_datetime(dtstart)}",
        f"DTEND:{format_datetime(dtend)}",
        f"RRULE:FREQ=WEEKLY;BYDAY={ical_day};UNTIL={format_date(semester_dates.end)}T235959",
        f"SUMMARY:{summary}",
    ]
    
    if location:
        lines.append(f"LOCATION:{location}")
    
    lines.append(f"DESCRIPTION:{description}")
    lines.append("END:VEVENT")
    
    return "\r\n".join(lines)


def generate_ics(courses: list[Course], term: str | None = None) -> str:
    """
    Generate iCalendar content for a list of courses.
    
    Args:
        courses: List of courses to include in calendar
        term: Term to use for semester dates (e.g., "Fall 2025").
              If None, uses the term from the first course.
    
    Returns:
        Valid iCalendar (.ics) file content as string
    """
    if not courses:
        return _empty_calendar()
    
    # Determine term from first course if not specified
    if term is None:
        term = courses[0].term
    
    # Get semester dates, default to Fall 2025 if unknown
    semester_dates = SEMESTER_DATES.get(term, SEMESTER_DATES[DEFAULT_SEMESTER])

    # Build calendar header
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//BU Course Search//bu-courses//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:BU Course Schedule",
    ]

    # Generate events for each course meeting
    for course in courses:
        for meeting in course.schedule:
            if not meeting.days or not meeting.start_time or not meeting.end_time:
                continue

            # Parse days and create an event for each day
            day_codes = parse_days_to_codes(meeting.days)
            for day_code in day_codes:
                vevent = generate_vevent(course, meeting, day_code, semester_dates)
                lines.append(vevent)
    
    lines.append("END:VCALENDAR")
    
    return "\r\n".join(lines)


def _empty_calendar() -> str:
    """Return an empty but valid iCalendar."""
    return "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//BU Course Search//bu-courses//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:BU Course Schedule",
        "END:VCALENDAR",
    ])
