"""
Tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from src.models import Course, Meeting, ProfessorRating, Conflict


class TestMeeting:
    """Tests for Meeting model."""
    
    def test_valid_meeting(self):
        meeting = Meeting(
            days="MWF",
            start_time="10:10 AM",
            end_time="11:00 AM",
            location="CAS 313",
        )
        assert meeting.days == "MWF"
        assert meeting.start_time == "10:10 AM"
        assert meeting.end_time == "11:00 AM"
        assert meeting.location == "CAS 313"
    
    def test_meeting_required_fields(self):
        with pytest.raises(ValidationError):
            Meeting(days="MWF")  # Missing required fields


class TestCourse:
    """Tests for Course model."""
    
    def test_valid_course(self, sample_courses):
        course = sample_courses[0]
        assert course.id == "CAS-CS-111-A1-Fall2025"
        assert course.code == "CAS CS 111"
        assert course.credits == 4
    
    def test_search_text_property(self, sample_courses):
        course = sample_courses[0]
        search_text = course.search_text
        assert "CAS CS 111" in search_text
        assert "Introduction to Computer Science" in search_text
        assert "John Smith" in search_text
        assert "CS" in search_text
    
    def test_course_defaults(self):
        course = Course(
            id="TEST-101-A1",
            code="TEST 101",
            title="Test Course",
            section="A1",
            professor="Test Prof",
            term="Fall 2025",
            credits=3,
            department="TEST",
            college="CAS",
        )
        assert course.description == ""
        assert course.hub_units == []
        assert course.schedule == []
        assert course.status == ""
        assert course.professor_rating is None
    
    def test_course_with_professor_rating(self):
        rating = ProfessorRating(
            name="Test Prof",
            rating=4.5,
            num_ratings=100,
            difficulty=3.0,
            would_take_again=85.0,
            rmp_url="https://ratemyprofessors.com/professor/123",
        )
        course = Course(
            id="TEST-101-A1",
            code="TEST 101",
            title="Test Course",
            section="A1",
            professor="Test Prof",
            term="Fall 2025",
            credits=3,
            department="TEST",
            college="CAS",
            professor_rating=rating,
        )
        assert course.professor_rating is not None
        assert course.professor_rating.rating == 4.5


class TestProfessorRating:
    """Tests for ProfessorRating model."""
    
    def test_valid_rating(self):
        rating = ProfessorRating(
            name="John Smith",
            rating=4.5,
            num_ratings=100,
            difficulty=3.0,
            would_take_again=85.0,
            rmp_url="https://ratemyprofessors.com/professor/123",
        )
        assert rating.name == "John Smith"
        assert rating.rating == 4.5
    
    def test_rating_with_none_values(self):
        rating = ProfessorRating(
            name="Unknown Prof",
            rating=None,
            num_ratings=0,
            difficulty=None,
            would_take_again=None,
            rmp_url=None,
        )
        assert rating.rating is None
        assert rating.num_ratings == 0


class TestConflict:
    """Tests for Conflict model."""
    
    def test_valid_conflict(self):
        conflict = Conflict(
            course1_id="CAS-CS-111-A1",
            course2_id="CAS-CS-112-A1",
            course1_code="CAS CS 111",
            course2_code="CAS CS 112",
            overlap_day="Monday",
            overlap_time="10:00 AM - 11:00 AM",
        )
        assert conflict.course1_id == "CAS-CS-111-A1"
        assert conflict.overlap_day == "Monday"
