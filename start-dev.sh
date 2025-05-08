#!/bin/bash

# Check if Ollama is running
# echo "Checking if Ollama is running..."
# if ! curl -s http://localhost:11434/api/tags >/dev/null; then
#     echo "Ollama is not running. Please start Ollama first."
#     echo "Run 'ollama serve' in a separate terminal."
#     exit 1
# fi

# Check if Llama3 model is available
echo "Checking for llama3 model..."
if ! curl -s http://localhost:11434/api/tags | grep -q "llama3.1:latest"; then
    echo "Llama3 model not found. Pulling llama3 model..."
    ollama pull llama3.1:latest
fi

# Start databases only
echo "Starting database services..."
docker-compose up -d postgres neo4j redis

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
sleep 5

# Start MCP server in development mode
echo "Starting MCP server in development mode..."
cd backend
source .venv/bin/activate

# Start MCP server with the fastmcp CLI in a separate terminal
echo "Starting MCP server..."
fastmcp dev services/mcp/server.py &
MCP_PID=$!

# Wait a moment for MCP server to start
sleep 2

# Start FastAPI backend in development mode
echo "Starting backend API in development mode..."
python -m uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend in development mode
echo "Starting frontend in development mode..."
cd ../frontend
pnpm dev &
FRONTEND_PID=$!

# Handle shutdown
function cleanup {
  echo "Shutting down services..."
  kill $MCP_PID
  kill $BACKEND_PID
  kill $FRONTEND_PID
  cd ..
  docker-compose down
  echo "All services stopped."
}

trap cleanup EXIT

# Keep script running
echo "Development environment is running. Press Ctrl+C to stop."
wait