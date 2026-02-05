"""
Tests for ICS calendar export functionality.
"""

from datetime import datetime

import pytest

from src.ics_export import (
    get_first_occurrence,
    escape_ics_text,
    format_datetime,
    format_date,
    generate_vevent,
    generate_ics,
)
from src.config import SEMESTER_DATES, SemesterDates
from src.utils.parsing import parse_days_to_codes, parse_time_to_hours_minutes
from src.models import Course, Meeting


class TestParseDays:
    """Tests for parse_days_to_codes function."""

    def test_mwf(self):
        assert set(parse_days_to_codes("MWF")) == {"M", "W", "F"}

    def test_tuth(self):
        assert set(parse_days_to_codes("TuTh")) == {"TU", "TH"}

    def test_mw(self):
        assert set(parse_days_to_codes("MW")) == {"M", "W"}

    def test_single_day(self):
        assert parse_days_to_codes("M") == ["M"]
        assert parse_days_to_codes("F") == ["F"]

    def test_tuth_uppercase(self):
        assert set(parse_days_to_codes("TUTH")) == {"TU", "TH"}

    def test_mixed(self):
        # MWF with Tuesday
        result = parse_days_to_codes("MTuWF")
        assert "M" in result
        assert "TU" in result
        assert "W" in result
        assert "F" in result

    def test_saturday(self):
        assert "SA" in parse_days_to_codes("Sa")

    def test_empty(self):
        assert parse_days_to_codes("") == []


class TestParseTime:
    """Tests for parse_time_to_hours_minutes function."""

    def test_am_time(self):
        assert parse_time_to_hours_minutes("10:10 AM") == (10, 10)
        assert parse_time_to_hours_minutes("9:30 AM") == (9, 30)

    def test_pm_time(self):
        assert parse_time_to_hours_minutes("2:30 PM") == (14, 30)
        assert parse_time_to_hours_minutes("1:00 PM") == (13, 0)

    def test_noon(self):
        assert parse_time_to_hours_minutes("12:00 PM") == (12, 0)
        assert parse_time_to_hours_minutes("12:30 PM") == (12, 30)

    def test_midnight(self):
        assert parse_time_to_hours_minutes("12:00 AM") == (0, 0)

    def test_no_space(self):
        assert parse_time_to_hours_minutes("10:10AM") == (10, 10)
        assert parse_time_to_hours_minutes("2:30PM") == (14, 30)

    def test_lowercase(self):
        assert parse_time_to_hours_minutes("10:10 am") == (10, 10)
        assert parse_time_to_hours_minutes("2:30 pm") == (14, 30)

    def test_military_format(self):
        assert parse_time_to_hours_minutes("1430") == (14, 30)
        assert parse_time_to_hours_minutes("0930") == (9, 30)

    def test_24h_format_no_period(self):
        assert parse_time_to_hours_minutes("14:30") == (14, 30)
        assert parse_time_to_hours_minutes("9:30") == (9, 30)

    def test_invalid(self):
        assert parse_time_to_hours_minutes("invalid") == (0, 0)


class TestGetFirstOccurrence:
    """Tests for get_first_occurrence function."""
    
    def test_same_day(self):
        # Sept 3, 2025 is a Wednesday
        start = datetime(2025, 9, 3)
        result = get_first_occurrence(start, "W")
        assert result.weekday() == 2  # Wednesday
        assert result == start
    
    def test_next_day(self):
        # Sept 3, 2025 is a Wednesday, Thursday is Sept 4
        start = datetime(2025, 9, 3)
        result = get_first_occurrence(start, "TH")
        assert result.weekday() == 3  # Thursday
        assert result.day == 4
    
    def test_monday_from_wednesday(self):
        # Sept 3, 2025 is Wednesday, next Monday is Sept 8
        start = datetime(2025, 9, 3)
        result = get_first_occurrence(start, "M")
        assert result.weekday() == 0  # Monday
        assert result.day == 8
    
    def test_friday_from_wednesday(self):
        # Sept 3, 2025 is Wednesday, Friday is Sept 5
        start = datetime(2025, 9, 3)
        result = get_first_occurrence(start, "F")
        assert result.weekday() == 4  # Friday
        assert result.day == 5


class TestEscapeIcsText:
    """Tests for escape_ics_text function."""
    
    def test_no_escaping_needed(self):
        assert escape_ics_text("Hello World") == "Hello World"
    
    def test_escape_comma(self):
        assert escape_ics_text("Hello, World") == "Hello\\, World"
    
    def test_escape_semicolon(self):
        assert escape_ics_text("Hello; World") == "Hello\\; World"
    
    def test_escape_backslash(self):
        assert escape_ics_text("Hello\\World") == "Hello\\\\World"
    
    def test_escape_newline(self):
        assert escape_ics_text("Hello\nWorld") == "Hello\\nWorld"
    
    def test_escape_multiple(self):
        text = "Hello, World; Goodbye\nFriend"
        expected = "Hello\\, World\\; Goodbye\\nFriend"
        assert escape_ics_text(text) == expected


class TestFormatDateTime:
    """Tests for format_datetime function."""
    
    def test_format(self):
        dt = datetime(2025, 9, 3, 10, 30, 0)
        assert format_datetime(dt) == "20250903T103000"
    
    def test_with_zeros(self):
        dt = datetime(2025, 1, 5, 9, 5, 0)
        assert format_datetime(dt) == "20250105T090500"


class TestFormatDate:
    """Tests for format_date function."""
    
    def test_format(self):
        dt = datetime(2025, 12, 10)
        assert format_date(dt) == "20251210"


class TestGenerateVevent:
    """Tests for generate_vevent function."""
    
    @pytest.fixture
    def sample_course(self):
        return Course(
            id="CAS-CS-111-A1-Fall2025",
            code="CAS CS 111",
            title="Intro to CS",
            section="A1",
            professor="John Smith",
            term="Fall 2025",
            credits=4,
            department="CS",
            college="CAS",
            schedule=[
                Meeting(
                    days="MWF",
                    start_time="10:10 AM",
                    end_time="11:00 AM",
                    location="CAS 313",
                )
            ],
        )
    
    @pytest.fixture
    def semester_dates(self):
        return SEMESTER_DATES["Fall 2025"]
    
    def test_vevent_structure(self, sample_course, semester_dates):
        meeting = sample_course.schedule[0]
        vevent = generate_vevent(sample_course, meeting, "M", semester_dates)
        
        assert "BEGIN:VEVENT" in vevent
        assert "END:VEVENT" in vevent
        assert "UID:" in vevent
        assert "DTSTART:" in vevent
        assert "DTEND:" in vevent
        assert "RRULE:" in vevent
        assert "SUMMARY:" in vevent
    
    def test_vevent_summary(self, sample_course, semester_dates):
        meeting = sample_course.schedule[0]
        vevent = generate_vevent(sample_course, meeting, "M", semester_dates)
        
        assert "SUMMARY:CAS CS 111: Intro to CS" in vevent
    
    def test_vevent_location(self, sample_course, semester_dates):
        meeting = sample_course.schedule[0]
        vevent = generate_vevent(sample_course, meeting, "M", semester_dates)
        
        assert "LOCATION:CAS 313" in vevent
    
    def test_vevent_rrule(self, sample_course, semester_dates):
        meeting = sample_course.schedule[0]
        vevent = generate_vevent(sample_course, meeting, "M", semester_dates)
        
        assert "RRULE:FREQ=WEEKLY;BYDAY=MO" in vevent
        assert "UNTIL=20251210" in vevent
    
    def test_vevent_description(self, sample_course, semester_dates):
        meeting = sample_course.schedule[0]
        vevent = generate_vevent(sample_course, meeting, "M", semester_dates)
        
        assert "DESCRIPTION:" in vevent
        assert "Section: A1" in vevent
        assert "Professor: John Smith" in vevent


class TestGenerateIcs:
    """Tests for generate_ics function."""
    
    @pytest.fixture
    def sample_courses(self):
        return [
            Course(
                id="CAS-CS-111-A1-Fall2025",
                code="CAS CS 111",
                title="Intro to CS",
                section="A1",
                professor="John Smith",
                term="Fall 2025",
                credits=4,
                department="CS",
                college="CAS",
                schedule=[
                    Meeting(
                        days="MWF",
                        start_time="10:10 AM",
                        end_time="11:00 AM",
                        location="CAS 313",
                    )
                ],
            ),
            Course(
                id="CAS-CS-112-A1-Fall2025",
                code="CAS CS 112",
                title="Data Structures",
                section="A1",
                professor="Jane Doe",
                term="Fall 2025",
                credits=4,
                department="CS",
                college="CAS",
                schedule=[
                    Meeting(
                        days="TuTh",
                        start_time="11:00 AM",
                        end_time="12:15 PM",
                        location="CAS 522",
                    )
                ],
            ),
        ]
    
    def test_ics_structure(self, sample_courses):
        ics = generate_ics(sample_courses)
        
        assert "BEGIN:VCALENDAR" in ics
        assert "END:VCALENDAR" in ics
        assert "VERSION:2.0" in ics
        assert "PRODID:" in ics
    
    def test_ics_contains_events(self, sample_courses):
        ics = generate_ics(sample_courses)
        
        # MWF course should generate 3 events
        # TuTh course should generate 2 events
        assert ics.count("BEGIN:VEVENT") == 5
        assert ics.count("END:VEVENT") == 5
    
    def test_ics_course_titles(self, sample_courses):
        ics = generate_ics(sample_courses)
        
        assert "CAS CS 111" in ics
        assert "CAS CS 112" in ics
    
    def test_ics_empty_courses(self):
        ics = generate_ics([])
        
        assert "BEGIN:VCALENDAR" in ics
        assert "END:VCALENDAR" in ics
        assert "BEGIN:VEVENT" not in ics
    
    def test_ics_with_term_override(self, sample_courses):
        ics = generate_ics(sample_courses, term="Spring 2026")
        
        # Should use Spring 2026 dates (ends May 6)
        assert "UNTIL=20260506" in ics
    
    def test_ics_course_no_schedule(self):
        course = Course(
            id="TEST-101",
            code="TEST 101",
            title="Test",
            section="A1",
            professor="Test",
            term="Fall 2025",
            credits=3,
            department="TEST",
            college="CAS",
            schedule=[],
        )
        ics = generate_ics([course])
        
        # Should still be valid but no events
        assert "BEGIN:VCALENDAR" in ics
        assert "BEGIN:VEVENT" not in ics
    
    def test_ics_uses_crlf(self, sample_courses):
        """ICS files should use CRLF line endings per RFC 5545."""
        ics = generate_ics(sample_courses)
        assert "\r\n" in ics
