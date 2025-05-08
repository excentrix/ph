#!/bin/bash

cd backend

# Test running the MCP server directly
echo "Testing MCP server directly..."
python -m services.mcp.server

# Wait for user input
read -p "Press Enter to continue..."

# Test running with fastmcp CLI
echo "Testing with fastmcp CLI..."
fastmcp dev services/mcp/server.py
