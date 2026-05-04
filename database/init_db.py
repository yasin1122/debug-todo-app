#!/usr/bin/env python3
# This script creates all three databases from scratch.
# Run it once before starting the app for the first time.
# It will DELETE existing databases and recreate them, so only run it when you
# want a fresh start (start.sh protects you from running it by accident).

import sqlite3  # Python's built-in library for working with SQLite databases
import hashlib  # Used to hash (scramble) passwords before storing them
import os       # Used to check whether a file already exists


def hash_password(password):
    # Never store plain-text passwords in a database.
    # SHA-256 converts the password into a fixed-length scrambled string.
    # The same password always produces the same hash, so we can compare them
    # later without ever storing the original.
    return hashlib.sha256(password.encode()).hexdigest()


def init_todos_db():
    # Creates todos.db — stores every todo item for every user.
    db_path = 'todos.db'

    # If a database file already exists, delete it so we start clean.
    if os.path.exists(db_path):
        os.remove(db_path)

    # sqlite3.connect() opens the file (or creates it if it doesn't exist).
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()  # A cursor is like a pen — you use it to write/read data.

    # CREATE TABLE defines the shape of our data, like a spreadsheet template.
    # Each line inside is a "column" with a name and data type.
    cursor.execute('''
        CREATE TABLE todos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT, -- unique ID, auto-assigned
            user_id     INTEGER NOT NULL,                  -- which user owns this todo
            title       TEXT NOT NULL,                     -- the todo's title (required)
            description TEXT,                              -- optional longer description
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- set automatically on insert
            updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- updated whenever we edit
            due_date    TIMESTAMP,                         -- optional deadline
            is_completed BOOLEAN DEFAULT 0,               -- 0 = not done, 1 = done
            priority    TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high'))
        )
    ''')

    # Indexes make lookups faster. Without an index, the database has to scan every
    # row to find matches. With one, it jumps straight to the relevant rows.
    cursor.execute('CREATE INDEX idx_todos_user_id ON todos(user_id)')
    cursor.execute('CREATE INDEX idx_todos_completed ON todos(is_completed)')

    conn.commit()  # Save all changes to disk (like pressing Save in a text editor).
    conn.close()   # Release the file so other processes can use it.
    print(f"✓ Created {db_path}")


def init_users_db():
    # Creates users.db — stores user accounts and login sessions.
    db_path = 'users.db'

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # The users table holds one row per registered account.
    cursor.execute('''
        CREATE TABLE users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,  -- UNIQUE means no two users can share a name
            password_hash TEXT NOT NULL,         -- the scrambled password (never the real one)
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login    TIMESTAMP              -- updated every time the user logs in
        )
    ''')

    # The sessions table tracks who is currently logged in.
    # When you log in, a random token is created and stored here.
    # When you make a request, we look up the token to know who you are.
    cursor.execute('''
        CREATE TABLE sessions (
            token      TEXT PRIMARY KEY,         -- the random string sent to the browser
            user_id    INTEGER NOT NULL,          -- which user this session belongs to
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,        -- sessions auto-expire after 24 hours
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            -- "ON DELETE CASCADE" means if a user is deleted, their sessions go too
        )
    ''')

    cursor.execute('CREATE INDEX idx_sessions_user_id ON sessions(user_id)')
    cursor.execute('CREATE INDEX idx_sessions_expires ON sessions(expires_at)')

    # Insert the three demo user accounts with their passwords already hashed.
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
    # Creates preferences.db — stores each user's UI settings (theme, sort order, etc.)
    # This is kept in a separate database so the proxy can handle it directly
    # without needing to talk to the todos or users backends.
    db_path = 'preferences.db'

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # user_preferences stores one row per user with their chosen UI settings.
    # CHECK(...) constraints make sure only valid values can be saved.
    cursor.execute('''
        CREATE TABLE user_preferences (
            user_id       INTEGER PRIMARY KEY,
            theme         TEXT DEFAULT 'light' CHECK(theme IN ('light', 'dark')),
            sort_by       TEXT DEFAULT 'created_at' CHECK(sort_by IN ('created_at', 'title', 'priority', 'due_date', 'completed')),
            sort_order    TEXT DEFAULT 'desc' CHECK(sort_order IN ('asc', 'desc')),
            filter_status TEXT DEFAULT 'all' CHECK(filter_status IN ('all', 'active', 'completed', 'overdue')),
            show_completed BOOLEAN DEFAULT 1,
            items_per_page INTEGER DEFAULT 10 CHECK(items_per_page IN (5, 10, 20))
        )
    ''')

    # table_settings stores which table columns the user has chosen to show or hide.
    # visible_columns is stored as JSON text, e.g. '["title","priority","due_date"]'
    cursor.execute('''
        CREATE TABLE table_settings (
            user_id         INTEGER PRIMARY KEY,
            visible_columns TEXT DEFAULT '["title","priority","due_date","completed","actions"]',
            column_widths   TEXT DEFAULT '{}',
            last_filter     TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✓ Created {db_path}")


if __name__ == '__main__':
    # "__main__" means: only run this block when you execute this file directly,
    # not when another file imports it.
    print("Initializing databases...")
    init_todos_db()
    init_users_db()
    init_preferences_db()
    print("\nAll databases initialized successfully!")
