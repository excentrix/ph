from fastmcp import FastMCP
# from core.config import settings
import importlib
import asyncio

# Import our MCP components
from services.mcp.patterns.academic_progress import academic_progress
from services.mcp.patterns.career_guidance import career_guidance
from services.mcp.resources.student_data import student_data
from services.mcp.resources.courses import courses_data
from services.mcp.tools.academic_tools import academic_tools
from services.mcp.tools.planning_tools import planning_tools
# from services.mcp.resources import courses_data


# Create the main MCP server
mcp_server = FastMCP("AI Student Mentor")

# Flag to track if setup is complete
setup_complete = False

# Setup function to import all servers asynchronously
async def setup_mcp_server():
    global setup_complete
    if setup_complete:
        return
    
    # Mount all our components
    await mcp_server.import_server(prefix="ap", server=academic_progress)
    await mcp_server.import_server(prefix="cg", server=career_guidance)
    await mcp_server.import_server(prefix="sd", server=student_data)
    await mcp_server.import_server(prefix="cd", server=courses_data)
    await mcp_server.import_server(prefix="at", server=academic_tools)
    await mcp_server.import_server(prefix="pt", server=planning_tools)
    
    setup_complete = True

# Function to ensure the server is set up before use
async def ensure_server_ready():
    await setup_mcp_server()
    return mcp_server

# Define a convenience function to run the server
def run_mcp_server(transport="stdio", host="127.0.0.1", port=8080):
    """Run the MCP server with the specified transport"""
    async def setup_and_run():
        await setup_mcp_server()
        # Since FastMCP's run method is synchronous, we need to run it in a separate thread
        import threading
        run_thread = threading.Thread(target=lambda: mcp_server.run(transport=transport))
        run_thread.daemon = True
        run_thread.start()
        # Keep the event loop alive
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    
    asyncio.run(setup_and_run())

if __name__ == "__main__":
    # When run directly, start the server with stdio transport
    run_mcp_server()