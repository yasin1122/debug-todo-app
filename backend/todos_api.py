#!/usr/bin/env python3
# This is the Todos API — it runs on port 8081 and handles all CRUD operations
# for todo items. CRUD = Create, Read, Update, Delete.
#
# "Internal only" means the browser never calls this directly. All requests
# come through the proxy (port 8080), which adds the user's ID and forwards them.

import sqlite3                              # Read/write the todos database
import json                                 # Convert Python dicts to/from JSON text
from http.server import HTTPServer, BaseHTTPRequestHandler  # Python's built-in web server
from urllib.parse import urlparse, parse_qs # Split URLs and decode query strings

import os
# Build an absolute path to todos.db so the script works regardless of which
# directory you launch it from.
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'todos.db')


class TodosAPIHandler(BaseHTTPRequestHandler):
    # This class defines how to respond to each type of HTTP request.
    # Python's BaseHTTPRequestHandler automatically calls do_GET when a GET
    # arrives, do_POST for POST, and so on.

    def do_OPTIONS(self):
        # Browsers send a preflight OPTIONS request before cross-origin calls.
        # We respond with 200 OK plus CORS headers to say "yes, proceed".
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        # CORS headers allow the browser (on port 8000) to call this API
        # (on port 8081) without the browser blocking the request.
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def send_json_response(self, data, status=200):
        # Reusable helper — every response from this API is JSON, so we
        # centralise the repetitive boilerplate here.
        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_user_id_from_headers(self):
        # The proxy injects the logged-in user's ID as the X-User-Id header.
        # Every database operation is scoped to this ID so users only see
        # their own todos — never anyone else's.
        return self.headers.get('X-User-Id')

    # -------------------------------------------------------------------------
    # GET  /api/todos        → list all todos (with optional filter/sort)
    # GET  /api/todos/<id>   → get one specific todo
    # -------------------------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)          # Break the URL into parts
        path_parts = parsed.path.split('/')   # e.g. "/api/todos/5" → ['', 'api', 'todos', '5']
        query_params = parse_qs(parsed.query) # e.g. "?status=active" → {'status': ['active']}

        if len(path_parts) >= 3 and path_parts[2] == 'todos':
            if len(path_parts) == 3:
                # /api/todos — list all todos
                self.handle_get_todos(query_params)
            elif len(path_parts) == 4:
                # /api/todos/5 — get one todo by ID
                todo_id = path_parts[3]
                self.handle_get_todo(todo_id)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def handle_get_todos(self, query_params):
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        # row_factory makes each database row behave like a dict, so we can
        # access columns by name (row['title']) instead of index (row[2]).
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Start with a base query that only fetches THIS user's todos.
        # The ? is a placeholder — sqlite3 fills it in safely to prevent
        # SQL injection attacks (never build queries with string formatting and
        # untrusted input).
        base_query = 'SELECT * FROM todos WHERE user_id = ?'
        params = [user_id]

        # Apply the status filter if one was requested.
        status_filter = query_params.get('status', ['all'])[0]
        if status_filter == 'active':
            base_query += ' AND is_completed = 0'
        elif status_filter == 'completed':
            base_query += ' AND is_completed = 1'
        elif status_filter == 'overdue':
            # datetime('now') is a SQLite function that returns the current UTC time.
            base_query += " AND due_date < datetime('now') AND is_completed = 0"

        # Apply sorting. We whitelist valid column names to prevent SQL injection.
        sort_by = query_params.get('sort_by', ['created_at'])[0]
        sort_order = query_params.get('sort_order', ['desc'])[0]
        valid_sort_fields = ['created_at', 'title', 'priority', 'due_date']

        if sort_by in valid_sort_fields:
            if sort_by == 'priority':
                # Priority is text ('low', 'medium', 'high'), but alphabetical
                # order would give us high < low < medium. Instead we use a CASE
                # expression to map each value to a number first, then sort by
                # that number to get the correct semantic order.
                base_query += f" ORDER BY CASE priority WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 END {sort_order.upper()}"
            elif sort_by == 'title':
                # COLLATE NOCASE makes the sort case-insensitive so 'Apple' and
                # 'apple' are treated as equal when ordering.
                base_query += f' ORDER BY title COLLATE NOCASE {sort_order.upper()}'
            else:
                base_query += f' ORDER BY {sort_by} {sort_order.upper()}'

        cursor.execute(base_query, params)
        # Convert each Row object to a plain dict so json.dumps() can serialise it.
        todos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response(todos)

    def handle_get_todo(self, todo_id):
        # Fetch a single todo by ID, but only if it belongs to the requesting user.
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM todos WHERE id = ? AND user_id = ?', (todo_id, user_id))
        todo = cursor.fetchone()  # Returns one row or None
        conn.close()

        if not todo:
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

        self.send_json_response(dict(todo))

    # -------------------------------------------------------------------------
    # POST /api/todos  →  create a new todo
    # -------------------------------------------------------------------------
    def do_POST(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 3 and path_parts[2] == 'todos':
            self.handle_create_todo()
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def handle_create_todo(self):
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        # Read the request body. Content-Length tells us how many bytes to read.
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())  # Parse the JSON text into a Python dict

        title = data.get('title')
        if not title:
            self.send_json_response({'error': 'Title is required'}, 400)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO todos (user_id, title, description, due_date, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            title,
            data.get('description', ''),      # Default to empty string if not provided
            data.get('due_date'),              # None if not provided (stored as NULL)
            data.get('priority', 'medium')    # Default priority is medium
        ))

        # lastrowid gives us the auto-generated ID of the row we just inserted.
        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # 201 Created is the conventional status code for a successful resource creation.
        self.send_json_response({'id': todo_id, 'message': 'Todo created successfully'}, 201)

    # -------------------------------------------------------------------------
    # PUT /api/todos/<id>          →  update a todo's fields
    # PUT /api/todos/<id>/complete →  toggle completed on/off
    # -------------------------------------------------------------------------
    def do_PUT(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 4 and path_parts[2] == 'todos':
            todo_id = path_parts[3]
            if len(path_parts) >= 5:
                # There's a 5th segment — check what action it is
                action = path_parts[4]
                if action == 'complete':
                    self.handle_toggle_complete(todo_id)
                else:
                    self.send_json_response({'error': 'Invalid action'}, 400)
            else:
                # No extra segment — plain update
                self.handle_update_todo(todo_id)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def handle_update_todo(self, todo_id):
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # First confirm the todo exists and belongs to this user.
        cursor.execute('SELECT id FROM todos WHERE id = ? AND user_id = ?', (todo_id, user_id))
        if not cursor.fetchone():
            conn.close()
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

        # Build the UPDATE statement dynamically — only update fields that were
        # actually sent in the request body. This way a partial update
        # (e.g. only changing the title) doesn't accidentally wipe other fields.
        update_fields = []
        params = []

        if 'title' in data:
            update_fields.append('title = ?')
            params.append(data['title'])
        if 'description' in data:
            update_fields.append('description = ?')
            params.append(data['description'])
        if 'due_date' in data:
            update_fields.append('due_date = ?')
            params.append(data['due_date'])
        if 'priority' in data:
            update_fields.append('priority = ?')
            params.append(data['priority'])
        if 'is_completed' in data:
            update_fields.append('is_completed = ?')
            params.append(data['is_completed'])

        # Always bump updated_at so we know when the last edit happened.
        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        params.extend([todo_id, user_id])  # Add the WHERE clause values at the end

        cursor.execute(f'''
            UPDATE todos SET {', '.join(update_fields)}
            WHERE id = ? AND user_id = ?
        ''', params)

        conn.commit()
        conn.close()

        self.send_json_response({'message': 'Todo updated successfully'})

    def handle_toggle_complete(self, todo_id):
        # Flip the is_completed flag between 0 and 1.
        # "NOT is_completed" in SQLite: 0 → 1, 1 → 0.
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE todos SET is_completed = NOT is_completed, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND user_id = ?
        ''', (todo_id, user_id))

        # rowcount tells us how many rows were actually changed.
        # If it's 0, no matching row was found (wrong ID or wrong user).
        if cursor.rowcount == 0:
            conn.close()
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

        conn.commit()
        conn.close()
        self.send_json_response({'message': 'Completion toggled successfully'})

    # -------------------------------------------------------------------------
    # DELETE /api/todos/<id>  →  permanently remove a todo
    # -------------------------------------------------------------------------
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 4 and path_parts[2] == 'todos':
            todo_id = path_parts[3]
            self.handle_delete_todo(todo_id)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def handle_delete_todo(self, todo_id):
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # The AND user_id = ? clause is critical — it ensures a user can only
        # delete their own todos, not anyone else's.
        cursor.execute('DELETE FROM todos WHERE id = ? AND user_id = ?', (todo_id, user_id))

        if cursor.rowcount == 0:
            conn.close()
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

        conn.commit()
        conn.close()
        self.send_json_response({'message': 'Todo deleted successfully'})


def run_server(port=8081):
    # '' as the host means "listen on all available network interfaces".
    server_address = ('', port)
    httpd = HTTPServer(server_address, TodosAPIHandler)
    print(f'Todos API running on port {port}...')
    httpd.serve_forever()  # Block here, handling requests indefinitely


if __name__ == '__main__':
    run_server()
