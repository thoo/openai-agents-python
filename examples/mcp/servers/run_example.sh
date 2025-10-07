#!/bin/bash

# Script to run all MCP servers and the client example

# Change to the servers directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "Starting MCP servers..."

# Start servers in the background
cd "$SCRIPT_DIR"
uv run uvicorn math_server:mcp.app --port 8001 &
PID_MATH=$!
echo "  Math server started (PID: $PID_MATH) on port 8001"

uv run uvicorn text_server:mcp.app --port 8002 &
PID_TEXT=$!
echo "  Text server started (PID: $PID_TEXT) on port 8002"

uv run uvicorn data_server:mcp.app --port 8003 &
PID_DATA=$!
echo "  Data server started (PID: $PID_DATA) on port 8003"

# Function to cleanup servers on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $PID_MATH $PID_TEXT $PID_DATA 2>/dev/null
    wait $PID_MATH $PID_TEXT $PID_DATA 2>/dev/null
    echo "All servers stopped"
}

# Register cleanup function
trap cleanup EXIT INT TERM

# Wait for servers to start
echo ""
echo "Waiting 3 seconds for servers to start..."
sleep 3

# Run the client
echo ""
echo "Running client example..."
cd "$PROJECT_ROOT"
uv run --env-file .env python examples/mcp/multiple_mcp_servers_example.py

# Cleanup will be called automatically
