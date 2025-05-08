from fastmcp import FastMCP, Context

# Create a component server
basic = FastMCP("Basic Tools")

@basic.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# Async tool example
@basic.tool()
async def greet(name: str, ctx: Context = None) -> str:
    """Greet a person with a friendly message."""
    if ctx:
        await ctx.info(f"Generating greeting for {name}")
    return f"Hello, {name}! Welcome to the AI Student Mentoring Platform."

@basic.resource("system://info")
def get_system_info() -> dict:
    """Get basic system info."""
    import platform
    return {
        "os": platform.system(),
        "python_version": platform.python_version(),
        "platform": platform.platform()
    }
