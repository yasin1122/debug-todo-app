# Debug Scenarios

This file is a catalogue of bugs you can deliberately inject into the app to
practice debugging. The codebase ships clean — no scenarios are active by
default. Each recipe below is **copy-paste ready**: it tells you exactly which
file to edit, what to add, and how to revert.

---

## How to use

1. Pick a scenario.
2. Follow the **Steps** exactly — file path, line anchor, and code block.
3. Restart the affected service (`Ctrl+C` then `bash run_all.sh`). The frontend
   is static, so a hard browser refresh (`Cmd+Shift+R` / `Ctrl+Shift+R`) is
   enough for frontend-only changes.
4. Reproduce the symptom in the browser.
5. Practice debugging it (DevTools, server logs, the database).
6. **Revert:** undo the additions. Each scenario tells you what to remove.

> ⚠️ **Don't run these against any data you care about.** Several scenarios
> introduce real vulnerabilities (SQL injection, XSS) or corrupt state.

---

## Layer 1 · Database & Backend Performance

### 1. Slow database queries

Make every `GET /api/todos` block for 3 seconds.

**File:** `backend/todos_api.py`

**Step 1.** Add to the imports at the top of the file:
```python
import time
```

**Step 2.** Inside `handle_get_todos`, immediately after this block:
```python
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
```
add:
```python
        time.sleep(3)  # DEBUG: simulate slow query
```

**Symptom:** Loading the todo list hangs for 3 seconds every time.
**Practice:** Network tab waterfall, loading-state UX, query optimization.
**Revert:** Delete the `import time` and the `time.sleep(3)` line.

---

### 2. Leaked database connections

Stop closing SQLite connections so they accumulate until SQLite locks up.

**File:** `backend/todos_api.py`

**Step 1.** Inside `handle_get_todos`, find the line:
```python
        conn.close()
```
(near the bottom of the function, after `cursor.fetchall()`) and **delete it**.

**Symptom:** After ~50 page loads you'll start seeing `database is locked` or
silent stalls. The Python process never releases the file handles.

**Practice:** Resource cleanup, `try/finally`, `with`-statements, connection
pooling.
**Revert:** Add the `conn.close()` line back. You may need to kill and restart
the Todos API to release the leaked connections.

---

## Layer 2 · Backend API Behavior

### 3. Random 500 errors

Make 30% of `GET /api/todos` calls fail.

**File:** `backend/todos_api.py`

**Step 1.** Add to the imports at the top:
```python
import random
```

**Step 2.** Inside `handle_get_todos`, immediately after the `if not user_id`
block (same anchor as scenario 1), add:
```python
        if random.random() < 0.3:  # DEBUG: 30% random failure
            self.send_json_response({'error': 'Random server error'}, 500)
            return
```

**Symptom:** The list intermittently fails to load. Browser console shows 500s.
**Practice:** Error handling, retry logic, user-facing error messages.
**Revert:** Delete the added block and the `import random` if no other scenario uses it.

---

### 4. Fast token expiry

Tokens expire one minute after login instead of 24 hours.

**File:** `backend/users_api.py`

**Step 1.** Inside `handle_login`, find:
```python
        expires_at = datetime.now() + timedelta(hours=24)  # Token is valid for 24 hours.
```
**Replace with:**
```python
        expires_at = datetime.now() + timedelta(minutes=1)  # DEBUG: fast expiry
```

**Symptom:** Login works, then a minute later every action redirects to login.
**Practice:** Session lifecycle, token refresh, "stay logged in" patterns.
**Revert:** Restore `timedelta(hours=24)`.

---

### 5. Missing input validation

Accept empty or null titles when creating todos.

**File:** `backend/todos_api.py`

**Step 1.** Inside `handle_create_todo`, find and **delete**:
```python
        title = data.get('title')
        if not title:
            self.send_json_response({'error': 'Title is required'}, 400)
            return
```

**Step 2.** Replace it with:
```python
        title = data.get('title')  # DEBUG: validation removed
```

**Symptom:** You can save todos with empty titles. They appear as blank rows.
**Practice:** Defense-in-depth, input validation, NULL handling in SQL.
**Revert:** Restore the original 4-line check.

---

## Layer 3 · Proxy

### 6. Broken CORS

The frontend stops being able to talk to the proxy.

**File:** `proxy/proxy.py`

**Step 1.** Inside `send_cors_headers`, find:
```python
        self.send_header('Access-Control-Allow-Origin', '*')
```
and **comment it out**:
```python
        # self.send_header('Access-Control-Allow-Origin', '*')  # DEBUG: CORS broken
```

**Symptom:** Every fetch fails. Console shows `CORS policy: No
'Access-Control-Allow-Origin' header is present`.
**Practice:** CORS preflight, browser security model, network-tab inspection.
**Revert:** Uncomment the line.

---

### 7. Random header stripping

Drop the `X-User-Id` header on 30% of forwarded requests.

**File:** `proxy/proxy.py`

**Step 1.** Add to the imports at the top:
```python
import random
```

**Step 2.** Inside `proxy_request`, find:
```python
        proxy_headers = {}
        if headers:
            for key, value in headers.items():
                if key.lower() not in ['host', 'connection']:
                    proxy_headers[key] = value
```
and add **immediately after**:
```python
        if 'X-User-Id' in proxy_headers and random.random() < 0.3:  # DEBUG
            del proxy_headers['X-User-Id']
```

**Symptom:** Random 401 Unauthorized responses despite being logged in.
**Practice:** Tracing a single request across services, intermittent failures.
**Revert:** Delete the added block.

---

### 8. Preference race condition

Make `GET /preferences` randomly slow.

**File:** `proxy/proxy.py`

**Step 1.** Add to the imports at the top:
```python
import time
import random
```

**Step 2.** Inside `handle_get_preferences`, immediately after this block:
```python
        user_id = self.get_user_id_from_headers()
        if not user_id:
            self.send_json_response({'error': 'Unauthorized'}, 401)
            return
```
add:
```python
        time.sleep(random.uniform(0.5, 2))  # DEBUG: random delay
```

**Symptom:** On page load, the table renders with default settings, then
"flashes" to the user's saved theme/sort a moment later.
**Practice:** Race conditions, render order, blocking vs awaiting.
**Revert:** Delete the line. Remove the imports if no other scenario uses them.

---

## Layer 4 · Frontend

### 9. State synchronization issue

Render todos before preferences are loaded.

**File:** `frontend/app.js`

**Step 1.** Find the `DOMContentLoaded` handler and the lines:
```javascript
    await loadPreferences();
    await loadTodos();
```
**Replace with:**
```javascript
    loadTodos();                              // DEBUG: not awaited
    setTimeout(() => loadPreferences(), 2000); // DEBUG: preferences load late
```

**Symptom:** Page renders, then 2 seconds later columns rearrange / theme flips.
Possible `Cannot read property of null` errors if a render fires before
`tableSettings` is set.
**Practice:** Async ordering, `await`, defensive null checks, loading states.
**Revert:** Restore the original two `await` calls.

---

### 10. Memory leak

Keep references to every todo list ever fetched.

**File:** `frontend/app.js`

**Step 1.** Inside `renderTodos`, immediately after this line:
```javascript
function renderTodos() {
```
add:
```javascript
    window.leakedData = window.leakedData || [];   // DEBUG: leak
    window.leakedData.push([...allTodos]);
```

**Symptom:** Open DevTools → Memory → take heap snapshots; size grows on every
toggle/sort/filter and never shrinks.
**Practice:** Heap snapshots, retained references, why DOM listeners and
globals can leak.
**Revert:** Delete the added lines.

---

### 11. Excessive re-renders

Re-render the whole table once per second whether data changed or not.

**File:** `frontend/app.js`

**Step 1.** At the very bottom of `app.js` (after the closing `});` of the
`DOMContentLoaded` handler), add:
```javascript
setInterval(() => renderTodos(), 1000);  // DEBUG: re-render every second
```

**Symptom:** You can see the table flicker during long sessions; CPU rises.
**Practice:** Render diffing, profiler timeline, why incremental updates beat
"redraw everything".
**Revert:** Delete the line.

---

## Layer 5 · Security

> ⚠️ Both of these introduce real vulnerabilities. Do not deploy a copy of the
> repo with these enabled.

### 12. SQL injection

String-concatenate `user_id` into the query instead of using `?`.

**File:** `backend/todos_api.py`

**Step 1.** Inside `handle_get_todos`, find:
```python
        base_query = 'SELECT * FROM todos WHERE user_id = ?'
        params = [user_id]
```
**Replace with:**
```python
        base_query = f'SELECT * FROM todos WHERE user_id = {user_id}'  # DEBUG: VULNERABLE
        params = []
```

**Symptom:** Sending `X-User-Id: 1 OR 1=1` returns *every user's* todos.
**Practice:** Parameterized queries, the difference between binding and
formatting, why "trusted" headers shouldn't be trusted.
**Revert:** Restore the original two lines.

---

### 13. XSS

Render todo titles as raw HTML instead of escaping them.

**File:** `frontend/app.js`

**Step 1.** Inside `renderTodos`, find:
```javascript
                <td data-column="title">${escapeHtml(todo.title)}</td>
```
**Replace with:**
```javascript
                <td data-column="title">${todo.title}</td>  <!-- DEBUG: VULNERABLE -->
```

**Symptom:** Create a todo with the title `<img src=x onerror=alert(1)>` —
it executes when the row renders.
**Practice:** Escaping vs sanitizing, `textContent` vs `innerHTML`, where
trust boundaries lie in a frontend.
**Revert:** Restore `escapeHtml(todo.title)`.

---

## Where to start — symptom → scenario map

If you want to practice debugging without picking a layer first, start with one
of these symptoms and find the matching scenario.

| Symptom you observe                              | Inject scenario | Layer  |
|--------------------------------------------------|-----------------|--------|
| "Page is slow with many todos."                  | 1               | DB/BE  |
| "App breaks after a while, can't recover."       | 2               | DB/BE  |
| "Some todos disappear randomly on refresh."      | 3               | BE     |
| "Can't log in after a couple of minutes."        | 4               | BE     |
| "Empty rows appear in the table."                | 5               | BE     |
| "Whole app stops working in the browser."        | 6               | Proxy  |
| "Logged in but getting random 401s."             | 7               | Proxy  |
| "Dark mode flashes to light on every refresh."   | 8               | Proxy  |
| "UI shows wrong settings on initial load."       | 9               | FE     |
| "Browser tab gets sluggish over time."           | 10              | FE     |
| "Battery drains fast / fan spins on this page."  | 11              | FE     |
| "Suspicious: I can see another user's data."     | 12              | DB/BE  |
| "Alert popup when I open the table."             | 13              | FE     |

---

## Tips

- **Network tab** is the best debugger you don't think to open. Status codes
  and response bodies tell you whether the bug is FE or BE.
- **`tail -f` the service output** while reproducing — the Python servers print
  every request.
- **Inspect the database directly:**
  ```bash
  sqlite3 database/todos.db "SELECT id, user_id, is_completed, title FROM todos;"
  sqlite3 database/preferences.db "SELECT * FROM user_preferences;"
  sqlite3 database/users.db "SELECT username, last_login FROM users;"
  ```
- **Restart the right service.** Python doesn't auto-reload. After editing a
  `.py` file, kill its process (`lsof -ti:<port> | xargs kill -9`) and run
  `bash run_all.sh` again. Frontend changes need only a browser hard-refresh.
- **Debug across layers in order:** Browser console → Network tab → Proxy
  output → backend output → database. Stop at the first layer that has the
  wrong data.
