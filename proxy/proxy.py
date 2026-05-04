#!/usr/bin/env python3
import sqlite3
import json
import http.client
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

import os
PREFERENCES_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'preferences.db')
TODOS_API = 'localhost:8081'
USERS_API = 'localhost:8082'

class ProxyHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-Id')

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_user_id_from_headers(self):
        return self.headers.get('X-User-Id')

    def proxy_request(self, target_host, method, path, headers=None, body=None):
        conn = http.client.HTTPConnection(target_host)

        proxy_headers = {}
        if headers:
            for key, value in headers.items():
                if key.lower() not in ['host', 'connection']:
                    proxy_headers[key] = value

        try:
            conn.request(method, path, body, proxy_headers)
            response = conn.getresponse()
            response_data = response.read()
            conn.close()
            return response.status, response_data.decode()
        except Exception as e:
            conn.close()
            return 500, json.dumps({'error': str(e)})

    def do_GET(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 2 and path_parts[1] == 'preferences':
            self.handle_get_preferences()
        elif len(path_parts) >= 3 and path_parts[1] == 'api':
            if path_parts[2] == 'todos':
                self.proxy_to_todos('GET')
            else:
                self.send_json_response({'error': 'Not found'}, 404)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 2 and path_parts[1] == 'preferences':
            self.handle_update_preferences()
        elif len(path_parts) >= 3 and path_parts[1] == 'api':
            if path_parts[2] == 'todos':
                self.proxy_to_todos('POST')
            elif path_parts[2] == 'auth':
                self.proxy_to_users('POST')
            else:
                self.send_json_response({'error': 'Not found'}, 404)
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 2 and path_parts[1] == 'preferences':
            self.handle_update_preferences()
        elif len(path_parts) >= 3 and path_parts[1] == 'api' and path_parts[2] == 'todos':
            self.proxy_to_todos('PUT')
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path_parts = parsed.path.split('/')

        if len(path_parts) >= 3 and path_parts[1] == 'api' and path_parts[2] == 'todos':
            self.proxy_to_todos('DELETE')
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def handle_get_preferences(self):
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        conn = sqlite3.connect(PREFERENCES_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        prefs = cursor.fetchone()

        cursor.execute('SELECT * FROM table_settings WHERE user_id = ?', (user_id,))
        settings = cursor.fetchone()

        conn.close()

        response = {
            'preferences': dict(prefs) if prefs else self.get_default_preferences(),
            'table_settings': dict(settings) if settings else self.get_default_table_settings()
        }

        self.send_json_response(response)

    def handle_update_preferences(self):
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        conn = sqlite3.connect(PREFERENCES_DB)
        cursor = conn.cursor()

        if 'preferences' in data:
            prefs = data['preferences']
            cursor.execute('SELECT user_id FROM user_preferences WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()

            if exists:
                update_fields = []
                params = []
                for field in ['theme', 'sort_by', 'sort_order', 'filter_status', 'show_completed', 'items_per_page']:
                    if field in prefs:
                        update_fields.append(f'{field} = ?')
                        params.append(prefs[field])

                if update_fields:
                    params.append(user_id)
                    cursor.execute(f'''
                        UPDATE user_preferences SET {', '.join(update_fields)}
                        WHERE user_id = ?
                    ''', params)
            else:
                cursor.execute('''
                    INSERT INTO user_preferences (user_id, theme, sort_by, sort_order, filter_status, show_completed, items_per_page)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    prefs.get('theme', 'light'),
                    prefs.get('sort_by', 'created_at'),
                    prefs.get('sort_order', 'desc'),
                    prefs.get('filter_status', 'all'),
                    prefs.get('show_completed', True),
                    prefs.get('items_per_page', 10)
                ))

        if 'table_settings' in data:
            settings = data['table_settings']
            cursor.execute('SELECT user_id FROM table_settings WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()

            if exists:
                update_fields = []
                params = []
                for field in ['visible_columns', 'column_widths', 'last_filter']:
                    if field in settings:
                        update_fields.append(f'{field} = ?')
                        value = json.dumps(settings[field]) if isinstance(settings[field], (list, dict)) else settings[field]
                        params.append(value)

                if update_fields:
                    params.append(user_id)
                    cursor.execute(f'''
                        UPDATE table_settings SET {', '.join(update_fields)}
                        WHERE user_id = ?
                    ''', params)
            else:
                cursor.execute('''
                    INSERT INTO table_settings (user_id, visible_columns, column_widths, last_filter)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    json.dumps(settings.get('visible_columns', ["title","priority","due_date","completed","actions"])),
                    json.dumps(settings.get('column_widths', {})),
                    settings.get('last_filter')
                ))

        conn.commit()
        conn.close()

        self.send_json_response({'message': 'Preferences updated successfully'})

    def get_default_preferences(self):
        return {
            'theme': 'light',
            'sort_by': 'created_at',
            'sort_order': 'desc',
            'filter_status': 'all',
            'show_completed': True,
            'items_per_page': 10
        }

    def get_default_table_settings(self):
        return {
            'visible_columns': ["title", "priority", "due_date", "completed", "actions"],
            'column_widths': {},
            'last_filter': None
        }

    def proxy_to_todos(self, method):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        path = self.path
        headers = dict(self.headers.items())
        status, response = self.proxy_request(TODOS_API, method, path, headers, body)

        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

    def proxy_to_users(self, method):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        path = self.path
        headers = dict(self.headers.items())
        status, response = self.proxy_request(USERS_API, method, path, headers, body)

        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f'Proxy server running on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()