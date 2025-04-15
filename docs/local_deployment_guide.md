# TORONTO AI Team Agent Team AI - Local Deployment Guide for Ubuntu

This guide provides step-by-step instructions for deploying the TORONTO AI Team Agent Team AI system locally on an Ubuntu machine.

## Prerequisites

- Ubuntu 22.04 LTS or newer
- Python 3.8+ (Python 3.10 recommended)
- Node.js 16+ and npm 8+
- Git
- OpenAI API key (for GPT-4o model access)
- At least 2GB of free disk space for frontend dependencies

## Step 1: System Preparation

First, ensure your system is up to date and has all required dependencies:

```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install required system dependencies
sudo apt install -y python3 python3-pip python3-venv nodejs npm git curl
```

Verify installations:

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check Node.js version
node --version  # Should be 16+

# Check npm version
npm --version  # Should be 8+
```

## Step 2: Clone the Repository

Clone the TORONTO AI Team Agent Team AI repository from GitHub:

```bash
# Create a directory for the project
mkdir -p ~/toronto-ai-team-agent-team-ai
cd ~/toronto-ai-team-agent-team-ai

# Clone the repository
git clone https://github.com/torontoai/TorontoAITeamAgent.git .
```

You will need to enter your GitHub username and personal access token when prompted.

## Step 3: Set Up Backend Environment

Create and activate a Python virtual environment for the backend:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package in development mode
pip install -e .
```

This will install all the required Python dependencies specified in setup.py.

## Step 4: Set Up Frontend Environment

For detailed frontend setup instructions, please refer to our comprehensive guides:

- [Frontend Environment Setup Guide](./frontend/environment_setup.md) - Detailed instructions for setting up the React application environment
- [Frontend Configuration Guide](./frontend/configuration_guide.md) - Instructions for configuring the frontend to connect with backend services

For a quick setup, navigate to the frontend directory and install dependencies:

```bash
# Navigate to the frontend directory
cd ~/toronto-ai-team-agent-team-ai/frontend

# Install frontend dependencies
npm install
```

**Important Note**: The frontend has substantial dependencies and requires approximately 800MB-1GB of disk space. If you encounter "ENOSPC: no space left on device" errors, free up disk space or deploy on a system with more available storage.

**Verify Frontend Files**: After installation, verify that all required React component files are present:

```bash
# Check main components
ls -la src/App.js src/project_dashboard.jsx

# Check component directories
ls -la src/components/
```

If you encounter a "Cannot find module './project_dashboard'" error or similar, please refer to the [Frontend Environment Setup Guide](./frontend/environment_setup.md) for detailed troubleshooting steps.

## Step 5: Configure API Keys

Create a configuration file for your API keys:

```bash
# Create a directory for API keys if it doesn't exist
mkdir -p ~/toronto-ai-team-agent-team-ai/config

# Create and edit the API keys file
nano ~/toronto-ai-team-agent-team-ai/config/api_keys.json
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

## Step 6: Configure the Deployment

Review and update the deployment configuration if needed:

```bash
# Edit the deployment configuration file
nano ~/toronto-ai-team-agent-team-ai/deployment/config.json
```

The default configuration should work for most local deployments, but you can adjust settings like:
- Agent models
- Communication parameters
- Host and port settings

Save any changes (Ctrl+X, then Y, then Enter).

## Step 7: Deploy the Backend

Deploy the multi-agent system backend:

```bash
# Navigate to the deployment directory
cd ~/toronto-ai-team-agent-team-ai/deployment

# Activate the virtual environment if not already activated
source ../venv/bin/activate

# Run the deployment script
python deploy.py
```

This will:
1. Initialize all agent instances
2. Set up communication channels
3. Run basic tests to verify functionality
4. Save test results to test_results.json

Keep this terminal window open as it runs the backend server.

## Step 8: Start the Frontend Development Server

Open a new terminal window and start the frontend development server:

```bash
# Navigate to the frontend directory
cd ~/toronto-ai-team-agent-team-ai/frontend

# Start the development server
npm start
```

This will start the React development server and automatically open the application in your default web browser. If it doesn't open automatically, you can access it at http://localhost:3000.

## Step 9: Verify the Deployment

To verify that everything is working correctly:

1. Check that the frontend loads without errors
2. Navigate to the Project Dashboard
3. Verify that you can see the Project Overview panel
4. Test communication with the Project Manager by sending a message

## Step 10: Run a Demo (Optional)

To run a demonstration of the multi-agent system's capabilities:

```bash
# Navigate to the deployment directory
cd ~/toronto-ai-team-agent-team-ai/deployment

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

## Troubleshooting

### Backend Connection Issues

If the frontend cannot connect to the backend:

1. Verify that the backend server is running
2. Check that the backend is running on the correct port (default: 8000)
3. Ensure the proxy setting in package.json is correct
4. Check for any error messages in the backend terminal

### API Key Issues

If you encounter authentication errors:

1. Verify that your OpenAI API key is correct
2. Check that the API key has access to the required models (GPT-4o)
3. Ensure the API key is properly formatted in the config file

### Python Dependency Issues

If you encounter Python dependency errors:

1. Ensure you're using the correct Python version
2. Try reinstalling dependencies: `pip install -e .`
3. Check for any specific error messages and install missing packages

### Frontend Build Issues

If you encounter issues with the frontend:

1. Clear npm cache: `npm cache clean --force`
2. Delete node_modules and reinstall: `rm -rf node_modules && npm install`
3. Check for JavaScript console errors in your browser
4. Refer to the [Frontend Environment Setup Guide](./frontend/environment_setup.md) for detailed troubleshooting

### Module Not Found Error

If you encounter "Cannot find module './project_dashboard'" or similar errors:

1. Verify all required component files are present in the correct locations
2. Check the [Frontend Environment Setup Guide](./frontend/environment_setup.md) for the complete component structure
3. Pull the latest changes from the repository: `git pull`

## Advanced Configuration

### Customizing Agent Roles

To modify agent behaviors or add new agent roles:

1. Edit the agent configuration files in the `app/agent` directory
2. Update the `agents` section in the `deployment/config.json` file
3. Restart the backend server

### Scaling for Production

For production deployments:

1. Use a production-ready web server like Nginx
2. Set up a proper database for persistent storage
3. Configure proper authentication and security measures
4. Build the frontend for production: `cd frontend && npm run build`

## Conclusion

You have successfully deployed the TORONTO AI Team Agent Team AI system locally on your Ubuntu machine. The system provides a multi-agent team with specialized roles working together on complex projects, with the human user maintaining oversight through the dashboard interface.

For more information on using the system, refer to the project documentation in the `docs` directory, particularly the frontend-specific guides in the `docs/frontend` directory.
