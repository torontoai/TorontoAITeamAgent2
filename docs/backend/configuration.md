# Backend Configuration Guide

This document provides detailed instructions for configuring the TORONTO AI TEAM AGENT backend system.

## Prerequisites

Before proceeding, ensure you have:
- Completed the [Installation](../getting-started/installation.md) process
- Reviewed the [Prerequisites](../getting-started/prerequisites.md) document
- Basic understanding of the system architecture

## Configuration Files

The backend configuration is managed through several key files:

### Main Configuration File

The primary configuration file is located at `deployment/config.json`:

```bash
# View the current configuration
cat deployment/config.json

# Edit the configuration
nano deployment/config.json
```

This file contains the following sections:

#### System Configuration

```json
"system": {
  "name": "TORONTO AI TEAM AGENT",
  "version": "0.1.0",
  "environment": "development"
}
```

- `name`: System name (should not be changed)
- `version`: System version
- `environment`: Deployment environment (`development`, `testing`, `staging`, or `production`)

#### Agent Configuration

```json
"agents": {
  "project_manager": {
    "id": "pm_agent",
    "role": "project_manager",
    "model": "gpt-4o",
    "enabled": true
  },
  "product_manager": {
    "id": "product_agent",
    "role": "product_manager",
    "model": "gpt-4o",
    "enabled": true
  }
}
```

For each agent:
- `id`: Unique identifier for the agent
- `role`: Agent role (must match a role defined in `app/agent/`)
- `model`: LLM model to use for the agent
- `enabled`: Whether the agent is active

#### Communication Configuration

```json
"communication": {
  "message_timeout": 30,
  "retry_attempts": 3,
  "log_level": "INFO",
  "history_limit": 100
}
```

- `message_timeout`: Timeout in seconds for message delivery
- `retry_attempts`: Number of retry attempts for failed messages
- `log_level`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `history_limit`: Maximum number of messages to keep in history

#### Collaboration Configuration

```json
"collaboration": {
  "session_timeout": 3600,
  "max_participants": 10,
  "default_session_type": "general"
}
```

- `session_timeout`: Session timeout in seconds
- `max_participants`: Maximum number of participants in a collaboration session
- `default_session_type`: Default session type

#### Deployment Configuration

```json
"deployment": {
  "host": "0.0.0.0",
  "port": 8000,
  "debug": true,
  "workers": 1
}
```

- `host`: Host to bind the server to
- `port`: Port to listen on
- `debug`: Whether to enable debug mode
- `workers`: Number of worker processes

### API Keys Configuration

API keys are stored in a separate file for security:

```bash
# Create API keys file if it doesn't exist
mkdir -p config
touch config/api_keys.json

# Edit API keys
nano config/api_keys.json
```

Example API keys configuration:

```json
{
  "openai": {
    "api_key": "YOUR_OPENAI_API_KEY"
  },
  "anthropic": {
    "api_key": "YOUR_ANTHROPIC_API_KEY"
  },
  "pinecone": {
    "api_key": "YOUR_PINECONE_API_KEY",
    "environment": "YOUR_PINECONE_ENVIRONMENT"
  }
}
```

### Vector Database Configuration

Vector database configuration is managed through the training configuration:

```bash
# View current vector database configuration
python -m app.training.cli config --show

# Update vector database configuration
python -m app.training.cli config --vector_db_type chroma --vector_db_path /path/to/db
```

## Environment Variables

The system also supports configuration through environment variables:

```bash
# Set environment variables
export TORONTO_AI_ENV=production
export TORONTO_AI_PORT=9000
export TORONTO_AI_LOG_LEVEL=INFO
export OPENAI_API_KEY=your_api_key_here
```

Environment variables take precedence over configuration files.

## Logging Configuration

Logging is configured in `app/utils/logging_config.py`:

```bash
# View logging configuration
cat app/utils/logging_config.py

# Edit logging configuration
nano app/utils/logging_config.py
```

You can adjust log formats, handlers, and destinations in this file.

## Advanced Configuration

### Scaling Configuration

For production deployments, you can configure scaling parameters:

```bash
# Edit scaling configuration
nano deployment/scaling_config.json
```

Example scaling configuration:

```json
{
  "auto_scaling": {
    "enabled": true,
    "min_instances": 2,
    "max_instances": 10,
    "target_cpu_utilization": 70
  },
  "resources": {
    "cpu_request": "1",
    "cpu_limit": "2",
    "memory_request": "2Gi",
    "memory_limit": "4Gi"
  }
}
```

### Security Configuration

Security settings can be configured in:

```bash
# Edit security configuration
nano deployment/security_config.json
```

Example security configuration:

```json
{
  "authentication": {
    "enabled": true,
    "jwt_secret": "YOUR_JWT_SECRET",
    "token_expiry": 86400
  },
  "cors": {
    "allowed_origins": ["https://your-frontend-domain.com"],
    "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
    "allowed_headers": ["Content-Type", "Authorization"]
  },
  "rate_limiting": {
    "enabled": true,
    "requests_per_minute": 60
  }
}
```

## Configuration Management

For managing configurations across environments:

```bash
# Create a new environment configuration
python -m app.deployment.config_manager create --env production

# Apply an environment configuration
python -m app.deployment.config_manager apply --env production

# Compare configurations
python -m app.deployment.config_manager compare --env1 development --env2 production
```

## Troubleshooting

### Configuration Validation

Validate your configuration:

```bash
# Validate configuration
python -m app.deployment.config_validator
```

### Common Configuration Issues

1. **Missing API Keys**: Ensure all required API keys are set in `config/api_keys.json`.

2. **Port Conflicts**: If the specified port is already in use, change the port in `deployment/config.json`.

3. **Invalid Model Names**: Ensure model names in agent configurations are valid and available.

4. **Permission Issues**: Ensure the application has write permissions to log directories and database paths.

## Next Steps

- [Local Deployment Guide](../deployment/local-deployment.md) - For deploying the system locally
- [Production Deployment Guide](../deployment/production-deployment.md) - For deploying to a production environment
- [Monitoring Guide](./monitoring.md) - For monitoring the backend system
