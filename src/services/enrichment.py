"""
Course enrichment service - adds professor ratings to courses.

Optimizations:
- Uses model_copy() instead of model_dump() for better performance
- Batches professor lookups to avoid redundant cache hits
"""

from src.models import Course, GroupedCourse, RelatedSection, ProfessorRating
from src.rmp import RMPCache


class EnrichmentService:
    """Service for enriching courses with professor ratings."""

    def __init__(self, rmp_cache: RMPCache):
        self.rmp_cache = rmp_cache

    def enrich_courses(self, courses: list[Course]) -> list[Course]:
        """
        Add professor ratings to a list of courses.

        Optimization: Batches unique professors to avoid redundant cache lookups.

        Args:
            courses: List of courses to enrich

        Returns:
            List of enriched courses with professor_rating field populated
        """
        # Batch lookup: get unique professors and their ratings
        unique_professors = {c.professor for c in courses}
        professor_ratings = {
            prof: self.rmp_cache.get_rating(prof)
            for prof in unique_professors
        }

        # Enrich courses using batched data
        enriched = []
        for course in courses:
            rating_data = professor_ratings.get(course.professor)
            if rating_data:
                enriched.append(course.model_copy(update={
                    "professor_rating": ProfessorRating(
                        name=rating_data.name,
                        rating=rating_data.rating,
                        num_ratings=rating_data.num_ratings,
                        difficulty=rating_data.difficulty,
                        would_take_again=rating_data.would_take_again,
                        rmp_url=rating_data.rmp_url,
                    )
                }))
            else:
                enriched.append(course)

        return enriched

    def enrich_grouped_courses(self, grouped_courses: list[GroupedCourse]) -> list[GroupedCourse]:
        """
        Add professor ratings to grouped courses and their related sections.

        Optimization: Batches all professors (main + related sections) for single lookup.

        Args:
            grouped_courses: List of grouped courses to enrich

        Returns:
            List of enriched grouped courses
        """
        # Batch lookup: collect all unique professors (main courses + related sections)
        unique_professors = set()
        for course in grouped_courses:
            unique_professors.add(course.professor)
            for section in course.related_sections:
                unique_professors.add(section.professor)

        professor_ratings = {
            prof: self.rmp_cache.get_rating(prof)
            for prof in unique_professors
        }

        # Enrich courses
        enriched = []
        for course in grouped_courses:
            # Prepare update dict for main course
            update_dict = {}

            # Enrich main course
            rating_data = professor_ratings.get(course.professor)
            if rating_data:
                update_dict["professor_rating"] = ProfessorRating(
                    name=rating_data.name,
                    rating=rating_data.rating,
                    num_ratings=rating_data.num_ratings,
                    difficulty=rating_data.difficulty,
                    would_take_again=rating_data.would_take_again,
                    rmp_url=rating_data.rmp_url,
                )

            # Enrich related sections
            enriched_related = []
            for section in course.related_sections:
                sec_rating = professor_ratings.get(section.professor)
                if sec_rating:
                    enriched_related.append(section.model_copy(update={
                        "professor_rating": ProfessorRating(
                            name=sec_rating.name,
                            rating=sec_rating.rating,
                            num_ratings=sec_rating.num_ratings,
                            difficulty=sec_rating.difficulty,
                            would_take_again=sec_rating.would_take_again,
                            rmp_url=sec_rating.rmp_url,
                        )
                    }))
                else:
                    enriched_related.append(section)

            update_dict["related_sections"] = enriched_related
            enriched.append(course.model_copy(update=update_dict))

        return enriched
