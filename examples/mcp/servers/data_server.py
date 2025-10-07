"""
Data MCP Server - provides data processing operations.

Tools:
- filter_list: Filter a list based on a condition
- sort_list: Sort a list
- aggregate: Aggregate a list (sum, average, min, max)

Run with: uv run examples/mcp/servers/data_server.py
"""

import os
from typing import Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Create FastMCP server
mcp = FastMCP("Data Operations Server",port=8003)


@mcp.tool()
def filter_list(numbers: list[float], threshold: float, comparison: str = "greater") -> list[float]:
    """Filter a list of numbers based on a threshold.

    Args:
        numbers: List of numbers to filter
        threshold: Threshold value
        comparison: Comparison type ('greater', 'less', 'equal')

    Returns:
        Filtered list
    """
    if comparison == "greater":
        return [n for n in numbers if n > threshold]
    elif comparison == "less":
        return [n for n in numbers if n < threshold]
    elif comparison == "equal":
        return [n for n in numbers if n == threshold]
    else:
        return numbers


@mcp.tool()
def sort_list(numbers: list[float], reverse: bool = False) -> list[float]:
    """Sort a list of numbers.

    Args:
        numbers: List of numbers to sort
        reverse: Sort in descending order if True

    Returns:
        Sorted list
    """
    return sorted(numbers, reverse=reverse)


@mcp.tool()
def aggregate(
    numbers: list[float], operation: Literal["sum", "average", "min", "max"] = "sum"
) -> float:
    """Aggregate a list of numbers using various operations.

    Args:
        numbers: List of numbers to aggregate
        operation: Type of aggregation ('sum', 'average', 'min', 'max')

    Returns:
        Aggregated result
    """
    if not numbers:
        return 0.0

    if operation == "sum":
        return sum(numbers)
    elif operation == "average":
        return sum(numbers) / len(numbers)
    elif operation == "min":
        return min(numbers)
    elif operation == "max":
        return max(numbers)
    else:
        return sum(numbers)


if __name__ == "__main__":
    # Run the server
    # To specify a port, use: uvicorn data_server:mcp.app --port 8003
    mcp.run(transport="streamable-http")
