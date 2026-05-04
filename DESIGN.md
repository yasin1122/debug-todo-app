# Design Document

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Service Responsibilities](#2-service-responsibilities)
3. [Request Flow](#3-request-flow)
4. [Database Schema](#4-database-schema)
5. [API Reference](#5-api-reference)
6. [Frontend Architecture](#6-frontend-architecture)
7. [Preferences System](#7-preferences-system)
8. [Authentication Flow](#8-authentication-flow)
9. [Key Design Decisions](#9-key-design-decisions)

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                 │
│                                                                 │
│   http://localhost:8000   (served by Python http.server)        │
│   ┌──────────────┐   ┌──────────────────────────────────────┐  │
│   │  login.html  │   │  index.html + app.js + style.css     │  │
│   └──────────────┘   └──────────────────────────────────────┘  │
│             │                         │                         │
│             └─────────────────────────┘                         │
│                           │ fetch() to :8080                    │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────────┐
│                    Proxy  :8080                               │
│                                                               │
│   ┌─────────────────────────────────┐                        │
│   │  CORS + request routing         │                        │
│   │  /preferences  ──► handled here │                        │
│   │  /api/todos    ──► :8081        │                        │
│   │  /api/auth/*   ──► :8082        │                        │
│   └─────────────────────────────────┘                        │
│               │                   │                           │
│        reads/writes          forwards via                     │
│               │              http.client                      │
│               ▼                   │                           │
│      preferences.db               │                          │
└───────────────────────────────────┼───────────────────────────┘
                                    │
              ┌─────────────────────┴──────────────────┐
              │                                        │
              ▼                                        ▼
┌─────────────────────────┐           ┌─────────────────────────┐
│   Todos API  :8081      │           │   Users API  :8082      │
│                         │           │                         │
│  GET    /api/todos      │           │  POST /api/auth/login   │
│  POST   /api/todos      │           │  POST /api/auth/logout  │
│  PUT    /api/todos/:id  │           │  POST /api/auth/verify  │
│  PUT    .../complete    │           │                         │
│  DELETE /api/todos/:id  │           │  ┌─────────────────┐   │
│                         │           │  │    users.db      │   │
│  ┌─────────────────┐   │           │  │  users           │   │
│  │    todos.db      │   │           │  │  sessions        │   │
│  │  todos           │   │           │  └─────────────────┘   │
│  └─────────────────┘   │           └─────────────────────────┘
└─────────────────────────┘
```

---

## 2. Service Responsibilities

| Service    | Port | Owns | Responsibility |
|------------|------|------|----------------|
| Frontend   | 8000 | —    | Serve static files; all UI logic in `app.js` |
| Proxy      | 8080 | `preferences.db` | CORS, routing, user preferences (theme, sort, filter, column visibility) |
| Todos API  | 8081 | `todos.db` | Full CRUD for todos; filtering and sorting |
| Users API  | 8082 | `users.db` | Login/logout/verify; session token lifecycle |

The proxy is the **only** service the browser talks to. The todos and users APIs are internal — they have no CORS configured for browser access.

---

## 3. Request Flow

### Login

```
Browser                  Proxy                  Users API
   │                       │                       │
   │  POST /api/auth/login │                       │
   │──────────────────────►│                       │
   │                       │  POST /api/auth/login │
   │                       │──────────────────────►│
   │                       │                       │ hash password
   │                       │                       │ create session
   │                       │  {token, user_id, ...}│
   │                       │◄──────────────────────│
   │  {token, user_id, ...}│                       │
   │◄──────────────────────│                       │
   │ store in localStorage │                       │
```

### Load todos page

```
Browser                    Proxy                Todos API     Users API
   │                         │                      │             │
   │ POST /api/auth/verify   │                      │             │
   │────────────────────────►│                      │             │
   │                         │  POST /api/auth/verify             │
   │                         │───────────────────────────────────►│
   │                         │◄───────────────────────────────────│
   │◄────────────────────────│                      │             │
   │                         │                      │             │
   │ GET /preferences        │                      │             │
   │────────────────────────►│                      │             │
   │                         │ query preferences.db │             │
   │  {preferences,          │                      │             │
   │   table_settings}       │                      │             │
   │◄────────────────────────│                      │             │
   │                         │                      │             │
   │ GET /api/todos?...      │                      │             │
   │────────────────────────►│                      │             │
   │                         │  GET /api/todos?...  │             │
   │                         │─────────────────────►│             │
   │                         │  [{todo}, {todo}...] │             │
   │                         │◄─────────────────────│             │
   │  [{todo}, {todo}...]    │                      │             │
   │◄────────────────────────│                      │             │
   │ render table            │                      │             │
```

### Create todo

```
Browser                    Proxy                Todos API
   │                         │                      │
   │ POST /api/todos         │                      │
   │ {title, priority, ...}  │                      │
   │────────────────────────►│                      │
   │                         │  POST /api/todos     │
   │                         │─────────────────────►│
   │                         │                      │ INSERT INTO todos
   │                         │  {id: 7, message}    │
   │                         │◄─────────────────────│
   │  {id: 7, message}       │                      │
   │◄────────────────────────│                      │
   │ GET /api/todos?... (reload)                     │
   │────────────────────────►│ ...                  │
```

---

## 4. Database Schema

### todos.db

```
┌─────────────────────────────────────────────────────────────┐
│  todos                                                      │
├──────────────┬──────────────────────────────────────────────┤
│  id          │  INTEGER PRIMARY KEY AUTOINCREMENT           │
│  user_id     │  INTEGER NOT NULL                            │
│  title       │  TEXT NOT NULL                               │
│  description │  TEXT                                        │
│  created_at  │  TIMESTAMP DEFAULT CURRENT_TIMESTAMP         │
│  updated_at  │  TIMESTAMP DEFAULT CURRENT_TIMESTAMP         │
│  due_date    │  TIMESTAMP                                   │
│  is_completed│  BOOLEAN DEFAULT 0                           │
│  priority    │  TEXT DEFAULT 'medium'                       │
│              │  CHECK(priority IN ('low','medium','high'))  │
├──────────────┴──────────────────────────────────────────────┤
│  Indexes: idx_todos_user_id, idx_todos_completed            │
└─────────────────────────────────────────────────────────────┘
```

### users.db

```
┌─────────────────────────────────────────────────────────────┐
│  users                                                      │
├───────────────┬─────────────────────────────────────────────┤
│  id           │  INTEGER PRIMARY KEY AUTOINCREMENT          │
│  username     │  TEXT UNIQUE NOT NULL                       │
│  password_hash│  TEXT NOT NULL  (SHA-256)                   │
│  created_at   │  TIMESTAMP DEFAULT CURRENT_TIMESTAMP        │
│  last_login   │  TIMESTAMP                                  │
└───────────────┴─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  sessions                                                   │
├────────────┬────────────────────────────────────────────────┤
│  token     │  TEXT PRIMARY KEY  (URL-safe random 32 bytes)  │
│  user_id   │  INTEGER NOT NULL → users(id) ON DELETE CASCADE│
│  created_at│  TIMESTAMP DEFAULT CURRENT_TIMESTAMP           │
│  expires_at│  TIMESTAMP NOT NULL  (24 hours from login)     │
├────────────┴────────────────────────────────────────────────┤
│  Indexes: idx_sessions_user_id, idx_sessions_expires        │
└─────────────────────────────────────────────────────────────┘
```

### preferences.db

```
┌─────────────────────────────────────────────────────────────┐
│  user_preferences                                           │
├───────────────┬─────────────────────────────────────────────┤
│  user_id      │  INTEGER PRIMARY KEY                        │
│  theme        │  TEXT DEFAULT 'light'  CHECK(IN('light','dark'))│
│  sort_by      │  TEXT DEFAULT 'created_at'                  │
│  sort_order   │  TEXT DEFAULT 'desc'   CHECK(IN('asc','desc'))  │
│  filter_status│  TEXT DEFAULT 'all'                         │
│  show_completed│ BOOLEAN DEFAULT 1                          │
│  items_per_page│ INTEGER DEFAULT 10   CHECK(IN(5,10,20))    │
└───────────────┴─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  table_settings                                             │
├─────────────────┬───────────────────────────────────────────┤
│  user_id        │  INTEGER PRIMARY KEY                      │
│  visible_columns│  TEXT  (JSON array of column names)       │
│  column_widths  │  TEXT  (JSON object, reserved)            │
│  last_filter    │  TEXT  (reserved)                         │
└─────────────────┴───────────────────────────────────────────┘
```

---

## 5. API Reference

All endpoints are accessed through the proxy at `http://localhost:8080`.

### Authentication

#### POST /api/auth/login

Request:
```json
{ "username": "demo", "password": "demo123" }
```
Response `200`:
```json
{
  "token": "z_BUcIRJlD6...",
  "user_id": 1,
  "username": "demo",
  "expires_at": "2026-05-04T22:48:00"
}
```
Response `401`: `{ "error": "Invalid credentials" }`

---

#### POST /api/auth/verify

Request:
```json
{ "token": "z_BUcIRJlD6..." }
```
Response `200`: `{ "valid": true, "user_id": 1, "username": "demo", "expires_at": "..." }`
Response `401`: `{ "valid": false }`

---

#### POST /api/auth/logout

Request:
```json
{ "token": "z_BUcIRJlD6..." }
```
Response `200`: `{ "message": "Logged out successfully" }`

---

### Todos

All todo endpoints require header: `X-User-Id: <user_id>`

#### GET /api/todos

Query parameters:

| Parameter   | Values                              | Default      |
|-------------|-------------------------------------|--------------|
| status      | all / active / completed / overdue  | all          |
| sort_by     | created_at / title / priority / due_date | created_at |
| sort_order  | asc / desc                          | desc         |

Response `200`: Array of todo objects
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "created_at": "2026-05-03 10:00:00",
    "updated_at": "2026-05-03 10:00:00",
    "due_date": "2026-05-10 00:00:00",
    "is_completed": 0,
    "priority": "medium"
  }
]
```

Priority sort uses semantic ordering: `low=1 < medium=2 < high=3`.
Title sort is case-insensitive (`COLLATE NOCASE`).

---

#### POST /api/todos

Request:
```json
{
  "title": "Buy groceries",
  "description": "Optional",
  "priority": "medium",
  "due_date": "2026-05-10T12:00" 
}
```
`due_date` is optional (omit or pass `null`).

Response `201`: `{ "id": 7, "message": "Todo created successfully" }`
Response `400`: `{ "error": "Title is required" }`

---

#### PUT /api/todos/:id

Request — any subset of fields:
```json
{
  "title": "Updated title",
  "description": "Updated",
  "priority": "high",
  "due_date": "2026-05-15T09:00",
  "is_completed": 0
}
```
Response `200`: `{ "message": "Todo updated successfully" }`
Response `404`: `{ "error": "Todo not found" }`

---

#### PUT /api/todos/:id/complete

No request body.
Response `200`: `{ "message": "Completion toggled successfully" }`

---

#### DELETE /api/todos/:id

Response `200`: `{ "message": "Todo deleted successfully" }`
Response `404`: `{ "error": "Todo not found" }`

---

### Preferences

#### GET /preferences

Header: `X-User-Id: <user_id>`

Response `200`:
```json
{
  "preferences": {
    "user_id": 1,
    "theme": "dark",
    "sort_by": "priority",
    "sort_order": "desc",
    "filter_status": "all",
    "show_completed": 1,
    "items_per_page": 10
  },
  "table_settings": {
    "user_id": 1,
    "visible_columns": ["title", "priority", "due_date", "completed", "actions"],
    "column_widths": {},
    "last_filter": null
  }
}
```
If no record exists for the user, defaults are returned (no row created until first save).

---

#### POST /preferences

Header: `X-User-Id: <user_id>`

Request — send only the keys you want to update:
```json
{
  "preferences": { "theme": "dark", "sort_by": "title" },
  "table_settings": { "visible_columns": ["title", "due_date", "completed", "actions"] }
}
```
Uses upsert logic: INSERT if no row exists, UPDATE otherwise.

Response `200`: `{ "message": "Preferences updated successfully" }`

---

## 6. Frontend Architecture

All client-side logic lives in `app.js` (~420 lines). There is no build step, no framework, no bundler.

### State variables

| Variable        | Type    | Description                                         |
|-----------------|---------|-----------------------------------------------------|
| `currentUser`   | object  | `{ id, username, token }` from localStorage         |
| `allTodos`      | array   | Full list returned by the last `/api/todos` fetch   |
| `filteredTodos` | array   | Same as `allTodos` (server does all filtering)      |
| `currentPage`   | number  | Active pagination page; reset on sort/filter change |
| `userPreferences`| object | Loaded from proxy on startup                        |
| `tableSettings` | object  | Column visibility; loaded from proxy on startup     |
| `editingTodoId` | number\|null | `null` = Add mode, number = Edit mode         |

### Startup sequence

```
DOMContentLoaded
    │
    ├── checkAuth()        verify token → redirect to login if invalid
    │
    ├── loadPreferences()  fetch /preferences
    │       │              apply theme, sort, filter dropdowns
    │       └──────────── applyColumnSettings()
    │
    └── loadTodos()        fetch /api/todos with current filter/sort
            └──────────── renderTodos()
```

### Key functions

| Function             | Triggered by              | Description                               |
|----------------------|---------------------------|-------------------------------------------|
| `loadTodos()`        | Sort/filter change, CRUD  | Fetches and renders the full todo list    |
| `renderTodos()`      | `loadTodos()`, page change| Slices to current page, builds table HTML |
| `applyColumnSettings()`| `renderTodos()`, preferences load | Shows/hides columns in `#todos-table` only |
| `updateSortIndicators()` | `renderTodos()`       | Updates ↑/↓ on active column header      |
| `savePreferences()`  | Any setting change        | Merges and POSTs to /preferences          |
| `editTodo(id)`       | Edit button               | Populates modal with existing todo data   |
| `toggleComplete(id)` | ✓ button                  | PUT .../complete, then reload             |

### Column visibility scope

`applyColumnSettings()` queries `#todos-table [data-column]` — scoped to the table element only. This prevents the Column Settings modal checkboxes (which also have `data-column` attributes) from being hidden when a column is toggled off.

---

## 7. Preferences System

Preferences are split into two categories stored in separate DB tables:

```
User action                 Frontend                   Proxy DB
─────────────────────────────────────────────────────────────────
Toggle dark mode     ──►  savePreferences({            UPDATE user_preferences
                            preferences: {theme:'dark'}  SET theme = 'dark'
                          })                           WHERE user_id = ?

Sort by priority     ──►  savePreferences({            UPDATE user_preferences
(dropdown or header)        preferences: {             SET sort_by = 'priority',
                              sort_by:'priority',          sort_order = 'desc'
                              sort_order:'desc'        WHERE user_id = ?
                          }})

Hide priority column ──►  savePreferences({            UPDATE table_settings
                            table_settings: {          SET visible_columns =
                              visible_columns:[...]      '[...]'
                          }})                          WHERE user_id = ?
```

On page load, `loadPreferences()` fetches both objects and:
1. Sets DOM element values (dropdowns, body class)
2. Stores them in `userPreferences` and `tableSettings` globals
3. Calls `applyColumnSettings()` to show/hide columns

If a user has never saved a preference, the proxy returns hardcoded defaults and no row is written to the database until their first explicit save.

---

## 8. Authentication Flow

```
Login
  │
  ├── POST /api/auth/login
  │     ├── hash password (SHA-256)
  │     ├── DELETE FROM sessions WHERE user_id = ? (single active session)
  │     ├── INSERT INTO sessions (token, user_id, expires_at)
  │     └── return { token, user_id, username, expires_at }
  │
  ├── Store in localStorage: token, user_id, username
  │
  └── Redirect to index.html

Every page load (index.html)
  │
  └── checkAuth()
        ├── Read token from localStorage
        ├── POST /api/auth/verify
        │     └── SELECT session WHERE token = ? AND expires_at > now()
        ├── If invalid → localStorage.clear() → redirect to login.html
        └── If valid  → set currentUser, show username in header

Logout
  │
  ├── POST /api/auth/logout  (DELETE FROM sessions WHERE token = ?)
  ├── localStorage.clear()
  └── Redirect to login.html
```

Token properties:
- Generated with `secrets.token_urlsafe(32)` — 43 characters, URL-safe
- One active session per user (previous session deleted on new login)
- Expiry checked server-side on every verify call
- Stored client-side in `localStorage` (not httpOnly cookies)

---

## 9. Key Design Decisions

### Single proxy entry point
The browser only ever talks to port 8080. This means CORS only needs to be configured once (in the proxy), the backend services don't need to be hardened for browser access, and routing can be changed without updating the frontend.

### Preferences in the proxy layer
User preferences (theme, sort, column visibility) are stored and served by the proxy rather than the todos or users APIs. This keeps the todos API focused on data and avoids coupling UI state to domain logic.

### Server-side filtering and sorting
All filtering (`status=active`) and sorting (`sort_by=priority`) happens in SQL, not in the browser. This keeps the frontend simple — `allTodos` is always exactly what should be displayed, no client-side array manipulation needed.

### Priority sort via CASE expression
Priority is stored as text (`low`/`medium`/`high`), so lexicographic ordering would be wrong (`high < low < medium`). The query maps values to integers for correct semantic ordering:
```sql
ORDER BY CASE priority WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 END
```

### Case-insensitive title sort
Title uses `COLLATE NOCASE` so `apple`, `Banana`, `cherry` sort correctly across mixed-case values.

### No external dependencies
The entire stack runs with Python's standard library and vanilla JS. No pip installs, no npm build step, no framework. This makes the app portable and easy to inspect — every line of behaviour is visible in the four source files.
