"""
Optimized course search engine.

Performance targets:
- Search: < 0.5ms p99
- Filter: < 0.1ms
- Startup: < 500ms for 7k courses

Key optimizations:
1. Trigram index for candidate reduction before fuzzy match
2. Roaring bitmaps for O(1) filter intersection
3. Pre-computed sort orders
"""

import re
from collections import defaultdict
from typing import Callable

from src.models import Course, Conflict, GroupedCourse, RelatedSection
from src.utils.parsing import parse_time_to_minutes, parse_days_to_set
from src.utils.constants import PRIMARY_SECTION_TYPES, SECONDARY_SECTION_TYPES
from src.utils.departments import get_department_name, resolve_department_query
from src.utils.logger import setup_logger

from pyroaring import BitMap
from rapidfuzz import fuzz, process

logger = setup_logger(__name__)


class TrigramIndex:
    """
    Trigram index for fast candidate retrieval.
    
    Instead of fuzzy matching against 7k courses, we:
    1. Extract trigrams from query: "cs 111" -> {"cs ", "s 1", " 11", "111"}
    2. Find courses containing those trigrams: O(1) per trigram
    3. Fuzzy match only against candidates: ~50-200 courses instead of 7k
    
    This reduces fuzzy matching from O(n) to O(candidates).
    """
    
    def __init__(self):
        self.trigram_to_ids: dict[str, set[int]] = defaultdict(set)
        self.id_to_text: dict[int, str] = {}
    
    def add(self, doc_id: int, text: str):
        """Add a document to the index."""
        text = self._normalize(text)
        self.id_to_text[doc_id] = text
        
        for trigram in self._extract_trigrams(text):
            self.trigram_to_ids[trigram].add(doc_id)
    
    def get_candidates(self, query: str, min_matches: int = 1) -> set[int]:
        """
        Get candidate document IDs that might match the query.
        
        Returns IDs that share at least `min_matches` trigrams with query.
        """
        query = self._normalize(query)
        trigrams = self._extract_trigrams(query)
        
        if not trigrams:
            return set(self.id_to_text.keys())
        
        # Count trigram matches per document
        match_counts: dict[int, int] = defaultdict(int)
        for trigram in trigrams:
            for doc_id in self.trigram_to_ids.get(trigram, []):
                match_counts[doc_id] += 1
        
        # Return docs with enough matches
        return {doc_id for doc_id, count in match_counts.items() if count >= min_matches}
    
    def _normalize(self, text: str) -> str:
        """Normalize text for indexing."""
        return re.sub(r'\s+', ' ', text.lower().strip())
    
    def _extract_trigrams(self, text: str) -> set[str]:
        """Extract character trigrams from text."""
        if len(text) < 3:
            return {text} if text else set()
        return {text[i:i+3] for i in range(len(text) - 2)}


class BitmapIndex:
    """
    Bitmap index for fast filter intersection.
    
    Each filter value (e.g., subject="CS") maps to a bitmap of course IDs.
    Intersection is O(1) bitwise AND instead of O(n) set operations.
    """
    
    def __init__(self):
        self.indices: dict[str, dict[str, BitMap]] = {}
        self.all_ids: BitMap | None = None
    
    def build(self, courses: list[Course]):
        """Build bitmap indices for all filterable fields."""
        n = len(courses)
        
        self.all_ids = BitMap(range(n))
        
        # Build indices for each filterable field
        self.indices = {
            'subject': defaultdict(BitMap),
            'term': defaultdict(BitMap),
            'hub': defaultdict(BitMap),
            'college': defaultdict(BitMap),
            'status': defaultdict(BitMap),
        }
        
        for i, course in enumerate(courses):
            self.indices['subject'][course.department].add(i)
            self.indices['term'][course.term].add(i)
            self.indices['college'][course.college].add(i)
            if course.status:
                self.indices['status'][course.status].add(i)
            for hub in course.hub_units:
                self.indices['hub'][hub].add(i)
    
    def filter(self, **filters: str | list[str] | None) -> set[int]:
        """
        Get course IDs matching all specified filters.
        
        Uses OR logic within a field, AND logic between fields.
        
        Args:
            **filters: Field-value pairs. Values can be single string or list.
                       e.g., subject="CS" or subject=["CS", "MA"]
        
        Returns:
            Set of indices into the courses list.
        """
        result = self.all_ids.copy()
        
        for field, values in filters.items():
            if not values or field not in self.indices:
                continue
            
            # Normalize to list
            if isinstance(values, str):
                values = [values]
            
            # OR within field: union all matching bitmaps
            field_matches = BitMap()
            for value in values:
                if value in self.indices[field]:
                    field_matches |= self.indices[field][value]
            
            # AND between fields
            if field_matches:
                result &= field_matches
        
        return set(result)
    
    def get_values(self, field: str) -> list[str]:
        """Get all unique values for a field."""
        if field in self.indices:
            return sorted(self.indices[field].keys())
        return []


class CourseIndex:
    """
    Optimized in-memory course index.

    Combines:
    - Trigram index for fast candidate retrieval
    - Bitmap index for O(1) filter intersection
    - Pre-sorted course lists for common sort orders
    - Pre-computed search texts for fast fuzzy matching
    """

    def __init__(self, courses: list[Course]):
        self.courses = courses
        self.by_id: dict[str, Course] = {c.id: c for c in courses}
        
        # Pre-compute search texts: base + department name + compressed code (for CS411-style lookup)
        self.search_texts: list[str] = []
        for c in courses:
            base = c.search_text
            dept_name = get_department_name(c.department)
            compressed_code = c.code.replace(" ", "").lower()
            self.search_texts.append(f"{base} {dept_name} {compressed_code}")
        
        # Build optimized indices
        self._build_indices()
    
    def _build_indices(self):
        """Build all search and filter indices."""
        # Trigram index for search (use pre-computed texts)
        self.trigram_index = TrigramIndex()
        for i, text in enumerate(self.search_texts):
            self.trigram_index.add(i, text)
        
        # Bitmap index for filters
        self.bitmap_index = BitmapIndex()
        self.bitmap_index.build(self.courses)
        
        # Pre-sorted indices for common sort orders
        self._build_sort_indices()
        
        # Build prefix index for short queries (< 3 chars)
        self._build_prefix_index()
    
    def _build_prefix_index(self):
        """Build prefix index for handling short queries."""
        self.prefix_index: dict[str, set[int]] = defaultdict(set)
        for i, course in enumerate(self.courses):
            # Index by code prefix (e.g., "CS", "MA")
            code_parts = course.code.upper().split()
            for part in code_parts:
                if len(part) >= 2:
                    self.prefix_index[part[:2]].add(i)
            # Index by department
            if course.department:
                self.prefix_index[course.department.upper()].add(i)
    
    def _build_sort_indices(self):
        """Pre-compute sorted course indices for common sort orders."""
        indices = list(range(len(self.courses)))
        
        self.sorted_by = {
            'code': sorted(indices, key=lambda i: self.courses[i].code),
            'title': sorted(indices, key=lambda i: self.courses[i].title.lower()),
            'professor': sorted(indices, key=lambda i: self.courses[i].professor.lower()),
            'credits': sorted(indices, key=lambda i: -self.courses[i].credits),  # Descending
        }
    
    @property
    def total_courses(self) -> int:
        return len(self.courses)
    
    def get_by_id(self, course_id: str) -> Course | None:
        return self.by_id.get(course_id)
    
    def get_subjects(self) -> list[str]:
        return self.bitmap_index.get_values('subject')
    
    def get_terms(self) -> list[str]:
        from src.config import DISPLAY_TERMS
        terms = set(self.bitmap_index.get_values('term'))
        # Only return terms in DISPLAY_TERMS that have courses
        return [t for t in DISPLAY_TERMS if t in terms]
    
    def get_hub_units(self) -> list[str]:
        return self.bitmap_index.get_values('hub')
    
    def search(
        self,
        query: str = "",
        sort_by: str = "relevance",
        limit: int = 100,
        **filters: str | None,
    ) -> list[Course]:
        """
        Search courses with optional filters.
        
        Args:
            query: Search text (fuzzy matched against course code, title, professor)
            sort_by: Sort order for results
            limit: Maximum results to return
            **filters: Field filters (subject, term, hub, status, college)
        """
        candidate_ids = self.bitmap_index.filter(**filters)
        query = query.strip()
        
        if not query:
            return self._get_sorted(candidate_ids, sort_by, limit)
        
        candidate_ids &= self._get_query_candidates(query)
        
        if not candidate_ids:
            return []
        
        return self._fuzzy_match(query, candidate_ids, limit)
    
    def _get_query_candidates(self, query: str) -> set[int]:
        """Get candidate IDs matching the query using trigram or prefix index."""
        if len(query) < 3:
            return self._prefix_lookup(query.upper())
        
        min_matches = max(1, len(query) // 4)
        return self.trigram_index.get_candidates(query, min_matches=min_matches)
    
    def _prefix_lookup(self, prefix: str) -> set[int]:
        """Look up candidates by prefix (for short queries)."""
        if prefix in self.prefix_index:
            return self.prefix_index[prefix]
        
        # Partial prefix match
        return {
            id for p, ids in self.prefix_index.items() 
            if p.startswith(prefix) for id in ids
        }
    
    def _fuzzy_match(self, query: str, candidate_ids: set[int], limit: int) -> list[Course]:
        """Fuzzy match query against candidates and return top results."""
        candidate_indices = list(candidate_ids)
        search_texts = [self.search_texts[i] for i in candidate_indices]
        
        results = process.extract(
            query,
            search_texts,
            scorer=fuzz.partial_ratio,
            limit=min(limit * 2, len(candidate_indices)),
        )
        
        matched = [
            (self.courses[candidate_indices[idx]], score)
            for _, score, idx in results if score > 50
        ]
        matched.sort(key=lambda x: -x[1])
        
        return [course for course, _ in matched[:limit]]
    
    def _get_sorted(self, ids: set[int], sort_by: str, limit: int) -> list[Course]:
        """Get courses by IDs in specified sort order."""
        if sort_by in self.sorted_by:
            # Use pre-sorted index
            sorted_ids = [i for i in self.sorted_by[sort_by] if i in ids]
        else:
            sorted_ids = sorted(ids)
        
        return [self.courses[i] for i in sorted_ids[:limit]]
    
    def detect_conflicts(self, courses: list[Course]) -> list[Conflict]:
        """Detect time conflicts between courses."""
        conflicts = []
        
        for i, c1 in enumerate(courses):
            for c2 in courses[i + 1:]:
                conflict = self._check_conflict(c1, c2)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _check_conflict(self, c1: Course, c2: Course) -> Conflict | None:
        """Check if two courses have a time conflict."""
        for m1 in c1.schedule:
            for m2 in c2.schedule:
                overlap_day = self._days_overlap(m1.days, m2.days)
                if overlap_day and self._times_overlap(m1, m2):
                    return Conflict(
                        course1_id=c1.id,
                        course2_id=c2.id,
                        course1_code=c1.code,
                        course2_code=c2.code,
                        overlap_day=overlap_day,
                        overlap_time=f"{m1.start_time}-{m1.end_time}",
                    )
        return None
    
    def _days_overlap(self, days1: str, days2: str) -> str | None:
        """Check if two day strings share any days."""
        d1 = parse_days_to_set(days1)
        d2 = parse_days_to_set(days2)
        common = d1 & d2
        return ", ".join(sorted(common)) if common else None
    
    def _times_overlap(self, m1, m2) -> bool:
        """Check if two meeting times overlap."""
        s1 = parse_time_to_minutes(m1.start_time)
        e1 = parse_time_to_minutes(m1.end_time)
        s2 = parse_time_to_minutes(m2.start_time)
        e2 = parse_time_to_minutes(m2.end_time)
        return s1 < e2 and s2 < e1
    
    # === Grouping Methods ===
    
    def _get_section_prefix(self, section: str) -> str:
        """Extract the letter prefix from a section code (e.g., 'A1' -> 'A', 'B2' -> 'B')."""
        if not section:
            return ""
        # Extract leading letters
        prefix = ""
        for char in section:
            if char.isalpha():
                prefix += char
            else:
                break
        return prefix.upper()
    
    def _section_sort_key(self, section: str) -> tuple[str, int]:
        """Generate a sort key for section codes (e.g., 'A1' -> ('A', 1), 'B10' -> ('B', 10))."""
        if not section:
            return ("", 0)
        
        prefix = ""
        num_str = ""
        
        for char in section:
            if char.isalpha():
                if not num_str:  # Still in prefix
                    prefix += char
            elif char.isdigit():
                num_str += char
        
        num = int(num_str) if num_str else 0
        return (prefix.upper(), num)
    
    def group_sections(self, courses: list[Course]) -> list[GroupedCourse]:
        """
        Group courses by code+term, with primary sections containing related sections.

        Grouping rules:
        - Primary types: Lecture, IND, DRS, EXP, MUO, PLB, THP, OTH (shown as main entry)
        - Secondary types: Discussion, Laboratory (grouped under matching primary)
        - Multiple lectures for same code = separate groups (each gets its own discussions)
        - Discussions are matched to lectures by section prefix (A1 lecture gets A2, A3 discussions)
        - Discussion-only courses = show as primary
        """
        
        # Group by code+term
        by_code_term: dict[tuple[str, str], list[Course]] = defaultdict(list)
        for course in courses:
            key = (course.code, course.term)
            by_code_term[key].append(course)
        
        result: list[GroupedCourse] = []
        
        for (code, term), group in by_code_term.items():
            # Separate primary and secondary sections
            primaries = [c for c in group if c.section_type in PRIMARY_SECTION_TYPES]
            secondaries = [c for c in group if c.section_type in SECONDARY_SECTION_TYPES]
            
            # If no primaries, promote first secondary to primary
            if not primaries and secondaries:
                primaries = [secondaries[0]]
                secondaries = secondaries[1:]
            
            # Build a map of section prefix -> primary course
            prefix_to_primary: dict[str, Course] = {}
            for primary in primaries:
                prefix = self._get_section_prefix(primary.section)
                if prefix and prefix not in prefix_to_primary:
                    prefix_to_primary[prefix] = primary
            
            # Match secondaries to primaries by section prefix
            primary_to_related: dict[str, list[RelatedSection]] = {p.id: [] for p in primaries}
            unmatched_secondaries: list[Course] = []
            
            for sec in secondaries:
                sec_prefix = self._get_section_prefix(sec.section)
                matched_primary = prefix_to_primary.get(sec_prefix)
                
                if matched_primary:
                    primary_to_related[matched_primary.id].append(RelatedSection(
                        id=sec.id,
                        section=sec.section,
                        section_type=sec.section_type,
                        professor=sec.professor,
                        schedule=sec.schedule,
                        status=sec.status,
                        enrollment_cap=sec.enrollment_cap,
                        enrollment_total=sec.enrollment_total,
                        professor_rating=sec.professor_rating,
                    ))
                else:
                    unmatched_secondaries.append(sec)
            
            # Unmatched secondaries are shared across ALL primaries
            # (e.g., EK381 has lectures A1, B1, C1 that all share discussions D1, D2, D3)
            if unmatched_secondaries and primaries:
                for sec in unmatched_secondaries:
                    related_section = RelatedSection(
                        id=sec.id,
                        section=sec.section,
                        section_type=sec.section_type,
                        professor=sec.professor,
                        schedule=sec.schedule,
                        status=sec.status,
                        enrollment_cap=sec.enrollment_cap,
                        enrollment_total=sec.enrollment_total,
                        professor_rating=sec.professor_rating,
                    )
                    # Add to ALL primaries since they share these sections
                    for primary in primaries:
                        primary_to_related[primary.id].append(related_section)
            
            # Create grouped courses with sorted related sections
            for primary in primaries:
                related = primary_to_related.get(primary.id, [])
                # Sort related sections by section code (e.g., A1, A2, A3, B1, B2)
                related.sort(key=lambda s: (s.section_type, self._section_sort_key(s.section)))
                result.append(GroupedCourse.from_course(primary, related))
        
        return result
    
    def search_grouped(
        self,
        query: str = "",
        sort_by: str = "relevance",
        limit: int = 100,
        offset: int = 0,
        **filters: str | None,
    ) -> tuple[list[GroupedCourse], int]:
        """
        Search courses and return grouped results.
        
        Returns tuple of (grouped_courses, total_count).
        Pagination applies to grouped courses, not individual sections.
        """
        # Get all matching courses (we need full results for grouping)
        candidate_ids = self.bitmap_index.filter(**filters)
        query = query.strip()
        
        if query:
            candidate_ids &= self._get_query_candidates(query)
            if not candidate_ids:
                return [], 0
            # Get matched courses with scores
            matched_courses = self._fuzzy_match(query, candidate_ids, len(candidate_ids))
        else:
            matched_courses = self._get_sorted(candidate_ids, sort_by, len(candidate_ids))
        
        # Group all matched courses
        grouped = self.group_sections(matched_courses)
        
        # Sort grouped results
        if sort_by == "code":
            grouped.sort(key=lambda g: g.code)
        elif sort_by == "title":
            grouped.sort(key=lambda g: g.title.lower())
        # For relevance, keep the order from fuzzy match
        
        total = len(grouped)
        
        # Apply pagination to grouped results
        paginated = grouped[offset:offset + limit]
        
        return paginated, total
