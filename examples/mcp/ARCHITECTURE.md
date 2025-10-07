# Multi-Agent MCP Architecture

This directory contains a scalable, modular architecture for building multi-agent systems with MCP servers.

## Directory Structure

```
examples/mcp/
├── __init__.py                          # Package exports
├── mcp_client_manager.py                # MCP connection management
├── agent_factory.py                     # Agent creation and configuration
├── multiple_mcp_servers_example.py      # Main example
├── ARCHITECTURE.md                      # This file
├── servers/                             # MCP server implementations
│   ├── math_server.py
│   ├── text_server.py
│   ├── data_server.py
│   └── README.md
└── ...other examples...
```

## Core Components

### 1. `mcp_client_manager.py`

**Purpose**: Manages lifecycle of MCP server connections

**Key Features**:
- Connection pooling
- Double-shielded cleanup (anyio + asyncio)
- Concurrent shutdown with timeouts
- Graceful error handling

**Usage**:
```python
from examples.mcp import StreamableHttpClientManager

manager = StreamableHttpClientManager()
server = await manager.start_client("my-server", "http://localhost:8000/mcp")
# ... use server ...
await manager.stop_all()
```

### 2. `agent_factory.py`

**Purpose**: Creates and configures specialized agents

**Key Features**:
- Agent templates/configurations
- Custom tool wrapping with streaming
- Easy addition of new agent types
- Orchestrator creation

**Usage**:
```python
from examples.mcp import AgentFactory

# Create factory with MCP servers
factory = AgentFactory(
    math_server=math_server,
    text_server=text_server,
)

# Create individual agents
math_agent = factory.create_math_agent()
text_agent = factory.create_text_agent()

# Create orchestrator
orchestrator = factory.create_orchestrator()
```

### 3. `multiple_mcp_servers_example.py`

**Purpose**: Demonstrates the complete architecture

**Shows**:
- Multi-server connection setup
- Agent creation via factory
- Streaming orchestration
- Proper cleanup

## Adding New Agent Types

### Step 1: Add Agent Configuration

```python
# In agent_factory.py _setup_configs()
"code": AgentConfig(
    name="Code Agent",
    instructions="You are a coding assistant...",
    max_turns=15,
    mcp_servers=[code_server] if code_server else [],
),
```

### Step 2: Add Convenience Method (Optional)

```python
# In AgentFactory class
def create_code_agent(self) -> Agent:
    """Create a code assistant agent."""
    return self.create_agent("code")
```

### Step 3: Add to Orchestrator

```python
# When creating orchestrator
code_agent = factory.create_code_agent()
tool_agents = [
    (code_agent, "code_operations", "Perform code-related tasks..."),
    # ... other agents
]
orchestrator = factory.create_orchestrator(tool_agents=tool_agents)
```

## Scaling to 100+ Agents

The architecture is designed for scale:

### Dynamic Agent Registration

```python
# Add agents at runtime
from examples.mcp import AgentConfig

for i in range(100):
    config = AgentConfig(
        name=f"Agent {i}",
        instructions=f"You are agent number {i}...",
        max_turns=10,
        mcp_servers=[servers[i % len(servers)]]
    )
    factory.add_agent_config(f"agent_{i}", config)
```

### Agent Groups

```python
# Group related agents
data_agents = [
    factory.create_agent(f"data_agent_{i}")
    for i in range(10)
]

analysis_agents = [
    factory.create_agent(f"analysis_agent_{i}")
    for i in range(10)
]
```

### Hierarchical Orchestration

```python
# Create sub-orchestrators for different domains
data_orchestrator = factory.create_orchestrator(
    tool_agents=[(agent, f"data_op_{i}", "...") for i, agent in enumerate(data_agents)]
)

analysis_orchestrator = factory.create_orchestrator(
    tool_agents=[(agent, f"analysis_op_{i}", "...") for i, agent in enumerate(analysis_agents)]
)

# Top-level orchestrator coordinates sub-orchestrators
main_orchestrator = factory.create_orchestrator(
    tool_agents=[
        (data_orchestrator, "data_operations", "Handle data tasks"),
        (analysis_orchestrator, "analysis_operations", "Handle analysis tasks"),
    ]
)
```

## Best Practices

### 1. Connection Management

- Always use `StreamableHttpClientManager` for multiple servers
- Set appropriate timeouts for your use case
- Use `stop_all()` in a finally block for cleanup

### 2. Agent Organization

- Group related agents by domain
- Use descriptive names and instructions
- Set appropriate `max_turns` per agent type

### 3. Error Handling

- Leverage the built-in shielded cleanup
- Suppress cleanup errors (they're harmless)
- Add custom error handling for business logic

### 4. Performance

- MCP servers can be shared across multiple agents
- Connection pooling is automatic
- Cleanup happens concurrently

## Common Patterns

### Pattern 1: Specialized Agent Pool

```python
# Create a pool of specialized agents
agents = {
    "math": factory.create_math_agent(),
    "text": factory.create_text_agent(),
    "data": factory.create_data_agent(),
}

# Use based on task type
task_type = determine_task_type(user_input)
agent = agents[task_type]
result = await Runner.run(agent, user_input)
```

### Pattern 2: Dynamic Agent Selection

```python
# Let orchestrator choose the right agent
orchestrator = factory.create_orchestrator()
result = await Runner.run(orchestrator, user_input)
# Orchestrator automatically delegates to specialized agents
```

### Pattern 3: Pipeline Processing

```python
# Chain agents for multi-step processing
async def process_pipeline(data):
    # Step 1: Data cleaning
    data_agent = factory.create_data_agent()
    cleaned = await Runner.run(data_agent, f"Clean this data: {data}")

    # Step 2: Analysis
    analysis_agent = factory.create_agent("analysis")
    analyzed = await Runner.run(analysis_agent, f"Analyze: {cleaned.final_output}")

    # Step 3: Reporting
    report_agent = factory.create_agent("report")
    report = await Runner.run(report_agent, f"Create report: {analyzed.final_output}")

    return report.final_output
```

## Troubleshooting

### Issue: Cancel Scope Errors

**Solution**: The architecture includes double-shielded cleanup and logger suppression. Make sure you're using the latest version of the managers.

### Issue: Connection Timeouts

**Solution**: Increase timeout values when creating clients:
```python
server = await manager.start_client(
    "my-server",
    url,
    timeout=30.0,  # Increase from default 5.0
    sse_read_timeout=600.0  # Increase from default 300.0
)
```

### Issue: Too Many Open Connections

**Solution**: Reuse MCP server connections across agents:
```python
# Good: Share one server across many agents
math_server = await manager.start_client("math", url)
for i in range(100):
    agent = AgentConfig(..., mcp_servers=[math_server])

# Bad: Create separate connection per agent
# (Don't do this)
```

## Future Enhancements

Potential additions to the architecture:

1. **Agent Registry**: Central registry for discovering available agents
2. **Load Balancing**: Distribute work across multiple MCP servers
3. **Caching**: Cache agent responses for common queries
4. **Monitoring**: Built-in metrics and tracing
5. **Configuration Files**: YAML/JSON configs for agent definitions
