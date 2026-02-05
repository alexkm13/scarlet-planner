# BU Course Search API - production image
FROM python:3.12-slim

WORKDIR /app

# Build deps for C extensions (e.g. pyroaring)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install package and runtime deps (no dev/scraper extras)
COPY pyproject.toml .
COPY README.md .
COPY src/ ./src/
RUN pip install --no-cache-dir -e .

# Non-root user
RUN useradd -m -u 1000 app
USER app

EXPOSE 8000

# Override with env: HOST, PORT, CORS_ORIGINS, COURSES_JSON_PATH
CMD ["bu-courses"]
