# TorontoAITeamAgent Team AI - Installation Guide

This guide provides step-by-step instructions for installing and setting up the TorontoAITeamAgent Team AI system.

## Prerequisites

Before installing TorontoAITeamAgent Team AI, ensure your system meets the following requirements:

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows 10+
- **Python**: 3.10+ (3.10.12 recommended)
- **Node.js**: 20.0+ (for Pyright and other JavaScript-based tools)
- **Docker**: 20.10+ (optional, for containerized deployment)
- **Git**: 2.30+
- **RAM**: Minimum 8GB, 16GB+ recommended for running multiple agents
- **Storage**: Minimum 10GB free space
- **Network**: Stable internet connection for API access

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/torontoai/torontoai-team-agent.git
cd torontoai-team-agent
```

### 2. Set Up Python Environment

It's recommended to use a virtual environment to avoid dependency conflicts:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Core Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt
```

### 4. Install Tool-Specific Dependencies

The TorontoAITeamAgent Team AI system uses 20 different tools across various categories. You can install all dependencies at once or by category:

```bash
# Install all tool dependencies
pip install -r requirements-tools.txt

# Or install by category
pip install -r requirements-core-ai.txt
pip install -r requirements-agentic-coding.txt
pip install -r requirements-execution.txt
pip install -r requirements-formatting.txt
pip install -r requirements-analysis.txt
pip install -r requirements-type-checking.txt
pip install -r requirements-security.txt
pip install -r requirements-deployment.txt
pip install -r requirements-ui.txt
```

### 5. Install Node.js Dependencies

Some tools require Node.js:

```bash
# Install Pyright for type checking
npm install -g pyright
```

### 6. Configure Environment Variables

Create a `.env` file in the root directory with your API keys and configuration:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Anthropic (Claude) API
ANTHROPIC_API_KEY=your_anthropic_api_key

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key

# GitHub Token (for GitPython)
GITHUB_TOKEN=your_github_token

# Replit API
REPLIT_API_KEY=your_replit_api_key

# Other configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 7. Initialize the Database

```bash
# Run database migrations
alembic upgrade head
```

### 8. Start the Server

```bash
# Start the server in development mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Installation (Alternative)

If you prefer to use Docker, you can build and run the application in a container:

### 1. Build the Docker Image

```bash
docker build -t torontoai-team-agent .
```

### 2. Run the Container

```bash
docker run -d --name torontoai-team-agent \
  -p 8000:8000 \
  --env-file .env \
  torontoai-team-agent
```

## Verifying Installation

To verify that the installation was successful:

1. Open a web browser and navigate to `http://localhost:8000`
2. You should see the TorontoAITeamAgent Team AI dashboard
3. Check the logs for any error messages:
   ```bash
   tail -f logs/torontoai.log
   ```

## Troubleshooting

### Common Installation Issues

#### Missing Dependencies

If you encounter errors about missing dependencies:

```bash
# Update pip
pip install --upgrade pip

# Reinstall dependencies with verbose output
pip install -v -r requirements.txt
```

#### API Key Issues

If you encounter authentication errors with external APIs:
- Verify that your API keys are correctly set in the `.env` file
- Check that the API keys have the necessary permissions
- Ensure that billing is enabled for paid APIs

#### Port Already in Use

If port 8000 is already in use:

```bash
# Change the port
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### Docker Issues

If you encounter issues with Docker:

```bash
# Check Docker logs
docker logs torontoai-team-agent

# Restart the container
docker restart torontoai-team-agent
```

## Next Steps

After successful installation:

1. Configure agent roles in the `config.yaml` file
2. Set up inter-agent communication channels
3. Deploy your first multi-agent team

For more detailed information, refer to the [Dependencies and Configuration Guide](dependencies_and_configuration.md) and [User Manual](user_manual.md).
