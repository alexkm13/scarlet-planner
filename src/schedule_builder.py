"""
Schedule Builder - Manages course schedules with conflict detection and column assignment.

Features:
- Add/remove courses from schedule
- Detect time conflicts between courses
- Assign columns to overlapping events for visual display
- Generate calendar events grouped by day
"""

from dataclasses import dataclass, field
from typing import Optional

from src.models import Course, Meeting
from src.utils.parsing import parse_time_to_minutes, parse_days_to_full_names, DAY_ORDER


@dataclass
class ScheduleEvent:
    """A single event on the schedule calendar."""
    course_id: str
    course_code: str
    course_title: str
    section: str
    section_type: str
    professor: str
    day: str                    # "Monday", "Tuesday", etc.
    start_minutes: int          # Minutes since midnight
    end_minutes: int            # Minutes since midnight
    start_time: str             # Original time string
    end_time: str               # Original time string
    location: str
    color: Optional[str] = None # Hex color for display
    column: int = 0             # Column for overlapping events
    total_columns: int = 1      # Total columns for this time slot
    
    @property
    def duration_minutes(self) -> int:
        return self.end_minutes - self.start_minutes
    
    def overlaps(self, other: "ScheduleEvent") -> bool:
        """Check if this event overlaps with another on the same day."""
        if self.day != other.day:
            return False
        return self.start_minutes < other.end_minutes and other.start_minutes < self.end_minutes


@dataclass
class ScheduleConflict:
    """Represents a time conflict between two courses."""
    event1: ScheduleEvent
    event2: ScheduleEvent
    day: str
    overlap_start: int  # Minutes
    overlap_end: int    # Minutes
    
    @property
    def overlap_duration(self) -> int:
        return self.overlap_end - self.overlap_start


@dataclass
class ScheduleBuilder:
    """
    Manages a course schedule with conflict detection and layout.
    """
    courses: dict[str, Course] = field(default_factory=dict)
    _color_index: int = 0
    
    # Color palette for courses
    COLORS = [
        "#CC0000",  # BU Scarlet
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#8B5CF6",  # Purple
        "#F59E0B",  # Amber
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#F97316",  # Orange
        "#6366F1",  # Indigo
    ]
    
    def add_course(self, course: Course) -> list[ScheduleConflict]:
        """
        Add a course to the schedule.
        
        Returns list of conflicts with existing courses.
        """
        conflicts = self._detect_conflicts_with(course)
        self.courses[course.id] = course
        return conflicts
    
    def remove_course(self, course_id: str) -> bool:
        """Remove a course from the schedule."""
        if course_id in self.courses:
            del self.courses[course_id]
            return True
        return False
    
    def get_course(self, course_id: str) -> Optional[Course]:
        """Get a course by ID."""
        return self.courses.get(course_id)
    
    def clear(self):
        """Remove all courses from the schedule."""
        self.courses.clear()
        self._color_index = 0
    
    def _get_next_color(self) -> str:
        """Get the next color from the palette."""
        color = self.COLORS[self._color_index % len(self.COLORS)]
        self._color_index += 1
        return color
    
    def _detect_conflicts_with(self, new_course: Course) -> list[ScheduleConflict]:
        """Detect conflicts between a new course and existing courses."""
        conflicts = []
        new_events = self._course_to_events(new_course, "temp")
        
        for existing_course in self.courses.values():
            existing_events = self._course_to_events(existing_course, "temp")
            
            for new_event in new_events:
                for existing_event in existing_events:
                    if new_event.overlaps(existing_event):
                        overlap_start = max(new_event.start_minutes, existing_event.start_minutes)
                        overlap_end = min(new_event.end_minutes, existing_event.end_minutes)
                        
                        conflicts.append(ScheduleConflict(
                            event1=new_event,
                            event2=existing_event,
                            day=new_event.day,
                            overlap_start=overlap_start,
                            overlap_end=overlap_end,
                        ))
        
        return conflicts
    
    def get_all_conflicts(self) -> list[ScheduleConflict]:
        """Get all conflicts in the current schedule."""
        conflicts = []
        course_list = list(self.courses.values())
        
        for i, course1 in enumerate(course_list):
            events1 = self._course_to_events(course1, "temp")
            
            for course2 in course_list[i + 1:]:
                events2 = self._course_to_events(course2, "temp")
                
                for e1 in events1:
                    for e2 in events2:
                        if e1.overlaps(e2):
                            overlap_start = max(e1.start_minutes, e2.start_minutes)
                            overlap_end = min(e1.end_minutes, e2.end_minutes)
                            
                            conflicts.append(ScheduleConflict(
                                event1=e1,
                                event2=e2,
                                day=e1.day,
                                overlap_start=overlap_start,
                                overlap_end=overlap_end,
                            ))
        
        return conflicts
    
    def _course_to_events(self, course: Course, color: str) -> list[ScheduleEvent]:
        """Convert a course to a list of schedule events."""
        events = []

        for meeting in course.schedule:
            if not meeting.days or meeting.days.upper() == "TBA":
                continue

            days = parse_days_to_full_names(meeting.days)
            start = parse_time_to_minutes(meeting.start_time) if meeting.start_time else 0
            end = parse_time_to_minutes(meeting.end_time) if meeting.end_time else 0

            if start == 0 and end == 0:
                continue  # Skip TBA times

            for day in days:
                events.append(ScheduleEvent(
                    course_id=course.id,
                    course_code=course.code,
                    course_title=course.title,
                    section=course.section,
                    section_type=course.section_type,
                    professor=course.professor,
                    day=day,
                    start_minutes=start,
                    end_minutes=end,
                    start_time=meeting.start_time,
                    end_time=meeting.end_time,
                    location=meeting.location,
                    color=color,
                ))
        
        return events
    
    def get_events(self) -> list[ScheduleEvent]:
        """
        Get all events with column assignments for overlapping events.
        
        Uses greedy interval scheduling algorithm.
        """
        all_events = []
        
        # Assign colors to courses
        course_colors = {}
        for course_id in self.courses:
            course_colors[course_id] = self._get_next_color()
        self._color_index = 0  # Reset for next call
        
        # Generate events with colors
        for course in self.courses.values():
            color = course_colors[course.id]
            events = self._course_to_events(course, color)
            all_events.extend(events)
        
        # Assign columns per day
        events_by_day: dict[str, list[ScheduleEvent]] = {}
        for event in all_events:
            if event.day not in events_by_day:
                events_by_day[event.day] = []
            events_by_day[event.day].append(event)
        
        result = []
        for day in DAY_ORDER:
            if day in events_by_day:
                day_events = self._assign_columns(events_by_day[day])
                result.extend(day_events)
        
        return result
    
    def _assign_columns(self, events: list[ScheduleEvent]) -> list[ScheduleEvent]:
        """
        Greedy interval scheduling - assign columns to overlapping events.
        
        Example:
            CS 111: 12:00-1:00  → column 0
            MA 225: 12:30-2:00  → column 1 (overlaps CS 111)
            PH 100: 1:30-3:00   → column 0 (no conflict with CS 111)
        """
        # Sort by start time, then by end time
        events = sorted(events, key=lambda e: (e.start_minutes, e.end_minutes))
        columns: list[int] = []  # Each column tracks end time of last event
        
        for event in events:
            placed = False
            for i, col_end in enumerate(columns):
                if event.start_minutes >= col_end:
                    event.column = i
                    columns[i] = event.end_minutes
                    placed = True
                    break
            
            if not placed:
                event.column = len(columns)
                columns.append(event.end_minutes)
        
        # Set total_columns for each event based on overlapping events
        total_cols = len(columns) if columns else 1
        for event in events:
            event.total_columns = total_cols
        
        return events
    
    def get_events_by_day(self) -> dict[str, list[ScheduleEvent]]:
        """Get events grouped by day with column assignments."""
        events = self.get_events()
        
        by_day: dict[str, list[ScheduleEvent]] = {}
        for day in DAY_ORDER:
            by_day[day] = []
        
        for event in events:
            by_day[event.day].append(event)
        
        return by_day
    
    @property
    def total_credits(self) -> int:
        """Get total credits for all courses in the schedule."""
        return sum(c.credits for c in self.courses.values())
    
    @property
    def course_count(self) -> int:
        """Get number of courses in the schedule."""
        return len(self.courses)
    
    def to_dict(self) -> dict:
        """Export schedule to dictionary for API response."""
        events = self.get_events()
        conflicts = self.get_all_conflicts()
        
        return {
            "courses": [
                {
                    "id": c.id,
                    "code": c.code,
                    "title": c.title,
                    "section": c.section,
                    "credits": c.credits,
                    "professor": c.professor,
                    "term": c.term,
                }
                for c in self.courses.values()
            ],
            "events": [
                {
                    "course_id": e.course_id,
                    "course_code": e.course_code,
                    "course_title": e.course_title,
                    "section": e.section,
                    "section_type": e.section_type,
                    "professor": e.professor,
                    "day": e.day,
                    "start_minutes": e.start_minutes,
                    "end_minutes": e.end_minutes,
                    "start_time": e.start_time,
                    "end_time": e.end_time,
                    "location": e.location,
                    "color": e.color,
                    "column": e.column,
                    "total_columns": e.total_columns,
                }
                for e in events
            ],
            "conflicts": [
                {
                    "course1_id": c.event1.course_id,
                    "course1_code": c.event1.course_code,
                    "course2_id": c.event2.course_id,
                    "course2_code": c.event2.course_code,
                    "day": c.day,
                    "overlap_minutes": c.overlap_duration,
                }
                for c in conflicts
            ],
            "total_credits": self.total_credits,
            "course_count": self.course_count,
            "has_conflicts": len(conflicts) > 0,
        }
