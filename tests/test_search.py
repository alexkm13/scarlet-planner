"""
Tests for search engine functionality.
"""

import pytest

from src.search import TrigramIndex, BitmapIndex, CourseIndex
from src.models import Course, Meeting


class TestTrigramIndex:
    """Tests for trigram indexing."""
    
    @pytest.fixture
    def index(self):
        idx = TrigramIndex()
        idx.add(0, "Introduction to Computer Science")
        idx.add(1, "Data Structures and Algorithms")
        idx.add(2, "Calculus I")
        idx.add(3, "Computer Networks")
        return idx
    
    def test_extract_trigrams(self, index):
        trigrams = index._extract_trigrams("hello")
        assert "hel" in trigrams
        assert "ell" in trigrams
        assert "llo" in trigrams
        assert len(trigrams) == 3
    
    def test_extract_trigrams_short_text(self, index):
        assert index._extract_trigrams("hi") == {"hi"}
        assert index._extract_trigrams("a") == {"a"}
        assert index._extract_trigrams("") == set()
    
    def test_normalize(self, index):
        assert index._normalize("  HELLO   WORLD  ") == "hello world"
        assert index._normalize("CS 111") == "cs 111"
    
    def test_get_candidates_exact(self, index):
        candidates = index.get_candidates("Computer")
        assert 0 in candidates  # Introduction to Computer Science
        assert 3 in candidates  # Computer Networks
    
    def test_get_candidates_partial(self, index):
        candidates = index.get_candidates("Calc")
        assert 2 in candidates  # Calculus I
    
    def test_get_candidates_no_match(self, index):
        candidates = index.get_candidates("xyz123")
        # May return empty or few candidates depending on min_matches
        assert 0 not in candidates or len(candidates) < 4
    
    def test_get_candidates_empty_query(self, index):
        candidates = index.get_candidates("")
        # Should return all documents
        assert len(candidates) == 4


class TestBitmapIndex:
    """Tests for bitmap filter indexing."""
    
    @pytest.fixture
    def index_with_courses(self, sample_courses):
        idx = BitmapIndex()
        idx.build(sample_courses)
        return idx, sample_courses
    
    def test_filter_by_subject(self, index_with_courses):
        idx, courses = index_with_courses
        result = idx.filter(subject=["CS"])
        # Should match CS courses (indices 0, 1, 3)
        assert 0 in result
        assert 1 in result
        assert 3 in result
        assert 2 not in result  # MA course
    
    def test_filter_by_term(self, index_with_courses):
        idx, courses = index_with_courses
        result = idx.filter(term=["Fall 2025"])
        # Should match Fall 2025 courses (indices 0, 1, 2)
        assert 0 in result
        assert 1 in result
        assert 2 in result
        assert 3 not in result  # Spring 2026
    
    def test_filter_by_status(self, index_with_courses):
        idx, courses = index_with_courses
        result = idx.filter(status=["Open"])
        assert 0 in result
        assert 1 in result
        assert 3 in result
        assert 2 not in result  # Closed
    
    def test_filter_multiple_subjects(self, index_with_courses):
        """Multiple values for same filter use OR logic."""
        idx, courses = index_with_courses
        result = idx.filter(subject=["CS", "MA"])
        # Should match all courses
        assert len(result) == 4
    
    def test_filter_combined(self, index_with_courses):
        """Different filters use AND logic."""
        idx, courses = index_with_courses
        result = idx.filter(subject=["CS"], status=["Open"])
        # CS AND Open = indices 0, 1, 3
        assert 0 in result
        assert 1 in result
        assert 3 in result
        assert 2 not in result
    
    def test_filter_no_match(self, index_with_courses):
        """When filter value doesn't exist, returns all courses (filter is skipped)."""
        idx, courses = index_with_courses
        result = idx.filter(subject=["FAKE"])
        # Current behavior: non-matching filter is skipped, returns all
        assert len(result) == len(courses)
    
    def test_get_subjects(self, index_with_courses):
        idx, _ = index_with_courses
        subjects = idx.get_values("subject")
        assert "CS" in subjects
        assert "MA" in subjects


class TestCourseIndex:
    """Tests for main course index."""
    
    @pytest.fixture
    def course_index(self, sample_courses):
        return CourseIndex(sample_courses)
    
    def test_search_by_code(self, course_index):
        results = course_index.search("CS 111")
        assert len(results) >= 1
        assert any(c.code == "CAS CS 111" for c in results)
    
    def test_search_by_title(self, course_index):
        results = course_index.search("Data Structures")
        assert len(results) >= 1
        assert any("Data Structures" in c.title for c in results)
    
    def test_search_by_professor(self, course_index):
        results = course_index.search("John Smith")
        assert len(results) >= 1
        assert all(c.professor == "John Smith" for c in results)
    
    def test_search_fuzzy(self, course_index):
        """Fuzzy search should handle typos."""
        results = course_index.search("Introdution")  # typo
        # Should still find "Introduction to Computer Science"
        assert len(results) >= 1
    
    def test_search_with_filter(self, course_index):
        results = course_index.search("", subject=["CS"])
        assert all(c.department == "CS" for c in results)
    
    def test_search_with_multiple_filters(self, course_index):
        results = course_index.search("", subject=["CS"], term=["Fall 2025"])
        assert all(c.department == "CS" and c.term == "Fall 2025" for c in results)
    
    def test_search_limit(self, course_index):
        results = course_index.search("", limit=2)
        assert len(results) <= 2
    
    def test_get_by_id(self, course_index):
        course = course_index.get_by_id("CAS-CS-111-A1-Fall2025")
        assert course is not None
        assert course.code == "CAS CS 111"
    
    def test_get_by_id_not_found(self, course_index):
        course = course_index.get_by_id("FAKE-ID")
        assert course is None
    
    def test_get_subjects(self, course_index):
        subjects = course_index.get_subjects()
        assert "CS" in subjects
        assert "MA" in subjects
    
    def test_get_terms(self, course_index):
        terms = course_index.get_terms()
        assert "Fall 2025" in terms
        assert "Spring 2026" in terms
    
    def test_total_courses(self, course_index):
        assert course_index.total_courses == 4


class TestConflictDetection:
    """Tests for schedule conflict detection."""
    
    @pytest.fixture
    def conflicting_courses(self):
        """Two courses that overlap on MWF 10:00-11:00."""
        return [
            Course(
                id="TEST-101-A1",
                code="TEST 101",
                title="Test Course 1",
                section="A1",
                professor="Prof A",
                term="Fall 2025",
                credits=3,
                department="TEST",
                college="CAS",
                schedule=[
                    Meeting(days="MWF", start_time="10:00 AM", end_time="11:00 AM", location="Room 1")
                ],
            ),
            Course(
                id="TEST-102-A1",
                code="TEST 102",
                title="Test Course 2",
                section="A1",
                professor="Prof B",
                term="Fall 2025",
                credits=3,
                department="TEST",
                college="CAS",
                schedule=[
                    Meeting(days="MWF", start_time="10:30 AM", end_time="11:30 AM", location="Room 2")
                ],
            ),
        ]
    
    @pytest.fixture
    def non_conflicting_courses(self):
        """Two courses that don't overlap."""
        return [
            Course(
                id="TEST-101-A1",
                code="TEST 101",
                title="Test Course 1",
                section="A1",
                professor="Prof A",
                term="Fall 2025",
                credits=3,
                department="TEST",
                college="CAS",
                schedule=[
                    Meeting(days="MWF", start_time="9:00 AM", end_time="10:00 AM", location="Room 1")
                ],
            ),
            Course(
                id="TEST-102-A1",
                code="TEST 102",
                title="Test Course 2",
                section="A1",
                professor="Prof B",
                term="Fall 2025",
                credits=3,
                department="TEST",
                college="CAS",
                schedule=[
                    Meeting(days="TuTh", start_time="10:00 AM", end_time="11:00 AM", location="Room 2")
                ],
            ),
        ]
    
    def test_detect_conflict(self, sample_courses, conflicting_courses):
        index = CourseIndex(sample_courses)
        conflicts = index.detect_conflicts(conflicting_courses)
        assert len(conflicts) >= 1
    
    def test_no_conflict(self, sample_courses, non_conflicting_courses):
        index = CourseIndex(sample_courses)
        conflicts = index.detect_conflicts(non_conflicting_courses)
        assert len(conflicts) == 0
