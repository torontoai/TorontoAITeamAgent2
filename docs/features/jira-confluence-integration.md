# Jira and Confluence Integration

## Overview

The Jira and Confluence Integration module enables seamless collaboration between AI agents and human team members through Atlassian's project management and knowledge sharing platforms. This integration allows the TORONTO AI TEAM AGENT system to synchronize tasks, issues, and documentation with Jira and Confluence, creating a unified workflow for mixed teams.

## Key Features

- **Bidirectional Synchronization**: Keep data in sync between the AI system and Jira/Confluence
- **Real-time Updates**: Webhook handlers for immediate notification of changes
- **Entity Mapping**: Comprehensive mapping between internal entities and Jira/Confluence objects
- **Authentication Management**: Secure OAuth and API token handling
- **Rate Limiting**: Smart handling of API rate limits with exponential backoff
- **Error Recovery**: Robust error handling and recovery mechanisms
- **MCP/A2A Integration**: Seamless connection with existing agent communication frameworks

## Architecture

The Jira/Confluence integration consists of several components:

1. **Configuration Module**: Manages connection settings and credentials
2. **Authentication Module**: Handles OAuth and API token authentication
3. **Data Models**: Defines entity types and synchronization records
4. **API Clients**: Provides interfaces to Jira and Confluence APIs
5. **Webhook Handlers**: Processes incoming events from Jira and Confluence
6. **Synchronization Manager**: Coordinates entity synchronization with database persistence
7. **MCP/A2A Integration**: Connects with agent communication frameworks

## Usage

### Basic Setup

```python
from app.integration.config import JiraConfig, ConfluenceConfig
from app.integration.jira_client import JiraApiClient
from app.integration.confluence_client import ConfluenceApiClient
from app.integration.sync_manager import SynchronizationManager

# Configure Jira and Confluence
jira_config = JiraConfig(
    base_url="https://your-instance.atlassian.net",
    api_token="your_api_token",
    username="your_email@example.com"
)

confluence_config = ConfluenceConfig(
    base_url="https://your-instance.atlassian.net",
    api_token="your_api_token",
    username="your_email@example.com"
)

# Create API clients
jira_client = JiraApiClient(jira_config)
confluence_client = ConfluenceApiClient(confluence_config)

# Initialize synchronization manager
sync_manager = SynchronizationManager(
    jira_client=jira_client,
    confluence_client=confluence_client,
    db_path="/path/to/sync_database.db"
)

# Start synchronization
sync_manager.start()
```

### Integration with MCP/A2A Frameworks

```python
from app.integration.mcp_a2a_integration import JiraConfluenceAgent
from app.collaboration.mcp_framework import MCPMessage, MCPMessageType

# Create Jira/Confluence agent
jira_confluence_agent = JiraConfluenceAgent(sync_manager)

# Start the agent
jira_confluence_agent.start()

# Send a task to create a Jira issue
jira_confluence_agent.send_mcp_message(
    MCPMessage(
        message_type=MCPMessageType.TASK_ASSIGNMENT,
        sender="project_manager_agent",
        recipient="jira_confluence_agent",
        content={
            "task_id": "task-123",
            "task_data": {
                "type": "create_jira_issue",
                "project_key": "PROJ",
                "summary": "Implement new feature",
                "description": "Detailed description of the feature",
                "issue_type": "Task",
                "priority": "Medium",
                "assignee": "john.doe@example.com"
            }
        }
    )
)
```

## Entity Types

The integration supports the following entity types:

### Jira Entities

- **Projects**: Project settings and metadata
- **Issues**: Tasks, bugs, stories, and other issue types
- **Comments**: Comments on issues
- **Attachments**: Files attached to issues
- **Worklogs**: Time tracking records

### Confluence Entities

- **Spaces**: Content organization spaces
- **Pages**: Documentation pages
- **Comments**: Comments on pages
- **Attachments**: Files attached to pages

## Synchronization Process

The synchronization process follows these steps:

1. **Entity Creation/Update**: Entities are created or updated in either system
2. **Queue for Sync**: Entities are queued for synchronization with priority
3. **Conversion**: Entities are converted between internal and external formats
4. **API Call**: The appropriate API call is made to create/update the entity
5. **Status Update**: Synchronization status is updated in the database
6. **Notification**: Relevant agents are notified of the synchronization result

## Webhook Integration

The system supports webhooks for real-time updates:

1. **Webhook Registration**: Registers webhooks with Jira and Confluence
2. **Event Processing**: Processes incoming webhook events
3. **Entity Synchronization**: Triggers synchronization based on events
4. **Notification**: Notifies relevant agents of changes

## Error Handling

The system includes comprehensive error handling for:

- Authentication failures
- Rate limiting
- Network issues
- Data conversion errors
- Synchronization conflicts

All errors are logged with appropriate context for troubleshooting.

## Configuration Options

### Jira Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `base_url` | Jira instance URL | Required |
| `api_token` | Jira API token | Required |
| `username` | Jira username (email) | Required |
| `max_retries` | Maximum number of retries for failed requests | 3 |
| `timeout` | Request timeout in seconds | 30 |

### Confluence Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `base_url` | Confluence instance URL | Required |
| `api_token` | Confluence API token | Required |
| `username` | Confluence username (email) | Required |
| `max_retries` | Maximum number of retries for failed requests | 3 |
| `timeout` | Request timeout in seconds | 30 |

## Limitations

- Requires valid Jira and Confluence instances with API access
- API access is subject to Atlassian's rate limits and terms of service
- Some advanced Jira/Confluence features may not be supported
- Complex workflows may require additional configuration

## Future Enhancements

- Support for additional Jira features (Agile boards, sprints, etc.)
- Enhanced Confluence integration (templates, macros, etc.)
- Improved conflict resolution for bidirectional synchronization
- Advanced permission handling and user management
- Integration with additional Atlassian products (Bitbucket, Bamboo, etc.)
