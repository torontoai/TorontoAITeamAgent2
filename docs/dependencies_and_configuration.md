# TorontoAITeamAgent Team AI - Dependencies and Configuration Guide

This document provides comprehensive information about dependencies, configuration requirements, and deployment instructions for the TorontoAITeamAgent Team AI system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
   - [Core Dependencies](#core-dependencies)
   - [Tool-Specific Dependencies](#tool-specific-dependencies)
3. [Configuration](#configuration)
   - [API Keys](#api-keys)
   - [Environment Variables](#environment-variables)
   - [Configuration Files](#configuration-files)
4. [Deployment](#deployment)
   - [Local Deployment](#local-deployment)
   - [Cloud Deployment](#cloud-deployment)
5. [Multi-Agent Setup](#multi-agent-setup)
   - [Agent Roles](#agent-roles)
   - [Inter-Agent Communication](#inter-agent-communication)
6. [Troubleshooting](#troubleshooting)

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows 10+
- **Python**: 3.10+ (3.10.12 recommended)
- **Node.js**: 20.0+ (for Pyright and other JavaScript-based tools)
- **Docker**: 20.10+ (for containerization and deployment)
- **Git**: 2.30+ (for version control and deployment)
- **RAM**: Minimum 8GB, 16GB+ recommended for running multiple agents
- **Storage**: Minimum 10GB free space
- **Network**: Stable internet connection for API access

## Installation

### Core Dependencies

Install the core Python dependencies:

```bash
# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt
```

The `requirements.txt` file includes:

```
# Core framework
fastapi>=0.95.0
uvicorn>=0.21.1
pydantic>=2.0.0
python-dotenv>=1.0.0
httpx>=0.24.0
websockets>=11.0.0
asyncio>=3.4.3
aiohttp>=3.8.4

# Database
sqlalchemy>=2.0.0
alembic>=1.10.0

# Utilities
pyyaml>=6.0
jinja2>=3.1.2
```

### Tool-Specific Dependencies

#### Core AI/LLM Tools

```bash
# OpenAI
pip install openai>=1.0.0

# Ollama
pip install ollama>=0.1.0

# Claude (Anthropic)
pip install anthropic>=0.5.0

# DeepSeek
pip install deepseek-ai>=0.1.0
```

#### Agentic Coding Tools

```bash
# Aider
pip install aider-chat>=0.18.0

# Cursor
# Note: Cursor integration requires the Cursor desktop application
# Download from: https://cursor.sh/
pip install cursor-api>=0.1.0
```

#### Execution/Testing Tools

```bash
# Pytest
pip install pytest>=7.3.1

# Replit
pip install replit-api>=0.5.0
```

#### Formatting/Style Tools

```bash
# Black
pip install black>=23.3.0

# Flake8
pip install flake8>=6.0.0
```

#### Analysis Tools

```bash
# Pylint
pip install pylint>=2.17.0
```

#### Type Checking Tools

```bash
# MyPy
pip install mypy>=1.3.0

# Pyright
npm install -g pyright
```

#### Security Tools

```bash
# Bandit
pip install bandit>=1.7.5
```

#### Deployment Tools

```bash
# GitPython
pip install gitpython>=3.1.31

# Docker
pip install docker>=6.1.0
```

#### UI/Utilities Tools

```bash
# Gradio
pip install gradio>=3.36.0
```

## Configuration

### API Keys

Create a `.env` file in the root directory with the following API keys:

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

### Environment Variables

The following environment variables can be set to customize the behavior of the system:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port for the web server | `8000` |
| `HOST` | Host for the web server | `0.0.0.0` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment (development, production) | `development` |
| `DATABASE_URL` | Database connection URL | `sqlite:///./torontoai.db` |
| `MAX_THREADS` | Maximum number of threads for ThreadingTool | `10` |
| `MAX_QUEUES` | Maximum number of queues for QueueTool | `10` |
| `DEFAULT_MODEL` | Default model for OpenAI | `gpt-4o` |
| `OLLAMA_HOST` | Host for Ollama API | `http://localhost:11434` |

### Configuration Files

#### Main Configuration

Create a `config.yaml` file in the root directory:

```yaml
# TorontoAITeamAgent Team AI Configuration

# Server settings
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  reload: true  # Set to false in production

# Database settings
database:
  url: sqlite:///./torontoai.db
  pool_size: 20
  max_overflow: 10
  echo: false

# Logging settings
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/torontoai.log

# Agent settings
agents:
  project_manager:
    model: gpt-4o
    temperature: 0.2
    max_tokens: 4096
  product_manager:
    model: gpt-4o
    temperature: 0.3
    max_tokens: 4096
  developer:
    model: gpt-4o
    temperature: 0.1
    max_tokens: 8192

# Tool settings
tools:
  core_ai:
    openai:
      default_model: gpt-4o
      timeout: 60
    ollama:
      host: http://localhost:11434
      timeout: 120
    claude:
      default_model: claude-3-opus-20240229
      timeout: 60
    deepseek:
      default_model: deepseek-coder
      timeout: 60
  agentic_coding:
    aider:
      edit_format: diff
      timeout: 300
    cursor:
      timeout: 300
  execution:
    subprocess:
      timeout: 60
    pytest:
      timeout: 120
    replit:
      timeout: 180
  formatting:
    black:
      line_length: 88
      timeout: 30
    flake8:
      max_line_length: 88
      timeout: 30
  analysis:
    pylint:
      timeout: 60
  type_checking:
    mypy:
      python_version: 3.10
      timeout: 60
    pyright:
      timeout: 60
  security:
    bandit:
      timeout: 60
  deployment:
    gitpython:
      timeout: 60
    docker:
      timeout: 300
  ui:
    gradio:
      timeout: 60
    threading:
      max_threads: 10
    queue:
      max_queues: 10
      default_timeout: 5

# Communication settings
communication:
  websocket:
    ping_interval: 30
    ping_timeout: 120
  http:
    timeout: 30
    max_retries: 3
```

#### Tool-Specific Configuration

Some tools require additional configuration files:

##### Pylint Configuration

Create a `.pylintrc` file in the root directory:

```ini
[MASTER]
ignore=CVS
ignore-patterns=
persistent=yes
load-plugins=

[MESSAGES CONTROL]
disable=C0111,C0103,C0303,W0511,R0903,C0330

[REPORTS]
output-format=text
reports=yes
evaluation=10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)

[BASIC]
good-names=i,j,k,ex,Run,_
bad-names=foo,bar,baz,toto,tutu,tata
```

##### Flake8 Configuration

Create a `.flake8` file in the root directory:

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,docs/source/conf.py,old,build,dist,venv
```

##### MyPy Configuration

Create a `mypy.ini` file in the root directory:

```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False

[mypy.plugins.pydantic.*]
follow_imports = skip
```

##### Pyright Configuration

Create a `pyrightconfig.json` file in the root directory:

```json
{
  "include": ["app"],
  "exclude": ["**/node_modules", "**/__pycache__", "venv"],
  "ignore": ["**/site-packages"],
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "pythonVersion": "3.10",
  "typeCheckingMode": "basic"
}
```

## Deployment

### Local Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/torontoai/torontoai-team-agent.git
   cd torontoai-team-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t torontoai-team-agent .
   ```

2. Run the container:
   ```bash
   docker run -d --name torontoai-team-agent \
     -p 8000:8000 \
     --env-file .env \
     torontoai-team-agent
   ```

### Cloud Deployment

For cloud deployment, you can use the following services:

#### AWS Deployment

1. Set up an EC2 instance with Docker installed
2. Clone the repository and build the Docker image
3. Run the container with appropriate environment variables
4. Set up an Application Load Balancer for HTTPS support

#### Azure Deployment

1. Use Azure Container Instances or Azure Kubernetes Service
2. Deploy the Docker image from Azure Container Registry
3. Configure environment variables in the Azure portal
4. Set up Azure Application Gateway for HTTPS support

#### Google Cloud Deployment

1. Use Google Cloud Run or Google Kubernetes Engine
2. Deploy the Docker image from Google Container Registry
3. Configure environment variables in the Google Cloud console
4. Set up Google Cloud Load Balancing for HTTPS support

## Multi-Agent Setup

### Agent Roles

The TorontoAITeamAgent Team AI system includes three main agent roles:

1. **Project Manager**: Responsible for overall project coordination, task assignment, and progress tracking
2. **Product Manager**: Responsible for requirements gathering, feature prioritization, and user experience
3. **Developer**: Responsible for code implementation, testing, and deployment

Each agent can be configured with different models and parameters to optimize for their specific role.

### Inter-Agent Communication

Agents communicate with each other through a message passing system implemented using the Queue tool. The communication framework is defined in `app/collaboration/framework.py`.

To set up inter-agent communication:

1. Create a shared queue for each communication channel:
   ```python
   from app.tools.registry import registry
   
   queue_tool = registry.get_tool("queue")
   pm_to_dev_queue = await queue_tool.execute({
       "operation": "create",
       "queue_id": "pm_to_dev"
   })
   ```

2. Configure agents to use these queues for sending and receiving messages:
   ```python
   # In Project Manager agent
   await queue_tool.execute({
       "operation": "put",
       "queue_id": "pm_to_dev",
       "item": {"type": "task", "content": "Implement feature X"}
   })
   
   # In Developer agent
   result = await queue_tool.execute({
       "operation": "get",
       "queue_id": "pm_to_dev",
       "timeout": 10
   })
   task = result.data["item"]
   ```

## Troubleshooting

### Common Issues

#### API Key Issues

If you encounter authentication errors with external APIs:
- Verify that your API keys are correctly set in the `.env` file
- Check that the API keys have the necessary permissions
- Ensure that billing is enabled for paid APIs

#### Dependency Issues

If you encounter dependency conflicts:
- Use a virtual environment to isolate dependencies
- Update to the latest versions of packages
- Check for compatibility between packages

#### Docker Issues

If you encounter issues with Docker deployment:
- Ensure Docker is properly installed and running
- Check that the Docker image builds successfully
- Verify that environment variables are correctly passed to the container

#### Agent Communication Issues

If agents are not communicating properly:
- Check that the Queue tool is properly initialized
- Verify that queue IDs are consistent across agents
- Ensure that message formats are compatible between agents

### Getting Help

If you encounter issues not covered in this guide:
- Check the GitHub repository issues section
- Join the TorontoAITeamAgent community Discord server
- Contact the maintainers at info@torontoai.digital
