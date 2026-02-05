# BU Course Search - Backend

Fast course search and schedule building API for Boston University students.

## Features

- **Sub-millisecond fuzzy search** across 7k+ courses
- **Filter by subject, term, Hub requirements**
- **Schedule conflict detection**
- **Calendar export** (.ics for Google Calendar, Apple Calendar, etc.)

## Quick Start

```bash
# Install dependencies
pip install -e .

# Run the server (development)
bu-courses
# or: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Run the server (production)
HOST=0.0.0.0 PORT=8000 RELOAD=false bu-courses
# or: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Configuration

Copy `.env.example` to `.env` and adjust as needed. All settings are optional and have defaults.

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | Port |
| `RELOAD` | `false` | Enable auto-reload (dev only) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Comma-separated origins, or `*` for allow all |
| `COURSES_JSON_PATH` | (none) | Path to `courses.json`; if unset, uses `src/data/courses.json` |

For the course scraper (`bu-scrape`), set one of:

- **`BU_COOKIES_JSON`**: JSON string of cookie name → value (e.g. from browser DevTools).
- **`BU_COOKIES_FILE`**: Path to a `.json` file with the same format. Prefer a gitignored file so cookies are not committed.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Liveness/readiness (for proxy or orchestrator) |
| `/api/courses` | GET | Search courses with filters |
| `/api/courses/{id}` | GET | Get single course details |
| `/api/subjects` | GET | List all departments |
| `/api/terms` | GET | List all terms |
| `/api/schedule/validate` | POST | Check for time conflicts |
| `/api/schedule/export` | POST | Generate .ics calendar file |

## Search Examples

```bash
# Basic search
curl "http://localhost:8000/api/courses?q=cs+111"

# Filter by subject
curl "http://localhost:8000/api/courses?subject=CS&term=Fall2026"

# Filter by Hub requirement
curl "http://localhost:8000/api/courses?hub=Quantitative+Reasoning+I"
```

## Data Format

Courses are loaded from `src/data/courses.json` by default (override with `COURSES_JSON_PATH`). Expected format:

```json
[
  {
    "code": "CAS CS 111",
    "title": "Introduction to Computer Science",
    "section": "A1",
    "professor": "John Lapets",
    "term": "Fall 2026",
    "credits": 4,
    "hub_units": ["Quantitative Reasoning I", "Critical Thinking"],
    "schedule": [
      {
        "days": "MWF",
        "start_time": "10:10",
        "end_time": "11:00",
        "location": "CAS 313"
      }
    ]
  }
]
```

## Architecture

```
src/
├── main.py           # FastAPI app, endpoints
├── models.py         # Pydantic schemas
├── config.py         # Env-based config (CORS, host, port)
├── search.py         # In-memory search engine
├── schedule_builder.py  # Schedule conflict detection
├── data_loader.py    # Load courses from JSON
└── ics_export.py     # Calendar file generation
```

## Deployment

1. **Environment**: Set `CORS_ORIGINS` to your frontend origin(s), e.g. `https://your-app.example.com`. Do not use `*` in production if you need credentials.
2. **Process**: Run `bu-courses` or `uvicorn src.main:app --host 0.0.0.0 --port 8000` behind a reverse proxy (nginx, Caddy, etc.). Use a process manager so the app restarts on failure (see below).
3. **Data**: Ensure `courses.json` is present at the path used by the app (default `src/data/courses.json`, or set `COURSES_JSON_PATH`).
4. **Scraper**: To refresh course data, run `bu-scrape` with `BU_COOKIES_JSON` or `BU_COOKIES_FILE` set (session cookies from a logged-in BU Student Link session).
5. **Health**: Probe `GET /api/health` for liveness/readiness; response includes `"ready": true` once course data is loaded.

### Docker

```bash
docker build -t bu-courses .
docker run -p 8000:8000 -e CORS_ORIGINS=https://your-frontend.com bu-courses
```

Mount a custom `courses.json` with `-v /path/to/courses.json:/app/src/data/courses.json` or set `COURSES_JSON_PATH` and a volume.

### systemd

See `deploy/bu-courses.service.example`. Copy to `/etc/systemd/system/bu-courses.service`, set `WorkingDirectory`, `EnvironmentFile`, and `ExecStart` to your venv, then `systemctl enable --now bu-courses`.

### Design Decisions

1. **In-memory search**: 7k courses × ~1KB = ~7MB. Trivial to keep in memory, avoids DB round-trips.

2. **Pre-computed indices**: Filter sets built at startup for O(1) filtering.

3. **rapidfuzz for search**: C-optimized fuzzy matching, battle-tested.

4. **No auth required**: Public course data, no user accounts needed for MVP.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .
```
