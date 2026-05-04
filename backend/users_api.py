#!/usr/bin/env python3
import sqlite3
import json
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta

import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'users.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_urlsafe(32)

class UsersAPIHandler(BaseHTTPRequestHandler):
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

    def do_POST(self):
        path_parts = urlparse(self.path).path.split('/')

        if len(path_parts) >= 4 and path_parts[3] == 'login':
            self.handle_login()
        elif len(path_parts) >= 4 and path_parts[3] == 'logout':
            self.handle_logout()
        elif len(path_parts) >= 4 and path_parts[3] == 'verify':
            self.handle_verify()
        else:
            self.send_json_response({'error': 'Not found'}, 404)

    def handle_login(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            self.send_json_response({'error': 'Username and password required'}, 400)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if not user or user[1] != hash_password(password):
            conn.close()
            self.send_json_response({'error': 'Invalid credentials'}, 401)
            return

        user_id = user[0]
        token = generate_token()
        expires_at = datetime.now() + timedelta(hours=24)

        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        cursor.execute(
            'INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)',
            (token, user_id, expires_at.isoformat())
        )
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))

        conn.commit()
        conn.close()

        self.send_json_response({
            'token': token,
            'user_id': user_id,
            'username': username,
            'expires_at': expires_at.isoformat()
        })

    def handle_logout(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        token = data.get('token')
        if not token:
            self.send_json_response({'error': 'Token required'}, 400)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
        conn.commit()
        conn.close()

        self.send_json_response({'message': 'Logged out successfully'})

    def handle_verify(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        token = data.get('token')
        if not token:
            self.send_json_response({'error': 'Token required'}, 400)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.user_id, u.username, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > datetime('now')
        ''', (token,))

        session = cursor.fetchone()
        conn.close()

        if not session:
            self.send_json_response({'valid': False}, 401)
            return

        self.send_json_response({
            'valid': True,
            'user_id': session[0],
            'username': session[1],
            'expires_at': session[2]
        })

def run_server(port=8082):
    server_address = ('', port)
    httpd = HTTPServer(server_address, UsersAPIHandler)
    print(f'Users API running on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()