# Multiple MCP Servers Example

This directory contains MCP server implementations that work with the modular multi-agent architecture.

**📖 For architecture details, see [../ARCHITECTURE.md](../ARCHITECTURE.md)**

## Overview

The example includes:

1. **Three MCP Servers** (each with multiple tools):
   - `math_server.py` - Mathematical operations (add, multiply, power)
   - `text_server.py` - Text manipulation (reverse_text, count_words, to_uppercase)
   - `data_server.py` - Data processing (filter_list, sort_list, aggregate)

2. **Client Application** (`multiple_mcp_servers_example.py`):
   - Uses `StreamableHttpClientManager` to manage multiple server connections
   - Creates specialized agents for each domain (math, text, data)
   - Uses custom tool functions with `Runner.run_streamed()` for advanced configuration
   - Creates an orchestrator agent that coordinates between specialized agents
   - Demonstrates streaming responses and complex multi-step operations

## Setup

1. Create a `.env` file in the project root with your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

## Running the Example

### Quick Start

Run the provided shell script that starts all servers and the client:

```bash
./examples/mcp/servers/run_example.sh
```

Or manually start servers in separate terminals:

If you prefer to run servers manually, open three separate terminals:

**Terminal 1 - Math Server (port 8001):**
```bash
cd examples/mcp/servers
uv run uvicorn math_server:mcp.app --port 8001
```

**Terminal 2 - Text Server (port 8002):**
```bash
cd examples/mcp/servers
uv run uvicorn text_server:mcp.app --port 8002
```

**Terminal 3 - Data Server (port 8003):**
```bash
cd examples/mcp/servers
uv run uvicorn data_server:mcp.app --port 8003
```

**Terminal 4 - Run Client:**
```bash
uv run --env-file .env examples/mcp/multiple_mcp_servers_example.py
```

## What Happens

The client will:
1. Connect to all three MCP servers
2. Collect all available tools from each server
3. Create specialized agents (math, text, data) with their respective tools
4. Create custom tool functions using `Runner.run_streamed()` with advanced configuration (max_turns, etc.)
5. Create an orchestrator agent that uses these custom tool-agents
6. Run several example queries with streaming output
7. Demonstrate complex operations that chain multiple agents together

## Example Queries

The demo includes four examples:

1. **Math Operations**: `(5 + 3) * 2 ^ 2`
2. **Text Operations**: Reverse, count words, uppercase
3. **Data Operations**: Filter, sort, aggregate numbers
4. **Combined**: Mix text and math operations

## Architecture

```
┌────────────────────────────────────────────────────────┐
│              Orchestrator Agent                        │
│         (coordinates specialized agents)               │
└────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Math Agent   │    │Text Agent   │    │Data Agent   │
│(custom tool)│    │(custom tool)│    │(custom tool)│
└─────────────┘    └─────────────┘    └─────────────┘
        │                   │                   │
        │  StreamableHttpClientManager          │
        │                   │                   │
    ┌───▼────┐         ┌───▼────┐         ┌───▼────┐
    │ Math   │         │ Text   │         │ Data   │
    │ Server │         │ Server │         │ Server │
    │ :8001  │         │ :8002  │         │ :8003  │
    └────────┘         └────────┘         └────────┘
```

## Key Concepts

- **StreamableHttpClientManager**: Manages multiple MCP server connections without context managers
- **Specialized Agents**: Each domain (math, text, data) has its own agent with specific tools
- **Custom Tool Functions**: Using `@function_tool` with `Runner.run_streamed()` for advanced configuration:
  - Set `max_turns` per agent
  - Configure `run_config` options
  - Handle streaming responses
  - Add custom logging/monitoring
- **Agent Orchestration**: Top-level agent coordinates between specialized agents
- **Streaming**: Real-time response streaming at both agent and orchestrator levels
