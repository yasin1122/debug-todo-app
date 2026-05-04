#!/bin/bash
# Start the entire debug-todo-app stack.
#   - Initializes databases on first run (only if they don't already exist).
#   - Kills any process already bound to the four ports we use, so re-running
#     the script never produces "address already in use" errors.
#   - Preserves existing data on every subsequent run.

set -e
cd "$(dirname "$0")"

# Free up our four ports if anything is still listening from a previous run.
lsof -ti:8000,8080,8081,8082 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Initialize the databases on first run.
if [ ! -f "database/todos.db" ] || [ ! -f "database/users.db" ] || [ ! -f "database/preferences.db" ]; then
    echo "First run detected — initializing databases..."
    (cd database && python3 init_db.py)
fi

echo "Starting all services..."

python3 backend/users_api.py &
USERS_PID=$!
echo "  Users API   :8082  (PID $USERS_PID)"

python3 backend/todos_api.py &
TODOS_PID=$!
echo "  Todos API   :8081  (PID $TODOS_PID)"

python3 proxy/proxy.py &
PROXY_PID=$!
echo "  Proxy       :8080  (PID $PROXY_PID)"

(cd frontend && python3 -m http.server 8000) &
FRONTEND_PID=$!
echo "  Frontend    :8000  (PID $FRONTEND_PID)"

echo ""
echo "All services running. Open http://localhost:8000"
echo "Press Ctrl+C to stop."

trap "kill $USERS_PID $TODOS_PID $PROXY_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
