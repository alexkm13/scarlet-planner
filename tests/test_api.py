"""
Tests for API endpoints.
"""

import pytest


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_check(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "courses_loaded" in data
        assert "rmp_cache" in data


class TestCourseSearchEndpoint:
    """Tests for /api/courses endpoint."""
    
    def test_search_no_query(self, test_client):
        response = test_client.get("/api/courses")
        assert response.status_code == 200
        data = response.json()
        assert "courses" in data
        assert "total" in data
        assert "query_time_ms" in data
    
    def test_search_with_query(self, test_client):
        response = test_client.get("/api/courses?q=Computer")
        assert response.status_code == 200
        data = response.json()
        assert len(data["courses"]) >= 1
    
    def test_search_with_subject_filter(self, test_client):
        response = test_client.get("/api/courses?subject=CS")
        assert response.status_code == 200
        data = response.json()
        for course in data["courses"]:
            assert course["department"] == "CS"
    
    def test_search_with_multiple_subjects(self, test_client):
        response = test_client.get("/api/courses?subject=CS&subject=MA")
        assert response.status_code == 200
        data = response.json()
        for course in data["courses"]:
            assert course["department"] in ["CS", "MA"]
    
    def test_search_with_term_filter(self, test_client):
        response = test_client.get("/api/courses?term=Fall%202025")
        assert response.status_code == 200
        data = response.json()
        for course in data["courses"]:
            assert course["term"] == "Fall 2025"
    
    def test_search_with_status_filter(self, test_client):
        response = test_client.get("/api/courses?status=Open")
        assert response.status_code == 200
        data = response.json()
        for course in data["courses"]:
            assert course["status"] == "Open"
    
    def test_search_with_limit(self, test_client):
        response = test_client.get("/api/courses?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["courses"]) <= 2
    
    def test_search_includes_professor_rating(self, test_client):
        response = test_client.get("/api/courses?q=John%20Smith")
        assert response.status_code == 200
        data = response.json()
        # Find John Smith's course
        for course in data["courses"]:
            if course["professor"] == "John Smith":
                assert "professor_rating" in course
                if course["professor_rating"]:
                    assert course["professor_rating"]["rating"] == 4.5
                break
    
    def test_search_combined_filters(self, test_client):
        response = test_client.get("/api/courses?subject=CS&status=Open&term=Fall%202025")
        assert response.status_code == 200
        data = response.json()
        for course in data["courses"]:
            assert course["department"] == "CS"
            assert course["status"] == "Open"
            assert course["term"] == "Fall 2025"


class TestCourseBatchEndpoint:
    """Tests for /api/courses/batch endpoint."""

    def test_get_courses_batch(self, test_client):
        response = test_client.get(
            "/api/courses/batch?id=CAS-CS-111-A1-Fall2025&id=CAS-CS-112-A1-Fall2025"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        ids = {c["id"] for c in data}
        assert "CAS-CS-111-A1-Fall2025" in ids
        assert "CAS-CS-112-A1-Fall2025" in ids

    def test_get_courses_batch_empty(self, test_client):
        response = test_client.get("/api/courses/batch")
        assert response.status_code == 422  # Missing required query param

    def test_get_courses_batch_unknown_id(self, test_client):
        response = test_client.get(
            "/api/courses/batch?id=CAS-CS-111-A1-Fall2025&id=FAKE-ID"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "CAS-CS-111-A1-Fall2025"


class TestCourseDetailEndpoint:
    """Tests for /api/courses/{course_id} endpoint."""
    
    def test_get_course_exists(self, test_client):
        response = test_client.get("/api/courses/CAS-CS-111-A1-Fall2025")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "CAS CS 111"
        assert data["professor"] == "John Smith"
    
    def test_get_course_not_found(self, test_client):
        response = test_client.get("/api/courses/FAKE-COURSE-ID")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_course_includes_rating(self, test_client):
        response = test_client.get("/api/courses/CAS-CS-111-A1-Fall2025")
        assert response.status_code == 200
        data = response.json()
        assert "professor_rating" in data


class TestSubjectsEndpoint:
    """Tests for /api/subjects endpoint."""
    
    def test_list_subjects(self, test_client):
        response = test_client.get("/api/subjects")
        assert response.status_code == 200
        data = response.json()
        assert "subjects" in data
        assert "CS" in data["subjects"]
        assert "MA" in data["subjects"]


class TestTermsEndpoint:
    """Tests for /api/terms endpoint."""
    
    def test_list_terms(self, test_client):
        response = test_client.get("/api/terms")
        assert response.status_code == 200
        data = response.json()
        assert "terms" in data
        assert "Fall 2025" in data["terms"]


class TestHubUnitsEndpoint:
    """Tests for /api/hub-units endpoint."""
    
    def test_list_hub_units(self, test_client):
        response = test_client.get("/api/hub-units")
        assert response.status_code == 200
        data = response.json()
        assert "hub_units" in data


class TestScheduleValidationEndpoint:
    """Tests for /api/schedule/validate endpoint."""
    
    def test_validate_no_conflicts(self, test_client):
        # CS 111 (MWF 10:10-11:00) and CS 112 (TuTh 11:00-12:15) don't conflict
        response = test_client.post(
            "/api/schedule/validate",
            json=["CAS-CS-111-A1-Fall2025", "CAS-CS-112-A1-Fall2025"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "conflicts" in data
        assert "total_credits" in data
    
    def test_validate_empty_schedule(self, test_client):
        response = test_client.post("/api/schedule/validate", json=[])
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["total_credits"] == 0


class TestScheduleExportEndpoint:
    """Tests for /api/schedule/export endpoint."""
    
    def test_export_schedule(self, test_client):
        response = test_client.post(
            "/api/schedule/export",
            json=["CAS-CS-111-A1-Fall2025"]
        )
        assert response.status_code == 200
        data = response.json()
        assert "ics" in data
        assert "filename" in data
        assert data["filename"] == "bu_schedule.ics"
        assert "BEGIN:VCALENDAR" in data["ics"]
    
    def test_export_empty_schedule(self, test_client):
        response = test_client.post("/api/schedule/export", json=[])
        assert response.status_code == 200
        data = response.json()
        assert "ics" in data


class TestProfessorRatingEndpoint:
    """Tests for /api/professors/{name}/rating endpoint."""
    
    def test_get_rating_response_structure(self, test_client):
        """Test that rating endpoint returns correct structure."""
        response = test_client.get("/api/professors/Some%20Professor/rating")
        assert response.status_code == 200
        data = response.json()
        # Check response has expected fields
        assert "name" in data
        assert "rating" in data
        assert "num_ratings" in data
        assert "difficulty" in data
        assert "would_take_again" in data
        assert "rmp_url" in data
    
    def test_get_rating_not_found(self, test_client):
        response = test_client.get("/api/professors/Unknown%20Professor%20XYZ/rating")
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] is None
        assert data["num_ratings"] == 0
    
    def test_get_rating_tba(self, test_client):
        response = test_client.get("/api/professors/TBA/rating")
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] is None


class TestBulkRatingsEndpoint:
    """Tests for /api/professors/ratings endpoint."""
    
    def test_get_bulk_ratings_response_structure(self, test_client):
        """Test that bulk ratings endpoint returns correct structure."""
        response = test_client.get(
            "/api/professors/ratings?names=Prof%20A&names=Prof%20B"
        )
        assert response.status_code == 200
        data = response.json()
        assert "ratings" in data
        assert isinstance(data["ratings"], dict)
        assert "Prof A" in data["ratings"]
        assert "Prof B" in data["ratings"]
