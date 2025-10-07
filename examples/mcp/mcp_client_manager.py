"""
MCP Client Manager for managing multiple Streamable HTTP MCP server connections.

This module provides a robust client manager that handles connection lifecycle
with proper cleanup using double-shielded (anyio + asyncio) teardown to avoid
cancel scope conflicts during shutdown.
"""

import asyncio
from contextlib import suppress

import anyio

from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams


class StreamableHttpClientManager:
    """
    Manages multiple Streamable HTTP MCP server connections without context managers.

    Features:
    - Connection pooling and lifecycle management
    - Double-shielded cleanup (anyio + asyncio) for safe teardown
    - Concurrent cleanup with timeouts
    - Graceful error handling during shutdown

    Usage:
        manager = StreamableHttpClientManager()
        server = await manager.start_client("my-server", "http://localhost:8000/mcp")
        # ... use server ...
        await manager.stop_all()
    """

    def __init__(self):
        self._servers: dict[str, MCPServerStreamableHttp] = {}

    async def start_client(
        self,
        name: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        timeout: float | None = 5.0,
        sse_read_timeout: float | None = 300.0,
        terminate_on_close: bool | None = True,
        cache_tools_list: bool = True,
        **server_kwargs,
    ) -> MCPServerStreamableHttp:
        """
        Start and connect to an MCP server.

        Args:
            name: Unique identifier for this server connection
            url: MCP server URL (e.g., "http://localhost:8000/mcp")
            headers: Optional HTTP headers for authentication
            timeout: Connection timeout in seconds
            sse_read_timeout: Server-Sent Events read timeout in seconds
            terminate_on_close: Send termination signal on close
            cache_tools_list: Cache the tools list after first fetch
            **server_kwargs: Additional arguments for MCPServerStreamableHttp

        Returns:
            Connected MCPServerStreamableHttp instance

        Raises:
            ValueError: If a client with this name already exists
        """
        if name in self._servers:
            raise ValueError(f"Client '{name}' already exists")

        # Build connection parameters using MCPServerStreamableHttpParams
        params = MCPServerStreamableHttpParams(
            url=url,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout,
            terminate_on_close=terminate_on_close,
        )

        # Create and connect server
        server = MCPServerStreamableHttp(
            params=params,
            cache_tools_list=cache_tools_list,
            **server_kwargs,
        )

        try:
            await server.connect()
            self._servers[name] = server
            return server
        except (asyncio.CancelledError, Exception) as e:
            # Failed to connect - cleanup and re-raise
            try:
                await server.cleanup()
            except Exception:
                pass  # Ignore cleanup errors
            raise ConnectionError(f"Failed to connect to MCP server '{name}' at {url}: {e}") from e

    def get(self, name: str) -> MCPServerStreamableHttp:
        """Get a server connection by name."""
        return self._servers[name]

    def list_servers(self) -> list[str]:
        """List all active server connection names."""
        return list(self._servers.keys())

    async def _shielded_cleanup(
        self, server: MCPServerStreamableHttp, *, timeout: float | None
    ):
        """
        Run server.cleanup() with double shielding to prevent cancel scope conflicts.

        Uses both anyio.CancelScope(shield=True) and asyncio.shield() to ensure
        cleanup completes even during event loop teardown.

        Args:
            server: The MCP server to clean up
            timeout: Optional timeout in seconds (None = no timeout)
        """

        async def _inner():
            # AnyIO shield prevents cancel scopes from interrupting cleanup()
            with anyio.CancelScope(shield=True):
                await server.cleanup()

        if timeout is None:
            # Don't allow outer-task cancellation to kill cleanup
            with suppress(asyncio.CancelledError):
                await asyncio.shield(_inner())
        else:
            # Timebox *outside* the shields
            with suppress(asyncio.TimeoutError, asyncio.CancelledError):
                await asyncio.wait_for(asyncio.shield(_inner()), timeout=timeout)

    async def stop_client(
        self, name: str, *, timeout: float = 5.0, suppress_errors: bool = True
    ):
        """
        Stop a specific MCP client connection with shielded cleanup.

        Args:
            name: Name of the client to stop
            timeout: Cleanup timeout in seconds
            suppress_errors: Whether to suppress cleanup errors (default: True)
        """
        server = self._servers.pop(name, None)
        if not server:
            return

        try:
            await self._shielded_cleanup(server, timeout=timeout)
        except Exception:
            if not suppress_errors:
                raise
            # Silently ignore cleanup errors during shutdown

    async def stop_all(self, *, timeout_per_client: float = 5.0):
        """
        Close all connections concurrently with shielded cleanup.

        Args:
            timeout_per_client: Timeout for each client cleanup in seconds
        """
        items = list(self._servers.items())
        self._servers.clear()

        if not items:
            return

        # Clean up all servers concurrently
        tasks = [
            asyncio.create_task(
                self._shielded_cleanup(server, timeout=timeout_per_client)
            )
            for _, server in items
        ]

        # Best-effort: don't explode on cancellation/errors during shutdown
        with suppress(asyncio.CancelledError):
            await asyncio.gather(*tasks, return_exceptions=True)

    def __len__(self) -> int:
        """Return the number of active connections."""
        return len(self._servers)

    def __contains__(self, name: str) -> bool:
        """Check if a server connection exists."""
        return name in self._servers
