# Multi-Agent MCP System

A scalable, modular architecture for building multi-agent systems with MCP (Model Context Protocol) servers.

## Quick Start

```bash
# 1. Start MCP servers (in separate terminals)
uv run python examples/mcp/servers/math_server.py
uv run python examples/mcp/servers/text_server.py
uv run python examples/mcp/servers/data_server.py

# 2. Run the main example
uv run --env-file .env python examples/mcp/multiple_mcp_servers_example.py
```

## Architecture

The system is built with three core components:

### 1. **MCP Client Manager** (`mcp_client_manager.py`)
Manages MCP server connections with robust cleanup.

```python
from examples.mcp import StreamableHttpClientManager

manager = StreamableHttpClientManager()
server = await manager.start_client("math", "http://localhost:8001/mcp")
await manager.stop_all()  # Automatic cleanup
```

### 2. **Agent Factory** (`agent_factory.py`)
Creates and configures specialized agents.

```python
from examples.mcp import AgentFactory

factory = AgentFactory(
    math_server=math_server,
    text_server=text_server
)

# Create individual agents
math_agent = factory.create_math_agent()

# Or create an orchestrator
orchestrator = factory.create_orchestrator()
```

### 3. **Examples**
- `multiple_mcp_servers_example.py` - Complete demo
- `adding_agents_example.py` - How to add new agents

## Key Features

✅ **Scalable** - Easily add 10-100+ agents
✅ **Modular** - Clean separation of concerns
✅ **Robust** - Double-shielded cleanup prevents errors
✅ **Streaming** - Real-time response streaming
✅ **Reusable** - Share MCP connections across agents

## Adding New Agents

```python
from examples.mcp import AgentConfig

# Define new agent
config = AgentConfig(
    name="Code Review Agent",
    instructions="You are a code review specialist...",
    max_turns=15,
    mcp_servers=[server]
)

# Add to factory
factory.add_agent_config("code_review", config)

# Use it
agent = factory.create_agent("code_review")
```

## File Structure

```
examples/mcp/
├── README.md                       # This file
├── ARCHITECTURE.md                 # Detailed architecture docs
├── mcp_client_manager.py           # Connection management
├── agent_factory.py                # Agent creation
├── multiple_mcp_servers_example.py # Main demo
├── adding_agents_example.py        # Scaling example
└── servers/                        # MCP server implementations
    ├── math_server.py
    ├── text_server.py
    └── data_server.py
```

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete architecture guide
- **[servers/README.md](servers/README.md)** - Server setup and usage

## Common Use Cases

### Use Case 1: Multi-Domain Assistant

```python
# Create domain-specific agents
finance_agent = factory.create_agent("finance")
legal_agent = factory.create_agent("legal")
hr_agent = factory.create_agent("hr")

# Let orchestrator route to the right agent
orchestrator = factory.create_orchestrator(
    tool_agents=[
        (finance_agent, "finance_help", "Financial advice"),
        (legal_agent, "legal_help", "Legal guidance"),
        (hr_agent, "hr_help", "HR support"),
    ]
)

result = await Runner.run(orchestrator, user_query)
```

### Use Case 2: Processing Pipeline

```python
# Chain specialized agents
data_cleaned = await Runner.run(data_agent, f"Clean: {raw_data}")
data_analyzed = await Runner.run(analysis_agent, f"Analyze: {data_cleaned.final_output}")
report = await Runner.run(report_agent, f"Report on: {data_analyzed.final_output}")
```

### Use Case 3: Agent Pool

```python
# Create pool of similar agents for load distribution
agents = [factory.create_agent("analyzer") for _ in range(10)]

# Round-robin or random selection
agent = agents[request_id % len(agents)]
result = await Runner.run(agent, task)
```

## Troubleshooting

### "Error cleaning up server" messages

These are harmless and suppressed by the architecture. Add this to your main:

```python
import logging
logging.getLogger("agents.mcp.server").setLevel(logging.CRITICAL)
```

### Connection timeouts

Increase timeout values:

```python
server = await manager.start_client(
    "my-server", url,
    timeout=30.0,
    sse_read_timeout=600.0
)
```

### Too many agents

Reuse MCP servers across agents - one server can serve many agents.

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) for scaling patterns
2. Try [adding_agents_example.py](adding_agents_example.py) to see how to add agents
3. Build your own custom agents using `AgentConfig`
4. Create hierarchical orchestrators for complex workflows

## Contributing

To add a new agent type:
1. Define an `AgentConfig` in `agent_factory.py`
2. Add a convenience method (optional)
3. Update this README with your use case

Happy building! 🚀
