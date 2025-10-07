"""
Example: Adding New Agents to the Factory

This example demonstrates how easy it is to add new agent types
to the AgentFactory for scaling to 10-100+ agents.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.mcp import AgentConfig, AgentFactory, StreamableHttpClientManager


async def main():
    """Demonstrate adding custom agents to the factory."""

    # Set up MCP servers (assuming they're running)
    manager = StreamableHttpClientManager()

    try:
        # Connect to servers
        math_server = await manager.start_client(
            "math", "http://localhost:8001/mcp"
        )
        text_server = await manager.start_client(
            "text", "http://localhost:8002/mcp"
        )

        # Create factory
        factory = AgentFactory(math_server=math_server, text_server=text_server)

        # ============================================================
        # Example 1: Add a single custom agent
        # ============================================================
        print("Example 1: Adding a custom agent\n")

        # Define configuration
        code_review_config = AgentConfig(
            name="Code Review Agent",
            instructions="""You are a code review specialist.
            Analyze code for best practices, bugs, and improvements.
            Provide constructive feedback.""",
            max_turns=15,
            mcp_servers=[text_server],  # Uses text analysis tools
        )

        # Add to factory
        factory.add_agent_config("code_review", code_review_config)

        # Create and use the agent
        code_review_agent = factory.create_agent("code_review")
        print(f"Created: {code_review_agent.name}")
        print(f"Available types: {factory.list_agent_types()}\n")

        # ============================================================
        # Example 2: Add multiple agents programmatically
        # ============================================================
        print("Example 2: Adding multiple agents programmatically\n")

        # Define agent types
        agent_definitions = [
            {
                "type": "calculator",
                "name": "Calculator Agent",
                "instructions": "Perform complex calculations using math tools",
                "server": math_server,
                "max_turns": 8,
            },
            {
                "type": "summarizer",
                "name": "Summarizer Agent",
                "instructions": "Summarize text concisely while preserving key points",
                "server": text_server,
                "max_turns": 10,
            },
            {
                "type": "translator",
                "name": "Translator Agent",
                "instructions": "Translate text between languages",
                "server": text_server,
                "max_turns": 5,
            },
        ]

        # Add all agents to factory
        for defn in agent_definitions:
            config = AgentConfig(
                name=defn["name"],
                instructions=defn["instructions"],
                max_turns=defn["max_turns"],
                mcp_servers=[defn["server"]],
            )
            factory.add_agent_config(defn["type"], config)

        print(f"Total agent types: {len(factory.list_agent_types())}")
        print(f"Available: {factory.list_agent_types()}\n")

        # ============================================================
        # Example 3: Create orchestrator with custom agents
        # ============================================================
        print("Example 3: Custom orchestrator with new agents\n")

        # Create custom agent instances
        calculator = factory.create_agent("calculator")
        summarizer = factory.create_agent("summarizer")
        translator = factory.create_agent("translator")

        # Define tool-agent mappings
        custom_tool_agents = [
            (calculator, "calculate", "Perform mathematical calculations"),
            (summarizer, "summarize", "Summarize text content"),
            (translator, "translate", "Translate text between languages"),
        ]

        # Create orchestrator
        orchestrator = factory.create_orchestrator(
            tool_agents=custom_tool_agents,
            custom_instructions="""You are a multi-purpose assistant.
            You can calculate, summarize, and translate.
            Choose the right tool for each task.""",
        )

        print(f"Created orchestrator with {len(orchestrator.tools)} tools")
        print(f"Tools: {[t.__name__ for t in orchestrator.tools]}\n")

        # ============================================================
        # Example 4: Scaling to many agents
        # ============================================================
        print("Example 4: Scaling to many specialized agents\n")

        # Create 10 domain-specific agents
        domains = [
            "finance",
            "healthcare",
            "education",
            "legal",
            "marketing",
            "hr",
            "sales",
            "engineering",
            "design",
            "research",
        ]

        for domain in domains:
            config = AgentConfig(
                name=f"{domain.capitalize()} Agent",
                instructions=f"You are a {domain} specialist. Use available tools to help with {domain}-related tasks.",
                max_turns=12,
                mcp_servers=[
                    math_server if domain in ["finance", "engineering"] else text_server
                ],
            )
            factory.add_agent_config(domain, config)

        print(f"Total agent types now: {len(factory.list_agent_types())}")
        print(f"Specialized domains: {domains}")
        print("\nYou can now create any agent with:")
        print("  agent = factory.create_agent('domain_name')")

    finally:
        await manager.stop_all()


if __name__ == "__main__":
    import logging

    # Suppress MCP cleanup errors
    logging.getLogger("agents.mcp.server").setLevel(logging.CRITICAL)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
