import asyncio
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl



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
    
async def check_resource_discovery():
    """Connect to InfraMCP and discover registered Resources."""

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

    # Start the server and establish a session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the MCP connection
            await session.initialize()

            # Ask the server for available Resources
            response = await session.list_resources()

            # Extract Resource URIs
            resource_uris = {
                str(resource.uri)
                for resource in response.resources
            }

            # Verify our Resource is registered
            assert "infra://services" in resource_uris


def test_mcp_resource_discovery():
    """Run the asynchronous Resource discovery test."""

    asyncio.run(check_resource_discovery())


async def check_services_resource_read():
    """Read the approved services Resource through MCP."""

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

    # Start the server and establish a session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the MCP connection
            await session.initialize()

            # Read the Resource
            response = await session.read_resource(
                AnyUrl("infra://services")
            )

            # Verify the response contains content
            assert len(response.contents) == 1

            # Extract the Resource content
            content = response.contents[0]

            # Verify the Resource URI
            assert str(content.uri) == "infra://services"

            # Convert JSON text into a Python dictionary
            data = json.loads(content.text)

            # Verify the approved services
            assert data["services"] == {
                "example": "https://example.com",
                "github": "https://github.com"
            }


def test_mcp_services_resource_read():
    """Run the asynchronous Resource reading test."""

    asyncio.run(check_services_resource_read())

async def check_resource_template_discovery():
    """Discover Resource Templates through the MCP protocol."""

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

            # Discover Resource Templates
            response = await session.list_resource_templates()

            # Extract the URI templates
            template_uris = {
                str(template.uriTemplate)
                for template in response.resourceTemplates
            }

            # Verify our dynamic template exists
            assert (
                "infra://services/{service_name}"
                in template_uris
            )


def test_mcp_resource_template_discovery():
    """Run the asynchronous Resource Template discovery test."""

    asyncio.run(check_resource_template_discovery())

async def check_dynamic_service_resource():
    """Read a specific service through an MCP Resource Template."""

    # Locate the InfraMCP project directory
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

            # Initialize the MCP connection
            await session.initialize()

            # Read the dynamic Resource
            response = await session.read_resource(
                AnyUrl("infra://services/github")
            )

            # Verify one content item was returned
            assert len(response.contents) == 1

            # Extract the Resource content
            content = response.contents[0]

            # Verify the returned URI
            assert str(content.uri) == "infra://services/github"

            # Convert JSON text into a Python dictionary
            data = json.loads(content.text)

            # Verify the service configuration
            assert data["status"] == "success"
            assert data["service"] == "github"
            assert data["url"] == "https://github.com"


def test_mcp_dynamic_service_resource():
    """Run the dynamic Resource integration test."""

    asyncio.run(check_dynamic_service_resource())

async def check_unknown_service_resource():
    """Verify an unknown service returns error content."""

    # Locate the InfraMCP project directory
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

            # Initialize the MCP connection
            await session.initialize()

            # Request an unapproved service Resource
            response = await session.read_resource(
                AnyUrl("infra://services/unknown")
            )

            # Verify one content item was returned
            assert len(response.contents) == 1

            # Extract the Resource content
            content = response.contents[0]

            # Verify the returned URI
            assert str(content.uri) == "infra://services/unknown"

            # Convert JSON text to a Python dictionary
            data = json.loads(content.text)

            # Verify the error response
            assert data["status"] == "error"
            assert data["service"] == "unknown"
            assert data["message"] == "Service is not approved"

            # Ensure no service URL was exposed
            assert "url" not in data


def test_mcp_unknown_service_resource():
    """Run the unknown-service Resource integration test."""

    asyncio.run(check_unknown_service_resource())


async def check_prompt_discovery():
    """Verify MCP clients can discover registered prompts."""

    # Locate the InfraMCP project directory
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

            # Initialize the MCP connection
            await session.initialize()

            # Discover available MCP Prompts
            response = await session.list_prompts()

            # Extract prompt names
            prompt_names = {
                prompt.name
                for prompt in response.prompts
            }

            # Verify our prompt is registered
            assert "investigate_api_failure" in prompt_names


def test_mcp_prompt_discovery():
    """Run the asynchronous Prompt discovery test."""

    asyncio.run(check_prompt_discovery())

async def check_prompt_retrieval():
    """Retrieve API troubleshooting instructions through MCP."""

    # Locate the InfraMCP project directory
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

            # Initialize the MCP connection
            await session.initialize()

            # Retrieve the troubleshooting prompt
            response = await session.get_prompt(
                "investigate_api_failure",
                arguments={"service": "github"}
            )

            # Verify the prompt contains one message
            assert len(response.messages) == 1

            # Extract the prompt message
            message = response.messages[0]

            # Verify the message role
            assert message.role == "user"

            # Verify the content is text
            assert message.content.type == "text"

            # Extract the generated instructions
            prompt_text = message.content.text

            # Verify the selected service
            assert "github" in prompt_text
            assert "https://github.com" in prompt_text

            # Verify troubleshooting instructions
            assert "check_api_health" in prompt_text
            assert "get_api_health_report" in prompt_text
            assert "HTTP status code" in prompt_text

            # Verify the safety instruction
            assert "Do not claim a root cause" in prompt_text


def test_mcp_prompt_retrieval():
    """Run the asynchronous MCP Prompt retrieval test."""

    asyncio.run(check_prompt_retrieval())

async def check_prompt_unknown_service():
    """Verify the prompt rejects unapproved services."""

    # Locate the InfraMCP project directory
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

            # Initialize the MCP connection
            await session.initialize()

            # Request the prompt for an unknown service
            response = await session.get_prompt(
                "investigate_api_failure",
                arguments={"service": "unknown"}
            )

            # Verify one prompt message was returned
            assert len(response.messages) == 1

            # Extract the message
            message = response.messages[0]

            # Verify the message format
            assert message.role == "user"
            assert message.content.type == "text"

            # Extract the prompt text
            prompt_text = message.content.text

            # Verify the validation message
            assert "unknown" in prompt_text
            assert "is not approved" in prompt_text
            assert "select a configured service" in prompt_text

            # Verify normal troubleshooting steps are absent
            assert "check_api_health" not in prompt_text
            assert "get_api_health_report" not in prompt_text


def test_mcp_prompt_unknown_service():
    """Run the unknown-service prompt integration test."""

    asyncio.run(check_prompt_unknown_service())
