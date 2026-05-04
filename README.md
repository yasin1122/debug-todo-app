# Debug Todo App

A full-stack todo application built specifically for practicing debugging across all layers of a web application. Zero dependencies - uses only Python standard library and vanilla JavaScript.

## 🚀 Quick Start

```bash
./start.sh
```

Then open: http://localhost:8000

## 🔑 Demo Accounts

| Username | Password  |
|----------|-----------|
| demo     | demo123   |
| alice    | alice123  |
| bob      | bob123    |

## 🏗️ Architecture

### 4-Layer Stack:
1. **Frontend** (Port 8000)
   - Pure HTML/CSS/JavaScript
   - No frameworks or libraries

2. **Proxy Layer** (Port 8080)
   - Routes requests to backend services
   - Manages user preferences (theme, sorting, filters)
   - Handles CORS

3. **Backend APIs**
   - **Users API** (Port 8082) - Authentication & sessions
   - **Todos API** (Port 8081) - Todo CRUD operations

4. **Databases** (SQLite)
   - `todos.db` - Todo items and tags
   - `users.db` - User accounts and sessions
   - `preferences.db` - User preferences and table settings

## ✨ Features

- **Authentication**: Login/logout with session tokens
- **Todo Management**: Create, read, update, delete todos
- **Starring**: Mark important todos
- **Priority Levels**: Low, Medium, High
- **Due Dates**: With overdue highlighting
- **Tags**: Categorize todos
- **Dark/Light Theme**: Persisted preference
- **Sorting**: By date, title, priority, starred
- **Filtering**: All, active, completed, starred, overdue
- **Pagination**: 5, 10, or 20 items per page
- **Column Settings**: Show/hide table columns

## 🐛 Debugging Practice

Check `debug/debug_scenarios.md` for 20+ debugging scenarios you can enable:

- Database performance issues
- API failures and errors
- Authentication problems
- Race conditions
- CORS issues
- Security vulnerabilities
- Memory leaks
- State synchronization bugs

## 📁 Project Structure

```
debug-todo-app/
├── frontend/          # HTML/CSS/JS files
├── proxy/            # Proxy server with preferences
├── backend/          # API servers
├── database/         # SQLite databases and init script
├── debug/            # Debug scenarios documentation
├── start.sh          # Startup script
└── README.md         # This file
```

## 🛠️ Manual Service Start

If you prefer to start services individually:

```bash
# Initialize databases
cd database && python3 init_db.py

# Start each service in separate terminals:
cd backend && python3 users_api.py      # Port 8082
cd backend && python3 todos_api.py      # Port 8081
cd proxy && python3 proxy.py            # Port 8080
cd frontend && python3 -m http.server 8000
```

## 🎯 Learning Objectives

This app helps you practice debugging:
- Frontend → Backend communication
- Authentication and session management
- Database queries and performance
- State synchronization
- Error handling
- Security vulnerabilities
- Performance optimization

## 🔍 Debugging Tips

1. **Browser DevTools**: Network tab, Console, Application storage
2. **Python debugging**: Add print statements or use `pdb`
3. **Database inspection**: `sqlite3 database/todos.db`
4. **Network monitoring**: `curl` commands to test APIs
5. **Process monitoring**: `ps aux | grep python`

## 📝 Notes

- This app intentionally uses NO external dependencies
- All features work correctly by default
- Debug scenarios must be manually enabled
- Perfect for learning debugging without framework complexity