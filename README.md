# Taskflow — Backend Developer Intern Assignment

> **Submitted by:** Aarush Srivatsa
> **Role:** Backend Developer Intern
> **Assignment:** Scalable REST API with Authentication & Role-Based Access Control + Basic Frontend UI
> **Contact:** pitlaaarushsrivatsa@gmail.com/+91 6281636970

---

## Table of Contents

- [Project Overview](#project-overview)
- [Assignment Checklist](#assignment-checklist)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Authentication Flow](#authentication-flow)
- [Database Schema](#database-schema)
- [Frontend UI](#frontend-ui)
- [Security Practices](#security-practices)
- [Scalability Note](#scalability-note)

---

## Project Overview

**Taskflow** is a production-grade role-based task management system. It exposes a versioned REST API built with **FastAPI** and backed by **PostgreSQL** (async). Two roles exist — **Manager** (admin) and **Employee** (user) — each with separate authentication, permissions, and capabilities.

A fully functional **Vanilla JS frontend** connects to all APIs and demonstrates registration, login, JWT-protected dashboards, and complete CRUD on the task entity.

---

## Assignment Checklist

### Backend

| Requirement | Implementation |
|---|---|
| User registration & login with password hashing | `POST /api/v1/employee/register`, `/login` and `POST /api/v1/manager/register`, `/login` — passwords hashed with **Argon2id** |
| JWT authentication | Access tokens (24h) issued on login/register; verified on every protected route via `HTTPBearer` |
| Role-based access (user vs admin) | `Employee` = user role, `Manager` = admin role — enforced via separate `get_current_employee` / `get_current_manager` FastAPI dependencies |
| CRUD on secondary entity (Tasks) | Full `POST`, `GET` (paginated + filtered), `PATCH`, `DELETE` on `/api/v1/manager/tasks` + `GET` + `PATCH status` on `/api/v1/employee/tasks` |
| API versioning | All routes prefixed with `/api/v1/` |
| Error handling & validation | Pydantic v2 validators on all schemas; HTTP exceptions with proper status codes throughout |
| API documentation (Swagger) | Auto-generated at `/docs` by FastAPI |
| Database schema (Postgres) | Full relational schema with UUIDs, FK constraints, cascade rules — see [Database Schema](#database-schema) |

### Frontend

| Requirement | Implementation |
|---|---|
| Built with Vanilla JS | Three single-file HTML pages — no build step, no framework required |
| Register & login | `index.html` — role selector (Employee / Manager), email + password form |
| Protected dashboard (JWT required) | `manager.html` and `employee.html` — redirect to login if no valid token in localStorage |
| CRUD actions on entity | Manager: create, edit (inline), delete tasks, assign to members. Employee: view and update task status |
| Error / success messages from API | Alert banners on every action with auto-dismiss |

### Security & Scalability

| Requirement | Implementation |
|---|---|
| Secure JWT handling | Signed with HS256, expiry enforced server-side, role embedded in payload |
| Rotating refresh tokens | Refresh tokens stored as SHA-256 hashes; revoked on use and on logout |
| Input sanitization & validation | Pydantic field validators on all inputs; HTML-escaped in all frontend renders |
| Scalable project structure | Routers, models, security, and database layers are fully decoupled modules |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI (Python 3.11+) |
| ORM | SQLAlchemy (async) |
| Database | PostgreSQL via asyncpg |
| Password hashing | argon2-cffi (Argon2id) |
| Auth tokens | python-jose (JWT HS256) |
| Validation | Pydantic v2 |
| Frontend | Vanilla HTML / CSS / JS |
| Config management | python-dotenv |
| API docs | Swagger UI (built into FastAPI at `/docs`) |

---

## Project Structure

```
taskflow/
├── main.py                     # App factory, CORS, router registration, lifespan
├── config.py                   # Environment config (DATABASE_URL, SECRET_KEY, token TTLs)
├── requirements.txt
│
├── database/
│   ├── __init__.py
│   ├── initialization.py       # Async engine, session factory, get_db dependency
│   └── models.py               # ORM models: Employee, Manager, Team, Task, RefreshTokens
│
├── security/
│   ├── passwords.py            # Argon2 hash_password() / verify_password()
│   └── tokens.py               # JWT encode/decode, refresh token rotation, auth dependencies
│
├── routers/
│   ├── employee.py             # /api/v1/employee/* — auth, team join/exit, task status updates
│   └── manager.py              # /api/v1/manager/* — auth, team/member management, full task CRUD
│
└── frontend/
    ├── index.html              # Login + register (both roles)
    ├── manager.html            # Manager SPA (dashboard, tasks, members, settings)
    └── employee.html           # Employee SPA (dashboard, my tasks, team, settings)
```

Each concern (auth, routing, DB, security) lives in its own module. Adding a new role or entity means adding a new router + model file — existing code stays untouched.

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database (SSL connection recommended)

### Installation

```bash
# 1. Clone the repository
git clone <your-github-repo-url>
cd taskflow

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and SECRET_KEY

# 5. Start the server
uvicorn main:app --reload --port 8000
```

Visit **http://localhost:8000** — you will be redirected to the login page.
Swagger UI is available at **http://localhost:8000/docs**.

> Database tables are created automatically on first startup via the FastAPI `lifespan` event — no migration step needed to get started.

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
SECRET_KEY=your-random-secret-key-minimum-32-characters
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | Yes | Random secret for signing JWTs — never commit this |

Token lifetimes (configurable in `config.py`):

```python
ACCESS_TOKEN_EXPIRE_HOURS  = 24
REFRESH_TOKEN_EXPIRE_DAYS  = 30
```

---

## API Reference

**Base URL:** `http://localhost:8000/api/v1`
**Full interactive docs:** `http://localhost:8000/docs`

---

### Auth Endpoints (both roles)

> Replace `{role}` with `employee` or `manager`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/{role}/register` | — | Register a new account |
| `POST` | `/api/v1/{role}/login` | — | Login, receive JWT pair |
| `POST` | `/api/v1/{role}/refresh` | — | Rotate refresh token |
| `POST` | `/api/v1/{role}/logout` | Bearer | Revoke refresh token |
| `PATCH` | `/api/v1/{role}/change-password` | Bearer | Update password |

**Register / Login body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Token response:**
```json
{
  "access_token": "<jwt>",
  "refresh_token": "<opaque-token>",
  "token_type": "bearer"
}
```

---

### Employee Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/employee/team/join` | Bearer | Join a team via UUID |
| `POST` | `/api/v1/employee/team/exit` | Bearer | Leave current team |
| `GET` | `/api/v1/employee/team/info` | Bearer | Get current team details |
| `GET` | `/api/v1/employee/tasks` | Bearer | List assigned tasks (paginated + filtered) |
| `PATCH` | `/api/v1/employee/tasks/{task_id}/status` | Bearer | Update task status |

**GET /tasks query params:**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `limit` | int | 10 | Results per page (max 100) |
| `status` | string | — | Filter: `pending`, `in_progress`, `completed` |

---

### Manager Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/manager/team` | Bearer | Create a team |
| `GET` | `/api/v1/manager/team` | Bearer | Get team details |
| `GET` | `/api/v1/manager/team/members` | Bearer | List team members (paginated) |
| `DELETE` | `/api/v1/manager/team/members/{employee_id}` | Bearer | Remove a member |
| `POST` | `/api/v1/manager/tasks` | Bearer | Create a task |
| `GET` | `/api/v1/manager/tasks` | Bearer | List all tasks (paginated + filtered) |
| `PATCH` | `/api/v1/manager/tasks/{task_id}` | Bearer | Update a task |
| `DELETE` | `/api/v1/manager/tasks/{task_id}` | Bearer | Delete a task |
| `GET` | `/api/v1/manager/dashboard` | Bearer | Team stats summary |

**Create Task body:**
```json
{
  "taskname": "Fix login bug",
  "task_description": "OAuth flow fails on Safari.",
  "deadline": "2025-06-01T12:00:00Z",
  "employee_id": "<uuid or omit>"
}
```

**Update Task body** (all fields optional):
```json
{
  "taskname": "Updated name",
  "task_description": "Updated description",
  "deadline": "2025-07-01T12:00:00Z",
  "status": "in_progress",
  "employee_id": "<uuid>",
  "unassign_employee": false
}
```

> Set `unassign_employee: true` to explicitly remove the assignee without providing a replacement.

**Dashboard response:**
```json
{
  "total_tasks": 42,
  "completed": 18,
  "pending": 10,
  "in_progress": 9,
  "overdue": 5,
  "total_members": 6
}
```

---

## Authentication Flow

```
Client                          Server
  |                               |
  |-- POST /register -----------> |  Hash password (Argon2id)
  |<-- access_token + refresh --- |  Sign JWT (HS256, 24h), store refresh hash
  |                               |
  |-- GET /tasks (Bearer JWT) --> |  Decode + verify JWT, check role claim
  |<-- 200 task list ------------ |
  |                               |
  |-- POST /refresh ------------> |  Verify SHA-256 hash in DB
  |                               |  Revoke old token (is_revoked = true)
  |<-- new access + refresh ----- |  Issue new pair
  |                               |
  |-- POST /logout -------------> |  Set is_revoked = true on refresh token
  |<-- 200 logged out ----------- |
```

Key design decisions:

- **Refresh tokens are hashed** before storage — a leaked database does not expose valid tokens
- **Token rotation** — every `/refresh` call immediately invalidates the previous refresh token
- **Role isolation** — `get_current_employee` and `get_current_manager` dependencies reject cross-role tokens with `403 Forbidden`, not `401`
- **Single commit pattern** — `create_tokens()` never commits internally; each calling endpoint owns its transaction, preventing partial writes on failure

---

## Database Schema

```
┌─────────────┐         ┌────────────────┐         ┌──────────────┐
│   manager   │ 1──── 1 │      team      │ 1 ────∞ │   employee   │
│─────────────│         │────────────────│         │──────────────│
│ id (UUID PK)│         │ id (UUID PK)   │         │ id (UUID PK) │
│ email       │         │ created_at     │         │ email        │
│ hashed_pass │         │ manager_id FK  │         │ hashed_pass  │
└─────────────┘         └────────────────┘         │ team_id FK   │
       │                        │                  └──────────────┘
       │                        │ 1                       │
       │                        ∞                         │
       │                 ┌──────────────┐                 │
       └──────────── ∞── │     task     │ ──∞ ────────────┘
                         │──────────────│
                         │ id (UUID PK) │
                         │ taskname     │
                         │ description  │
                         │ status       │  pending | in_progress | completed
                         │ deadline     │
                         │ completed_at │  auto-set when status = completed
                         │ created_at   │
                         │ manager_id FK│  CASCADE on delete
                         │ employee_id  │  SET NULL on delete
                         │ team_id FK   │  CASCADE on delete
                         └──────────────┘

┌─────────────────────────────┐   ┌──────────────────────────────┐
│  employee_refresh_tokens    │   │  manager_refresh_tokens      │
│─────────────────────────────│   │──────────────────────────────│
│ id (UUID PK)                │   │ id (UUID PK)                 │
│ employee_id FK (CASCADE)    │   │ manager_id FK (CASCADE)      │
│ token_hash (SHA-256)        │   │ token_hash (SHA-256)         │
│ expires_at                  │   │ expires_at                   │
│ is_revoked (bool)           │   │ is_revoked (bool)            │
│ created_at                  │   │ created_at                   │
└─────────────────────────────┘   └──────────────────────────────┘
```

All primary keys are server-generated UUIDs (`gen_random_uuid()`). Foreign keys use `CASCADE` for ownership relationships and `SET NULL` for optional references (task assignee, employee's team), so removing a record never silently orphans data.

---

## Frontend UI

Three pages served as static files via FastAPI's `StaticFiles`:

| Page | Route | Purpose |
|---|---|---|
| `index.html` | `/` | Login & register for both roles — role selector toggles between employee/manager endpoints |
| `manager.html` | `/frontend/manager.html` | Manager SPA: dashboard stats, team management, inline task editing, paginated member list |
| `employee.html` | `/frontend/employee.html` | Employee SPA: task list with status dropdowns, team join/leave, completion progress bar |

**JWT handling client-side:**
- Tokens stored in `localStorage` after login
- Every `apiFetch()` helper injects `Authorization: Bearer <token>` automatically
- Any `401` response clears localStorage and redirects to the login page
- The JWT `role` claim is decoded client-side (base64 only, no signature check) purely for routing — all real authorization is enforced server-side

**XSS prevention:** Every piece of user-supplied data rendered into the DOM passes through `escHtml()`, which encodes `&`, `<`, and `>` before insertion.

---

## Security Practices

| Practice | Details |
|---|---|
| **Password hashing** | Argon2id via `argon2-cffi` — winner of the Password Hashing Competition, resistant to GPU and side-channel attacks |
| **JWT signing** | HS256 with a secret loaded from environment variables — never hardcoded |
| **Refresh token storage** | SHA-256 hash only — a leaked database does not expose usable refresh tokens |
| **Token rotation** | Every refresh call invalidates the previous token, limiting the blast radius of a stolen token |
| **Role enforcement** | Server-side dependency injection rejects wrong-role tokens with `403 Forbidden` |
| **Input validation** | Pydantic validators enforce minimum lengths, enum values, and future-only deadlines on every input |
| **SQL injection** | Not possible — all queries go through SQLAlchemy's parameterized ORM layer |
| **XSS** | All user-controlled content is HTML-escaped before DOM insertion |
| **CORS** | Restricted to `http://localhost:8000` by default — update `allow_origins` in `main.py` for production |

---

## Scalability Note

The architecture is designed to scale horizontally with minimal changes.

**Stateless API layer**
JWT auth means any number of API server instances can handle any request — no sticky sessions required. Dropping 10 instances behind a load balancer (AWS ALB, Nginx) requires zero application changes.

**Async throughout**
The full stack is non-blocking: FastAPI runs on ASGI (uvicorn), SQLAlchemy uses async sessions, and asyncpg is a native async PostgreSQL driver. A single process handles thousands of concurrent connections without thread starvation.

**Database scalability**
Connection pooling is already configured (`pool_recycle=1800`, `pool_pre_ping=True`). A connection pooler like **PgBouncer** can be dropped in front of Postgres with no code changes. Read replicas can be introduced by creating a second read-only engine for `SELECT` queries. Any changes and migrations can be done easily using alembic.

**Modular router structure**
Each domain (employee, manager) is a self-contained FastAPI router. A new module — say, `notifications` or `analytics` — is a new file and a single `app.include_router()` call. No existing code changes. This pattern extends naturally to a **microservices split**: each router becomes its own service behind an API gateway, sharing a database or owning its own bounded schema.