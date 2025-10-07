"""
Agent Factory for creating and configuring specialized agents with MCP tools.

This module provides a scalable way to define and create agents that work with
MCP servers. It supports:
- Agent templates/configs for reusability
- Custom tool wrapping with streaming support
- Easy addition of new agent types

Usage:
    factory = AgentFactory(mcp_servers)
    math_agent = factory.create_math_agent()
    orchestrator = factory.create_orchestrator()
"""

from typing import Any, Callable

from openai.types.responses import ResponseTextDeltaEvent

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStreamableHttp


class AgentConfig:
    """Configuration for an agent type."""

    def __init__(
        self,
        name: str,
        instructions: str,
        max_turns: int = 10,
        mcp_servers: list[MCPServerStreamableHttp] | None = None,
        tools: list[Any] | None = None,
    ):
        self.name = name
        self.instructions = instructions
        self.max_turns = max_turns
        self.mcp_servers = mcp_servers or []
        self.tools = tools or []


class AgentFactory:
    """
    Factory for creating specialized agents with MCP tool integration.

    This factory encapsulates agent creation logic and makes it easy to:
    - Define agent templates
    - Create agents with MCP server tools
    - Wrap agents as custom tools with streaming
    - Scale to many agent types
    """

    def __init__(
        self,
        math_server: MCPServerStreamableHttp | None = None,
        text_server: MCPServerStreamableHttp | None = None,
        data_server: MCPServerStreamableHttp | None = None,
    ):
        """
        Initialize the factory with MCP servers.

        Args:
            math_server: MCP server for math operations
            text_server: MCP server for text operations
            data_server: MCP server for data operations
        """
        self.math_server = math_server
        self.text_server = text_server
        self.data_server = data_server

        # Agent configurations
        self._configs = self._setup_configs()

    def _setup_configs(self) -> dict[str, AgentConfig]:
        """Define all agent configurations."""
        return {
            "math": AgentConfig(
                name="Math Agent",
                instructions="""You are a math specialist. Use the available math tools to perform calculations.
                Always show your work step by step.""",
                max_turns=10,
                mcp_servers=[self.math_server] if self.math_server else [],
            ),
            "text": AgentConfig(
                name="Text Agent",
                instructions="""You are a text processing specialist. Use the available text tools to manipulate text.
                Explain what transformations you're applying.""",
                max_turns=8,
                mcp_servers=[self.text_server] if self.text_server else [],
            ),
            "data": AgentConfig(
                name="Data Agent",
                instructions="""You are a data processing specialist. Use the available data tools to process lists and arrays.
                Explain each step of data transformation.""",
                max_turns=8,
                mcp_servers=[self.data_server] if self.data_server else [],
            ),
        }

    def create_agent(self, agent_type: str) -> Agent:
        """
        Create an agent by type.

        Args:
            agent_type: Type of agent to create ("math", "text", "data", etc.)

        Returns:
            Configured Agent instance

        Raises:
            ValueError: If agent_type is unknown
        """
        if agent_type not in self._configs:
            raise ValueError(
                f"Unknown agent type: {agent_type}. Available: {list(self._configs.keys())}"
            )

        config = self._configs[agent_type]
        return Agent(
            name=config.name,
            instructions=config.instructions,
            mcp_servers=config.mcp_servers,
            tools=config.tools,
        )

    def create_math_agent(self) -> Agent:
        """Create a math specialist agent."""
        return self.create_agent("math")

    def create_text_agent(self) -> Agent:
        """Create a text processing agent."""
        return self.create_agent("text")

    def create_data_agent(self) -> Agent:
        """Create a data processing agent."""
        return self.create_agent("data")

    def create_custom_tool(
        self,
        agent: Agent,
        tool_name: str,
        tool_description: str,
        max_turns: int = 10,
        show_streaming: bool = True,
    ) -> Callable:
        """
        Wrap an agent as a custom tool with streaming support.

        Args:
            agent: The agent to wrap
            tool_name: Name for the tool
            tool_description: Description of what the tool does
            max_turns: Maximum turns for agent execution
            show_streaming: Whether to print streaming output

        Returns:
            A function_tool decorated async function
        """

        @function_tool
        async def custom_tool(task: str) -> str:
            f"""
            {tool_description}

            Args:
                task: Description of the task to perform

            Returns:
                Result of the operation
            """
            if show_streaming:
                print(f"  [{agent.name}] Processing: {task}")

            result_stream = Runner.run_streamed(
                agent,
                input=task,
                max_turns=max_turns,
            )

            # Stream and collect output
            final_output = ""
            if show_streaming:
                print(f"  [{agent.name}] Result: ", end="", flush=True)

            async for event in result_stream.stream_events():
                if event.type == "raw_response_event" and isinstance(
                    event.data, ResponseTextDeltaEvent
                ):
                    if show_streaming:
                        print(event.data.delta, end="", flush=True)
                    final_output += event.data.delta

            if show_streaming:
                print()  # New line after streaming

            return final_output

        # Set the function name for better debugging
        custom_tool.__name__ = tool_name
        return custom_tool

    def create_orchestrator(
        self,
        tool_agents: list[tuple[Agent, str, str]] | None = None,
        custom_instructions: str | None = None,
    ) -> Agent:
        """
        Create an orchestrator agent that coordinates multiple specialized agents.

        Args:
            tool_agents: List of (agent, tool_name, description) tuples.
                        If None, uses default math/text/data agents.
            custom_instructions: Custom instructions for the orchestrator.
                               If None, uses default instructions.

        Returns:
            Orchestrator Agent with custom tool-agents
        """
        # Use default agents if none provided
        if tool_agents is None:
            math_agent = self.create_math_agent()
            text_agent = self.create_text_agent()
            data_agent = self.create_data_agent()

            tool_agents = [
                (
                    math_agent,
                    "math_operations",
                    "Perform mathematical operations like addition, multiplication, and exponentiation.",
                ),
                (
                    text_agent,
                    "text_operations",
                    "Perform text operations like reversing, counting words, or converting case.",
                ),
                (
                    data_agent,
                    "data_operations",
                    "Perform data operations like filtering, sorting, or aggregating lists.",
                ),
            ]

        # Create custom tools from agents
        tools = [
            self.create_custom_tool(
                agent,
                tool_name,
                description,
                max_turns=self._configs.get(
                    tool_name.replace("_operations", ""), AgentConfig("", "", 10)
                ).max_turns,
            )
            for agent, tool_name, description in tool_agents
        ]

        # Default orchestrator instructions
        if custom_instructions is None:
            custom_instructions = """You are a data processing orchestrator.
            You coordinate between specialized agents:
            - math_operations: for calculations (add, multiply, power)
            - text_operations: for text manipulation (reverse, count words, uppercase)
            - data_operations: for data processing (filter, sort, aggregate)

            For complex tasks, break them down and delegate to the appropriate specialist agent.
            Combine results when needed to answer the user's question."""

        return Agent(
            name="Data Processing Orchestrator",
            instructions=custom_instructions,
            tools=tools,
        )

    def add_agent_config(self, agent_type: str, config: AgentConfig):
        """
        Add a new agent configuration to the factory.

        Args:
            agent_type: Unique identifier for this agent type
            config: AgentConfig instance defining the agent

        Example:
            config = AgentConfig(
                name="Code Agent",
                instructions="You are a coding assistant...",
                max_turns=15,
                mcp_servers=[code_server]
            )
            factory.add_agent_config("code", config)
        """
        self._configs[agent_type] = config

    def list_agent_types(self) -> list[str]:
        """List all available agent types."""
        return list(self._configs.keys())
