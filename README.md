# Todo App

A multi-service todo application with authentication, persistent user preferences, and per-user data isolation. Zero external dependencies — Python standard library and vanilla JavaScript only.

---

## Features

- **Authentication** — session-based login with 24-hour token expiry
- **Todo management** — create, edit, delete, and toggle completion
- **Overdue detection** — past-due incomplete todos highlighted in red
- **Sorting** — by title (case-insensitive), priority, due date, or created date; persists across sessions
- **Filtering** — all / active / completed / overdue
- **Column visibility** — show/hide any table column; persists per user
- **Themes** — light/dark mode; persists per user
- **Pagination** — configurable 5 / 10 / 20 items per page
- **Multi-user** — each user sees only their own todos and preferences

---

## Architecture

```
Browser (port 8000)
        │
        ▼
  Proxy (port 8080)  ◄─── preferences.db
    │          │
    ▼          ▼
Todos API   Users API
(port 8081) (port 8082)
    │            │
 todos.db    users.db
```

The **proxy** is the single entry point for all API calls from the browser. It handles user preferences directly (reading/writing `preferences.db`) and forwards todo and auth requests to the appropriate backend service.

---

## Prerequisites

- Python 3.8+

---

## Setup & Running

### First run

```bash
# 1. Clone the repository
git clone https://github.com/yasin1122/debug-todo-app
cd debug-todo-app

# 2. Start all services (initializes databases on first run)
bash run_all.sh
```

Open **http://localhost:8000** in your browser.

### Subsequent runs

```bash
bash run_all.sh
```

`run_all.sh` only initializes databases the first time — your data is preserved on every subsequent run.

### Stopping

Press `Ctrl+C` in the terminal running `run_all.sh`.

---

## Demo Users

| Username | Password |
|----------|----------|
| demo     | demo123  |
| alice    | alice123 |
| bob      | bob123   |

---

## Service URLs

| Service   | URL                   | Description                       |
|-----------|-----------------------|-----------------------------------|
| Frontend  | http://localhost:8000 | Login and todo UI                 |
| Proxy     | http://localhost:8080 | API gateway + preferences storage |
| Todos API | http://localhost:8081 | Todo CRUD (internal only)         |
| Users API | http://localhost:8082 | Authentication (internal only)    |

The frontend talks exclusively to the proxy. The todo and users APIs are internal — never called directly from the browser.

---

## Project Structure

```
debug-todo-app/
├── backend/
│   ├── todos_api.py       # Todo CRUD API — port 8081
│   └── users_api.py       # Auth API — port 8082
├── proxy/
│   └── proxy.py           # Request router + preferences — port 8080
├── frontend/
│   ├── index.html         # Main app page
│   ├── login.html         # Login page
│   ├── app.js             # All frontend logic
│   └── style.css          # Styles (light + dark theme)
├── database/
│   ├── init_db.py         # One-time database initializer
│   ├── todos.db           # Todo data (git-ignored, auto-created)
│   ├── users.db           # User accounts + sessions (git-ignored)
│   └── preferences.db     # Per-user settings (git-ignored)
├── debug/
│   └── debug_scenarios.md # Debugging practice scenarios
└── run_all.sh             # Start all services (auto-initializes DBs on first run)
```

---

## API Quick Reference

All requests go through the proxy at `http://localhost:8080`.

| Method | Path                    | Header required | Description               |
|--------|-------------------------|-----------------|---------------------------|
| POST   | /api/auth/login         | —               | Login, returns token      |
| POST   | /api/auth/logout        | —               | Invalidate session        |
| POST   | /api/auth/verify        | —               | Validate a token          |
| GET    | /api/todos              | X-User-Id       | List todos (with filters) |
| POST   | /api/todos              | X-User-Id       | Create todo               |
| PUT    | /api/todos/:id          | X-User-Id       | Update todo fields        |
| PUT    | /api/todos/:id/complete | X-User-Id       | Toggle completion         |
| DELETE | /api/todos/:id          | X-User-Id       | Delete todo               |
| GET    | /preferences            | X-User-Id       | Load user preferences     |
| POST   | /preferences            | X-User-Id       | Save user preferences     |

The `X-User-Id` value is returned by the login endpoint.

---

## Debugging Practice

`debug/debug_scenarios.md` documents 20+ injectable debug scenarios covering:

- Slow database queries
- Random API failures
- CORS issues
- Fast token expiry
- Race conditions in preference loading
- SQL injection points
- XSS vulnerabilities
- Memory leaks
- N+1 query problems
