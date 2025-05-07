#!/bin/bash

# Start databases only
echo "Starting database services..."
docker-compose up -d postgres neo4j redis

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 5

# Start backend in development mode
echo "Starting backend in development mode..."
cd backend
source .venv/bin/activate
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=

# Start frontend in development mode
echo "Starting frontend in development mode..."
cd ../frontend
pnpm dev &
FRONTEND_PID=

# Handle shutdown
function cleanup {
  echo "Shutting down services..."
  kill 
  kill 
  cd ..
  docker-compose down
  echo "All services stopped."
}

trap cleanup EXIT

# Keep script running
echo "Development environment is running. Press Ctrl+C to stop."
wait

# if not executing:=> chmod +x start-dev.sh