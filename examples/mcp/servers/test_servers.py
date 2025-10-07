"""
Simple test script to verify MCP servers are running and accessible.

Run this after starting all three servers to verify they're working correctly.
"""

import asyncio

from agents.mcp import MCPServerStreamableHttp


async def test_server(name: str, url: str, port: int):
    """Test a single MCP server."""
    print(f"\n{'='*60}")
    print(f"Testing {name} on port {port}")
    print(f"{'='*60}")

    try:
        server = MCPServerStreamableHttp(
            params={"url": url, "timeout": 5.0},
            cache_tools_list=True,
        )

        await server.connect()
        print(f"✓ Connected to {name}")

        # List available tools
        tools = await server.list_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")

        await server.cleanup()
        print(f"✓ Connection closed successfully")
        return True

    except Exception as e:
        print(f"✗ Failed to connect to {name}: {e}")
        print(f"  Make sure the server is running: uv run examples/mcp/servers/{name.lower().replace(' ', '_')}.py")
        return False


async def main():
    """Test all three servers."""
    print("\nMCP Servers Connection Test")
    print("=" * 60)

    results = await asyncio.gather(
        test_server("Math Server", "http://localhost:8001/sse", 8001),
        test_server("Text Server", "http://localhost:8002/sse", 8002),
        test_server("Data Server", "http://localhost:8003/sse", 8003),
        return_exceptions=True,
    )

    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")

    success_count = sum(1 for r in results if r is True)
    total_count = len(results)

    if success_count == total_count:
        print(f"✓ All {total_count} servers are running correctly!")
        print("\nYou can now run the main example:")
        print("  uv run --env-file .env examples/mcp/multiple_mcp_servers_example.py")
    else:
        print(f"✗ {total_count - success_count} server(s) failed to connect")
        print("\nMake sure all servers are running in separate terminals:")
        print("  Terminal 1: uv run examples/mcp/servers/math_server.py")
        print("  Terminal 2: uv run examples/mcp/servers/text_server.py")
        print("  Terminal 3: uv run examples/mcp/servers/data_server.py")


if __name__ == "__main__":
    asyncio.run(main())
