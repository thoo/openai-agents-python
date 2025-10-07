"""
MCP Multi-Server Example Package

This package provides a modular architecture for building multi-agent systems
with MCP (Model Context Protocol) servers.

Components:
- mcp_client_manager: Manages MCP server connections with robust cleanup
- agent_factory: Creates and configures specialized agents
- multiple_mcp_servers_example: Main example demonstrating the architecture
"""

from examples.mcp.agent_factory import AgentConfig, AgentFactory
from examples.mcp.mcp_client_manager import StreamableHttpClientManager

__all__ = [
    "StreamableHttpClientManager",
    "AgentFactory",
    "AgentConfig",
]
