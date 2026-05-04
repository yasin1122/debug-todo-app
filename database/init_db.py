#!/usr/bin/env python3
import sqlite3
import hashlib
import os
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_todos_db():
    db_path = 'todos.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP,
            is_completed BOOLEAN DEFAULT 0,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high'))
        )
    ''')

    cursor.execute('CREATE INDEX idx_todos_user_id ON todos(user_id)')
    cursor.execute('CREATE INDEX idx_todos_completed ON todos(is_completed)')

    conn.commit()
    conn.close()
    print(f"✓ Created {db_path}")

def init_users_db():
    db_path = 'users.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('CREATE INDEX idx_sessions_user_id ON sessions(user_id)')
    cursor.execute('CREATE INDEX idx_sessions_expires ON sessions(expires_at)')

    cursor.execute('''
        INSERT INTO users (username, password_hash) VALUES
        ('demo', ?),
        ('alice', ?),
        ('bob', ?)
    ''', (
        hash_password('demo123'),
        hash_password('alice123'),
        hash_password('bob123')
    ))

    conn.commit()
    conn.close()
    print(f"✓ Created {db_path} with demo users (demo/demo123, alice/alice123, bob/bob123)")

def init_preferences_db():
    db_path = 'preferences.db'
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE user_preferences (
            user_id INTEGER PRIMARY KEY,
            theme TEXT DEFAULT 'light' CHECK(theme IN ('light', 'dark')),
            sort_by TEXT DEFAULT 'created_at' CHECK(sort_by IN ('created_at', 'title', 'priority', 'due_date')),
            sort_order TEXT DEFAULT 'desc' CHECK(sort_order IN ('asc', 'desc')),
            filter_status TEXT DEFAULT 'all' CHECK(filter_status IN ('all', 'active', 'completed', 'overdue')),
            show_completed BOOLEAN DEFAULT 1,
            items_per_page INTEGER DEFAULT 10 CHECK(items_per_page IN (5, 10, 20))
        )
    ''')

    cursor.execute('''
        CREATE TABLE table_settings (
            user_id INTEGER PRIMARY KEY,
            visible_columns TEXT DEFAULT '["title","priority","due_date","tags","completed","actions"]',
            column_widths TEXT DEFAULT '{}',
            last_filter TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✓ Created {db_path}")

if __name__ == '__main__':
    print("Initializing databases...")
    init_todos_db()
    init_users_db()
    init_preferences_db()
    print("\nAll databases initialized successfully!")