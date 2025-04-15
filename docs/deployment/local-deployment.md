# Local Deployment Guide

This guide provides detailed instructions for deploying the TORONTO AI TEAM AGENT system in a local development environment.

## Prerequisites

Before proceeding, ensure you have:
- Completed the [Installation](../getting-started/installation.md) process
- Reviewed the [Prerequisites](../getting-started/prerequisites.md) document
- Configured your API keys as described in the [Quick Start Guide](../getting-started/quick-start.md)

## Backend Deployment

### Configure the Deployment

Review and update the deployment configuration:

```bash
# Edit the deployment configuration file
nano ~/toronto-ai-team-agent/deployment/config.json
```

For local development, use the following configuration:

```json
{
  "system": {
    "name": "TORONTO AI TEAM AGENT",
    "version": "0.1.0",
    "environment": "development"
  },
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
    },
    "developer": {
      "id": "dev_agent",
      "role": "developer",
      "model": "gpt-4o",
      "enabled": true
    },
    "system_architect": {
      "id": "arch_agent",
      "role": "system_architect",
      "model": "gpt-4o",
      "enabled": true
    },
    "qa_testing_specialist": {
      "id": "qa_agent",
      "role": "qa_testing_specialist",
      "model": "gpt-4o",
      "enabled": true
    }
  },
  "communication": {
    "message_timeout": 30,
    "retry_attempts": 3,
    "log_level": "DEBUG",
    "history_limit": 100
  },
  "collaboration": {
    "session_timeout": 3600,
    "max_participants": 10,
    "default_session_type": "general"
  },
  "deployment": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": true,
    "workers": 1
  },
  "api_config_path": "../config/api_keys.json"
}
```

### Deploy the Backend

```bash
# Navigate to the deployment directory
cd ~/toronto-ai-team-agent/deployment

# Activate the virtual environment if not already activated
source ../venv/bin/activate

# Run the deployment script
python deploy.py
```

This will:
1. Initialize all agent instances
2. Set up communication channels
3. Run basic tests to verify functionality
4. Start the backend server on port 8000

Keep this terminal window open as it runs the backend server.

## Frontend Deployment

### Configure the Frontend

Create a `.env` file in the frontend directory:

```bash
cd ~/toronto-ai-team-agent/frontend
touch .env
```

Add the following content to the `.env` file:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

Alternatively, you can configure the proxy setting in `package.json`:

```json
{
  "name": "toronto-ai-team-agent-frontend",
  "version": "0.1.0",
  "private": true,
  "proxy": "http://localhost:8000",
  "dependencies": {
    // existing dependencies...
  }
}
```

### Install Frontend Dependencies

```bash
# Navigate to the frontend directory
cd ~/toronto-ai-team-agent/frontend

# Install dependencies
npm install
```

**Note**: This process may take several minutes as it downloads and installs all required packages. The frontend dependencies require significant disk space (approximately 800MB-1GB).

### Start the Frontend Development Server

```bash
# Start the development server
npm start
```

This will:
1. Compile the React application
2. Start a development server on port 3000
3. Open your default web browser to http://localhost:3000

## Verify the Deployment

To verify that everything is working correctly:

1. Check that the frontend loads without errors
2. Navigate to the Project Dashboard
3. Verify that you can see the Project Overview panel
4. Test communication with the Project Manager by sending a message

## Run a Demo (Optional)

To run a demonstration of the multi-agent system's capabilities:

```bash
# Navigate to the deployment directory
cd ~/toronto-ai-team-agent/deployment

# Activate the virtual environment if not already activated
source ../venv/bin/activate

# Run the demo script
python demo.py
```

This will:
1. Create a collaboration session between agents
2. Simulate a feature development scenario
3. Generate artifacts and exchange messages
4. Save results to demo_results.json

## Local Development

### Backend Development

For backend development:

1. Make changes to the Python code
2. Restart the backend server to apply changes:
   ```bash
   # Stop the current server (Ctrl+C)
   # Start it again
   python deploy.py
   ```

### Frontend Development

For frontend development:

1. Make changes to the React components
2. The development server will automatically reload with your changes

## Troubleshooting

For common issues and solutions, refer to the [Troubleshooting Guide](../troubleshooting/common-issues.md).

## Next Steps

- [Production Deployment](./production-deployment.md) - For deploying to a production environment
- [Frontend Configuration](../frontend/configuration.md) - For advanced frontend configuration
- [Backend Configuration](../backend/configuration.md) - For advanced backend configuration
