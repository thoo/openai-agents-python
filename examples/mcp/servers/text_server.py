"""
Text MCP Server - provides text manipulation operations.

Tools:
- reverse_text: Reverse a string
- count_words: Count words in a string
- to_uppercase: Convert text to uppercase

Run with: uv run examples/mcp/servers/text_server.py
"""

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Create FastMCP server
mcp = FastMCP("Text Operations Server",port=8002)


@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse a string.

    Args:
        text: Text to reverse

    Returns:
        Reversed text
    """
    return text[::-1]


@mcp.tool()
def count_words(text: str) -> int:
    """Count the number of words in a text.

    Args:
        text: Text to count words in

    Returns:
        Number of words
    """
    return len(text.split())


@mcp.tool()
def to_uppercase(text: str) -> str:
    """Convert text to uppercase.

    Args:
        text: Text to convert

    Returns:
        Text in uppercase
    """
    return text.upper()


if __name__ == "__main__":
    # Run the server
    # To specify a port, use: uvicorn text_server:mcp.app --port 8002
    mcp.run(transport="streamable-http")
