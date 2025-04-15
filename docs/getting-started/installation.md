# Installation Guide

This guide provides instructions for installing the TORONTO AI TEAM AGENT system on your machine.

## Prerequisites

- Ubuntu 22.04 LTS or newer
- Python 3.10 or newer
- Node.js 18+ and npm 8+
- Git
- At least 2GB of free disk space for frontend dependencies
- OpenAI API key (for GPT-4o model access)

## System Preparation

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
python3 --version  # Should be 3.10+

# Check Node.js version
node --version  # Should be 18+

# Check npm version
npm --version  # Should be 8+
```

## Clone the Repository

Clone the TORONTO AI TEAM AGENT repository from GitHub:

```bash
# Create a directory for the project
mkdir -p ~/toronto-ai-team-agent
cd ~/toronto-ai-team-agent

# Clone the repository
git clone https://github.com/torontoai/TorontoAITeamAgent.git .
```

If you're accessing a private repository, you may need to use a GitHub token:

```bash
git clone https://[YOUR_GITHUB_TOKEN]@github.com/torontoai/TorontoAITeamAgent.git .
```

## Set Up Python Environment

Create and activate a Python virtual environment:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the package in development mode
pip install -e .
```

This will install all the required Python dependencies specified in setup.py.

## Next Steps

After completing the installation, you can proceed to:

- [Quick Start Guide](./quick-start.md) - For a quick introduction to the system
- [Local Deployment](../deployment/local-deployment.md) - For setting up a local development environment
- [Frontend Setup](../frontend/setup.md) - For setting up the frontend application
