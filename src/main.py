"""
BU Course Search API
Fast course search and schedule building for Boston University students.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.models import (
    CourseResponse, GroupedCourseResponse, SubjectsResponse, TermsResponse,
    ScheduleValidation, ScheduleExport,
    ScheduleResponse, ScheduleCourse, ScheduleEvent, ScheduleConflictInfo, AddCourseRequest, AddCourseResponse,
)
from src.config import CORS_ORIGINS, HOST, PORT, RELOAD
from src.schedule_builder import ScheduleBuilder
from src.search import CourseIndex
from src.data_loader import load_courses
from src.rmp import rmp_client
from src.services.enrichment import EnrichmentService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


# Global instances - loaded once at startup
course_index: CourseIndex | None = None
enrichment_service: EnrichmentService | None = None
schedule_builder: ScheduleBuilder = ScheduleBuilder()  # Single-user local app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load course data into memory on startup."""
    global course_index, enrichment_service
    logger.info("Loading course data...")
    courses = load_courses()
    course_index = CourseIndex(courses)
    enrichment_service = EnrichmentService(rmp_client)
    logger.info(f"Loaded {len(courses)} courses into index")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="BU Course Search API",
    description="Fast course search and schedule building for BU students",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: set CORS_ORIGINS env (comma-separated) in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Redirect root to API docs."""
    return RedirectResponse(url="/docs")


@app.get("/api/health")
async def health():
    """Liveness/readiness for reverse proxy or orchestrator."""
    return {"status": "ok", "ready": course_index is not None}


@app.get("/api/courses")
async def search_courses(
    q: str = Query(default="", description="Search query"),
    subject: list[str] = Query(default=[], description="Filter by subject(s) (e.g., CS, MA)"),
    term: list[str] = Query(default=[], description="Filter by term(s) (e.g., Fall 2026)"),
    hub: list[str] = Query(default=[], description="Filter by Hub requirement(s)"),
    status: list[str] = Query(default=[], description="Filter by status (Open/Closed)"),
    limit: int = Query(default=50, le=500, description="Max results"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination"),
    grouped: bool = Query(default=True, description="Group sections under primary course"),
):
    """
    Search courses with optional filters.
    
    Multiple values for the same filter use OR logic (e.g., subject=CS&subject=MA).
    Different filters use AND logic (e.g., subject=CS&status=Open).
    
    Set grouped=true (default) to group discussions/labs under their lecture.
    Set grouped=false to get flat list of all sections.
    """
    start = time.perf_counter()
    
    # Build filters dict, excluding empty lists
    filters = {k: v for k, v in {
        "subject": subject, "term": term, "hub": hub, "status": status
    }.items() if v}
    
    if grouped:
        # Return grouped courses with related sections
        results, total = course_index.search_grouped(
            query=q, limit=limit, offset=offset, **filters
        )
        results = enrichment_service.enrich_grouped_courses(results)
        query_time_sec = time.perf_counter() - start

        return GroupedCourseResponse(
            courses=results,
            total=total,
            query_time_sec=round(query_time_sec, 2),
        )
    else:
        # Return flat list of all sections
        results = course_index.search(query=q, limit=limit, **filters)
        results = enrichment_service.enrich_courses(results)
        query_time_sec = time.perf_counter() - start

        return CourseResponse(
            courses=results,
            total=len(results),
            query_time_sec=round(query_time_sec, 2),
        )


@app.get("/api/courses/{course_id}")
async def get_course(course_id: str):
    """Get detailed info for a single course."""
    course = course_index.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course not found: {course_id}")

    # Enrich with professor rating
    enriched = enrichment_service.enrich_courses([course])
    return enriched[0]


@app.get("/api/subjects", response_model=SubjectsResponse)
async def list_subjects():
    """Get all available subjects/departments for filtering."""
    return SubjectsResponse(subjects=course_index.get_subjects())


@app.get("/api/terms", response_model=TermsResponse)
async def list_terms():
    """Get all available terms for filtering."""
    return TermsResponse(terms=course_index.get_terms())


@app.get("/api/hub-units")
async def list_hub_units():
    """Get all available Hub units for filtering."""
    return {"hub_units": course_index.get_hub_units()}


@app.post("/api/schedule/validate", response_model=ScheduleValidation)
async def validate_schedule(course_ids: list[str]):
    """
    Check if selected courses have time conflicts.
    Returns list of conflicting course pairs.
    """
    courses = [course_index.get_by_id(cid) for cid in course_ids]
    courses = [c for c in courses if c is not None]
    
    conflicts = course_index.detect_conflicts(courses)
    total_credits = sum(c.credits for c in courses)
    
    return ScheduleValidation(
        valid=len(conflicts) == 0,
        conflicts=conflicts,
        total_credits=total_credits,
    )


@app.post("/api/schedule/export")
async def export_schedule(course_ids: list[str] = Body(..., embed=False)):
    """
    Generate .ics calendar file for selected courses.
    """
    from src.ics_export import generate_ics
    
    courses = [course_index.get_by_id(cid) for cid in course_ids]
    courses = [c for c in courses if c is not None]
    
    ics_content = generate_ics(courses)
    
    return {
        "ics": ics_content,
        "filename": "bu_schedule.ics",
    }


@app.get("/api/professors/{professor_name}/rating")
async def get_professor_rating(professor_name: str):
    """
    Get RateMyProfessor rating for a professor.
    
    Returns rating data if found in cache, null fields otherwise.
    """
    rating = rmp_client.get_rating(professor_name)
    
    if rating:
        return rating.to_dict()
    
    return {
        "name": professor_name,
        "rating": None,
        "num_ratings": 0,
        "difficulty": None,
        "would_take_again": None,
        "rmp_url": None,
    }


@app.get("/api/professors/ratings")
async def get_professors_ratings(names: list[str] = Query(..., description="List of professor names")):
    """
    Get RateMyProfessor ratings for multiple professors.
    """
    results = {}
    for name in names:
        rating = rmp_client.get_rating(name)
        results[name] = rating.to_dict() if rating else None
    return {"ratings": results}


# === Schedule Builder Endpoints ===

def _build_schedule_response() -> ScheduleResponse:
    """Helper to build ScheduleResponse from current schedule."""
    data = schedule_builder.to_dict()
    return ScheduleResponse(
        courses=[ScheduleCourse(**c) for c in data["courses"]],
        events=[ScheduleEvent(**e) for e in data["events"]],
        conflicts=[ScheduleConflictInfo(**c) for c in data["conflicts"]],
        total_credits=data["total_credits"],
        course_count=data["course_count"],
        has_conflicts=data["has_conflicts"],
    )


@app.get("/api/schedule", response_model=ScheduleResponse)
async def get_schedule():
    """
    Get the current schedule with all events and conflicts.
    """
    return _build_schedule_response()


@app.post("/api/schedule/add", response_model=AddCourseResponse)
async def add_to_schedule(request: AddCourseRequest):
    """
    Add a course to the schedule.

    Returns the updated schedule and any new conflicts created.
    """
    course = course_index.get_by_id(request.course_id)
    if not course:
        raise HTTPException(status_code=404, detail=f"Course not found: {request.course_id}")

    # Enrich with professor rating
    enriched = enrichment_service.enrich_courses([course])
    course = enriched[0]

    # Add to schedule and get conflicts
    conflicts = schedule_builder.add_course(course)

    new_conflicts = [
        ScheduleConflictInfo(
            course1_id=c.event1.course_id,
            course1_code=c.event1.course_code,
            course2_id=c.event2.course_id,
            course2_code=c.event2.course_code,
            day=c.day,
            overlap_minutes=c.overlap_duration,
        )
        for c in conflicts
    ]

    return AddCourseResponse(
        success=True,
        schedule=_build_schedule_response(),
        new_conflicts=new_conflicts,
    )


@app.delete("/api/schedule/{course_id}")
async def remove_from_schedule(course_id: str):
    """
    Remove a course from the schedule.
    """
    success = schedule_builder.remove_course(course_id)
    return {
        "success": success,
        "schedule": _build_schedule_response(),
    }


@app.delete("/api/schedule")
async def clear_schedule():
    """
    Clear all courses from the schedule.
    """
    schedule_builder.clear()
    return {
        "success": True,
        "schedule": _build_schedule_response(),
    }


@app.post("/api/schedule/bulk")
async def set_schedule(course_ids: list[str]):
    """
    Set the schedule to a specific list of courses (replaces existing).
    """
    schedule_builder.clear()

    # Batch lookup all courses at once
    courses = [course_index.get_by_id(cid) for cid in course_ids]
    courses = [c for c in courses if c is not None]

    # Batch enrich all courses
    enriched = enrichment_service.enrich_courses(courses)

    # Add all to schedule
    for course in enriched:
        schedule_builder.add_course(course)

    return _build_schedule_response()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "courses_loaded": course_index.total_courses if course_index else 0,
        "rmp_cache": rmp_client.cache_stats(),
        "schedule_courses": schedule_builder.course_count,
    }


def run():
    """CLI entry point for `bu-courses` script. Set RELOAD=1 for dev."""
    import uvicorn
    uvicorn.run("src.main:app", host=HOST, port=PORT, reload=RELOAD)
