"""
Application configuration.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name, "").strip().lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


# Server (used by run() and for production)
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = _env_int("PORT", 8000)
RELOAD = _env_bool("RELOAD", default=False)

# CORS: comma-separated origins, or "*" for allow all (use only in dev)
_cors_raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173")
CORS_ORIGINS: list[str] = [o.strip() for o in _cors_raw.split(",") if o.strip()] if _cors_raw != "*" else ["*"]

# Data path (optional; data_loader defaults to src/data/courses.json)
COURSES_JSON_PATH: Path | None = None
_path = os.environ.get("COURSES_JSON_PATH", "").strip()
if _path:
    COURSES_JSON_PATH = Path(_path)


class SemesterDates(NamedTuple):
    """Start and end dates for a semester."""
    start: datetime
    end: datetime


# BU semester dates
SEMESTER_DATES: dict[str, SemesterDates] = {
    "Fall 2025": SemesterDates(
        start=datetime(2025, 9, 3),
        end=datetime(2025, 12, 10),
    ),
    "Spring 2026": SemesterDates(
        start=datetime(2026, 1, 21),
        end=datetime(2026, 5, 6),
    ),
    "Summer 2026": SemesterDates(
        start=datetime(2026, 5, 20),
        end=datetime(2026, 8, 14),
    ),
    "Fall 2026": SemesterDates(
        start=datetime(2026, 9, 2),
        end=datetime(2026, 12, 9),
    ),
}

# Default semester if term not found
DEFAULT_SEMESTER = "Fall 2025"

# Terms to exclude from loading
EXCLUDED_TERMS = {"Term 2265"}  # Summer terms

# Terms to show in the filter dropdown (others are hidden)
DISPLAY_TERMS = ["Fall 2025", "Spring 2026"]
