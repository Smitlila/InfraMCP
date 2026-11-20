
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Step 1: Read the tool name from terminal arguments
    if len(sys.argv) < 2:
        print("Usage: python test_client.py <tool_name> [name]")
        return

    tool_name = sys.argv[1]

    # Step 2: Prepare arguments for the selected tool
    arguments = {}

    if tool_name == "say_hello":
        if len(sys.argv) < 3:
            print("Usage: python test_client.py say_hello <name>")
            return

        arguments = {"name": sys.argv[2]}
    elif tool_name == "search_logs":
        if len(sys.argv) < 3:
            print("Usage: python test_client.py search_logs <keyword>")
            return

        arguments = {"keyword": " ".join(sys.argv[2:])}
    
    elif tool_name == "check_api_health":
        if len(sys.argv) >= 3:
            arguments = {"service": sys.argv[2]}



    # Step 3: Locate the MCP server
    project_dir = Path(__file__).resolve().parent

    server_params = StdioServerParameters(
        command=str(project_dir / ".venv" / "bin" / "python"),
        args=[str(project_dir / "server.py")],
        cwd=str(project_dir)
    )

    # Step 4: Connect to the MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Step 5: Discover and validate tool name
            tools = await session.list_tools()
            available_tools = [tool.name for tool in tools.tools]

            if tool_name not in available_tools:
                print(f"Unknown tool: {tool_name}")
                print("Available tools:", ", ".join(available_tools))
                return

            # Step 6: Execute selected tool
            result = await session.call_tool(
                tool_name,
                arguments=arguments
            )

            if result.isError:
                print("Tool execution failed:", result)
                return

            # Step 7: Display result
            if result.structuredContent is not None:
                print(json.dumps(result.structuredContent, indent=2))
            else:
                for content in result.content:
                    if content.type == "text":
                        print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
