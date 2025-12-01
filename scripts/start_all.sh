#!/bin/bash

# Script to start both backend and frontend servers

echo "🚀 Starting NextLeap Chatbot..."
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY environment variable is not set"
    echo "   Please set it before starting:"
    echo "   export GEMINI_API_KEY='your_api_key_here'"
    echo ""
fi

# Kill any existing servers
echo "Cleaning up existing servers..."
pkill -f "run_server.py" 2>/dev/null
pkill -f "http.server.*3000" 2>/dev/null
sleep 2

# Start backend server
echo "Starting backend server on http://localhost:8000..."
cd "$(dirname "$0")/.."
export GEMINI_API_KEY="${GEMINI_API_KEY:-AIzaSyAowbwS15xpzN2bs8Q3rGhvlQe4SN3kMSc}"
python3 scripts/run_server.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start. Check backend.log for errors"
    exit 1
fi

# Start frontend server
echo "Starting frontend server on http://localhost:3000..."
cd frontend
python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for frontend to start
sleep 2

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend failed to start. Check frontend.log for errors"
    exit 1
fi

echo ""
echo "="*60
echo "✅ Both servers are running!"
echo ""
echo "Access points:"
echo "  🌐 Frontend: http://localhost:3000"
echo "  🔧 Backend:  http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To stop servers, run:"
echo "  pkill -f 'run_server.py'"
echo "  pkill -f 'http.server.*3000'"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo "="*60

