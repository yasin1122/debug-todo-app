# Build This App From Scratch — A Beginner's Guide

This guide walks you through building the entire todo app **incrementally**.
You'll start with a single static HTML page and end up with a four-service
architecture (Frontend → Proxy → Backend → Database). At every step you'll
have a **working app you can run and play with** — we never leave you in a
half-broken state for an hour while you implement the next big chunk.

That's the agile spirit: ship something small, see it work, build on it.

---

## Who this is for

You've written a tiny bit of HTML, JavaScript, or Python before. You know
what a function is. You don't have to know anything about databases, HTTP,
servers, or "the stack." You just want to see how all the pieces fit
together when you build a real-ish web app.

You'll write code in **three languages** by the end:

- **HTML** — what the page looks like (the skeleton)
- **JavaScript** — what happens when you click things (in the browser)
- **Python** — what happens on the server (data storage, business logic)
- **SQL** — how to talk to a database (technically a 4th, but it lives inside Python strings)

No frameworks. No `npm install`. No `pip install`. We use only what comes
with Python and what every modern browser already has.

---

## Prerequisites

- **Python 3.8 or newer.** Check with `python3 --version`.
- **A text editor.** Any will do (VS Code, Sublime, even nano).
- **A terminal.** macOS Terminal, Linux bash, or Windows PowerShell/WSL.
- **A modern browser.** Chrome, Firefox, Safari, Edge — any of them.

That's it. No accounts, no installs.

---

## How to use this guide

Each **Phase** below produces a runnable app. The phases are designed so
that:

1. You can stop after any phase and you'll still have something that works.
2. The next phase always builds on the previous one — never a rewrite.
3. Concepts are introduced exactly when you need them, not before.

If you get stuck, the **finished app** is what's in this repo
(`backend/`, `proxy/`, `frontend/`, `database/`). You can always peek there.

Each phase has these sections:

- **Goal** — one sentence about what you'll have at the end.
- **Concepts** — programming ideas you'll meet for the first time.
- **Steps** — numbered, do-them-in-order instructions.
- **Run it** — how to actually see it work.
- **What you just learned** — a short recap.

---

## Setup

Make a fresh directory and `cd` into it. We'll work inside this folder for
the rest of the guide.

```bash
mkdir my-todo-app
cd my-todo-app
```

---

# Act 1 — A todo list in your browser (no server yet)

We'll build the entire frontend first, with no server, no database. The data
will live in your browser only. By the end of Act 1 you'll have a functional
todo list — it just won't survive if you switch devices.

---

## Phase 1 · A static HTML page

**Goal:** open an HTML file in your browser and see a list of todos.

**Concepts:**
- HTML elements and tags
- The `<table>` family of elements
- How a browser opens a file

### Step 1.1 — Create `index.html`

Create a file called `index.html` in your `my-todo-app/` folder, with this
exact content:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Todos</title>
</head>
<body>
    <h1>My Todos</h1>

    <table border="1">
        <thead>
            <tr>
                <th>Title</th>
                <th>Priority</th>
                <th>Done?</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Buy groceries</td><td>High</td><td>○</td></tr>
            <tr><td>Walk the dog</td><td>Medium</td><td>✓</td></tr>
            <tr><td>Finish homework</td><td>Low</td><td>○</td></tr>
        </tbody>
    </table>
</body>
</html>
```

### Step 1.2 — Open it in your browser

You can literally double-click `index.html` in your file manager, or from
the terminal:

- **macOS:** `open index.html`
- **Linux:** `xdg-open index.html`
- **Windows:** `start index.html`

You should see a small table with three rows.

### Concept break: what is HTML?

**HTML** stands for *HyperText Markup Language*. It's a tree of nested tags
that tells the browser what to draw.

- `<tag>content</tag>` is the basic shape. Tags come in opening/closing
  pairs.
- Every page has `<html>` at the root, with `<head>` (metadata, like the
  title in the browser tab) and `<body>` (the visible content).
- `<table>` builds tables: `<thead>` for the header, `<tbody>` for the
  rows, `<tr>` for each row, `<th>` for header cells, `<td>` for data cells.
- `<h1>` is the biggest heading.

The `border="1"` attribute on `<table>` is an old-school way to draw lines.
We'll throw it away in the next phase and use CSS instead.

### What you just learned

- How to write a complete HTML page from scratch.
- The structure of a table.
- How a browser turns text in a file into a visible page.

---

## Phase 2 · Make it look like a real app (CSS)

**Goal:** the page should look halfway decent — proper fonts, spacing, a
clean table. We'll keep the styles in **their own file**, separate from the
HTML, from day one.

**Concepts:**
- CSS selectors
- The browser's default styles
- The cascade
- Why we put styles in a separate file (separation of concerns)

### Step 2.1 — Create `style.css`

Make a new file called `style.css` in the same folder as `index.html`,
with this content:

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    max-width: 700px;
    margin: 2rem auto;
    padding: 0 1rem;
    color: #222;
    background: #f6f6f6;
}

h1 {
    margin-bottom: 1.5rem;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

th, td {
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    background: #fafafa;
    font-weight: 600;
}

tr:hover {
    background: #f0f8ff;
}
```

### Step 2.2 — Tell `index.html` about the stylesheet

Replace your `index.html` with this version. The only difference is the
new `<link>` line in the `<head>` — and we dropped the `border="1"`
because CSS is doing that job now.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Todos</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>My Todos</h1>

    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Priority</th>
                <th>Done?</th>
            </tr>
        </thead>
        <tbody>
            <tr><td>Buy groceries</td><td>High</td><td>○</td></tr>
            <tr><td>Walk the dog</td><td>Medium</td><td>✓</td></tr>
            <tr><td>Finish homework</td><td>Low</td><td>○</td></tr>
        </tbody>
    </table>
</body>
</html>
```

### Step 2.3 — Reload the browser

Save both files and refresh the tab. The table should look much nicer —
soft shadows, a hover effect, proper padding.

### Concept break: what is CSS?

**CSS** stands for *Cascading Style Sheets*. It tells the browser how each
HTML element should look.

A CSS rule has two parts:

```
selector {
    property: value;
}
```

- **Selector** — which element(s). `body` selects the `<body>` tag.
  `th, td` selects all `<th>` and `<td>` tags. `tr:hover` selects a `<tr>`
  while the mouse is over it.
- **Property** — what aspect to change (`color`, `padding`, `font-family`).
- **Value** — what to set it to.

"Cascading" means rules can override each other. A more specific rule wins
(e.g., `body table th` beats plain `th`).

### Concept break: why a separate file?

You **could** put all this CSS inside a `<style>` block in `index.html`,
and the browser would render it identically. But three reasons to split:

1. **Separation of concerns.** Each file does one job — `index.html` is
   structure, `style.css` is appearance. When the page misbehaves, you
   know which file to look at.
2. **Reuse.** When we add a `login.html` later, it can `<link>` the
   same stylesheet and inherit the look for free.
3. **Browser caching.** The browser fetches `style.css` once and reuses
   it across pages. Inline styles are re-downloaded with every page.

`<link rel="stylesheet" href="style.css">` is the magic line. The browser
sees it, fetches the file from the same folder, and applies the rules.

### What you just learned

- CSS lives in a `.css` file that HTML loads with `<link>`.
- Selectors target elements; properties change how they look.
- A bit of styling goes a long way — same HTML, totally different vibe.
- Splitting structure (HTML) from style (CSS) is a habit you build
  from day one.

---

## Phase 3 · Make it interactive (JavaScript)

**Goal:** add new todos by typing and clicking. Toggle done. Delete a todo.
The JavaScript lives in **its own file** (`app.js`), separate from the HTML.

**Concepts:**
- JavaScript variables and arrays
- The DOM (Document Object Model)
- Event listeners
- Re-rendering
- Loading external scripts with `<script src="…">`

### Step 3.1 — Add a few new styles to `style.css`

Append these rules to your existing `style.css` (don't replace the file —
just add to the end):

```css
.add-row {
    margin-bottom: 1rem;
    display: flex;
    gap: 0.5rem;
}
.add-row input { flex: 1; padding: 0.5rem; }
.add-row button { padding: 0.5rem 1rem; }
.done td { color: #999; text-decoration: line-through; }
button { cursor: pointer; }
```

### Step 3.2 — Create `app.js`

Make a new file called `app.js` next to `index.html`, with this content:

```javascript
// The whole list of todos lives in this array.
// Every time we change it, we re-render the table.
let todos = [
    { id: 1, title: 'Buy groceries', done: false },
    { id: 2, title: 'Walk the dog',  done: true  }
];

// Build one <tr> per todo and shove them into the <tbody>.
function render() {
    const tbody = document.getElementById('todos-tbody');
    tbody.innerHTML = todos.map(t => `
        <tr class="${t.done ? 'done' : ''}">
            <td>${t.title}</td>
            <td>${t.done ? '✓' : '○'}</td>
            <td>
                <button onclick="toggleDone(${t.id})">Toggle</button>
                <button onclick="deleteTodo(${t.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

function addTodo() {
    const input = document.getElementById('new-todo');
    const title = input.value.trim();
    if (!title) return;                        // ignore empty input
    const id = Date.now();                     // quick & dirty unique id
    todos.push({ id, title, done: false });
    input.value = '';
    render();
}

function toggleDone(id) {
    const t = todos.find(t => t.id === id);
    if (t) t.done = !t.done;
    render();
}

function deleteTodo(id) {
    todos = todos.filter(t => t.id !== id);
    render();
}

// Wire the Add button up to the addTodo function.
document.getElementById('add-btn').addEventListener('click', addTodo);
// Also handle Enter inside the input box.
document.getElementById('new-todo').addEventListener('keydown', e => {
    if (e.key === 'Enter') addTodo();
});

// First paint.
render();
```

### Step 3.3 — Update `index.html` to add the input row and load `app.js`

Replace `index.html` with this. Two new things: the `<div class="add-row">`
above the table, and the `<script src="app.js"></script>` at the bottom of
the body.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Todos</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>My Todos</h1>

    <div class="add-row">
        <input id="new-todo" placeholder="What needs doing?">
        <button id="add-btn">Add</button>
    </div>

    <table>
        <thead>
            <tr>
                <th>Title</th>
                <th>Done?</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="todos-tbody"></tbody>
    </table>

    <!-- Load app.js LAST, after the elements it touches exist. -->
    <script src="app.js"></script>
</body>
</html>
```

### Step 3.4 — Reload and play

Refresh. Try:
- Typing "Drink water" and pressing Enter.
- Clicking *Toggle* on a row to flip its done state.
- Clicking *Delete*.

The list updates instantly. Refresh the page — and *poof*, your changes are
gone. We'll fix that in Phase 4.

### Concept break: the DOM and re-rendering

The browser keeps an internal tree of all the elements on the page — the
**DOM** (Document Object Model). JavaScript can:

- **Read** elements: `document.getElementById('foo')`
- **Modify** elements: `element.innerHTML = '...'`
- **Listen** for events: `element.addEventListener('click', fn)`

Our `render()` function is the heart of this app: take the `todos` array,
generate one row of HTML per todo, and drop the whole thing into the
`<tbody>` at once. Every time data changes, we just call `render()` again.

This **"re-render the world"** approach is exactly what frameworks like
React do under the hood — except they're smart about only redrawing what
actually changed. For a small app, throwing the whole table away and
rebuilding it is fine.

### Concept break: events

The browser fires **events** for almost everything: clicks, keypresses,
hovers, scrolls. Your code can listen for them with `addEventListener`.
The `(e) => { ... }` style is an arrow function — a short way to write
a function in JavaScript.

### Concept break: why `<script>` at the bottom?

The browser reads HTML top-to-bottom. If you put `<script>` in the
`<head>`, it runs *before* the rest of the page exists, and lines like
`document.getElementById('add-btn')` return `null` because the button
hasn't been created yet.

Two options solve this:

1. Put the `<script>` tag at the **end of `<body>`** (what we did).
2. Use `<script defer src="app.js">` in the `<head>` — `defer` tells the
   browser "wait until the HTML is fully parsed, then run."

Either works. Bottom-of-body is the easiest mental model: code runs when
the page below it has already been built.

### What you just learned

- HTML, CSS, and JavaScript each live in their own file. The HTML loads
  the other two via `<link>` and `<script>`.
- Storing data in a JavaScript array and re-rendering is a totally valid
  way to build a small app.
- Events are how user actions talk to your code.
- Scripts that touch elements need those elements to already exist —
  hence `<script>` at the bottom of `<body>`.

---

## Phase 4 · Make it remember (localStorage)

**Goal:** changes survive a page refresh.

**Concepts:**
- Browser storage (`localStorage`)
- Serialization (JSON)
- The page lifecycle (load / save)

> 📝 **Heads up:** This phase uses `localStorage` as a **temporary stand-in
> for a real database** — it's the simplest way to have a working,
> persistent app before we introduce a backend. **Phase 5 throws all this
> away** and moves the data to a Python server + SQLite. The finished
> repo only uses `localStorage` for one thing: the session token after
> login (Phase 9). Todos themselves never live in `localStorage` in the
> final app.

### Step 4.1 — Add load/save helpers

Open `app.js`. Replace the lines

```javascript
let todos = [
    { id: 1, title: 'Buy groceries', done: false },
    { id: 2, title: 'Walk the dog',  done: true  }
];
```

with this:

```javascript
// Load todos from the browser's localStorage on first run.
// localStorage only stores strings, so we JSON.parse the saved value.
let todos = JSON.parse(localStorage.getItem('todos') || '[]');

// Helper: write the current todos back to localStorage.
function save() {
    localStorage.setItem('todos', JSON.stringify(todos));
}
```

Now add a call to `save()` at the end of `addTodo`, `toggleDone`, and
`deleteTodo` — anywhere the array changes:

```javascript
function addTodo() {
    const input = document.getElementById('new-todo');
    const title = input.value.trim();
    if (!title) return;
    todos.push({ id: Date.now(), title, done: false });
    input.value = '';
    save();        // 👈 new
    render();
}

function toggleDone(id) {
    const t = todos.find(t => t.id === id);
    if (t) t.done = !t.done;
    save();        // 👈 new
    render();
}

function deleteTodo(id) {
    todos = todos.filter(t => t.id !== id);
    save();        // 👈 new
    render();
}
```

### Step 4.2 — Test it

Reload, add a few todos, refresh the page. They're still there!

Open DevTools (`F12` or right-click → Inspect) → **Application** tab →
**Local Storage** → click your origin. You'll see a key called `todos`
with your data as JSON.

### Concept break: localStorage

`localStorage` is a tiny, browser-built-in **key-value store**. Both keys
and values are strings. It's persistent — survives refreshes, browser
restarts, even reboots. It's per-origin, so `localhost:8000`'s data is
hidden from any other site.

Two methods you care about:

- `localStorage.setItem('key', 'value')` — write
- `localStorage.getItem('key')` — read (returns `null` if missing)

To store a JavaScript object or array, you have to **serialize** it first
because localStorage only knows strings:

```javascript
localStorage.setItem('todos', JSON.stringify(todos));   // object → string
const todos = JSON.parse(localStorage.getItem('todos')); // string → object
```

`JSON` (JavaScript Object Notation) is the universal format for moving
structured data around. You'll see it again when we add a server.

### What you just learned

- The browser ships with a tiny database called `localStorage`.
- JSON is how you turn objects into strings and back.
- Persistence often means: **load on start, save on every change**.

🎉 **Act 1 done.** You have a fully functional todo app that works
entirely in the browser. No server, no internet needed. For a single user
on a single device, this is genuinely complete.

---

# Act 2 — Add a real backend

Now we'll move the data out of the browser and into a Python server. This
is the moment "frontend" and "backend" become two separate things in your
mental model.

---

## Phase 5 · A Python server replaces localStorage

**Goal:** the data lives on the server now. The browser asks for it.

**Concepts:**
- HTTP (request/response)
- A server vs a client
- `fetch` in JavaScript
- Serving static files and an API from the same Python process

### Step 5.1 — Create `server.py`

In your `my-todo-app/` folder, create `server.py`:

```python
#!/usr/bin/env python3
# A tiny web server that does two jobs:
#   1. Serves index.html (and any other files) from the current directory.
#   2. Provides a JSON API at /api/todos.

from http.server import SimpleHTTPRequestHandler, HTTPServer
import json

# In-memory list of todos. We'll replace this with a real database next phase.
todos = [
    {'id': 1, 'title': 'Buy groceries', 'done': False},
    {'id': 2, 'title': 'Walk the dog',  'done': True},
]
next_id = 3   # what id the next-created todo will get


class Handler(SimpleHTTPRequestHandler):
    """Handle one HTTP request at a time."""

    # ---- helpers ----
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---- GET ----
    def do_GET(self):
        if self.path == '/api/todos':
            self.send_json(todos)
        else:
            # Anything that isn't /api/todos falls back to the parent class,
            # which serves files from the current directory (index.html etc.)
            super().do_GET()

    # ---- POST ----
    def do_POST(self):
        global next_id
        if self.path == '/api/todos':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            todo = {'id': next_id, 'title': data['title'], 'done': False}
            next_id += 1
            todos.append(todo)
            self.send_json(todo, status=201)
        else:
            self.send_response(404); self.end_headers()


if __name__ == '__main__':
    print('Server running at http://localhost:8000')
    HTTPServer(('', 8000), Handler).serve_forever()
```

### Step 5.2 — Update `app.js` to talk to the server

The HTML and CSS stay the same. Only `app.js` changes — we remove the
localStorage stuff and instead `fetch` from the server.

Replace the entire contents of `app.js` with:

```javascript
// The list lives in memory only as a cache of what the server has.
// The "source of truth" is now the server.
let todos = [];

function render() {
    const tbody = document.getElementById('todos-tbody');
    tbody.innerHTML = todos.map(t => `
        <tr class="${t.done ? 'done' : ''}">
            <td>${t.title}</td>
            <td>${t.done ? '✓' : '○'}</td>
            <td>
                <button onclick="toggleDone(${t.id})">Toggle</button>
                <button onclick="deleteTodo(${t.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

// Fetch the todo list from the server.
async function loadTodos() {
    const response = await fetch('/api/todos');
    todos = await response.json();
    render();
}

async function addTodo() {
    const input = document.getElementById('new-todo');
    const title = input.value.trim();
    if (!title) return;
    await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
    });
    input.value = '';
    loadTodos();
}

// We'll wire up Toggle and Delete in Phase 7 once the server supports them.
function toggleDone(id) { alert('Coming in Phase 7!'); }
function deleteTodo(id) { alert('Coming in Phase 7!'); }

document.getElementById('add-btn').addEventListener('click', addTodo);
document.getElementById('new-todo').addEventListener('keydown', e => {
    if (e.key === 'Enter') addTodo();
});

loadTodos();
```

### Step 5.3 — Run the server

In your terminal, from inside `my-todo-app/`:

```bash
python3 server.py
```

You should see:
```
Server running at http://localhost:8000
```

Open **http://localhost:8000** in your browser. You'll see the todos
loaded from the server. Add a new one — it appears, the page refreshes.

But: **stop the server (Ctrl+C) and start it again.** Your todos reset!
That's because they live in memory — they're gone when the Python process
dies. We'll fix that in the next phase with a real database.

### Concept break: HTTP

When your browser asks for `/api/todos`, it's sending an **HTTP request**.
The server sends an **HTTP response**. Every interaction is a request +
response pair.

Anatomy of a request:

```
GET /api/todos HTTP/1.1            ← method + path + version
Host: localhost:8000               ← which host
Accept: application/json           ← what content type the client wants
                                   ← (blank line)
                                   ← (no body for GET)
```

Anatomy of a response:

```
HTTP/1.1 200 OK                    ← version + status code
Content-Type: application/json     ← what's in the body
Content-Length: 137                ← how many bytes
                                   ← (blank line)
[{"id":1,"title":"..."},...]       ← the body
```

The methods you care about:
- **GET** — read something
- **POST** — create something
- **PUT** — update something existing
- **DELETE** — remove something

Status codes you'll meet:
- **200** OK
- **201** Created (we send this for POST)
- **400** Bad Request (the client sent garbage)
- **401** Unauthorized
- **404** Not Found
- **500** Server Error (we crashed)

### Concept break: fetch and async/await

`fetch(url)` makes an HTTP request from the browser. It returns a
**Promise** — a placeholder for "the answer will arrive later".

`async/await` is JavaScript's way of writing asynchronous code that *looks*
synchronous:

```javascript
async function loadTodos() {
    const response = await fetch('/api/todos');   // wait for the response
    const data = await response.json();           // wait for the body to parse
    todos = data;
}
```

Without `await`, you'd be passing callbacks. With `await`, you write line by
line and the runtime handles the waiting.

### What you just learned

- A "frontend" is the code running in the browser.
- A "backend" is the code running on a server.
- They talk to each other over HTTP.
- The same Python script can serve both static files and a JSON API.
- The browser's `fetch()` is how you call an API from JavaScript.

---

## Phase 6 · A real database (SQLite)

**Goal:** todos survive a server restart.

**Concepts:**
- What a database is
- SQL: `CREATE TABLE`, `INSERT`, `SELECT`
- Parameterized queries (don't build SQL with string concatenation!)

### Step 6.1 — Create `init_db.py`

Make a new file `init_db.py`:

```python
#!/usr/bin/env python3
# Run this ONCE to create todos.db with the right shape.

import sqlite3
import os

if os.path.exists('todos.db'):
    os.remove('todos.db')   # start clean every time we run this

conn = sqlite3.connect('todos.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE todos (
        id    INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        done  INTEGER DEFAULT 0
    )
''')

# Seed a couple so the app isn't empty on first launch.
cursor.execute("INSERT INTO todos (title, done) VALUES ('Buy groceries', 0)")
cursor.execute("INSERT INTO todos (title, done) VALUES ('Walk the dog',  1)")

conn.commit()
conn.close()
print('Created todos.db')
```

Run it:

```bash
python3 init_db.py
```

You'll see a new file `todos.db` appear. That's a real SQLite database.

### Step 6.2 — Update `server.py` to use the DB

Replace `server.py` with this version:

```python
#!/usr/bin/env python3
import sqlite3
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

DB_PATH = 'todos.db'


def get_all_todos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row    # rows behave like dicts
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos ORDER BY id')
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def insert_todo(title):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # The ? is a placeholder — sqlite3 fills it in safely.
    # NEVER use f"INSERT ... VALUES ('{title}')" — that's SQL injection.
    cursor.execute('INSERT INTO todos (title) VALUES (?)', (title,))
    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {'id': todo_id, 'title': title, 'done': 0}


class Handler(SimpleHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/todos':
            self.send_json(get_all_todos())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/todos':
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            todo = insert_todo(data['title'])
            self.send_json(todo, status=201)
        else:
            self.send_response(404); self.end_headers()


if __name__ == '__main__':
    print('Server running at http://localhost:8000')
    HTTPServer(('', 8000), Handler).serve_forever()
```

### Step 6.3 — Run it

```bash
python3 server.py
```

Open http://localhost:8000. The seeded todos appear. Add a new one. Stop
the server (Ctrl+C). Restart it. **The data is still there.** That's the
database doing its job.

### Concept break: what is SQLite?

A **database** is just a smarter, faster, structured file for storing
data. **SQLite** is a database that lives entirely inside one file
(`todos.db` here). No separate server process. Every Python install ships
with the `sqlite3` module — zero setup.

Real-world databases like PostgreSQL or MySQL are servers you connect to
over the network. SQLite is the perfect choice for tiny apps, prototypes,
mobile apps, and learning.

### Concept break: SQL

**SQL** (Structured Query Language) is how you talk to almost every
database in existence. The basics:

```sql
-- Create a table (its "shape").
CREATE TABLE todos (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done  INTEGER DEFAULT 0
);

-- Insert a row.
INSERT INTO todos (title) VALUES ('Buy milk');

-- Read rows.
SELECT * FROM todos;
SELECT * FROM todos WHERE done = 0;
SELECT * FROM todos ORDER BY id DESC;

-- Update a row.
UPDATE todos SET done = 1 WHERE id = 7;

-- Delete a row.
DELETE FROM todos WHERE id = 7;
```

That's almost all the SQL you'll need.

### Concept break: parameterized queries

This is **wrong**:

```python
title = "'; DROP TABLE todos; --"
cursor.execute(f"INSERT INTO todos (title) VALUES ('{title}')")
# This actually executes: INSERT INTO todos (title) VALUES (''; DROP TABLE todos; --');
# Goodbye, todos.
```

This is **right**:

```python
cursor.execute("INSERT INTO todos (title) VALUES (?)", (title,))
# sqlite3 escapes the value safely — no matter what's in it.
```

The `?` is a **placeholder**. The library handles escaping for you.
Always use placeholders for any value that came from a user.

### What you just learned

- A database is just a smart file. SQLite needs zero setup.
- SQL has the same handful of commands no matter which DB you use.
- Always parameterize your queries to avoid SQL injection.
- Restarting the server doesn't lose your data anymore.

---

## Phase 7 · Full CRUD

**Goal:** the Toggle and Delete buttons actually work. You can also
update a todo's title.

**Concepts:**
- The "U" and "D" in CRUD
- HTTP methods PUT and DELETE
- URL parameters (`/api/todos/7`)

### Step 7.1 — Update `server.py`

Replace the contents of `server.py` with this expanded version:

```python
#!/usr/bin/env python3
import sqlite3
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer

DB_PATH = 'todos.db'


def query(sql, params=()):
    """Run a SELECT and return list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def execute(sql, params=()):
    """Run an INSERT/UPDATE/DELETE. Returns lastrowid + rowcount."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    last = cursor.lastrowid
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return last, affected


class Handler(SimpleHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def parse_id(self):
        # /api/todos/7 → 7
        parts = self.path.split('/')
        if len(parts) >= 4:
            try: return int(parts[3])
            except ValueError: return None
        return None

    # GET /api/todos
    def do_GET(self):
        if self.path == '/api/todos':
            self.send_json(query('SELECT * FROM todos ORDER BY id'))
        else:
            super().do_GET()

    # POST /api/todos
    def do_POST(self):
        if self.path == '/api/todos':
            data = self.read_body()
            todo_id, _ = execute('INSERT INTO todos (title) VALUES (?)',
                                 (data['title'],))
            self.send_json({'id': todo_id, 'title': data['title'], 'done': 0},
                           status=201)
        else:
            self.send_response(404); self.end_headers()

    # PUT /api/todos/7  →  edit fields
    # PUT /api/todos/7/toggle  →  flip done
    def do_PUT(self):
        todo_id = self.parse_id()
        if todo_id is None:
            self.send_response(404); self.end_headers(); return

        if self.path.endswith('/toggle'):
            _, affected = execute('UPDATE todos SET done = NOT done WHERE id = ?',
                                  (todo_id,))
            if affected == 0:
                self.send_json({'error': 'Not found'}, status=404)
            else:
                self.send_json({'message': 'toggled'})
        else:
            data = self.read_body()
            _, affected = execute('UPDATE todos SET title = ? WHERE id = ?',
                                  (data['title'], todo_id))
            if affected == 0:
                self.send_json({'error': 'Not found'}, status=404)
            else:
                self.send_json({'message': 'updated'})

    # DELETE /api/todos/7
    def do_DELETE(self):
        todo_id = self.parse_id()
        if todo_id is None:
            self.send_response(404); self.end_headers(); return
        _, affected = execute('DELETE FROM todos WHERE id = ?', (todo_id,))
        if affected == 0:
            self.send_json({'error': 'Not found'}, status=404)
        else:
            self.send_json({'message': 'deleted'})


if __name__ == '__main__':
    print('Server running at http://localhost:8000')
    HTTPServer(('', 8000), Handler).serve_forever()
```

### Step 7.2 — Wire up the buttons in `app.js`

Replace the placeholder `toggleDone` and `deleteTodo` functions in `app.js`
with real ones:

```javascript
async function toggleDone(id) {
    await fetch(`/api/todos/${id}/toggle`, { method: 'PUT' });
    loadTodos();
}

async function deleteTodo(id) {
    if (!confirm('Delete this todo?')) return;
    await fetch(`/api/todos/${id}`, { method: 'DELETE' });
    loadTodos();
}
```

### Step 7.3 — Try it

Restart the server (`Ctrl+C` then `python3 server.py`), reload the page.
Now Toggle and Delete actually do what they say. Refresh the page — the
state is preserved.

### Concept break: REST and CRUD

**CRUD** = Create / Read / Update / Delete. These are the four basic
operations on any data store.

**REST** is a convention that maps these to HTTP methods:

| CRUD   | HTTP method | Example                |
|--------|-------------|------------------------|
| Create | POST        | `POST /api/todos`      |
| Read   | GET         | `GET /api/todos/7`     |
| Update | PUT         | `PUT /api/todos/7`     |
| Delete | DELETE      | `DELETE /api/todos/7`  |

The path identifies *what* you're operating on (a collection like
`/api/todos` or a single thing like `/api/todos/7`). The method describes
*what kind of operation* you want.

### What you just learned

- The four CRUD operations and their HTTP equivalents.
- How to parse a path like `/api/todos/7` to extract the `7`.
- `cursor.rowcount` tells you how many rows actually changed (so you can
  return 404 if nothing matched).

---

## Phase 8 · Filtering and sorting in SQL

**Goal:** show only active or only completed todos. Sort alphabetically.

**Concepts:**
- Query string parameters (`?status=active&sort_by=title`)
- SQL `WHERE` and `ORDER BY`
- Why server-side filtering beats client-side

### Step 8.1 — Update the API to accept filters

Replace the `do_GET` method in `server.py` with this:

```python
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(self.path)
        if parsed.path == '/api/todos':
            params = parse_qs(parsed.query)
            status = params.get('status', ['all'])[0]
            sort_by = params.get('sort_by', ['id'])[0]

            sql = 'SELECT * FROM todos'
            args = []

            # Filter
            if status == 'active':
                sql += ' WHERE done = 0'
            elif status == 'completed':
                sql += ' WHERE done = 1'

            # Sort — whitelist column names so we can't be SQL-injected
            # via the URL. NEVER format an untrusted column name into SQL.
            if sort_by in ('id', 'title', 'done'):
                sql += f' ORDER BY {sort_by}'

            self.send_json(query(sql, args))
        else:
            super().do_GET()
```

Note: that `from urllib.parse import urlparse, parse_qs` line really
belongs at the top of the file — move it up next to the other imports.

### Step 8.2 — Add filter and sort dropdowns to the UI

Just above the table in `index.html`, add:

```html
<div class="add-row">
    <label>
        Filter:
        <select id="filter-status">
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
        </select>
    </label>
    <label>
        Sort by:
        <select id="sort-by">
            <option value="id">Date added</option>
            <option value="title">Title</option>
            <option value="done">Done</option>
        </select>
    </label>
</div>
```

And in `app.js`, replace `loadTodos` and add change listeners:

```javascript
async function loadTodos() {
    const status = document.getElementById('filter-status').value;
    const sortBy = document.getElementById('sort-by').value;
    const params = new URLSearchParams({ status, sort_by: sortBy });
    const response = await fetch(`/api/todos?${params}`);
    todos = await response.json();
    render();
}

document.getElementById('filter-status').addEventListener('change', loadTodos);
document.getElementById('sort-by').addEventListener('change', loadTodos);
```

### Step 8.3 — Try it

Restart server. Try the dropdowns. Notice that *the server* is doing the
filtering — your browser just gets back exactly the rows it wants to show.

### Concept break: query strings

When you go to `/api/todos?status=active&sort_by=title`, the part after
the `?` is the **query string**. It's a list of `key=value` pairs joined
with `&`. Servers parse it into a dictionary.

Browsers send query strings on `GET` requests when you submit a form, or
when JS builds them with `URLSearchParams`.

### Why server-side filtering beats client-side

You could load *all* todos and filter them in JavaScript. For 10 todos,
fine. For 10,000, the browser would download 10,000 rows just to show
you 5 of them — wasted bandwidth, slow page, dead battery.

The server is closer to the data and can use the database's index. So:
**filter and sort on the server when you can.** The frontend only
displays what comes back.

### What you just learned

- How to add query parameters to a GET request.
- SQL `WHERE` filters; `ORDER BY` sorts.
- Whitelist column names before splicing them into SQL — even from your
  own UI. Future-you might forget the rule.

🎉 **Act 2 done.** You have a real backend with a real database, and a
frontend that talks to it. This is genuinely how a lot of small web apps
in production are built.

---

# Act 3 — Multi-user, multi-service

This is where things get interesting. We'll add user accounts and split
the app into several backend services.

---

## Phase 9 · Users, sessions, and login

**Goal:** there's a login page. Different users see different todos.

**Concepts:**
- Password hashing
- Session tokens
- `localStorage` (yes, really — it's still useful)
- Per-user data (SQL `WHERE user_id = ?`)

### Step 9.1 — Extend the database

Edit `init_db.py` to add a `users` table and a `user_id` column on todos:

```python
#!/usr/bin/env python3
import sqlite3
import hashlib
import os

if os.path.exists('todos.db'):
    os.remove('todos.db')

conn = sqlite3.connect('todos.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE sessions (
        token   TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE todos (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title   TEXT NOT NULL,
        done    INTEGER DEFAULT 0
    )
''')

# Demo users — hashed passwords, never plain text.
def h(p): return hashlib.sha256(p.encode()).hexdigest()
cursor.execute("INSERT INTO users (username, password_hash) VALUES ('alice', ?)", (h('alice123'),))
cursor.execute("INSERT INTO users (username, password_hash) VALUES ('bob',   ?)", (h('bob123'),))

# A couple of seed todos for each user.
cursor.execute("INSERT INTO todos (user_id, title) VALUES (1, 'Alice: buy milk')")
cursor.execute("INSERT INTO todos (user_id, title) VALUES (2, 'Bob: book dentist')")

conn.commit()
conn.close()
print('Created todos.db')
```

Re-run it:

```bash
python3 init_db.py
```

### Step 9.2 — Add login endpoints to `server.py`

Add these helpers near the top (after `DB_PATH`):

```python
import hashlib
import secrets

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login(username, password):
    rows = query('SELECT id, password_hash FROM users WHERE username = ?',
                 (username,))
    if not rows: return None
    user = rows[0]
    if user['password_hash'] != hash_password(password):
        return None
    token = secrets.token_urlsafe(32)
    execute('INSERT INTO sessions (token, user_id) VALUES (?, ?)',
            (token, user['id']))
    return {'token': token, 'user_id': user['id'], 'username': username}

def user_id_from_token(token):
    rows = query('SELECT user_id FROM sessions WHERE token = ?', (token,))
    return rows[0]['user_id'] if rows else None
```

Now add a route in `do_POST` for login:

```python
        if self.path == '/api/login':
            data = self.read_body()
            result = login(data['username'], data['password'])
            if result:
                self.send_json(result)
            else:
                self.send_json({'error': 'Invalid credentials'}, status=401)
            return
```

And update *every* todos handler to require the user. At the start of each
handler, do:

```python
        token = self.headers.get('X-Token')
        user_id = user_id_from_token(token) if token else None
        if not user_id:
            self.send_json({'error': 'Unauthorized'}, status=401)
            return
```

Then change every SQL query that touches todos to scope by `user_id`:

```python
SELECT * FROM todos WHERE user_id = ?            -- list
INSERT INTO todos (user_id, title) VALUES (?, ?) -- create
UPDATE todos SET title = ? WHERE id = ? AND user_id = ?   -- update
DELETE FROM todos WHERE id = ? AND user_id = ?    -- delete
```

The full updated server is too long to repeat in one block — but the
pattern is what matters: add the auth check, then add `AND user_id = ?`
to every query.

### Step 9.3 — Add login styles to `style.css`

Append a few new rules to `style.css`:

```css
.login-page {
    max-width: 400px;
    margin: 4rem auto;
    text-align: center;
}
.login-page input {
    display: block;
    margin: 0.5rem auto;
    padding: 0.5rem;
    width: 100%;
}
.error { color: crimson; }
```

### Step 9.4 — Create `login.js` with the login logic

Make a new file `login.js`:

```javascript
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const r = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await r.json();
    if (r.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('username', data.username);
        window.location.href = 'index.html';
    } else {
        document.getElementById('error').textContent = data.error;
    }
});
```

### Step 9.5 — Create `login.html`

Create `login.html` next to `index.html`. It reuses our existing
`style.css` and loads our new `login.js`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Login</title>
    <link rel="stylesheet" href="style.css">
</head>
<body class="login-page">
    <h1>Log in</h1>
    <form id="login-form">
        <input id="username" placeholder="Username" required>
        <input id="password" type="password" placeholder="Password" required>
        <button type="submit">Log in</button>
        <p class="error" id="error"></p>
    </form>
    <p>Try <code>alice / alice123</code> or <code>bob / bob123</code></p>

    <script src="login.js"></script>
</body>
</html>
```

### Step 9.6 — Update `app.js` to send the token

At the top of `app.js`:

```javascript
const token = localStorage.getItem('token');
if (!token) window.location.href = 'login.html';
```

And in *every* fetch call, include the token as a header:

```javascript
const response = await fetch('/api/todos', {
    headers: { 'X-Token': token }
});
```

For POST/PUT/DELETE that already have headers:

```javascript
await fetch('/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Token': token },
    body: JSON.stringify({ title })
});
```

### Step 9.7 — Try it

Restart the server, go to **http://localhost:8000/login.html**, log in as
alice. You'll see Alice's todo. Log out (clear localStorage in DevTools or
add a logout button), log in as bob — you'll see Bob's instead.

### Concept break: hashing passwords

You **never** store passwords as plain text. Instead, you store a **hash**:
a one-way scramble.

`SHA-256` turns any input into a 64-character string. The same input
always produces the same hash, but you can't reverse the hash back to
the input. So when a user logs in, you hash what they typed and compare
it to the stored hash. Both should match.

Real apps add a "salt" (random bytes per user) and use slow hashes like
bcrypt or argon2 to make brute-force expensive. SHA-256 is fine for
learning.

### Concept break: session tokens

When the user logs in, the server creates a random string — the **token** —
and remembers which user it belongs to. The browser stores the token and
sends it with every request. The server looks up the token, finds the
user, and proceeds.

This is one of two main patterns:

1. **Server-side sessions** (this approach): server stores tokens in a
   table. Token is just a random opaque string. Easy to invalidate
   (just delete the row).
2. **JWT** (JSON Web Tokens): the token *itself* contains the user info,
   signed by the server. No DB lookup, but harder to invalidate.

Either is fine — use server-side sessions until you have a reason not to.

### What you just learned

- Hashes are one-way; passwords go in, come out scrambled, never back.
- A token is just "an opaque random string the server recognizes."
- Multi-user apps scope every query by `user_id` — anything else is a
  data-leak waiting to happen.

---

## Phase 10 · Split into two backends

**Goal:** auth lives in its own process, separate from todos.

**Concepts:**
- Why split? (separation of concerns)
- Multiple processes that don't share memory
- The frontend now has to know about *two* backends

### Why we're doing this

So far, `server.py` does everything: serves the HTML, handles auth, handles
todos. That's fine for a small project. But in a real system you might
have:

- A team that owns "users" — login, sessions, profiles.
- A team that owns "todos" — domain logic, business rules.

If they share one codebase, every change becomes everyone's problem. If
they're separate processes, each team can ship on its own schedule.

This is called **separation of concerns** or, more buzzwordy,
**microservices**. You don't need it for a side project, but it's a
useful exercise — and it teaches you to think about what crosses the
network.

### Step 10.1 — Reorganize files

Make this directory layout:

```
my-todo-app/
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── app.js
│   ├── login.js
│   └── style.css
├── backend/
│   ├── todos_api.py
│   └── users_api.py
└── database/
    ├── init_db.py
    ├── todos.db
    └── users.db
```

Move every frontend file (`index.html`, `login.html`, `app.js`, `login.js`,
`style.css`) into `frontend/`. Move `init_db.py` into `database/`. Delete
`server.py` — we'll write two new ones.

### Step 10.2 — Split the database in two

Edit `database/init_db.py` to create two separate `.db` files:

```python
#!/usr/bin/env python3
import sqlite3
import hashlib
import os

# --- users.db ---
if os.path.exists('users.db'): os.remove('users.db')
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, '
          'username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)')
c.execute('CREATE TABLE sessions (token TEXT PRIMARY KEY, user_id INTEGER NOT NULL)')
def h(p): return hashlib.sha256(p.encode()).hexdigest()
c.execute("INSERT INTO users (username, password_hash) VALUES ('alice', ?)", (h('alice123'),))
c.execute("INSERT INTO users (username, password_hash) VALUES ('bob',   ?)", (h('bob123'),))
conn.commit(); conn.close()

# --- todos.db ---
if os.path.exists('todos.db'): os.remove('todos.db')
conn = sqlite3.connect('todos.db')
c = conn.cursor()
c.execute('CREATE TABLE todos (id INTEGER PRIMARY KEY AUTOINCREMENT, '
          'user_id INTEGER NOT NULL, title TEXT NOT NULL, done INTEGER DEFAULT 0)')
c.execute("INSERT INTO todos (user_id, title) VALUES (1, 'Alice: buy milk')")
c.execute("INSERT INTO todos (user_id, title) VALUES (2, 'Bob: book dentist')")
conn.commit(); conn.close()
print('Initialized both databases')
```

Run from inside `database/`:

```bash
cd database
python3 init_db.py
cd ..
```

### Step 10.3 — `backend/users_api.py`

```python
#!/usr/bin/env python3
import sqlite3, json, hashlib, secrets, os
from http.server import HTTPServer, BaseHTTPRequestHandler

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'database', 'users.db')

def h(p): return hashlib.sha256(p.encode()).hexdigest()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers(); self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()

        if self.path == '/api/login':
            c.execute('SELECT id, password_hash FROM users WHERE username = ?',
                      (data['username'],))
            row = c.fetchone()
            if not row or row[1] != h(data['password']):
                conn.close(); self.send_json({'error': 'Invalid'}, 401); return
            user_id = row[0]
            token = secrets.token_urlsafe(32)
            c.execute('INSERT INTO sessions (token, user_id) VALUES (?, ?)',
                      (token, user_id))
            conn.commit(); conn.close()
            self.send_json({'token': token, 'user_id': user_id,
                            'username': data['username']})
        elif self.path == '/api/verify':
            c.execute('SELECT user_id FROM sessions WHERE token = ?',
                      (data['token'],))
            row = c.fetchone(); conn.close()
            if row: self.send_json({'valid': True, 'user_id': row[0]})
            else: self.send_json({'valid': False}, 401)
        else:
            conn.close(); self.send_json({'error': 'Not found'}, 404)

if __name__ == '__main__':
    print('Users API on :8082')
    HTTPServer(('', 8082), Handler).serve_forever()
```

### Step 10.4 — `backend/todos_api.py`

```python
#!/usr/bin/env python3
import sqlite3, json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       'database', 'todos.db')

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers(); self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-User-Id')
        self.end_headers()

    def get_user_id(self):
        return self.headers.get('X-User-Id')

    def do_GET(self):
        user_id = self.get_user_id()
        if not user_id: return self.send_json({'error': 'Unauthorized'}, 401)
        conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM todos WHERE user_id = ? ORDER BY id',
                            (user_id,)).fetchall()
        conn.close()
        self.send_json([dict(r) for r in rows])

    def do_POST(self):
        user_id = self.get_user_id()
        if not user_id: return self.send_json({'error': 'Unauthorized'}, 401)
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute('INSERT INTO todos (user_id, title) VALUES (?, ?)',
                  (user_id, data['title']))
        todo_id = c.lastrowid; conn.commit(); conn.close()
        self.send_json({'id': todo_id}, 201)

    def parse_id(self):
        parts = self.path.split('/')
        try: return int(parts[3]) if len(parts) >= 4 else None
        except ValueError: return None

    def do_PUT(self):
        user_id = self.get_user_id()
        if not user_id: return self.send_json({'error': 'Unauthorized'}, 401)
        todo_id = self.parse_id()
        if todo_id is None: return self.send_json({'error': 'Not found'}, 404)
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        if self.path.endswith('/toggle'):
            c.execute('UPDATE todos SET done = NOT done WHERE id = ? AND user_id = ?',
                      (todo_id, user_id))
        else:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            c.execute('UPDATE todos SET title = ? WHERE id = ? AND user_id = ?',
                      (data['title'], todo_id, user_id))
        affected = c.rowcount; conn.commit(); conn.close()
        if affected == 0: return self.send_json({'error': 'Not found'}, 404)
        self.send_json({'message': 'updated'})

    def do_DELETE(self):
        user_id = self.get_user_id()
        if not user_id: return self.send_json({'error': 'Unauthorized'}, 401)
        todo_id = self.parse_id()
        if todo_id is None: return self.send_json({'error': 'Not found'}, 404)
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute('DELETE FROM todos WHERE id = ? AND user_id = ?',
                  (todo_id, user_id))
        affected = c.rowcount; conn.commit(); conn.close()
        if affected == 0: return self.send_json({'error': 'Not found'}, 404)
        self.send_json({'message': 'deleted'})

if __name__ == '__main__':
    print('Todos API on :8081')
    HTTPServer(('', 8081), Handler).serve_forever()
```

### Step 10.5 — Run three things

You now need three terminals:

```bash
# Terminal 1
python3 backend/users_api.py

# Terminal 2
python3 backend/todos_api.py

# Terminal 3 — serve the frontend statically
cd frontend && python3 -m http.server 8000
```

### Step 10.6 — Update the frontend to talk to two backends

In `frontend/login.js`, change the fetch URL to point at `:8082`:

```javascript
const r = await fetch('http://localhost:8082/api/login', { ... });
```

After a successful login, also remember the `user_id` (from the response) —
the todos API at `:8081` wants it in the `X-User-Id` header:

```javascript
// In login.js, after a successful login:
localStorage.setItem('token', data.token);
localStorage.setItem('user_id', data.user_id);
localStorage.setItem('username', data.username);
```

In `frontend/app.js`, point todo requests at `:8081` and send the user id:

```javascript
// At the top of app.js:
const userId = localStorage.getItem('user_id');

// Every fetch:
fetch('http://localhost:8081/api/todos', {
    headers: { 'X-User-Id': userId }
});
```

### Step 10.7 — Try it

Reload `http://localhost:8000/login.html`, log in. The frontend now juggles
two servers. **You can see it happen** in the Network tab of DevTools —
some requests go to `:8081`, some to `:8082`.

### Concept break: CORS

Browsers don't let JavaScript on `http://localhost:8000` make a request
to `http://localhost:8081` *unless* the server at `:8081` says it's okay.
That permission slip is **CORS** (Cross-Origin Resource Sharing).

The way you grant permission is by sending response headers:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, X-User-Id
```

Before the actual request, the browser sends a "preflight" `OPTIONS`
request to ask if the real one is allowed. That's why every server here
has a `do_OPTIONS` method.

CORS exists to prevent malicious sites from making authenticated requests
to your bank's API just because you have a tab open. It's annoying when
you're learning but it's a load-bearing security feature.

### What you just learned

- One process per service is a real architectural pattern.
- Splitting code over the network forces you to be explicit about
  contracts (headers, paths, response shapes).
- CORS is the browser's way of letting servers say "yes, this other
  origin is allowed to talk to me."

---

## Phase 11 · Add a proxy

**Goal:** the frontend only talks to *one* backend. The proxy figures
out where each request really goes.

**Concepts:**
- API gateway / reverse proxy
- Why funneling everything through one front door simplifies the FE
- One CORS configuration to rule them all

### Why a proxy?

Right now your frontend hardcodes two URLs. If you add a third service,
you change the frontend. CORS has to be configured everywhere. Auth
checking has to be repeated.

A **proxy** sits in front of all your services. The frontend calls the
proxy at one URL. The proxy decides where each request goes based on the
path:

```
/api/auth/*   → users API
/api/todos/*  → todos API
/preferences  → handled by proxy itself
```

Now the frontend has a single `API_URL`. Adding a new service only changes
the proxy. Auth/CORS/logging/rate-limiting can all live in one place.

### Step 11.1 — Create `proxy/proxy.py`

```python
#!/usr/bin/env python3
import json
import http.client
from http.server import HTTPServer, BaseHTTPRequestHandler

TODOS_API = 'localhost:8081'
USERS_API = 'localhost:8082'

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-User-Id')
        self.end_headers()

    def forward(self, target_host):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else None

        # Strip headers that don't make sense to forward.
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ('host', 'connection')}

        conn = http.client.HTTPConnection(target_host)
        conn.request(self.command, self.path, body, headers)
        upstream = conn.getresponse()
        data = upstream.read()
        conn.close()

        self.send_response(upstream.status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data)

    def route(self):
        if self.path.startswith('/api/auth/'):
            self.forward(USERS_API)
        elif self.path.startswith('/api/todos'):
            self.forward(TODOS_API)
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):    self.route()
    def do_POST(self):   self.route()
    def do_PUT(self):    self.route()
    def do_DELETE(self): self.route()


if __name__ == '__main__':
    print('Proxy on :8080')
    HTTPServer(('', 8080), Handler).serve_forever()
```

### Step 11.2 — Update the user APIs' login path

The proxy sends `/api/auth/login` to the users API. So change
`users_api.py` to listen for that path:

```python
        if self.path == '/api/auth/login':       # was /api/login
            ...
        elif self.path == '/api/auth/verify':    # was /api/verify
            ...
```

### Step 11.3 — Update frontend URLs

In both `login.js` and `app.js`, replace **all** the hardcoded URLs with
one constant at the top:

```javascript
const API_URL = 'http://localhost:8080';
```

Then everywhere you had `http://localhost:8082/api/login`, write
`${API_URL}/api/auth/login`. Anywhere you had `:8081/api/todos`, write
`${API_URL}/api/todos`.

### Step 11.4 — Run four things

You'll need a fourth terminal now:

```bash
# Terminal 1: users
python3 backend/users_api.py
# Terminal 2: todos
python3 backend/todos_api.py
# Terminal 3: proxy
python3 proxy/proxy.py
# Terminal 4: static frontend
cd frontend && python3 -m http.server 8000
```

(See the actual `run_all.sh` in this repo for how to start them all in
one shell.)

### Step 11.5 — Try it

Open `http://localhost:8000/login.html`. Watch the Network tab in
DevTools. **Every** request now goes to `:8080`. The proxy is invisible
to the browser — it just gets the right answer.

### Concept break: API gateway

What you just built is sometimes called an **API gateway** or a **reverse
proxy**. In production you'd use nginx, Caddy, or Cloudflare for this —
but the idea is the same: a single front door that knows where every
request really belongs.

Common things gateways do:

- Route by path or hostname.
- Add CORS headers (so backends don't need to).
- Authenticate (verify the token before forwarding).
- Rate-limit (block clients hammering you).
- Log every request.

The minimal version above covers the routing piece, which is what you'll
build over and over throughout your career.

### What you just learned

- A proxy is a server that forwards requests to other servers.
- It lets the frontend pretend the world is simpler than it is.
- One CORS config in one place beats CORS scattered across N services.

---

## Phase 12 · Per-user preferences

**Goal:** each user can choose dark mode or light mode and it persists
across logins.

**Concepts:**
- Domain-specific data (preferences) vs core data (todos)
- Storing JSON in a TEXT column
- Why the proxy is a great place for cross-cutting state

### Why preferences live in the proxy

User preferences (theme, sort order, items-per-page) aren't really part
of the "todos" or "users" domains. They're more like UI knobs. Putting
them in the proxy keeps the backends focused on their own thing.

(In the finished app this is `preferences.db`, owned by the proxy.)

### Step 12.1 — Add a third database

Add to `database/init_db.py`:

```python
# --- preferences.db ---
if os.path.exists('preferences.db'): os.remove('preferences.db')
conn = sqlite3.connect('preferences.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE user_preferences (
        user_id INTEGER PRIMARY KEY,
        theme   TEXT DEFAULT 'light' CHECK(theme IN ('light','dark'))
    )
''')
conn.commit(); conn.close()
```

Re-run `python3 init_db.py` from inside `database/`. (Yes, this wipes
your data — you'll have to log in fresh.)

### Step 12.2 — Add preference handlers to the proxy

Inside `proxy/proxy.py`, add this near the top:

```python
import sqlite3, os
PREFS_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'database', 'preferences.db')
```

And add these methods to `Handler`:

```python
    def handle_get_preferences(self):
        user_id = self.headers.get('X-User-Id')
        if not user_id: return self.send_json({'error': 'Unauthorized'}, 401)
        conn = sqlite3.connect(PREFS_DB); conn.row_factory = sqlite3.Row
        row = conn.execute('SELECT * FROM user_preferences WHERE user_id = ?',
                           (user_id,)).fetchone()
        conn.close()
        self.send_json(dict(row) if row else {'theme': 'light'})

    def handle_save_preferences(self):
        user_id = self.headers.get('X-User-Id')
        if not user_id: return self.send_json({'error': 'Unauthorized'}, 401)
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        conn = sqlite3.connect(PREFS_DB); c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO user_preferences (user_id, theme) '
                  'VALUES (?, ?)', (user_id, data.get('theme', 'light')))
        conn.commit(); conn.close()
        self.send_json({'message': 'saved'})

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers(); self.wfile.write(body)
```

Now teach `route` about the new path:

```python
    def route(self):
        if self.path == '/preferences':
            if self.command == 'GET':  self.handle_get_preferences()
            else:                      self.handle_save_preferences()
        elif self.path.startswith('/api/auth/'):
            self.forward(USERS_API)
        elif self.path.startswith('/api/todos'):
            self.forward(TODOS_API)
        else:
            self.send_response(404); self.end_headers()
```

### Step 12.3 — Add a theme toggle to `index.html`

Add a button somewhere in the body:

```html
<button id="theme-toggle">🌙</button>
```

### Step 12.4 — Wire up the toggle in `app.js`

Append this to `app.js`:

```javascript
async function loadPreferences() {
    const r = await fetch(`${API_URL}/preferences`, {
        headers: { 'X-User-Id': userId }
    });
    const prefs = await r.json();
    document.body.className = prefs.theme + '-theme';
}

document.getElementById('theme-toggle').addEventListener('click', async () => {
    const newTheme = document.body.className === 'dark-theme' ? 'light' : 'dark';
    document.body.className = newTheme + '-theme';
    await fetch(`${API_URL}/preferences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-User-Id': userId },
        body: JSON.stringify({ theme: newTheme })
    });
});

loadPreferences();
```

### Step 12.5 — Add dark-theme rules to `style.css`

Append to `style.css`:

```css
.dark-theme { background: #1e1e1e; color: #ddd; }
.dark-theme table { background: #2a2a2a; }
.dark-theme th { background: #333; }
```

### Step 12.6 — Try it

Click the moon. The app goes dark. Refresh — still dark. Log in as
another user — *their* theme. Each user has their own preference.

### What you just learned

- Cross-cutting state (theme, sort order, layout) often makes more sense
  in a gateway/proxy than in any one domain backend.
- `INSERT OR REPLACE` is SQLite's "upsert" — insert if missing, update
  if there.

---

# Act 4 — Polish

You now have the same architecture as this repo's finished app. The
remaining differences are UI features. We won't write them all out
line-by-line, but here's the menu — pick what interests you.

---

## Phase 13 · UI features

The finished app in this repo has more than what we've built. Each item
below is a small project on its own:

### Add/edit modals
Instead of an inline input, pop up a modal with title, description,
priority, and due-date fields. Reuse the same modal for both Add and
Edit by tracking an `editingTodoId` global — `null` means add mode.

**Concepts:** controlled modals, `<form>` validation, separating
"creating" from "editing" while sharing the UI.

### Pagination
Add a `<select>` for "items per page". In `render()`, slice
`allTodos.slice(start, end)` instead of rendering everything. Track
`currentPage`. Reset to page 1 whenever filter or sort changes.

**Concepts:** paginating arrays in JS, Prev/Next button enable/disable,
why server-side pagination is better for huge datasets.

### Column visibility
Let users hide columns they don't care about. Store the list of visible
columns as a JSON string in `preferences.db`. Add a "Columns…" button
that opens a modal with checkboxes.

**Concepts:** `JSON.stringify` / `JSON.parse` for storing arrays in
SQLite TEXT columns, scoped query selectors (`#todos-table [data-column]`)
to avoid hiding non-table elements that share `data-column` attributes.

### Click column headers to sort
Add a click handler on `<th class="sortable">`. Same column → flip
direction. Different column → switch to it (start descending).
Visual `↑` / `↓` indicator via CSS pseudo-element.

**Concepts:** delegating to the same dropdown logic, CSS `::after` for
indicators, persisting "active sort column" in preferences.

### Overdue highlighting
A todo with `due_date < today` and `done == 0` should display in red.

**Concepts:** date math in JS (`new Date()`, comparisons), conditional
classes in template strings.

### Logout
Add a button. Make it `DELETE FROM sessions WHERE token = ?`, then
`localStorage.clear()`, then redirect to login.

**Concepts:** server-side invalidation, why "logging out" is more than
just clearing the browser.

---

## Where to go from here

You've now built all four layers, from HTML to SQL. Some natural next
challenges:

- **Tests.** Write a `test_api.py` that uses `urllib.request` to verify
  every endpoint. No frameworks needed — just `assert` statements.
- **A real auth check.** The current app trusts whatever `X-User-Id`
  the client sends. Make the proxy verify the token first, look up the
  user_id from the session, and inject it as a header *itself* — so
  clients can't spoof identity.
- **A frontend framework.** Take this exact backend and write the
  frontend in React, Svelte, or plain web components. You'll see how
  little the backend cares.
- **PostgreSQL.** Swap SQLite for Postgres. The Python code barely
  changes — `sqlite3` becomes `psycopg2`, the connection string changes,
  the SQL is mostly the same. You'll learn what "connection pooling"
  means.
- **Deployment.** Run all four services on a single $5 VPS using
  `systemd` units. Put nginx in front of the proxy. Get a free SSL cert
  with Let's Encrypt. Now your app is on the internet.

---

## Glossary

A few terms that came up; here's the short version:

- **HTML / CSS / JavaScript** — the three languages every browser speaks.
- **DOM** — the browser's in-memory tree of all the elements on the page.
- **`fetch`** — JavaScript's built-in way to make HTTP requests.
- **HTTP** — the protocol every web request uses. Request → response.
- **Method** — `GET`, `POST`, `PUT`, `DELETE`. Tells the server what kind
  of operation you want.
- **Status code** — the number that comes back. `200` good, `404` not
  found, `500` server crashed.
- **JSON** — text format for objects and arrays. Universal between
  languages.
- **CORS** — the browser's rule about which origins can talk to which.
  Servers opt in via headers.
- **CRUD** — Create / Read / Update / Delete. The four basic data
  operations.
- **REST** — convention that maps CRUD to HTTP methods.
- **SQL** — the language databases speak.
- **SQLite** — a database that lives in a single file, no server needed.
- **Session token** — random opaque string the server hands you on login;
  you send it with every subsequent request.
- **Hash** — one-way scramble of input. Same input → same hash; can't
  reverse.
- **Proxy / API gateway** — server that forwards requests to other
  servers based on the URL path.
- **CORS preflight** — the `OPTIONS` request the browser sends before a
  cross-origin call to check if it's allowed.

---

## You did it

If you got this far, you've built the same shape of system that
real production apps run on. The numbers are smaller, but the moving
parts are identical: a frontend, a proxy in front of multiple backends,
a database per concern, sessions, CORS, JSON over HTTP.

The repo this guide lives in (`debug/debug_scenarios.md`) has 13
copy-pasteable bugs you can inject to practice debugging across all
four layers. That's the next thing to do — build it, then break it,
then fix it. That's how you learn debugging.
