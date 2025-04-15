# API Integration Configuration Guide

This guide provides detailed instructions for configuring API integrations in the TORONTO AI Team Agent Team AI system. The system supports multiple AI service providers and external tools, allowing for flexible integration with various APIs.

## Supported API Providers

The TORONTO AI Team Agent Team AI system supports the following API providers:

- **OpenAI** - For GPT models (GPT-4, GPT-3.5-Turbo)
- **Anthropic** - For Claude models (Claude 3 Opus, Sonnet, Haiku)
- **DeepSeek** - For DeepSeek Coder and Chat models
- **Google** - For Gemini models (Gemini Pro, Gemini Pro Vision)
- **Cohere** - For Command models
- **HuggingFace** - For open-source models (Mistral, Llama 2)
- **Azure OpenAI** - For Azure-hosted OpenAI models
- **GitHub** - For repository integration
- **Jira** - For project management integration
- **Slack** - For team communication integration
- **Custom** - For custom API integrations

## Configuration File

API configurations are stored in a JSON file located at `~/.toronto-ai-team-agent/api_config.json`. This file contains encrypted API keys and configuration settings for each provider.

Example configuration file structure:
```json
{
  "api_123456789abc": {
    "provider": "openai",
    "api_key": "sk_*************************************abcd",
    "settings": {
      "organization": "org-123456",
      "default_model": "gpt-4"
    },
    "created_at": "2025-04-11T05:30:00.000Z",
    "updated_at": "2025-04-11T05:30:00.000Z",
    "status": "active"
  },
  "api_abcdef123456": {
    "provider": "anthropic",
    "api_key": "sk_*************************************efgh",
    "settings": {
      "default_model": "claude-3-opus-20240229"
    },
    "created_at": "2025-04-11T05:31:00.000Z",
    "updated_at": "2025-04-11T05:31:00.000Z",
    "status": "active"
  }
}
```

## Configuration Methods

### Using the API

You can configure API integrations using the `ApiIntegrationManager` class:

```python
from app.api.integration_manager import ApiIntegrationManager, ApiProvider

# Initialize the manager
manager = ApiIntegrationManager()

# Configure OpenAI
result = manager.configure_api({
    "provider": ApiProvider.OPENAI.value,
    "api_key": "sk-your-openai-api-key",
    "settings": {
        "organization": "your-org-id",
        "default_model": "gpt-4"
    }
})

# Test the connection
test_result = manager.test_api_connection({
    "provider": ApiProvider.OPENAI.value
})

# Get a client
client_result = manager.get_api_client({
    "provider": ApiProvider.OPENAI.value
})
client = client_result["client"]
```

### Using the Configuration Tool

The system includes a command-line configuration tool for managing API integrations:

```bash
# Configure an API
python -m app.tools.config_api --provider openai --key "sk-your-openai-api-key" --setting "organization=your-org-id" --setting "default_model=gpt-4"

# List configurations
python -m app.tools.config_api --list

# Test a connection
python -m app.tools.config_api --test --provider openai

# Delete a configuration
python -m app.tools.config_api --delete --config-id api_123456789abc
```

## Required API Keys

To fully utilize the TORONTO AI Team Agent Team AI system, you will need API keys for the following services:

1. **Primary LLM Provider** (at least one of the following):
   - OpenAI API Key (https://platform.openai.com/api-keys)
   - Anthropic API Key (https://console.anthropic.com/settings/keys)
   - DeepSeek API Key (https://platform.deepseek.com/)
   - Google AI Studio API Key (https://makersuite.google.com/app/apikey)

2. **Code Repository Integration**:
   - GitHub Personal Access Token with repo scope (https://github.com/settings/tokens)

3. **Optional Integrations**:
   - Jira API Token (for project management integration)
   - Slack API Token (for team communication integration)
   - HuggingFace API Token (for using open-source models)

## Configuration Settings

Each provider supports specific settings:

### OpenAI
- `organization` - OpenAI organization ID
- `default_model` - Default model to use (e.g., "gpt-4", "gpt-3.5-turbo")
- `temperature` - Default temperature for completions (0.0-2.0)
- `max_tokens` - Default maximum tokens for completions

### Anthropic
- `default_model` - Default model to use (e.g., "claude-3-opus-20240229")
- `temperature` - Default temperature for completions (0.0-1.0)
- `max_tokens` - Default maximum tokens for completions

### DeepSeek
- `default_model` - Default model to use (e.g., "deepseek-coder", "deepseek-chat")
- `temperature` - Default temperature for completions (0.0-1.0)

### GitHub
- `owner` - Repository owner (username or organization)
- `repo` - Repository name
- `branch` - Default branch

## Troubleshooting

### Connection Issues
If you encounter connection issues, try the following:

1. Verify that your API key is correct and has not expired
2. Check your internet connection
3. Ensure that the API service is available
4. Test the connection using the test_api_connection method
5. Check the error message in the configuration file

### Security Considerations
- API keys are stored with basic encryption in the configuration file
- For production environments, consider using environment variables or a secure key management service
- Regularly rotate your API keys for security

## Adding Custom API Providers

You can add custom API providers by extending the `ApiProvider` enum and implementing the corresponding test and client creation methods in the `ApiIntegrationManager` class.

Example:
```python
# Add to ApiProvider enum
class ApiProvider(Enum):
    # ... existing providers ...
    MY_CUSTOM_API = "my_custom_api"

# Implement test method
def _test_my_custom_api_connection(self, config_data):
    # Implementation
    pass

# Implement client creation method
def _create_my_custom_api_client(self, config_data):
    # Implementation
    pass
```

## API Usage Examples

### Using OpenAI
```python
manager = ApiIntegrationManager()
client_result = manager.get_api_client({"provider": "openai"})
client = client_result["client"]

# Use the client
# In a real implementation, you would use the OpenAI SDK
# This is a simplified example
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, world!"}
    ]
)
```

### Using GitHub
```python
manager = ApiIntegrationManager()
client_result = manager.get_api_client({"provider": "github"})
client = client_result["client"]

# Use the client
# In a real implementation, you would use the GitHub SDK
# This is a simplified example
repo = client.get_repo("owner/repo")
contents = repo.get_contents("README.md")
```

## Next Steps

After configuring your API integrations, you can:

1. Train agent roles using the Agent Training Framework
2. Deploy the TORONTO AI Team Agent Team AI system
3. Start collaborating with the multi-agent team

For more information, see the [Agent Training Framework Guide](agent_training_framework.md) and the [Deployment Guide](deployment_guide.md).
