# Scarlet Planner

A fast course search and schedule builder for Boston University students. Search 7,000+ courses with fuzzy matching, filter by subject and Hub requirements, build your schedule with conflict detection, and export to Google Calendar or Apple Calendar.

**[Live Demo](https://alexkm13.github.io/scarlet-planner/)** · [API Docs](https://upgraded-bu-course-schedule.onrender.com/docs)

## Features

- **Fast fuzzy search** — Sub-millisecond search across course codes, titles, and descriptions
- **Smart filters** — Subject, term, Hub units, and enrollment status
- **Schedule builder** — Add courses to your schedule with automatic conflict detection
- **Calendar export** — Download `.ics` files for Google Calendar, Apple Calendar, and Outlook
- **Professor ratings** — Rate My Professor integration (where available)
- **Dark mode** — Built-in theme toggle

## Tech Stack

| Layer   | Stack                         |
|---------|-------------------------------|
| Backend | FastAPI, Python 3.11+         |
| Search  | rapidfuzz, pyroaring          |
| Frontend| React, Vite, Tailwind CSS     |
| Hosting | Render (API), GitHub Pages (UI) |

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/courses` | GET | Search courses (fuzzy, filterable) |
| `/api/courses/{id}` | GET | Course details |
| `/api/subjects` | GET | All departments |
| `/api/terms` | GET | All terms |
| `/api/schedule` | GET/POST/DELETE | Schedule builder |
| `/api/schedule/export` | POST | Generate .ics file |
| `/api/health` | GET | Liveness check |

Full docs: [https://upgraded-bu-course-schedule.onrender.com/docs](https://upgraded-bu-course-schedule.onrender.com/docs)

## Deployment

- **Backend (Render):** Connect repo, set Dockerfile, add `CORS_ORIGINS` for your frontend URL
- **Frontend (GitHub Pages):** Workflow on push to `main`; set `VITE_API_URL` in Actions variables
- **Docker:** `docker build -t bu-courses . && docker run -p 8000:8000 -e CORS_ORIGINS=... bu-courses`
- **systemd:** See `deploy/bu-courses.service.example`

## License

MIT