#!/bin/bash

# Function to kill all background processes on exit
cleanup() {
    echo "Stopping all services..."
    if [ -n "$GATEWAY_PID" ]; then kill $GATEWAY_PID 2>/dev/null; fi
    if [ -n "$API_PID" ]; then kill $API_PID 2>/dev/null; fi
    if [ -n "$ORCHESTRATOR_PID" ]; then kill $ORCHESTRATOR_PID 2>/dev/null; fi
    if [ -n "$FRONTEND_PID" ]; then 
        kill $FRONTEND_PID 2>/dev/null
        # Also try to kill children of frontend (vite often spawns subprocesses)
        pkill -P $FRONTEND_PID 2>/dev/null
    fi
    kill $(jobs -p) 2>/dev/null
}

trap cleanup EXIT

# Activate Virtual Environment
source venv/bin/activate

echo "Starting Supervisor AI Components..."

# 1. Start Gateway (Port 6002)
echo "Starting Gateway on port 6002..."
./venv/bin/python -m gateway.main &
GATEWAY_PID=$!

# 2. Start Backend API (Port 6001)
echo "Starting Backend API on port 6001..."
./venv/bin/python -m backend.api &
API_PID=$!

# 3. Start Backend Orchestrator
echo "Starting Backend Orchestrator..."
./venv/bin/python -m backend.orchestrator &
ORCHESTRATOR_PID=$!

# 4. Start Frontend (Port 8081)
# 4. Start Frontend (Port 8081)
echo "Starting Frontend on port 8081..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "ERROR: node_modules not found in frontend directory!"
    echo "Please run 'npm install' inside the frontend directory."
    exit 1
fi

# Vite will pick up PORT from environment or we pass it explicitly if allowed
# passing -- --host 0.0.0.0 ensures it binds to all interfaces for remote access
HOST=0.0.0.0 PORT=8081 npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
cd ..

echo "All services started!"
echo "Gateway: http://localhost:6002"
echo "Backend API: http://localhost:6001"
echo "Frontend: http://localhost:8081"
echo "Press Ctrl+C to stop all services."

# Wait for all background processes
wait
