"""
Shared test fixtures.
"""

import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.models import Course, Meeting


@pytest.fixture
def sample_courses() -> list[Course]:
    """Sample courses for testing."""
    return [
        Course(
            id="CAS-CS-111-A1-Fall2025",
            code="CAS CS 111",
            title="Introduction to Computer Science",
            description="An introduction to programming.",
            section="A1",
            professor="John Smith",
            term="Fall 2025",
            credits=4,
            hub_units=["Quantitative Reasoning I"],
            department="CS",
            college="CAS",
            schedule=[
                Meeting(days="MWF", start_time="10:10 AM", end_time="11:00 AM", location="CAS 313")
            ],
            status="Open",
            enrollment_cap=100,
            enrollment_total=85,
            section_type="Lecture",
            class_nbr=12345,
        ),
        Course(
            id="CAS-CS-112-A1-Fall2025",
            code="CAS CS 112",
            title="Data Structures",
            description="Fundamental data structures.",
            section="A1",
            professor="Jane Doe",
            term="Fall 2025",
            credits=4,
            hub_units=["Quantitative Reasoning II"],
            department="CS",
            college="CAS",
            schedule=[
                Meeting(days="TuTh", start_time="11:00 AM", end_time="12:15 PM", location="CAS 522")
            ],
            status="Open",
            enrollment_cap=80,
            enrollment_total=80,
            section_type="Lecture",
            class_nbr=12346,
        ),
        Course(
            id="CAS-MA-123-A1-Fall2025",
            code="CAS MA 123",
            title="Calculus I",
            description="Introduction to calculus.",
            section="A1",
            professor="Bob Wilson",
            term="Fall 2025",
            credits=4,
            hub_units=["Quantitative Reasoning I"],
            department="MA",
            college="CAS",
            schedule=[
                Meeting(days="MWF", start_time="9:05 AM", end_time="9:55 AM", location="CAS 201")
            ],
            status="Closed",
            enrollment_cap=50,
            enrollment_total=50,
            section_type="Lecture",
            class_nbr=12347,
        ),
        Course(
            id="CAS-CS-111-A1-Spring2026",
            code="CAS CS 111",
            title="Introduction to Computer Science",
            description="An introduction to programming.",
            section="A1",
            professor="John Smith",
            term="Spring 2026",
            credits=4,
            hub_units=["Quantitative Reasoning I"],
            department="CS",
            college="CAS",
            schedule=[
                Meeting(days="MWF", start_time="10:10 AM", end_time="11:00 AM", location="CAS 313")
            ],
            status="Open",
            enrollment_cap=100,
            enrollment_total=50,
            section_type="Lecture",
            class_nbr=22345,
        ),
    ]


@pytest.fixture
def sample_rmp_cache() -> dict:
    """Sample RMP ratings cache."""
    return {
        "john smith": {
            "name": "John Smith",
            "rating": 4.5,
            "num_ratings": 50,
            "difficulty": 3.0,
            "would_take_again": 85.0,
            "rmp_id": "123456",
        },
        "jane doe": {
            "name": "Jane Doe",
            "rating": 3.8,
            "num_ratings": 30,
            "difficulty": 4.0,
            "would_take_again": 60.0,
            "rmp_id": "234567",
        },
        "bob wilson": None,  # Professor not found on RMP
    }


@pytest.fixture
def temp_rmp_cache(sample_rmp_cache, tmp_path) -> Path:
    """Create a temporary RMP cache file."""
    cache_file = tmp_path / "rmp_ratings.json"
    with open(cache_file, "w") as f:
        json.dump(sample_rmp_cache, f)
    return cache_file


@pytest.fixture
def test_client(sample_courses, temp_rmp_cache, monkeypatch):
    """Create a test client with sample data."""
    # Mock the data loader to return sample courses
    def mock_load_courses():
        return sample_courses
    
    monkeypatch.setattr("src.main.load_courses", mock_load_courses)
    
    # Mock the RMP cache file path
    monkeypatch.setattr("src.rmp.RATINGS_FILE", temp_rmp_cache)
    
    # Need to reload the rmp module to pick up new cache
    import importlib
    import src.rmp
    importlib.reload(src.rmp)
    monkeypatch.setattr("src.main.rmp_client", src.rmp.rmp_client)
    
    from src.main import app
    
    with TestClient(app) as client:
        yield client
