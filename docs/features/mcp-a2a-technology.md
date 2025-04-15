# MCP and A2A Technology

This document provides an overview of the Multi-agent Conversational Protocols (MCP) and Agent-to-Agent (A2A) technology implemented in the TORONTO AI TEAM AGENT system, including integration with industry standards from Google and Anthropic.

## Overview

The TORONTO AI TEAM AGENT system implements sophisticated agent communication capabilities through:

1. **Multi-agent Conversational Protocols (MCP)**: Structured conversation protocols with formal state machines for different interaction types.

2. **Agent-to-Agent (A2A) Technology**: Advanced capability discovery, trust management, and secure communication between agents.

3. **Industry Standard Integration**: Support for Google's A2A protocol and Anthropic's MCP, enabling interoperability with external systems.

## MCP Framework

The MCP framework provides structured conversation protocols for agent interactions:

### Protocol Types

The system supports five standard protocol types:

1. **Information Exchange**: For sharing information between agents
2. **Negotiation**: For reaching agreements on tasks or resources
3. **Task Delegation**: For assigning tasks to appropriate agents
4. **Collaborative Problem Solving**: For working together on complex problems
5. **Error Handling**: For managing and recovering from errors

### Key Features

- **State Machines**: Formal state machines for tracking conversation progress
- **Context Management**: Tracking multi-turn interactions with context preservation
- **Protocol Versioning**: Support for multiple protocol versions
- **Extensibility**: Framework for creating custom protocols

## A2A Framework

The A2A framework enables sophisticated agent-to-agent interactions:

### Key Components

1. **Capability Registry**: System for advertising and discovering agent abilities
2. **Trust Management System**: Mechanism for evaluating agent reliability based on interaction history
3. **Security Manager**: Authentication and secure messaging between agents
4. **Semantic Capability Matching**: Intelligent matching of tasks to agent capabilities

### Key Features

- **Dynamic Discovery**: Runtime discovery of agent capabilities
- **Trust Scoring**: Evaluation of agent reliability based on past interactions
- **Secure Communication**: Encrypted and authenticated messaging
- **Capability Semantics**: Understanding of agent capabilities beyond simple matching

## Industry Standard Integration

The system integrates with industry-standard protocols:

### Google A2A Protocol

The Google A2A protocol adapter provides:

- **Message Translation**: Converting between internal and Google A2A message formats
- **Capability Mapping**: Mapping internal capabilities to Google A2A capability format
- **Authentication**: Supporting Google A2A authentication mechanisms
- **External Connectivity**: Connecting to external Google A2A-compliant agents

### Anthropic MCP

The Anthropic MCP adapter provides:

- **Tool Mapping**: Mapping internal tools to Anthropic MCP tool format
- **Context Handling**: Managing conversation context according to Anthropic MCP
- **Response Formatting**: Formatting responses according to Anthropic MCP specifications
- **External Connectivity**: Connecting to external Anthropic MCP-compliant systems

## Usage

### Basic MCP Usage

```python
from app.collaboration.mcp_framework import ConversationManager, ProtocolType

# Create a conversation manager
conversation_manager = ConversationManager()

# Start a new conversation with a specific protocol
conversation_id = conversation_manager.start_conversation(
    initiator_id="project_manager",
    participants=["product_manager", "developer"],
    protocol_type=ProtocolType.TASK_DELEGATION
)

# Send a message in the conversation
conversation_manager.send_message(
    conversation_id=conversation_id,
    sender_id="project_manager",
    content="Can you implement the login feature?",
    metadata={"priority": "high"}
)

# Get conversation state
state = conversation_manager.get_conversation_state(conversation_id)
```

### Basic A2A Usage

```python
from app.collaboration.a2a_framework import CapabilityRegistry, TrustManager

# Register agent capabilities
capability_registry = CapabilityRegistry()
capability_registry.register_capability(
    agent_id="developer",
    capability="code_implementation",
    parameters={"languages": ["python", "javascript"]}
)

# Find agents with specific capabilities
agents = capability_registry.find_agents_with_capability(
    capability="code_implementation",
    parameters={"languages": ["python"]}
)

# Evaluate agent trust
trust_manager = TrustManager()
trust_score = trust_manager.get_trust_score("developer")
```

### Using Google A2A Protocol

```python
from app.collaboration.google_a2a_adapter import GoogleA2AClient

# Create a Google A2A client
a2a_client = GoogleA2AClient(
    agent_id="toronto_ai_agent",
    endpoint="https://a2a-endpoint.example.com"
)

# Send a message to an external A2A agent
response = a2a_client.send_message(
    recipient_id="external_agent",
    content="Can you provide market research data?",
    capabilities_required=["market_research"]
)
```

### Using Anthropic MCP

```python
from app.collaboration.anthropic_mcp_adapter import AnthropicMCPClient

# Create an Anthropic MCP client
mcp_client = AnthropicMCPClient(
    agent_id="toronto_ai_agent",
    endpoint="https://mcp-endpoint.example.com"
)

# Use an external tool via MCP
result = mcp_client.use_tool(
    tool_name="data_analysis",
    parameters={"dataset": "sales_2025_q1", "analysis_type": "trend"}
)
```

## Integration with Existing System

The MCP and A2A frameworks are integrated with the existing communication system through the `mcp_a2a_integration.py` module:

```python
from app.collaboration.mcp_a2a_integration import IntegratedCommunicationSystem

# Create an integrated communication system
comm_system = IntegratedCommunicationSystem()

# Send a message using the integrated system
comm_system.send_message(
    sender_id="project_manager",
    recipient_id="developer",
    content="Please implement the login feature",
    protocol_type="task_delegation"
)
```

## Testing

The system includes comprehensive tests for all MCP and A2A components:

```bash
# Run MCP and A2A tests
python -m app.collaboration.tests.mcp_a2a_tests

# Run protocol adapter tests
python -m app.collaboration.tests.protocol_adapters_test

# Run protocol compatibility tests
python -m app.collaboration.tests.protocol_compatibility_test
```

## Next Steps

- [Knowledge Integration Framework](./knowledge-integration.md) - For understanding the knowledge integration system
- [Local Deployment Guide](../deployment/local-deployment.md) - For deploying the system locally
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - For resolving common issues
