#!/bin/bash

# Kill any existing processes
lsof -ti:8000,8080,8081,8082 | xargs kill -9 2>/dev/null
sleep 1

echo "Starting all services..."

# Start all services
cd /Users/yasincakal/Documents/vs-code/projects/debug-todo-app

python3 backend/users_api.py &
USERS_PID=$!
echo "Users API started (PID: $USERS_PID)"

python3 backend/todos_api.py &
TODOS_PID=$!
echo "Todos API started (PID: $TODOS_PID)"

python3 proxy/proxy.py &
PROXY_PID=$!
echo "Proxy started (PID: $PROXY_PID)"

cd frontend && python3 -m http.server 8000 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "All services running!"
echo "Open http://localhost:8000 in your browser"
echo ""
echo "Press Ctrl+C to stop all services"

trap "kill $USERS_PID $TODOS_PID $PROXY_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait