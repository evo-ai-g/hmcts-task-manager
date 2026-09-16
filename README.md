# HMCTS Task Manager

A small full-stack application that lets caseworkers create, view, update, and delete their tasks.

- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, SQLite, Pydantic v2
- **Frontend:** Static HTML + vanilla JavaScript, styled with the [GOV.UK Design System](https://design-system.service.gov.uk/)
- **Tests:** pytest, 15 tests covering every endpoint and error path

---

## Running locally

### Prerequisites

- Python 3.11 or newer
- Git

### Setup

From a terminal:

```bash
git clone <your-repo-url>
cd hmcts-task-manager/backend

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
Start the server
bash
uvicorn app.main:app --reload --port 8001
Then open:

UI: http://localhost:8001/

API docs (Swagger UI): http://localhost:8001/docs

ReDoc: http://localhost:8001/redoc

Health check: http://localhost:8001/health

The SQLite database (tasks.db) is created automatically on first run. Delete it to reset.

Run the tests
bash
pytest -v
All 15 tests should pass in under a second. Tests run against an in-memory SQLite database — they never touch your real data.

API endpoints
All endpoints are under /api/v1. Request and response bodies use camelCase (to match the HMCTS starter repositories) and ISO 8601 timestamps.

Method	Path	Description	Success	Errors
POST	/api/v1/tasks	Create a task	201	422 validation
GET	/api/v1/tasks	List all tasks, ordered by due date	200	—
GET	/api/v1/tasks/{id}	Retrieve a task by ID	200	404
PATCH	/api/v1/tasks/{id}/status	Update a task's status	200	404, 422
DELETE	/api/v1/tasks/{id}	Delete a task	204	404
GET	/health	Liveness check	200	—
Task shape
json
{
  "id": 1,
  "title": "Review case file ABC-123",
  "description": "Check evidence pack before hearing",
  "status": "TODO",
  "dueDate": "2026-09-20T09:00:00Z",
  "createdAt": "2026-09-16T10:43:45",
  "updatedAt": "2026-09-16T10:43:45"
}
status is one of TODO, IN_PROGRESS, DONE.

Error shape
json
{ "detail": "Task 999 not found" }
Validation errors (HTTP 422) return FastAPI's standard field-level detail array, listing every field that failed and why.

Project layout
text
hmcts-task-manager/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app, CORS, router registration, static file serving
│   │   ├── config.py       # Settings loaded from env vars
│   │   ├── database.py     # SQLAlchemy engine, session factory, get_db dependency
│   │   ├── models.py       # ORM models (Task, TaskStatus)
│   │   ├── schemas.py      # Pydantic schemas (validation, camelCase serialisation)
│   │   ├── crud.py         # Database operations (create, list, get, update, delete)
│   │   └── routers/
│   │       └── tasks.py    # /api/v1/tasks HTTP layer
│   ├── tests/
│   │   ├── conftest.py     # Pytest fixtures: in-memory DB, TestClient
│   │   └── test_tasks.py   # 15 tests
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html          # Single-file UI (GOV.UK Design System)
└── README.md
Design decisions
Layered architecture
The backend is split into four layers, each with a single responsibility:

routers/ — HTTP concerns (URL paths, status codes, response models)

crud.py — database operations, one function per operation

models.py — the database schema (columns, types, constraints)

schemas.py — the API contract (what JSON goes in and out)

This means changing the database from SQLite to Postgres only touches database.py. Adding caching only touches crud.py. Changing an endpoint's URL only touches routers/. No layer bleeds into another.

camelCase JSON, snake_case Python
The HMCTS starter repositories use camelCase field names (caseNumber, createdDate). Python convention is snake_case. Rather than compromise either, the Pydantic schemas use an alias generator that converts on the way out. Python code reads task.due_date; the JSON on the wire is "dueDate".

UTC timestamps
All timestamps are stored in UTC (datetime.now(timezone.utc)). This is the only safe way to handle time zones — convert to local time only at display time. The frontend formats using toLocaleString('en-GB').

Validation in one place
Pydantic schemas define every rule:

title: non-blank, 1–200 characters

description: optional, up to 2000 characters

status: one of three enum values

dueDate: required, must parse as a date

FastAPI enforces these automatically before any endpoint code runs. Invalid input returns HTTP 422 with a field-level error list — no manual validation code required.

Tests use an in-memory database
tests/conftest.py sets DATABASE_URL=sqlite:// before importing the app, then overrides FastAPI's get_db dependency to point at a fresh in-memory SQLite database per test. The suite runs in 0.3 seconds, has zero side effects on the real database, and each test is fully isolated.

The frontend is a single static file
frontend/index.html is plain HTML, CSS, and JavaScript. There is no build step, no Node.js, no bundler. FastAPI serves it directly via StaticFiles. This was a deliberate choice:

It matches the real GOV.UK approach (server-rendered pages, progressive enhancement)

It removes an entire toolchain from the project

It can be moved behind nginx later without touching the HTML — the file doesn't care who serves it

GOV.UK Design System
The UI uses the official GOV.UK Design System — the same components used across government services, including HMCTS. This includes the header, footer, skip link, error summary, form groups, table, tags, and buttons. Using the real design system ensures accessibility compliance and visual consistency with the domain.

Assumptions and trade-offs
No authentication. The spec doesn't ask for it, and adding it would obscure the core deliverable. In production, this would sit behind HMCTS's existing auth layer.

SQLite by default. Fast enough for a single-instance service and requires zero setup. The DATABASE_URL environment variable makes swapping to Postgres a one-line change.

No migrations. Tables are created with Base.metadata.create_all() on startup. For a production system you'd use Alembic; for this scope, create_all is correct.

Timestamps lose their timezone marker in SQLite. SQLite doesn't store timezone info on DateTime columns, so 2026-09-16T10:43:45Z is read back as 2026-09-16T10:43:45. This is a SQLite limitation, not a code bug. Postgres doesn't have this problem.

No pagination on GET /tasks. The spec doesn't require it. If task counts grow, add limit/offset query parameters to crud.list_tasks.

No optimistic concurrency. Two users editing the same task at once would race. Adding a version column or If-Match header would fix it.

What I'd add next
If this were going further than a technical test:

Alembic migrations — proper schema versioning instead of create_all

Pagination — ?limit=&offset= on the list endpoint

Authentication — JWT or HMCTS SSO, with per-user task scoping

Structured logging — JSON logs with request IDs for observability

Docker and docker-compose — reproducible one-command startup

GitHub Actions CI — lint, test, build on every push

Rate limiting — on the API, per IP or per user

Richer filtering — list only tasks by status or due-date range

License
MIT — see LICENSE.