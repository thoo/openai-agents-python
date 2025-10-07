"""
Example demonstrating multiple localhost MCP servers with an orchestrator agent.

This example shows:
- Multiple MCP servers, each with multiple tools
- Modular architecture with separate manager and factory components
- Custom tool-agents using Runner.run_streamed for advanced configuration
- Orchestrator agent that coordinates specialized agents
- Streaming responses at all levels

Use case: Data processing pipeline with math and text operations

Prerequisites:
1. Start math_server: uv run python examples/mcp/servers/math_server.py
2. Start text_server: uv run python examples/mcp/servers/text_server.py
3. Start data_server: uv run python examples/mcp/servers/data_server.py
"""

import asyncio
from contextlib import suppress

from openai.types.responses import ResponseTextDeltaEvent

from agents import Runner

# Add project root to path for imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.mcp.agent_factory import AgentFactory
from examples.mcp.mcp_client_manager import StreamableHttpClientManager


async def main():
    """
    Main example showing how to use multiple MCP servers with custom tool-agents.

    Assumes MCP servers are already running on ports 8001, 8002, 8003.
    """

    # Initialize client manager
    client_manager = StreamableHttpClientManager()

    try:
        # Connect to multiple MCP servers
        print("Connecting to MCP servers...")

        math_server = await client_manager.start_client(
            name="math_server",
            url="http://localhost:8001/mcp",
            timeout=10.0,
        )

        text_server = await client_manager.start_client(
            name="text_server",
            url="http://localhost:8002/mcp",
            timeout=10.0,
        )

        data_server = await client_manager.start_client(
            name="data_server",
            url="http://localhost:8003/mcp",
            timeout=10.0,
        )

        print("✓ Connected to all MCP servers\n")

        # Get tools from each server for display
        math_tools = await math_server.list_tools()
        text_tools = await text_server.list_tools()
        data_tools = await data_server.list_tools()

        print(f"Math server tools: {[t.name for t in math_tools]}")
        print(f"Text server tools: {[t.name for t in text_tools]}")
        print(f"Data server tools: {[t.name for t in data_tools]}\n")

        # Create agent factory with MCP servers
        factory = AgentFactory(
            math_server=math_server,
            text_server=text_server,
            data_server=data_server,
        )

        # Create orchestrator with default agents
        orchestrator = factory.create_orchestrator()

        # Example 1: Math operations
        print("=" * 60)
        print("Example 1: Math Operations")
        print("=" * 60)
        stream1 = Runner.run_streamed(
            orchestrator,
            "Calculate (5 + 3) * 2 and then raise it to the power of 2",
            max_turns=15,
        )
        final_result1 = ""
        print("Orchestrator: ", end="", flush=True)
        async for event in stream1.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                print(event.data.delta, end="", flush=True)
                final_result1 += event.data.delta
        print(f"\n\nFinal Result: {final_result1}\n")

        # # Example 2: Text operations
        # print("=" * 60)
        # print("Example 2: Text Operations")
        # print("=" * 60)
        # stream2 = Runner.run_streamed(
        #     orchestrator,
        #     "Take the text 'hello world' and reverse it, then count the words, then convert to uppercase",
        #     max_turns=15,
        # )
        # final_result2 = ""
        # print("Orchestrator: ", end="", flush=True)
        # async for event in stream2.stream_events():
        #     if event.type == "raw_response_event" and isinstance(
        #         event.data, ResponseTextDeltaEvent
        #     ):
        #         print(event.data.delta, end="", flush=True)
        #         final_result2 += event.data.delta
        # print(f"\n\nFinal Result: {final_result2}\n")

        # # Example 3: Data operations
        # print("=" * 60)
        # print("Example 3: Data Operations")
        # print("=" * 60)
        # stream3 = Runner.run_streamed(
        #     orchestrator,
        #     "I have a list of numbers: [5, 2, 8, 1, 9, 3]. Filter those greater than 3, then sort them, then calculate their sum",
        #     max_turns=15,
        # )
        # final_result3 = ""
        # print("Orchestrator: ", end="", flush=True)
        # async for event in stream3.stream_events():
        #     if event.type == "raw_response_event" and isinstance(
        #         event.data, ResponseTextDeltaEvent
        #     ):
        #         print(event.data.delta, end="", flush=True)
        #         final_result3 += event.data.delta
        # print(f"\n\nFinal Result: {final_result3}\n")

        # # Example 4: Combined operations
        # print("=" * 60)
        # print("Example 4: Combined Operations")
        # print("=" * 60)
        # stream4 = Runner.run_streamed(
        #     orchestrator,
        #     "Reverse the text 'Data Science', count its words, then multiply that count by 10",
        #     max_turns=15,
        # )
        # final_result4 = ""
        # print("Orchestrator: ", end="", flush=True)
        # async for event in stream4.stream_events():
        #     if event.type == "raw_response_event" and isinstance(
        #         event.data, ResponseTextDeltaEvent
        #     ):
        #         print(event.data.delta, end="", flush=True)
        #         final_result4 += event.data.delta
        # print(f"\n\nFinal Result: {final_result4}\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up all connections with shielded cleanup
        print("\n\nShutting down...")
        # Ensure cleanup completes even if the main task is being cancelled
        with suppress(asyncio.CancelledError):
            await asyncio.shield(client_manager.stop_all())
        print("✓ All client connections closed")


if __name__ == "__main__":
    import logging

    # Suppress the "Error cleaning up server" messages from the MCP SDK
    # These are logged but harmless - they occur during normal shutdown
    # due to anyio cancel scope task migration
    logging.getLogger("agents.mcp.server").setLevel(logging.CRITICAL)

    # Use asyncio.run with shielded cleanup to avoid cancel scope errors
    # The shielded cleanup ensures proper MCP client teardown
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
