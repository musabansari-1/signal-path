# Rolewise

Rolewise is an AI-assisted job-search workspace for developers. It helps a candidate create a project, upload career material, define role criteria, collect jobs, score fit, draft truthful application materials, track applications, prepare for interviews, review portfolio projects, and plan the week.

The product name is configurable with `NEXT_PUBLIC_APP_NAME`.

## Core safety rule

Generated resumes and outreach are grounded in a verified fact registry. AI suggestions that cannot be tied to a source-backed or user-confirmed fact are withheld for review instead of being silently added. Exports are blocked until the user confirms the truthfulness checklist.

## Tech stack

- Frontend: Next.js 16 App Router, React 19, TypeScript, Tailwind CSS, TanStack Query
- Backend: FastAPI, SQLAlchemy 2, Alembic, Pydantic, PostgreSQL, Redis-ready boundaries
- Auth: custom JWT access/refresh flow with HttpOnly cookies and server-tracked refresh sessions
- AI: OpenAI-compatible backend abstraction via `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`
- Files: local private uploads for development; S3-compatible storage can replace the storage service later

## Local setup with Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

The backend container runs `alembic upgrade head` before starting the API.

## Local setup without Docker

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
$env:DATABASE_URL="sqlite:///./rolewise.db"
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

## Environment variables

Copy `.env.example` and adjust values:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `FRONTEND_URL`
- `LLM_API_KEY`
- `LLM_BASE_URL`
- `LLM_MODEL`
- `LOCAL_UPLOAD_DIR`
- `MAX_UPLOAD_BYTES`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_APP_NAME`

If no AI provider is configured, Rolewise uses conservative deterministic fallbacks. It does not invent experience to compensate for a missing key.

## Verification commands

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m ruff check app tests alembic
.\.venv\Scripts\python.exe -m pytest -q
$env:DATABASE_URL="sqlite:///./.migration-test.db"; .\.venv\Scripts\python.exe -m alembic upgrade head; .\.venv\Scripts\python.exe -m alembic check; Remove-Item -LiteralPath .migration-test.db -Force
```

Frontend:

```powershell
cd frontend
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build
```

## Main implemented workflows

1. Register/login with protected workspace routes.
2. Create and activate job-search projects.
3. Upload PDF/DOCX/TXT/Markdown career assets and extract text.
4. Analyze career material into a candidate profile with evidence-backed facts and review suggestions.
5. Define role criteria.
6. Add jobs manually or via CSV import.
7. Parse job requirements and score fit with deterministic category weights.
8. Generate grounded resume drafts and outreach messages.
9. Confirm truthfulness, then export resumes to PDF/DOCX.
10. Track applications and analytics.
11. Generate interview prep from job requirements and verified candidate facts.
12. Audit portfolio project presentation and produce a Codex-ready improvement prompt.
13. Generate and complete a weekly job-search plan.

## Deployment notes

- Frontend can deploy to Vercel with `NEXT_PUBLIC_API_BASE_URL` pointed at the API.
- Backend can deploy to Render/Fly/EC2 with PostgreSQL and Redis.
- Use a strong `JWT_SECRET`, HTTPS, and `AUTH_COOKIE_SECURE=true` in production.
- Replace local upload storage with S3-compatible storage before handling real production resumes at scale.
- Background job and AI log tables are present; a dedicated worker can later process long-running parsing/import/export tasks.

## Current no-scraping stance

The MVP supports manual job paste and CSV import. It intentionally avoids aggressive LinkedIn/job-board scraping and auto-apply behavior.
