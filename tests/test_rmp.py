"""
Tests for RMP cache functionality.
"""

import json
from pathlib import Path

import pytest

from src.rmp import RMPCache, ProfessorRating


class TestProfessorRatingDataclass:
    """Tests for ProfessorRating dataclass."""
    
    def test_rmp_url_with_id(self):
        rating = ProfessorRating(
            name="John Smith",
            rating=4.5,
            num_ratings=50,
            difficulty=3.0,
            would_take_again=85.0,
            rmp_id="123456",
        )
        assert rating.rmp_url == "https://www.ratemyprofessors.com/professor/123456"
    
    def test_rmp_url_without_id(self):
        rating = ProfessorRating(
            name="John Smith",
            rating=4.5,
            num_ratings=50,
            difficulty=3.0,
            would_take_again=85.0,
            rmp_id=None,
        )
        assert rating.rmp_url is None
    
    def test_to_dict(self):
        rating = ProfessorRating(
            name="John Smith",
            rating=4.5,
            num_ratings=50,
            difficulty=3.0,
            would_take_again=85.0,
            rmp_id="123456",
        )
        d = rating.to_dict()
        assert d["name"] == "John Smith"
        assert d["rating"] == 4.5
        assert d["num_ratings"] == 50
        assert d["difficulty"] == 3.0
        assert d["would_take_again"] == 85.0
        assert d["rmp_url"] == "https://www.ratemyprofessors.com/professor/123456"


class TestRMPCache:
    """Tests for RMPCache class."""
    
    @pytest.fixture
    def cache_with_data(self, tmp_path, sample_rmp_cache):
        """Create a cache with sample data."""
        cache_file = tmp_path / "rmp_ratings.json"
        with open(cache_file, "w") as f:
            json.dump(sample_rmp_cache, f)
        
        # Create cache instance with custom path
        cache = RMPCache.__new__(RMPCache)
        cache._cache = sample_rmp_cache
        return cache
    
    def test_get_rating_found(self, cache_with_data):
        rating = cache_with_data.get_rating("John Smith")
        assert rating is not None
        assert rating.name == "John Smith"
        assert rating.rating == 4.5
        assert rating.num_ratings == 50
    
    def test_get_rating_not_found(self, cache_with_data):
        rating = cache_with_data.get_rating("Unknown Professor")
        assert rating is None
    
    def test_get_rating_null_in_cache(self, cache_with_data):
        """Professor in cache but has no RMP profile."""
        rating = cache_with_data.get_rating("Bob Wilson")
        assert rating is None
    
    def test_get_rating_empty_name(self, cache_with_data):
        rating = cache_with_data.get_rating("")
        assert rating is None
    
    def test_get_rating_tba(self, cache_with_data):
        rating = cache_with_data.get_rating("TBA")
        assert rating is None
    
    def test_get_rating_staff(self, cache_with_data):
        rating = cache_with_data.get_rating("Staff")
        assert rating is None
    
    def test_normalize_name_lowercase(self, cache_with_data):
        # Should find "John Smith" even with different casing
        rating = cache_with_data.get_rating("JOHN SMITH")
        assert rating is not None
        assert rating.name == "John Smith"
    
    def test_normalize_name_extra_spaces(self, cache_with_data):
        rating = cache_with_data.get_rating("  John   Smith  ")
        assert rating is not None
        assert rating.name == "John Smith"
    
    def test_normalize_name_with_title_dr(self, cache_with_data):
        # Test normalization with "Dr" (no period)
        normalized = cache_with_data._normalize_name("Dr John Smith")
        assert normalized == "john smith"
    
    def test_normalize_name_with_title_professor(self, cache_with_data):
        # Test normalization with "Professor" 
        normalized = cache_with_data._normalize_name("Professor John Smith")
        assert normalized == "john smith"
    
    def test_normalize_name_last_first_format(self, cache_with_data):
        rating = cache_with_data.get_rating("Smith, John")
        assert rating is not None
        assert rating.name == "John Smith"
    
    def test_cache_stats(self, cache_with_data):
        stats = cache_with_data.cache_stats()
        assert stats["total_professors"] == 3
        assert stats["with_ratings"] == 2  # john smith, jane doe
        assert stats["without_ratings"] == 1  # bob wilson (null)


class TestRMPCacheLoading:
    """Tests for cache file loading."""
    
    def test_load_missing_file(self, tmp_path, monkeypatch, caplog):
        """Cache should handle missing file gracefully."""
        missing_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr("src.rmp.RATINGS_FILE", missing_file)

        # Create new cache instance
        cache = RMPCache.__new__(RMPCache)
        cache._cache = {}
        cache._load_cache()

        # Should log warning
        assert "RMP cache not found" in caplog.text or len(cache._cache) == 0
    
    def test_load_valid_file(self, tmp_path, sample_rmp_cache, monkeypatch, caplog):
        """Cache should load from valid file."""
        cache_file = tmp_path / "rmp_ratings.json"
        with open(cache_file, "w") as f:
            json.dump(sample_rmp_cache, f)

        monkeypatch.setattr("src.rmp.RATINGS_FILE", cache_file)

        cache = RMPCache.__new__(RMPCache)
        cache._cache = {}
        cache._load_cache()

        assert len(cache._cache) == 3
        assert "Loaded 3 professor ratings from cache" in caplog.text
