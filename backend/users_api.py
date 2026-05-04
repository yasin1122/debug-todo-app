#!/usr/bin/env python3
# This is the Users API — it runs on port 8082 and handles everything
# related to accounts: logging in, logging out, and checking whether a
# session token is still valid.
#
# The browser never talks to this service directly. All requests come
# through the proxy (port 8080), which forwards them here.

import os                                   # Build absolute file paths
import sqlite3                              # Read/write the users database
import json                                 # Convert Python dicts to/from JSON text
import hashlib                              # Hash passwords before comparing them
import secrets                              # Generate secure random tokens
from http.server import HTTPServer, BaseHTTPRequestHandler  # Python's built-in web server
from urllib.parse import urlparse           # Split a URL into its parts (path, query, etc.)
from datetime import datetime, timedelta    # Work with dates and time math

# Build the path to users.db relative to this file's location, so the
# script works no matter which directory you run it from.
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'users.db')


def hash_password(password):
    # Convert a plain-text password into a SHA-256 hash.
    # Example: "mypassword" → "89e495e7941cf9e40e6980d14a16bf023ccd4c91"
    # We store the hash, never the original. When the user logs in we hash
    # what they typed and compare it to the stored hash.
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token():
    # Create a cryptographically random string to use as a session token.
    # "urlsafe" means it only uses characters safe to put in a URL.
    # 32 bytes of randomness = effectively impossible to guess.
    return secrets.token_urlsafe(32)


class UsersAPIHandler(BaseHTTPRequestHandler):
    # This class handles every HTTP request that arrives on port 8082.
    # Python calls the appropriate do_GET / do_POST / etc. method
    # automatically based on the request's HTTP method.

    def do_OPTIONS(self):
        # Browsers send an OPTIONS "preflight" request before a cross-origin
        # request to ask: "is this allowed?" We just say yes.
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        # CORS (Cross-Origin Resource Sharing) headers tell the browser it's
        # okay for JavaScript on one origin (e.g. port 8000) to call this
        # server on a different origin (port 8082).
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def send_json_response(self, data, status=200):
        # A helper that sends a properly formatted JSON response every time.
        # 1. Set the HTTP status code (200 = OK, 401 = Unauthorized, etc.)
        # 2. Add CORS headers so the browser accepts the response
        # 3. Tell the browser the body is JSON
        # 4. Write the actual JSON data
        self.send_response(status)
        self.send_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_POST(self):
        # All auth actions use POST. We inspect the URL path to decide what to do.
        # /api/auth/login  → log the user in
        # /api/auth/logout → invalidate the session
        # /api/auth/verify → check if a token is still valid
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
        # Step 1: Read the JSON body the browser sent (username + password).
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            self.send_json_response({'error': 'Username and password required'}, 400)
            return

        # Step 2: Look up the user in the database.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()  # Returns one row, or None if the username doesn't exist.

        # Step 3: Check the password. We hash what they typed and compare it to
        # the stored hash. If either the username or password is wrong, respond
        # with the same vague error — never tell the attacker which one was wrong.
        if not user or user[1] != hash_password(password):
            conn.close()
            self.send_json_response({'error': 'Invalid credentials'}, 401)
            return

        # Step 4: Create a new session token for this user.
        user_id = user[0]
        token = generate_token()
        expires_at = datetime.now() + timedelta(hours=24)  # Token is valid for 24 hours.

        # Delete any existing session for this user (only one active session at a time).
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
        # Insert the new session into the database.
        cursor.execute(
            'INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)',
            (token, user_id, expires_at.isoformat())
        )
        # Record when this user last logged in.
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))

        conn.commit()
        conn.close()

        # Step 5: Send the token back to the browser. The browser saves it in
        # localStorage and includes it with every future request.
        self.send_json_response({
            'token': token,
            'user_id': user_id,
            'username': username,
            'expires_at': expires_at.isoformat()
        })

    def handle_logout(self):
        # Read the token from the request body.
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        token = data.get('token')
        if not token:
            self.send_json_response({'error': 'Token required'}, 400)
            return

        # Delete the session row from the database. After this, the token is
        # useless — any request using it will fail verification.
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
        conn.commit()
        conn.close()

        self.send_json_response({'message': 'Logged out successfully'})

    def handle_verify(self):
        # The browser calls this on every page load to confirm the stored token
        # is still valid (not expired, not deleted by logout).
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        data = json.loads(body.decode())

        token = data.get('token')
        if not token:
            self.send_json_response({'error': 'Token required'}, 400)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Join the sessions table with the users table to get the username too.
        # The WHERE clause checks both that the token exists AND that it hasn't
        # expired (expires_at > datetime('now') = expiry is in the future).
        cursor.execute('''
            SELECT s.user_id, u.username, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > datetime('now')
        ''', (token,))

        session = cursor.fetchone()
        conn.close()

        if not session:
            # Token not found or expired — send back 401 (Unauthorized).
            self.send_json_response({'valid': False}, 401)
            return

        self.send_json_response({
            'valid': True,
            'user_id': session[0],
            'username': session[1],
            'expires_at': session[2]
        })


def run_server(port=8082):
    # Start the HTTP server and keep it running forever, waiting for requests.
    server_address = ('', port)  # '' means listen on all network interfaces
    httpd = HTTPServer(server_address, UsersAPIHandler)
    print(f'Users API running on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
