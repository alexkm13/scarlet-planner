.PHONY: run dev test install install-all lint format clean

# Run the API server
run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000

# Run with auto-reload for development
dev:
	uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# Run tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest --cov=src --cov-report=term-missing

# Install basic dependencies
install:
	pip install -e .

# Install all dependencies including dev tools
install-all:
	pip install -e ".[all]"

# Install dev dependencies only
install-dev:
	pip install -e ".[dev]"

# Run linter
lint:
	ruff check src/

# Format code
format:
	ruff format src/
	ruff check --fix src/

# Type check
typecheck:
	mypy src/

# Clean up cache files
clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Scrape course data (requires cookies.txt)
scrape:
	python src/scrape_courses.py

# Refresh RateMyProfessor ratings cache
refresh-rmp:
	python -m src.refresh_rmp

# Show help
help:
	@echo "Available commands:"
	@echo "  make run         - Run the API server"
	@echo "  make dev         - Run with auto-reload"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage"
	@echo "  make install     - Install basic dependencies"
	@echo "  make install-all - Install all dependencies"
	@echo "  make lint        - Run linter"
	@echo "  make format      - Format code"
	@echo "  make typecheck   - Run type checker"
	@echo "  make clean       - Clean cache files"
	@echo "  make scrape      - Scrape course data"
	@echo "  make refresh-rmp - Refresh RMP ratings cache"
