#!/usr/bin/env python3
"""
Refresh RateMyProfessor ratings cache.

Fetches ratings for all professors in courses.json and saves to rmp_ratings.json.
Run periodically via cron or manually: python -m src.refresh_rmp
"""

import json
import re
import time
from pathlib import Path

import requests

# Paths
DATA_DIR = Path(__file__).parent / "data"
COURSES_FILE = DATA_DIR / "courses.json"
RATINGS_FILE = DATA_DIR / "rmp_ratings.json"

# RMP config
BU_SCHOOL_ID = "U2Nob29sLTEyNA=="  # Boston University
GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"

SEARCH_QUERY = """
query SearchTeacher($query: TeacherSearchQuery!) {
  newSearch {
    teachers(query: $query) {
      edges {
        node {
          id
          firstName
          lastName
          avgRating
          numRatings
          avgDifficulty
          wouldTakeAgainPercent
          legacyId
          school {
            id
          }
        }
      }
    }
  }
}
"""


def normalize_name(name: str) -> str:
    """Normalize professor name for consistent keying."""
    name = name.strip().lower()
    name = re.sub(r'\b(dr\.?|prof\.?|professor)\b', '', name, flags=re.IGNORECASE)
    if ',' in name:
        parts = name.split(',', 1)
        name = f"{parts[1].strip()} {parts[0].strip()}"
    return ' '.join(name.split())


def _parse_teacher_node(node: dict) -> dict:
    """Extract rating data from a teacher node."""
    first = node.get("firstName", "").strip()
    last = node.get("lastName", "").strip()
    legacy_id = node.get("legacyId")
    
    return {
        "name": f"{first} {last}".strip(),
        "rating": node.get("avgRating"),
        "num_ratings": node.get("numRatings", 0),
        "difficulty": node.get("avgDifficulty"),
        "would_take_again": node.get("wouldTakeAgainPercent"),
        "rmp_id": str(legacy_id) if legacy_id else None,
    }


def _find_matching_professor(teachers: list[dict], target_last_name: str) -> dict | None:
    """Find a BU professor matching the target last name."""
    for edge in teachers:
        node = edge.get("node", {})
        
        # Must be from BU
        if node.get("school", {}).get("id") != BU_SCHOOL_ID:
            continue
        
        # Last name must match
        if node.get("lastName", "").strip().lower() != target_last_name:
            continue
        
        return _parse_teacher_node(node)
    
    return None


def fetch_rating(session: requests.Session, name: str) -> dict | None:
    """Fetch a single professor's rating from RMP."""
    try:
        response = session.post(
            GRAPHQL_URL,
            json={
                "query": SEARCH_QUERY,
                "variables": {"query": {"text": name, "schoolID": BU_SCHOOL_ID}},
            },
            timeout=10,
        )
        
        if response.status_code != 200:
            return None
        
        teachers = (
            response.json()
            .get("data", {})
            .get("newSearch", {})
            .get("teachers", {})
            .get("edges", [])
        )
        
        if not teachers:
            return None
        
        # Extract last name for matching
        normalized = normalize_name(name)
        target_last = normalized.split()[-1] if normalized else ""
        
        return _find_matching_professor(teachers, target_last)
        
    except Exception as e:
        print(f"  Error fetching {name}: {e}")
        return None


def extract_professors(courses_file: Path) -> set[str]:
    """Extract unique professor names from courses.json."""
    with open(courses_file) as f:
        courses = json.load(f)
    
    professors = set()
    for course in courses:
        prof = course.get("professor", "")
        if prof and prof.lower() not in ("tba", "-", "staff", ""):
            professors.add(prof)
    
    return professors


def main():
    """Fetch all professor ratings and save to cache."""
    print("Extracting professors from courses.json...")
    professors = extract_professors(COURSES_FILE)
    print(f"Found {len(professors)} unique professors")
    
    # Set up session
    session = requests.Session()
    session.headers.update({
        "Authorization": "Basic dGVzdDp0ZXN0",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    })
    
    # Fetch ratings
    ratings = {}
    found = 0
    start_time = time.time()
    
    print("Fetching RMP ratings...")
    for i, name in enumerate(sorted(professors), 1):
        rating = fetch_rating(session, name)
        
        # Store by normalized name for consistent lookup
        key = normalize_name(name)
        ratings[key] = rating
        
        if rating:
            found += 1
        
        # Progress every 100
        if i % 100 == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed
            remaining = (len(professors) - i) / rate
            print(f"  {i}/{len(professors)} ({found} found) - ~{remaining:.0f}s remaining")
        
        # Small delay to be nice to the API
        time.sleep(0.05)
    
    # Save to file
    print(f"\nSaving to {RATINGS_FILE}...")
    with open(RATINGS_FILE, 'w') as f:
        json.dump(ratings, f, indent=2)
    
    elapsed = time.time() - start_time
    print(f"\nDone! {found}/{len(professors)} professors found ({elapsed:.1f}s)")
    print(f"Cache saved to: {RATINGS_FILE}")


if __name__ == "__main__":
    main()
