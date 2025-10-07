"""
Math MCP Server - provides mathematical operations.

Tools:
- add: Add two numbers
- multiply: Multiply two numbers
- power: Raise a number to a power

Run with: uv run examples/mcp/servers/math_server.py
"""

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Create FastMCP server
mcp = FastMCP("Math Operations Server",port=8001)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b
    """
    return a * b


@mcp.tool()
def power(base: float, exponent: float) -> float:
    """Raise a number to a power.

    Args:
        base: Base number
        exponent: Exponent to raise to

    Returns:
        Result of base^exponent
    """
    return base**exponent


if __name__ == "__main__":
    # Run the server
    # To specify a port, use: uvicorn math_server:mcp.app --port 8001
    mcp.run(transport="streamable-http")
