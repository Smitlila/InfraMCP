import asyncio
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



async def check_tool_discovery():
    """Connect to InfraMCP and verify its registered tools."""

    # Locate the project files
    project_dir = Path(__file__).resolve().parent.parent
    python_path = project_dir / ".venv" / "bin" / "python"
    server_path = project_dir / "server.py"

    # Configure the MCP server process
    server_params = StdioServerParameters(
        command=str(python_path),
        args=[str(server_path)],
        cwd=str(project_dir)
    )

    # Start the server and connect using STDIO
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Perform the MCP initialization handshake
            await session.initialize()

            # Request the server's available tools
            response = await session.list_tools()

            tool_names = {
                tool.name for tool in response.tools
            }

            expected_tools = {
                "say_hello",
                "get_cpu_usage",
                "get_memory_usage",
                "get_disk_usage",
                "read_logs",
                "search_logs",
                "count_errors"
            }

            # Verify that every expected tool exists
            assert expected_tools.issubset(tool_names)


def test_mcp_tool_discovery():
    """Run the asynchronous integration test using asyncio."""

    asyncio.run(check_tool_discovery())


async def check_read_logs_execution():
    """Execute read_logs through the MCP protocol."""

    # Locate the project files
    project_dir = Path(__file__).resolve().parent.parent
    python_path = project_dir / ".venv" / "bin" / "python"
    server_path = project_dir / "server.py"

    # Configure the MCP server
    server_params = StdioServerParameters(
        command=str(python_path),
        args=[str(server_path)],
        cwd=str(project_dir)
    )

    # Start the server and establish an MCP session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            # Execute the read_logs tool
            result = await session.call_tool(
                "read_logs",
                arguments={"lines": 5}
            )

            # Verify MCP execution succeeded
            assert result.isError is not True

            # Extract the tool's response
            if result.structuredContent is not None:
                data = result.structuredContent
            else:
                data = json.loads(result.content[0].text)

            # Verify the returned data
            assert data["status"] == "success"
            assert data["requested_lines"] == 5
            assert data["returned_lines"] == 5
            assert len(data["logs"]) == 5


def test_mcp_read_logs_execution():
    """Run the asynchronous MCP tool-execution test."""

    asyncio.run(check_read_logs_execution())


async def check_search_logs_execution():
    """Execute search_logs through the MCP protocol."""

    # Locate the project directory
    project_dir = Path(__file__).resolve().parent.parent

    python_path = project_dir / ".venv" / "bin" / "python"
    server_path = project_dir / "server.py"

    # Configure the MCP server process
    server_params = StdioServerParameters(
        command=str(python_path),
        args=[str(server_path)],
        cwd=str(project_dir)
    )

    # Start the server and connect
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            # Execute search_logs with a keyword
            result = await session.call_tool(
                "search_logs",
                arguments={"keyword": "database"}
            )

            # Verify MCP execution succeeded
            assert result.isError is not True

            # Extract the response data
            if result.structuredContent is not None:
                data = result.structuredContent
            else:
                data = json.loads(result.content[0].text)

            # Verify the search results
            assert data["status"] == "success"
            assert data["keyword"] == "database"
            assert data["total_matches"] == 2

            assert len(data["logs"]) == 2

            for log in data["logs"]:
                assert "database" in log.casefold()


def test_mcp_search_logs_execution():
    """Run the asynchronous search_logs integration test."""

    asyncio.run(check_search_logs_execution())


async def check_count_errors_execution():
    """Execute count_errors through the MCP protocol."""

    # Locate the project directory
    project_dir = Path(__file__).resolve().parent.parent

    python_path = project_dir / ".venv" / "bin" / "python"
    server_path = project_dir / "server.py"

    # Configure the MCP server process
    server_params = StdioServerParameters(
        command=str(python_path),
        args=[str(server_path)],
        cwd=str(project_dir)
    )

    # Start the server and establish an MCP session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            # Execute the count_errors tool
            result = await session.call_tool(
                "count_errors",
                arguments={}
            )

            # Verify MCP execution succeeded
            assert result.isError is not True

            # Extract the response data
            if result.structuredContent is not None:
                data = result.structuredContent
            else:
                data = json.loads(result.content[0].text)

            # Verify the error statistics
            assert data["status"] == "success"
            assert data["total_logs"] == 15
            assert data["error_count"] == 4
            assert data["critical_count"] == 1
            assert data["total_error_events"] == 5
            assert data["invalid_logs"] == 0


def test_mcp_count_errors_execution():
    """Run the asynchronous count_errors integration test."""

    asyncio.run(check_count_errors_execution())


async def check_api_health_report_execution():
    """Execute the health report through the MCP protocol."""

    # Locate the project directory
    project_dir = Path(__file__).resolve().parent.parent

    python_path = project_dir / ".venv" / "bin" / "python"
    server_path = project_dir / "server.py"

    # Configure the MCP server process
    server_params = StdioServerParameters(
        command=str(python_path),
        args=[str(server_path)],
        cwd=str(project_dir)
    )

    # Start the server and connect
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the MCP connection
            await session.initialize()

            # Execute the health report tool
            result = await session.call_tool(
                "get_api_health_report",
                arguments={}
            )

            # Verify MCP execution succeeded
            assert result.isError is not True

            # Extract the response
            if result.structuredContent is not None:
                data = result.structuredContent
            else:
                data = json.loads(result.content[0].text)

            # Verify the report structure
            assert data["status"] == "success"
            assert data["total_services"] == 2

            assert (
                data["healthy_services"]
                + data["unhealthy_services"]
                == data["total_services"]
            )

            assert len(data["services"]) == 2

            # Verify both approved services appear
            service_names = {
                item["service"]
                for item in data["services"]
            }

            assert service_names == {"example", "github"}

            # Verify every service has a health result
            for item in data["services"]:
                assert isinstance(item["healthy"], bool)


def test_mcp_api_health_report_execution():
    """Run the asynchronous MCP integration test."""

    asyncio.run(check_api_health_report_execution())
