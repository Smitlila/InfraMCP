from mcp.server.fastmcp import FastMCP
import psutil

# Create our MCP server
mcp = FastMCP("InfraMCP")


# Tool 1: Greeting
@mcp.tool()
def say_hello(name: str) -> str:
    """Greet a user by their name."""
    return f"Hello {name}! Welcome to InfraMCP."

#Tool 2: CPU monitoring
@mcp.tool()
def get_cpu_usage() -> dict:
    """Get the current CPU usage percentage."""
    cpu_percent = psutil.cpu_percent(interval=1)
    return {
        "cpu_usage_percent": cpu_percent,
        "status": "success"
    }


@mcp.tool()
def get_memory_usage() -> dict:
    """Get current system RAM usage and available memory."""

    memory = psutil.virtual_memory()

    return {
        "total_memory_gib": round(memory.total / (1024 ** 3), 2),
        "available_memory_gib": round(memory.available / (1024 ** 3), 2),
        "used_memory_percent": memory.percent
    }


@mcp.tool()
def get_disk_usage() -> dict:
    """Get disk storage usage for the root filesystem."""

    disk = psutil.disk_usage("/")

    return {
        "total_disk_gib": round(disk.total / (1024 ** 3), 2),
        "used_disk_gib": round(disk.used / (1024 ** 3), 2),
        "free_disk_gib": round(disk.free / (1024 ** 3), 2),
        "disk_usage_percent": disk.percent
    }


# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
