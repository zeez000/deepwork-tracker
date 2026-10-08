# Deep Work Session Tracker

A session tracker built with FastAPI, SQLite, SQLAlchemy, Alembic,
React, and Axios. Includes a Python SDK generated using OpenAPI
Generator CLI.

## Features

- Create, start, pause, resume, and complete work sessions.
- Record interruption reasons and pause counts.
- Enforce valid status transitions.
- Mark the fourth pause as interrupted.
- Classify late completion as overdue.
- Automatically abandon expired paused sessions.
- Display session history and completion statistics.
- Persist sessions in SQLite.

## Prerequisites

The project was tested on Windows with:

- Python 3.11.9
- Node.js 24 and npm 11
- Java 17
- Git

Python, npm, and Java must be available on PATH.
Internet access is required for the initial dependency installation
and generator download.

## Setup

Open PowerShell in the project root:

```powershell
.\setupdev.bat
```

The script creates or reuses `env`, installs dependencies, applies
migrations, loads demo sessions, exports the API specification,
generates and installs the Python SDK, runs backend tests, and
builds the frontend.

Stop running application servers before rerunning setup.

## Run

```powershell
.\runapplication.bat
```

Wait for the backend and frontend windows to report that they are ready.

- Frontend: http://localhost:5173
- API documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

Press Ctrl+C in each server window to stop the application.
Ports 8000 and 5173 must be available.

The launcher runs the frontend using Vite's development server.

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/sessions/` | Create a session |
| PATCH | `/sessions/{session_id}/start` | Start a scheduled session |
| PATCH | `/sessions/{session_id}/pause` | Pause an active session |
| PATCH | `/sessions/{session_id}/resume` | Resume a paused session |
| PATCH | `/sessions/{session_id}/complete` | Complete an active session |
| GET | `/sessions/history` | Read history and statistics |

Example creation body:

```json
{
  "title": "Practice Python",
  "goal": "Write API tests",
  "duration": 25
}
```

Example pause body:

```json
{
  "reason": "Taking a water break"
}
```

Invalid input returns 422, missing sessions return 404,
invalid status transitions return 409, and handled database
operation failures return 503.

## Status Rules and Implementation Assumptions

- New sessions are `scheduled`.
- Starting changes `scheduled` to `active`.
- Only `active` sessions can be paused or completed.
- The first three pauses change the status to `paused`.
- Resuming changes `paused` to `active`, provided its deadline
  has not passed.
- The fourth pause changes the status to `interrupted`.
- Completion within 110% of the planned duration is `completed`.
- Completion after that allowance is `overdue`.
- Paused sessions beyond the same deadline become `abandoned`.
  A background check runs approximately every five seconds while
  the backend is running; expired pauses are also checked on resume.
- Terminal statuses are `completed`, `overdue`, `interrupted`,
  and `abandoned`; further lifecycle actions are rejected.

Duration is a whole number of minutes between 1 and 1440.
Elapsed time includes pauses, and early completion is allowed.
Times are stored as UTC; the frontend displays local time.

Completion ratio is:

```text
completed sessions / all terminal sessions
```

It is zero when there are no terminal sessions.
Scheduled, active, and paused sessions are excluded from the denominator.

These timing and ratio choices document the implementation's
interpretation of the challenge.

## Database and Seed Data

Alembic manages the database schema.

```powershell
.\env\Scripts\python.exe -m alembic upgrade head
```

The database is `deepwork.db` in the project root.
It is excluded from Git.

`seed_data.sql` contains three demo sessions. Load them with:

```powershell
.\env\Scripts\python.exe .\load_seed.py
```

Running the loader again does not duplicate the named demo sessions.

## Generated Python SDK

The SDK source is generated in `sdk/`.
Its methods and models are generated from `openapi.json`;
`sdk_example.py` is a usage example.

Regenerate and install:

```powershell
.\env\Scripts\python.exe .\export_openapi.py
npx openapi-generator-cli generate -i .\openapi.json -g python -o .\sdk --additional-properties=packageName=deepwork_sdk,projectName=deepwork-sdk,packageVersion=1.0.0
.\env\Scripts\python.exe -m pip install -e .\sdk
```

With the backend running:

```powershell
.\env\Scripts\python.exe .\sdk_example.py
```

Generator version 7.26.0 is recorded in `openapitools.json`.
The npm wrapper is pinned to 2.41.0.
A `basic-ftp` override to 6.2.2 resolves the dependency advisory
reported during setup.

OpenAPI Generator reports that OpenAPI 3.1 support is in beta.
The generated history client has been checked against the running API.

## Tests and Build

```powershell
.\env\Scripts\python.exe -m pytest tests -q
npm --prefix frontend run build
```

The seven backend tests cover successful completion, invalid
transitions, the fourth-pause limit, validation and missing sessions,
late completion, expired resume, and automatic abandonment.

Tests use a temporary SQLite database.

A Starlette TestClient deprecation warning is currently emitted
for httpx; the seven tests pass.

Dependency checks:

```powershell
npm audit
npm --prefix frontend audit
```

Both npm audits reported zero vulnerabilities at the latest check.

## Main Files

| File or folder | Purpose |
| --- | --- |
| `main.py` | API routes and application configuration |
| `database.py` | Database engine and sessions |
| `models.py` | Database models |
| `schemas.py` | Request and response validation |
| `lifecycle.py` | Background abandonment checks |
| `alembic/` | Database migrations |
| `frontend/` | React interface |
| `tests/` | Backend tests |
| `sdk/` | Generated Python client |
| `setupdev.bat` | Development setup and checks |
| `runapplication.bat` | Application launcher |

## Troubleshooting

- **Port already in use:** stop the earlier server before launching
  another instance.
- **Java not recognized after installation:** reopen VS Code so
  its terminals receive the updated PATH.
- **Frontend cannot reach the API:** confirm the backend is running
  on port 8000 and the frontend uses port 5173.
- **409 response:** check the session's current status and deadline.
- **422 response:** check the request fields against the API documentation.