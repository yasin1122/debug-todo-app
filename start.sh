#!/bin/bash

echo "🚀 Starting Debug Todo App..."
echo ""

echo "📊 Checking databases..."
if [ ! -f "database/todos.db" ] || [ ! -f "database/users.db" ] || [ ! -f "database/preferences.db" ]; then
    echo "   Databases not found, initializing..."
    cd database
    python3 init_db.py
    cd ..
else
    echo "   Databases already exist, skipping initialization."
fi

echo ""
echo "🌐 Starting backend services..."

echo "Starting Users API on port 8082..."
cd backend
python3 users_api.py &
USERS_PID=$!
cd ..

sleep 2

echo "Starting Todos API on port 8081..."
cd backend
python3 todos_api.py &
TODOS_PID=$!
cd ..

sleep 2

echo "Starting Proxy Server on port 8080..."
cd proxy
python3 proxy.py &
PROXY_PID=$!
cd ..

sleep 2

echo "Starting Frontend Server on port 8000..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ All services started!"
echo ""
echo "📝 Service URLs:"
echo "   Frontend:    http://localhost:8000"
echo "   Proxy:       http://localhost:8080"
echo "   Todos API:   http://localhost:8081"
echo "   Users API:   http://localhost:8082"
echo ""
echo "🔑 Demo Users:"
echo "   demo / demo123"
echo "   alice / alice123"
echo "   bob / bob123"
echo ""
echo "Press Ctrl+C to stop all services..."

trap "echo ''; echo 'Stopping all services...'; kill $USERS_PID $TODOS_PID $PROXY_PID $FRONTEND_PID 2>/dev/null; exit" INT

wait