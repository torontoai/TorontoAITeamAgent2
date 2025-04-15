# Quick Start Guide

This guide provides a quick introduction to the TORONTO AI TEAM AGENT system, helping you get up and running quickly.

## Prerequisites

Ensure you have completed the [Installation](./installation.md) process before proceeding.

## Configuration

### 1. Configure API Keys

Create a configuration file for your API keys:

```bash
# Create a directory for API keys if it doesn't exist
mkdir -p ~/toronto-ai-team-agent/config

# Create and edit the API keys file
nano ~/toronto-ai-team-agent/config/api_keys.json
```

Add your OpenAI API key to the file:

```json
{
  "openai": {
    "api_key": "YOUR_OPENAI_API_KEY"
  }
}
```

Save and close the file (Ctrl+X, then Y, then Enter).

### 2. Configure the Deployment

Review and update the deployment configuration:

```bash
# Edit the deployment configuration file
nano ~/toronto-ai-team-agent/deployment/config.json
```

The default configuration should work for most local deployments, but you can adjust settings like:
- Agent models
- Communication parameters
- Host and port settings

## Starting the System

### 1. Start the Backend

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

Keep this terminal window open as it runs the backend server.

### 2. Start the Frontend

Open a new terminal window and start the frontend development server:

```bash
# Navigate to the frontend directory
cd ~/toronto-ai-team-agent/frontend

# Start the development server
npm start
```

This will start the React development server and automatically open the application in your default web browser. If it doesn't open automatically, you can access it at http://localhost:3000.

## Basic Usage

### Interacting with the Project Manager

1. Navigate to the Project Dashboard in the frontend application
2. Use the Project Manager Interaction Interface to send messages
3. The Project Manager will respond and coordinate with other agents as needed

### Creating a New Project

1. Click on "New Project" in the dashboard
2. Enter the project details:
   - Project name
   - Project description
   - Project goals
3. Submit the form to create a new project
4. The Project Manager will initialize the project and coordinate with the Product Manager to gather requirements

### Analyzing GitHub Repositories

1. Click on "Analyze Repository" in the dashboard
2. Enter the GitHub repository URL
3. Submit the form to start the analysis
4. The system will analyze the code and provide insights

## Next Steps

- [Local Deployment Guide](../deployment/local-deployment.md) - For more detailed deployment instructions
- [Frontend Configuration](../frontend/configuration.md) - For customizing the frontend
- [Knowledge Integration](../features/knowledge-integration.md) - For understanding the knowledge integration framework
- [MCP and A2A Technology](../features/mcp-a2a-technology.md) - For learning about the agent communication protocols
