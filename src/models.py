"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel
from src.utils.constants import SECONDARY_SECTION_TYPES


class Meeting(BaseModel):
    """A single meeting time for a course section."""
    days: str              # "MWF" or "TuTh"
    start_time: str        # "10:10"
    end_time: str          # "11:00"
    location: str          # "CAS 313"


class ProfessorRating(BaseModel):
    """Professor rating from RateMyProfessor."""
    name: str
    rating: float | None = None       # 1.0-5.0
    num_ratings: int = 0
    difficulty: float | None = None   # 1.0-5.0
    would_take_again: float | None = None  # percentage
    rmp_url: str | None = None


class Course(BaseModel):
    """Full course/section data."""
    id: str                          # "CAS-CS-111-A1-Fall2026"
    code: str                        # "CAS CS 111"
    title: str                       # "Introduction to Computer Science"
    description: str = ""
    section: str                     # "A1"
    professor: str                   # "John Lapets"
    term: str                        # "Fall 2026"
    credits: int                     # 4
    hub_units: list[str] = []        # ["Quantitative Reasoning I", "Critical Thinking"]
    department: str                  # "CS"
    college: str                     # "CAS"
    schedule: list[Meeting] = []
    status: str = ""                 # "Open" or "Closed"
    enrollment_cap: int = 0          # Maximum enrollment
    enrollment_total: int = 0        # Current enrollment
    section_type: str = ""           # "Lecture", "Discussion", etc.
    class_nbr: int = 0               # Class number
    professor_rating: ProfessorRating | None = None  # RMP rating
    
    @property
    def search_text(self) -> str:
        """Combined text for fuzzy search."""
        hub_text = " ".join(self.hub_units) if self.hub_units else ""
        return f"{self.code} {self.title} {self.professor} {self.department} {hub_text}"
    
    @property
    def is_primary_section(self) -> bool:
        """Check if this is a primary section type (Lecture, IND, or other non-secondary types)."""
        return self.section_type not in SECONDARY_SECTION_TYPES


class RelatedSection(BaseModel):
    """A related section (discussion, lab) for a grouped course."""
    id: str
    section: str
    section_type: str
    professor: str
    schedule: list[Meeting] = []
    status: str = ""
    enrollment_cap: int = 0
    enrollment_total: int = 0
    professor_rating: ProfessorRating | None = None


class GroupedCourse(BaseModel):
    """A course with its related sections grouped together."""
    id: str
    code: str
    title: str
    description: str = ""
    section: str
    professor: str
    term: str
    credits: int
    hub_units: list[str] = []
    department: str
    college: str
    schedule: list[Meeting] = []
    status: str = ""
    enrollment_cap: int = 0
    enrollment_total: int = 0
    section_type: str = ""
    class_nbr: int = 0
    professor_rating: ProfessorRating | None = None
    related_sections: list[RelatedSection] = []
    
    @classmethod
    def from_course(cls, course: Course, related: list[RelatedSection] = None) -> "GroupedCourse":
        """Create a GroupedCourse from a Course and its related sections."""
        return cls(
            id=course.id,
            code=course.code,
            title=course.title,
            description=course.description,
            section=course.section,
            professor=course.professor,
            term=course.term,
            credits=course.credits,
            hub_units=course.hub_units,
            department=course.department,
            college=course.college,
            schedule=course.schedule,
            status=course.status,
            enrollment_cap=course.enrollment_cap,
            enrollment_total=course.enrollment_total,
            section_type=course.section_type,
            class_nbr=course.class_nbr,
            professor_rating=course.professor_rating,
            related_sections=related or [],
        )


class CourseResponse(BaseModel):
    """Response for course search endpoint."""
    courses: list[Course]
    total: int
    query_time_ms: float


class GroupedCourseResponse(BaseModel):
    """Response for grouped course search endpoint."""
    courses: list[GroupedCourse]
    total: int
    query_time_ms: float


class SubjectsResponse(BaseModel):
    """Response for subjects list endpoint."""
    subjects: list[str]


class TermsResponse(BaseModel):
    """Response for terms list endpoint."""
    terms: list[str]


class Conflict(BaseModel):
    """A pair of conflicting courses."""
    course1_id: str
    course2_id: str
    course1_code: str
    course2_code: str
    overlap_day: str
    overlap_time: str


class ScheduleValidation(BaseModel):
    """Response for schedule validation endpoint."""
    valid: bool
    conflicts: list[Conflict]
    total_credits: int


class ScheduleExport(BaseModel):
    """Request for schedule export."""
    course_ids: list[str]


class ScheduleEvent(BaseModel):
    """A single event on the schedule calendar."""
    course_id: str
    course_code: str
    course_title: str
    section: str
    section_type: str
    professor: str
    day: str
    start_minutes: int
    end_minutes: int
    start_time: str
    end_time: str
    location: str
    color: str
    column: int
    total_columns: int


class ScheduleCourse(BaseModel):
    """Summary of a course in the schedule."""
    id: str
    code: str
    title: str
    section: str
    credits: int
    professor: str
    term: str


class ScheduleConflictInfo(BaseModel):
    """Information about a schedule conflict."""
    course1_id: str
    course1_code: str
    course2_id: str
    course2_code: str
    day: str
    overlap_minutes: int


class ScheduleResponse(BaseModel):
    """Full schedule with events, conflicts, and metadata."""
    courses: list[ScheduleCourse]
    events: list[ScheduleEvent]
    conflicts: list[ScheduleConflictInfo]
    total_credits: int
    course_count: int
    has_conflicts: bool


class AddCourseRequest(BaseModel):
    """Request to add a course to the schedule."""
    course_id: str


class AddCourseResponse(BaseModel):
    """Response after adding a course."""
    success: bool
    schedule: ScheduleResponse
    new_conflicts: list[ScheduleConflictInfo]
