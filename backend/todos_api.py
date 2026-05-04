#!/usr/bin/env python3
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'todos.db')

class TodosAPIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_user_id_from_headers(self):
        return self.headers.get('X-User-Id')

    def do_GET(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')
        query_params = parse_qs(parsed.query)

        if len(path_parts) >= 3 and path_parts[2] == 'todos':
            if len(path_parts) == 3:
                self.handle_get_todos(query_params)
            elif len(path_parts) == 4:
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
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        base_query = 'SELECT * FROM todos WHERE user_id = ?'
        params = [user_id]

        status_filter = query_params.get('status', ['all'])[0]
        if status_filter == 'active':
            base_query += ' AND is_completed = 0'
        elif status_filter == 'completed':
            base_query += ' AND is_completed = 1'
        elif status_filter == 'overdue':
            base_query += " AND due_date < datetime('now') AND is_completed = 0"

        sort_by = query_params.get('sort_by', ['created_at'])[0]
        sort_order = query_params.get('sort_order', ['desc'])[0]
        valid_sort_fields = ['created_at', 'title', 'priority', 'due_date']
        if sort_by in valid_sort_fields:
            if sort_by == 'priority':
                base_query += f" ORDER BY CASE t.priority WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 END {sort_order.upper()}"
            elif sort_by == 'title':
                base_query += f' ORDER BY t.title COLLATE NOCASE {sort_order.upper()}'
            else:
                base_query += f' ORDER BY t.{sort_by} {sort_order.upper()}'

        cursor.execute(base_query, params)
        todos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response(todos)

    def handle_get_todo(self, todo_id):
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM todos WHERE id = ? AND user_id = ?', (todo_id, user_id))
        todo = cursor.fetchone()
        conn.close()

        if not todo:
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

        self.send_json_response(dict(todo))

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

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

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
            data.get('description', ''),
            data.get('due_date'),
            data.get('priority', 'medium')
        ))

        todo_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self.send_json_response({'id': todo_id, 'message': 'Todo created successfully'}, 201)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 4 and path_parts[2] == 'todos':
            todo_id = path_parts[3]
            if len(path_parts) >= 5:
                action = path_parts[4]
                if action == 'complete':
                    self.handle_toggle_complete(todo_id)
                else:
                    self.send_json_response({'error': 'Invalid action'}, 400)
            else:
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

        cursor.execute('SELECT id FROM todos WHERE id = ? AND user_id = ?', (todo_id, user_id))
        if not cursor.fetchone():
            conn.close()
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

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

        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        params.extend([todo_id, user_id])

        cursor.execute(f'''
            UPDATE todos SET {', '.join(update_fields)}
            WHERE id = ? AND user_id = ?
        ''', params)

        conn.commit()
        conn.close()

        self.send_json_response({'message': 'Todo updated successfully'})

    def handle_toggle_complete(self, todo_id):
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

        if cursor.rowcount == 0:
            conn.close()
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

        conn.commit()
        conn.close()
        self.send_json_response({'message': 'Completion toggled successfully'})

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

        cursor.execute('DELETE FROM todos WHERE id = ? AND user_id = ?', (todo_id, user_id))

        if cursor.rowcount == 0:
            conn.close()
            self.send_json_response({'error': 'Todo not found'}, 404)
            return

        conn.commit()
        conn.close()
        self.send_json_response({'message': 'Todo deleted successfully'})

def run_server(port=8081):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TodosAPIHandler)
    print(f'Todos API running on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()