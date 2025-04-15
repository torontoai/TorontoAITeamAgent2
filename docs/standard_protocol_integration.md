# Standard Protocol Integration

This document provides an overview of the integration of Google's Agent-to-Agent (A2A) protocol and Anthropic's Model Context Protocol (MCP) with the TORONTO AI TEAM AGENT system.

## Overview

The TORONTO AI TEAM AGENT now supports two industry-standard protocols for agent interoperability:

1. **Google's Agent-to-Agent (A2A) Protocol**: Enables communication between independent AI agents across different frameworks and vendors.
2. **Anthropic's Model Context Protocol (MCP)**: Standardizes how applications provide context to LLMs and how LLMs access external tools and data sources.

These integrations allow the TORONTO AI TEAM AGENT to:

- Connect to external A2A-compliant agents and servers
- Expose its capabilities as A2A-compliant endpoints
- Connect to external MCP servers to utilize their tools
- Expose its tools as MCP-compliant endpoints
- Participate in multi-agent ecosystems using industry standards

## Google A2A Protocol Integration

### Components

#### A2A Client Adapter

The A2A Client Adapter allows the TORONTO AI TEAM AGENT to connect to external A2A-compliant agents and servers.

```python
from app.collaboration.google_a2a_adapter import GoogleA2AClientAdapter

# Initialize the client adapter
client_config = {
    "default_timeout": 30,
    "max_retries": 3,
    "streaming_buffer_size": 1024
}
client = GoogleA2AClientAdapter(client_config)
await client.initialize()

# Connect to an A2A server
server_url = "https://example.com/a2a"
connected = await client.connect_to_server(server_url)

# Discover agent capabilities
capabilities = await client.discover_agent_capabilities(server_url)

# Send a task
message = {
    "parts": [
        {
            "text": "Hello, this is a test message."
        }
    ]
}
response = await client.send_task(server_url, message)

# Stream task updates
async for update in client.subscribe_to_task(server_url, message):
    print(f"Update: {update['type']}")
```

#### A2A Server Adapter

The A2A Server Adapter exposes the TORONTO AI TEAM AGENT's capabilities as A2A-compliant endpoints.

```python
from app.collaboration.google_a2a_adapter import GoogleA2AServerAdapter

# Initialize the server adapter
server_config = {
    "expose_agent_card": True,
    "supported_capabilities": {
        "streaming": True,
        "pushNotifications": False,
        "stateTransitionHistory": True
    }
}
server = GoogleA2AServerAdapter(server_config, agent_manager)
await server.initialize()

# Generate agent card
agent_card = server.generate_agent_card()

# Handle task requests
response = await server.handle_task_send(request)
```

#### Message Translator

The Message Translator converts between the TORONTO AI TEAM AGENT's internal message format and Google's A2A message format.

```python
from app.collaboration.google_a2a_adapter import GoogleA2AMessageTranslator

# Convert internal message to A2A format
internal_message = {
    "role": "user",
    "content": "Hello, world!",
    "attachments": []
}
a2a_message = GoogleA2AMessageTranslator.internal_to_a2a(internal_message)

# Convert A2A message to internal format
internal_message = GoogleA2AMessageTranslator.a2a_to_internal(a2a_message)
```

### A2A Protocol Features

- **Agent Discovery**: Discover agent capabilities through Agent Cards
- **Task Management**: Send, monitor, and cancel tasks
- **Streaming**: Receive real-time updates on task progress
- **Push Notifications**: Receive proactive updates from agents
- **Secure Communication**: Authenticate and securely communicate with agents

## Anthropic MCP Integration

### Components

#### MCP Client Adapter

The MCP Client Adapter allows the TORONTO AI TEAM AGENT to connect to external MCP servers and utilize their tools.

```python
from app.collaboration.anthropic_mcp_adapter import AnthropicMCPClientAdapter

# Initialize the client adapter
client_config = {
    "default_timeout": 30,
    "max_retries": 3
}
client = AnthropicMCPClientAdapter(client_config)
await client.initialize()

# Connect to an MCP server
server_url = "https://example.com/mcp"
connected = await client.connect_to_server(server_url)

# Discover tools
tools = await client.discover_tools(server_url)

# Invoke a tool
params = {
    "operation": "read",
    "path": "/test/example.txt"
}
result = await client.invoke_tool(server_url, "file_system", params)

# Stream tool invocation
async for update in client.stream_tool_invocation(server_url, "file_system", params):
    print(f"Update: {update['status']}")
```

#### MCP Server Adapter

The MCP Server Adapter exposes the TORONTO AI TEAM AGENT's tools as MCP-compliant endpoints.

```python
from app.collaboration.anthropic_mcp_adapter import AnthropicMCPServerAdapter

# Initialize the server adapter
server_config = {
    "expose_tool_schema": True,
    "supported_workflow_patterns": [
        "augmented_llm",
        "router",
        "orchestrator_workers"
    ]
}
server = AnthropicMCPServerAdapter(server_config, tool_manager)
await server.initialize()

# Generate tool schema
schema = server.generate_tool_schema()

# Handle tool discovery
response = await server.handle_tool_discovery(request)

# Handle tool invocation
response = await server.handle_tool_invocation(request)
```

#### Tool Mapper

The Tool Mapper converts between the TORONTO AI TEAM AGENT's internal tool format and Anthropic's MCP tool format.

```python
from app.collaboration.anthropic_mcp_adapter import AnthropicMCPToolMapper

# Convert internal tool to MCP format
internal_tool = {
    "name": "calculator",
    "description": "Perform calculations",
    "parameters": {
        "expression": {
            "type": "string",
            "description": "The expression to calculate",
            "required": True
        }
    }
}
mcp_tool = AnthropicMCPToolMapper.internal_to_mcp(internal_tool)

# Convert MCP tool to internal format
internal_tool = AnthropicMCPToolMapper.mcp_to_internal(mcp_tool)
```

### MCP Features

- **Tool Discovery**: Discover available tools from MCP servers
- **Tool Invocation**: Invoke tools with parameters
- **Streaming**: Receive real-time updates on tool invocation progress
- **Session Management**: Maintain context across multiple tool invocations
- **Workflow Patterns**: Support for various agent workflow patterns

## Configuration

The protocol adapters can be configured through the system configuration:

```yaml
protocol_adapters:
  google_a2a:
    enabled: true
    client:
      default_timeout: 30
      max_retries: 3
      streaming_buffer_size: 1024
    server:
      expose_agent_card: true
      supported_capabilities:
        streaming: true
        pushNotifications: false
        stateTransitionHistory: true
      
  anthropic_mcp:
    enabled: true
    client:
      default_timeout: 30
      max_retries: 3
    server:
      expose_tool_schema: true
      supported_workflow_patterns:
        - augmented_llm
        - router
        - orchestrator_workers
```

## Testing

Comprehensive tests are available to verify the functionality of the protocol adapters:

- **Unit Tests**: Test individual components of the adapters
- **Integration Tests**: Test the adapters working together
- **Compatibility Tests**: Test compatibility with external systems

To run the tests:

```bash
# Run unit tests
python -m unittest app.collaboration.tests.protocol_adapters_test

# Run compatibility tests
python app/collaboration/tests/protocol_compatibility_test.py
```

## Security Considerations

When using the protocol adapters, consider the following security aspects:

1. **Authentication**: Configure appropriate authentication for external connections
2. **Authorization**: Control which capabilities and tools are exposed to external systems
3. **Data Privacy**: Be mindful of what information is shared through the protocols
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **Logging**: Enable comprehensive logging for security auditing

## Troubleshooting

Common issues and their solutions:

1. **Connection Failures**:
   - Check network connectivity
   - Verify server URL is correct
   - Ensure authentication credentials are valid

2. **Protocol Errors**:
   - Check message format conforms to protocol specifications
   - Verify required fields are present
   - Ensure data types are correct

3. **Performance Issues**:
   - Adjust timeouts for long-running operations
   - Consider using streaming for real-time updates
   - Implement caching for frequently used capabilities/tools

## Future Enhancements

Planned enhancements for the protocol adapters:

1. **Protocol Version Negotiation**: Support for different protocol versions
2. **Enhanced Security**: Additional authentication and authorization mechanisms
3. **Performance Optimizations**: Improved caching and connection pooling
4. **Monitoring**: Advanced monitoring and metrics collection
5. **Additional Protocols**: Support for other emerging agent interoperability protocols
