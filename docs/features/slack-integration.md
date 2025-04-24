# Slack Integration Guide

## Overview

This guide explains how to integrate Slack communication capabilities with the TORONTO AI TEAM AGENT system. The integration enables streamlined communication between agents and humans through Slack channels and direct messages.

## Features

- **Bidirectional Communication**: Send and receive messages between AI agents and Slack users
- **Rich Message Formatting**: Support for text, attachments, blocks, and interactive elements
- **Event-Based Communication**: Process Slack events in real-time
- **Webhook Support**: Handle incoming webhooks for events, commands, and interactive components
- **MCP/A2A Integration**: Seamless connection with existing Multi-agent Communication Protocol (MCP) and Agent-to-Agent (A2A) frameworks
- **Message Synchronization**: Reliable message delivery with retry mechanisms
- **Authentication and Security**: Secure token management and webhook verification

## Setup Requirements

1. **Slack App**: Create a Slack app in the [Slack API Console](https://api.slack.com/apps)
2. **Bot Token**: Generate a bot token with appropriate scopes
3. **Signing Secret**: Obtain the signing secret for webhook verification
4. **Event Subscriptions**: Configure event subscriptions in the Slack API Console
5. **Bot Scopes**: Add the following OAuth scopes to your bot:
   - `channels:history`
   - `channels:read`
   - `chat:write`
   - `files:read`
   - `files:write`
   - `groups:history`
   - `groups:read`
   - `im:history`
   - `im:read`
   - `reactions:read`
   - `reactions:write`
   - `users:read`

## Configuration

### Basic Configuration

Create a `slack_config.json` file with the following structure:

```json
{
  "bot_token": "xoxb-your-bot-token",
  "signing_secret": "your-signing-secret",
  "default_channel": "general",
  "max_retries": 3,
  "retry_delay": 1,
  "timeout": 30,
  "debug_mode": false
}
```

### Environment Variables

Alternatively, you can configure the integration using environment variables:

```bash
export SLACK_BOT_TOKEN="xoxb-your-bot-token"
export SLACK_SIGNING_SECRET="your-signing-secret"
export SLACK_DEFAULT_CHANNEL="general"
export SLACK_MAX_RETRIES=3
export SLACK_RETRY_DELAY=1
export SLACK_TIMEOUT=30
export SLACK_DEBUG_MODE=false
```

## Integration with TORONTO AI TEAM AGENT

### Initialization

```python
from app.integration.slack.config import SlackConfig
from app.integration.slack.client import SlackClient
from app.integration.slack.events import SlackEventHandler
from app.integration.slack.webhooks import SlackWebhookHandler
from app.integration.slack.sync_manager import SlackSyncManager
from app.integration.slack.mcp_a2a_integration import SlackMCPA2AIntegration

# Load configuration
config = SlackConfig.from_file("slack_config.json")
# or
config = SlackConfig.from_env()

# Create client
client = SlackClient(config)

# Create event handler
event_handler = SlackEventHandler(config, client)

# Create synchronization manager
sync_manager = SlackSyncManager(config, client)
sync_manager.start()

# Create webhook handler
webhook_handler = SlackWebhookHandler(config, event_handler, port=3000)
webhook_handler.start()

# Create MCP/A2A integration
mcp_a2a_integration = SlackMCPA2AIntegration(config, client, event_handler, sync_manager)

# Register with MCP/A2A frameworks
from app.orchestration.mcp import MCPManager
from app.orchestration.a2a import A2AManager

mcp_manager = MCPManager()
a2a_manager = A2AManager()

mcp_a2a_integration.register_with_mcp(mcp_manager)
mcp_a2a_integration.register_with_a2a(a2a_manager)
```

### Sending Messages

#### Direct API Usage

```python
from app.integration.slack.models import SlackMessage, SlackAttachment

# Send a simple text message
client.send_text_message(
    channel="general",
    text="Hello from the AI team agent!"
)

# Send a message with attachments
attachment = SlackAttachment(
    fallback="Task completed",
    title="Task Completed",
    text="The requested analysis has been completed.",
    color="#36a64f"
)

client.send_attachment_message(
    channel="general",
    text="Task update:",
    attachments=[attachment]
)
```

#### Using MCP/A2A Framework

```python
# Send a message through MCP
mcp_manager.send_message(
    destination="slack",
    channel="general",
    text="Hello from MCP!",
    attachments=[
        {
            "fallback": "Task update",
            "title": "Task Update",
            "text": "Progress: 75% complete",
            "color": "#36a64f"
        }
    ]
)

# Send a message through A2A
a2a_manager.send_message(
    destination="slack",
    channel="general",
    text="Hello from A2A!",
    thread_ts="1234567890.123456"  # Reply in thread
)
```

### Receiving Messages

Messages from Slack are automatically processed by the event handler and routed to the MCP/A2A frameworks. To handle these messages, implement the appropriate handlers in your MCP/A2A components.

#### Example MCP Handler

```python
class MyMCPHandler:
    def handle_message(self, message):
        if message["source"] == "slack":
            print(f"Received Slack message: {message['text']}")
            
            # Respond to the message
            return {
                "destination": "slack",
                "channel": message["channel"],
                "text": "I received your message!",
                "thread_ts": message.get("thread_ts") or message.get("timestamp")
            }
```

## Webhook Setup

To receive events from Slack, you need to expose your webhook endpoint to the internet and configure it in the Slack API Console.

1. Start the webhook handler on your server
2. Use a service like ngrok to expose your local server: `ngrok http 3000`
3. Configure the Event Subscriptions URL in the Slack API Console: `https://your-ngrok-url/slack/events`
4. Subscribe to the bot events you need (e.g., `message.channels`, `app_mention`)

## Advanced Usage

### Rich Message Formatting

```python
from app.integration.slack.formatter import SlackFormatter
from app.integration.slack.models import SlackTextBlock, SlackDividerBlock, SlackImageBlock

# Create blocks
blocks = [
    SlackFormatter.create_text_block("*Important announcement*"),
    SlackFormatter.create_divider_block(),
    SlackFormatter.create_text_block("We have a new team member joining us today!"),
    SlackFormatter.create_image_block(
        image_url="https://example.com/welcome.png",
        alt_text="Welcome image",
        title="Welcome!"
    )
]

# Send message with blocks
client.send_block_message(
    channel="general",
    text="Important announcement",
    blocks=blocks
)
```

### Interactive Components

```python
from app.integration.slack.models import SlackButtonElement, SlackActionsBlock

# Create buttons
approve_button = SlackFormatter.create_button(
    text="Approve",
    action_id="approve_request",
    value="approve",
    style="primary"
)

reject_button = SlackFormatter.create_button(
    text="Reject",
    action_id="reject_request",
    value="reject",
    style="danger"
)

# Create actions block
actions_block = SlackFormatter.create_actions_block([approve_button, reject_button])

# Add to blocks
blocks.append(actions_block)

# Send message with interactive components
client.send_block_message(
    channel="approvals",
    text="New approval request",
    blocks=blocks
)
```

### File Uploads

```python
# Upload a file
client.upload_file(
    channels="general",
    file_path="/path/to/report.pdf",
    title="Monthly Report",
    filename="monthly_report.pdf"
)

# Upload file content
client.upload_file(
    channels="general",
    content="This is the content of the file",
    filename="notes.txt",
    title="Meeting Notes"
)
```

## Error Handling

The Slack integration includes comprehensive error handling with automatic retries for failed operations. You can customize the retry behavior in the configuration.

```python
# Check message status
message_id = client.send_text_message(
    channel="general",
    text="Hello world!"
)

# Later, check the status
status = sync_manager.get_message_status(message_id)
print(f"Message status: {status['status']}")
```

## Security Considerations

1. **Token Security**: Store your bot token and signing secret securely
2. **Webhook Verification**: Always verify incoming webhook requests
3. **Rate Limiting**: Respect Slack's rate limits
4. **User Data**: Handle user data according to your privacy policy

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Verify your bot token and scopes
2. **Webhook Errors**: Check your webhook URL and signing secret
3. **Rate Limiting**: Implement proper rate limiting and retry mechanisms
4. **Message Delivery Issues**: Check the synchronization manager logs

### Debugging

Enable debug mode in the configuration to get detailed logs:

```json
{
  "debug_mode": true
}
```

## API Reference

For detailed API documentation, refer to the following modules:

- `app.integration.slack.config`: Configuration management
- `app.integration.slack.auth`: Authentication and security
- `app.integration.slack.client`: Slack API client
- `app.integration.slack.models`: Data models
- `app.integration.slack.formatter`: Message formatting
- `app.integration.slack.events`: Event handling
- `app.integration.slack.webhooks`: Webhook processing
- `app.integration.slack.sync_manager`: Message synchronization
- `app.integration.slack.mcp_a2a_integration`: MCP/A2A integration
