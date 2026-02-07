"""
Data loader for course JSON files.
"""

import json
from pathlib import Path

from src.models import Course
from src.config import EXCLUDED_TERMS, DISPLAY_TERMS, COURSES_JSON_PATH
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_courses(path: str | Path | None = None) -> list[Course]:
    """
    Load courses from JSON file and convert to Course models.
    
    Args:
        path: Path to JSON file. Defaults to COURSES_JSON_PATH env or src/data/courses.json
        
    Returns:
        List of Course objects
    """
    if path is None:
        path = COURSES_JSON_PATH or (Path(__file__).parent / "data" / "courses.json")
    else:
        path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Course data file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    courses = []
    skipped_count = 0
    allowed_terms = set(DISPLAY_TERMS)
    for item in data:
        try:
            term = item.get("term", "")
            # Skip excluded terms (e.g., Summer terms)
            if term in EXCLUDED_TERMS:
                skipped_count += 1
                continue
            # Only include Fall 2025 and Spring 2026
            if term not in allowed_terms:
                skipped_count += 1
                continue
            course = Course(**item)
            courses.append(course)
        except Exception as e:
            # Skip invalid entries but log the error
            logger.warning(f"Skipping invalid course entry: {e}")
            continue

    if skipped_count > 0:
        logger.info(f"Skipped {skipped_count} courses from excluded terms")

    return courses


def load_test_courses() -> list[Course]:
    """Load the smaller test dataset for development."""
    path = Path(__file__).parent / "data" / "test.json"
    return load_courses(path)


def load_cs_courses() -> list[Course]:
    """Load CS courses test dataset."""
    path = Path(__file__).parent / "data" / "test_cs.json"
    return load_courses(path)
