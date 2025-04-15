# Frontend Environment Setup Guide

This guide provides detailed instructions for setting up the development environment for the TORONTO AI Team Agent Team AI frontend application on an Ubuntu machine.

## Prerequisites

- Ubuntu 22.04 LTS or newer
- Node.js 16+ (recommended: Node.js 18 LTS)
- npm 8+ (comes with Node.js)
- Git
- At least 2GB of free disk space for dependencies

## System Preparation

First, ensure your system has the required software:

```bash
# Update package lists
sudo apt update

# Install Node.js and npm if not already installed
sudo apt install -y nodejs npm

# Verify installations
node --version  # Should be 16.x or higher
npm --version   # Should be 8.x or higher

# Install n for easier Node.js version management (optional but recommended)
sudo npm install -g n

# Install and use the LTS version of Node.js (recommended)
sudo n lts
```

After installing a new Node.js version with n, you may need to restart your terminal or run:

```bash
hash -r  # Refresh the shell's program cache
```

## Repository Setup

Clone the TORONTO AI Team Agent Team AI repository from GitHub:

```bash
# Create a directory for the project
mkdir -p ~/toronto-ai-team-agent-team-ai
cd ~/toronto-ai-team-agent-team-ai

# Clone the repository using your GitHub credentials
git clone https://github.com/torontoai/TorontoAITeamAgent.git .
```

You will need to enter your GitHub username and personal access token when prompted.

## Frontend Directory Structure

The React application has the following key files and directories:

```
frontend/
├── node_modules/        # Dependencies (created after npm install)
├── public/
│   └── index.html       # HTML template
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── project_overview_panel.jsx
│   │   ├── progress_tracking_visualizations.jsx
│   │   └── project_manager_interaction_interface.jsx
│   ├── agent_conversation_monitoring_panel.jsx
│   ├── sprint_tracking_visualization.jsx
│   ├── project_dashboard.jsx  # Main dashboard component
│   ├── App.js                 # Main application component
│   ├── index.js               # Application entry point
│   └── index.css              # Global styles
└── package.json               # Dependencies and scripts
```

**Important**: All these files must be present for the application to work correctly. The error "Cannot find module './project_dashboard'" occurs when the `project_dashboard.jsx` file is missing or not in the correct location.

## Installing Dependencies

Install the frontend dependencies:

```bash
# Navigate to the frontend directory
cd ~/toronto-ai-team-agent-team-ai/frontend

# Install dependencies
npm install
```

This process may take several minutes as it downloads and installs all required packages.

**Important Notes**:
- The frontend dependencies require significant disk space (approximately 800MB-1GB).
- If you encounter "ENOSPC: no space left on device" errors, free up disk space or deploy on a system with more available storage.
- Modern React applications have many dependencies, so be patient during installation.

## Verifying Installation

After installation, verify that all React components are properly structured:

```bash
# Check the main components
ls -la src/App.js src/project_dashboard.jsx

# Check imported components
ls -la src/components/
ls -la src/agent_conversation_monitoring_panel.jsx src/sprint_tracking_visualization.jsx
```

## Starting the Development Server

Once all dependencies are installed and files are verified, start the development server:

```bash
npm start
```

This will:
1. Compile the React application
2. Start a development server on port 3000
3. Open your default web browser to http://localhost:3000

If the browser doesn't open automatically, you can manually navigate to http://localhost:3000.

## Next Steps

After setting up the environment, refer to the [Configuration Guide](./configuration_guide.md) for details on configuring the frontend application to connect with the backend services.

For troubleshooting common issues, see the [Troubleshooting](../local_deployment_guide.md#troubleshooting) section in the main deployment guide.
