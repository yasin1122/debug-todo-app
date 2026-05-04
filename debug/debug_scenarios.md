# Debug Scenarios for Todo App

This document contains various debugging scenarios you can enable to practice debugging across all layers of the application.

## How to Enable Debug Scenarios

Each backend file (users_api.py, todos_api.py, proxy.py) contains commented debug flags at the top. To enable a scenario, uncomment the relevant flag and set it to `True`.

## 1. Database Layer Debugging

### Slow Query Simulation
**File:** `backend/todos_api.py`
```python
# Add at top of file:
DEBUG_SLOW_DB = True  # Simulates slow database queries

# In handle_get_todos():
if DEBUG_SLOW_DB:
    import time
    time.sleep(3)  # 3 second delay
```
**What to debug:** Performance issues, loading states, user experience during slow responses

### Missing Index Simulation
**File:** `backend/todos_api.py`
```python
# In handle_get_todos(), comment out the index usage:
# cursor.execute('CREATE INDEX idx_todos_user_id ON todos(user_id)')
```
**What to debug:** Slow queries on large datasets, query optimization

### Connection Pool Exhaustion
**File:** `backend/todos_api.py`
```python
DEBUG_LEAK_CONNECTIONS = True

# Don't close connections:
if not DEBUG_LEAK_CONNECTIONS:
    conn.close()
```
**What to debug:** Connection leaks, "database locked" errors

## 2. Backend API Debugging

### Random 500 Errors
**File:** `backend/todos_api.py`
```python
DEBUG_RANDOM_FAIL = True

# In any handler:
if DEBUG_RANDOM_FAIL:
    import random
    if random.random() < 0.3:  # 30% chance
        self.send_json_response({'error': 'Random server error'}, 500)
        return
```
**What to debug:** Error handling, retry logic, user feedback

### Authentication Token Expiry
**File:** `backend/users_api.py`
```python
DEBUG_FAST_EXPIRE = True

# In handle_login():
if DEBUG_FAST_EXPIRE:
    expires_at = datetime.now() + timedelta(minutes=1)  # 1 minute instead of 24 hours
```
**What to debug:** Session management, auto-refresh tokens, logout flows

### Input Validation Missing
**File:** `backend/todos_api.py`
```python
DEBUG_SKIP_VALIDATION = True

# In handle_create_todo():
if not DEBUG_SKIP_VALIDATION:
    if not title:
        self.send_json_response({'error': 'Title is required'}, 400)
        return
```
**What to debug:** SQL injection, XSS attacks, data integrity

## 3. Proxy Layer Debugging

### CORS Issues
**File:** `proxy/proxy.py`
```python
DEBUG_CORS_ISSUES = True

# In send_cors_headers():
if not DEBUG_CORS_ISSUES:
    self.send_header('Access-Control-Allow-Origin', '*')
```
**What to debug:** Cross-origin request failures, preflight requests

### Request Header Stripping
**File:** `proxy/proxy.py`
```python
DEBUG_STRIP_HEADERS = True

# In proxy_request():
if DEBUG_STRIP_HEADERS:
    # Remove user ID header randomly
    if 'X-User-Id' in proxy_headers and random.random() < 0.3:
        del proxy_headers['X-User-Id']
```
**What to debug:** Authentication failures, missing context

### Preference Race Conditions
**File:** `proxy/proxy.py`
```python
DEBUG_PREF_DELAY = True

# In handle_get_preferences():
if DEBUG_PREF_DELAY:
    import time
    time.sleep(random.uniform(0.5, 2))  # Random delay
```
**What to debug:** UI inconsistencies, preference not applying

## 4. Frontend JavaScript Debugging

### State Synchronization Issues
**File:** `frontend/app.js`
```javascript
// Add debug flag:
const DEBUG_ASYNC_ISSUES = true;

// In loadTodos():
if (DEBUG_ASYNC_ISSUES) {
    // Load todos before preferences are ready
    renderTodos();
    setTimeout(() => loadPreferences(), 2000);
}
```
**What to debug:** Race conditions, undefined errors

### Double-Click Issues
**File:** `frontend/app.js`
```javascript
// Remove click debouncing:
const DEBUG_NO_DEBOUNCE = true;

// Allow rapid clicking without protection
```
**What to debug:** Duplicate todo creation, multiple API calls

### Memory Leaks
**File:** `frontend/app.js`
```javascript
const DEBUG_MEMORY_LEAK = true;

// Keep references to old data:
if (DEBUG_MEMORY_LEAK) {
    window.leakedData = window.leakedData || [];
    window.leakedData.push([...allTodos]);
}
```
**What to debug:** Browser memory usage, performance degradation

## 5. Common Real-World Scenarios

### Scenario 1: "My sort preference doesn't persist"
Enable: `DEBUG_PREF_DELAY` in proxy
Debug path: Frontend → Proxy → Database → Response timing

### Scenario 2: "Todos disappear randomly"
Enable: `DEBUG_RANDOM_FAIL` in todos_api
Debug path: Network tab → Error handling → Retry logic

### Scenario 3: "Can't login after a few minutes"
Enable: `DEBUG_FAST_EXPIRE` in users_api
Debug path: Session storage → Token validation → Refresh logic

### Scenario 4: "Page is slow with many todos"
Enable: `DEBUG_SLOW_DB` in todos_api
Debug path: SQL queries → Indexes → Pagination → Caching

### Scenario 5: "Dark mode flashes to light on refresh"
Enable: `DEBUG_PREF_DELAY` in proxy
Debug path: Initial render → Preference loading → Theme application

## 6. Security Debugging

### SQL Injection Vulnerability
**File:** `backend/todos_api.py`
```python
DEBUG_SQL_INJECTION = True

# In handle_get_todos():
if DEBUG_SQL_INJECTION:
    # UNSAFE: Direct string concatenation
    query = f"SELECT * FROM todos WHERE user_id = {user_id}"
    cursor.execute(query)  # Vulnerable!
```

### XSS Vulnerability
**File:** `frontend/app.js`
```javascript
const DEBUG_XSS = true;

// In renderTodos():
if (DEBUG_XSS) {
    // UNSAFE: Direct HTML insertion
    td.innerHTML = todo.title;  // Instead of escapeHtml()
}
```

## 7. Performance Debugging

### N+1 Query Problem
**File:** `backend/todos_api.py`
```python
DEBUG_N_PLUS_ONE = True

# Load tags separately for each todo:
if DEBUG_N_PLUS_ONE:
    for todo in todos:
        cursor.execute('SELECT * FROM todo_tags WHERE todo_id = ?', (todo['id'],))
        # Separate query for each todo!
```

### Unnecessary Re-renders
**File:** `frontend/app.js`
```javascript
const DEBUG_EXCESSIVE_RENDERS = true;

// Re-render entire table for single changes:
if (DEBUG_EXCESSIVE_RENDERS) {
    setInterval(() => renderTodos(), 1000);  // Render every second!
}
```

## Tips for Debugging

1. **Use Browser DevTools:**
   - Network tab: Monitor API calls
   - Console: Check for errors
   - Application tab: Inspect localStorage
   - Performance tab: Find bottlenecks

2. **Use Python Debugging:**
   - Add `print()` statements
   - Use `import pdb; pdb.set_trace()`
   - Check SQLite with: `sqlite3 database.db`

3. **Common Commands:**
   ```bash
   # Check if services are running
   ps aux | grep python

   # Monitor network traffic
   curl -X GET http://localhost:8080/api/todos -H "X-User-Id: 1"

   # Check database
   sqlite3 database/todos.db "SELECT * FROM todos;"
   ```

4. **Debugging Order:**
   - Start with the browser console
   - Check Network tab for API calls
   - Review proxy logs
   - Check backend logs
   - Examine database state

## Learning Objectives

By working through these scenarios, you'll learn to:
1. Debug across multiple layers (Frontend → Proxy → Backend → Database)
2. Use developer tools effectively
3. Understand common web app issues
4. Implement proper error handling
5. Optimize performance
6. Fix security vulnerabilities
7. Handle race conditions
8. Manage state synchronization

Remember: The goal is to understand HOW to debug, not just fix the specific issue. Take time to explore the entire request/response flow!