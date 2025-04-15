# Deployment Guide: TORONTO AI Team Agent Team AI on Ubuntu

## Prerequisites
- Ubuntu 22.04 LTS or newer
- Python 3.10 or newer
- Git
- GitHub token for accessing the private repository
- API keys for any external services (OpenAI, Ollama, etc.)

## Step 1: System Preparation

1. Update your system packages:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. Install required system dependencies:
   ```bash
   sudo apt install -y python3-pip python3-venv git curl
   ```

## Step 2: Clone the Repository

1. Create a directory for the project:
   ```bash
   mkdir -p ~/toronto-ai-team-agent-team-ai
   cd ~/toronto-ai-team-agent-team-ai
   ```

2. Clone the repository using the GitHub token:
   ```bash
   git clone https://[YOUR_GITHUB_TOKEN]@github.com/torontoai/TorontoAITeamAgent.git .
   ```

   Note: If you prefer not to include the token in the command, you can use:
   ```bash
   git clone https://github.com/torontoai/TorontoAITeamAgent.git .
   ```
   And then enter your GitHub username and the token when prompted.

## Step 3: Set Up Python Environment

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install the project in development mode:
   ```bash
   pip install -e .
   ```

   If you encounter any errors about missing setup.py, create one with:
   ```bash
   echo 'from setuptools import setup, find_packages

   setup(
       name="toronto-ai-team-agent-team-ai",
       version="0.1.0",
       packages=find_packages(),
       install_requires=[
           "asyncio",
           "aiohttp",
           "pydantic",
           "pytest",
           "pytest-asyncio",
       ],
       python_requires=">=3.8",
   )' > setup.py
   ```
   Then run `pip install -e .` again.

## Step 4: Configure API Keys and Services

1. Create a configuration directory:
   ```bash
   mkdir -p config
   ```

2. Create a configuration file for API keys:
   ```bash
   touch config/api_keys.json
   ```

3. Edit the API keys file with your preferred text editor:
   ```bash
   nano config/api_keys.json
   ```

4. Add your API keys to the file:
   ```json
   {
     "openai": {
       "api_key": "YOUR_OPENAI_API_KEY"
     },
     "ollama": {
       "base_url": "http://localhost:11434"
     },
     "claude": {
       "api_key": "YOUR_ANTHROPIC_API_KEY"
     },
     "deepseek": {
       "api_key": "YOUR_DEEPSEEK_API_KEY"
     }
   }
   ```

5. Save and close the file (Ctrl+X, then Y, then Enter in nano)

## Step 5: Configure the Multi-Agent System

1. Create a deployment directory:
   ```bash
   mkdir -p deployment
   ```

2. Create a configuration file for the multi-agent system:
   ```bash
   touch deployment/config.json
   ```

3. Edit the configuration file:
   ```bash
   nano deployment/config.json
   ```

4. Add the following configuration:
   ```json
   {
     "system": {
       "name": "TORONTO AI Team Agent Team AI",
       "version": "0.1.0",
       "environment": "local"
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
       "log_level": "INFO",
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
       "workers": 4
     },
     "api_config_path": "../config/api_keys.json"
   }
   ```

5. Save and close the file

## Step 6: Install Ollama (Optional, for local LLM support)

1. Install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. Start the Ollama service:
   ```bash
   ollama serve
   ```

3. In a new terminal, pull the models you want to use:
   ```bash
   ollama pull llama3
   ollama pull mistral
   ```

## Step 7: Create Deployment Scripts

1. Create a deployment script:
   ```bash
   touch deployment/deploy.py
   ```

2. Edit the deployment script:
   ```bash
   nano deployment/deploy.py
   ```

3. Copy the deployment script content from the repository or create a new one with the necessary code to initialize and run the multi-agent system.

4. Save and close the file

## Step 8: Run the System

1. Make sure your virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```

2. Run the deployment script:
   ```bash
   cd deployment
   python deploy.py
   ```

3. The system should start and display logs indicating that the agents have been deployed and are communicating with each other.

## Step 9: Test the System

1. Create a test script:
   ```bash
   touch deployment/test.py
   ```

2. Edit the test script:
   ```bash
   nano deployment/test.py
   ```

3. Add code to test the basic functionality of the system, such as sending messages between agents and creating collaboration sessions.

4. Run the test script:
   ```bash
   python test.py
   ```

## Step 10: Run the Demonstration

1. Create a demonstration script (if not already in the repository):
   ```bash
   touch deployment/demo.py
   ```

2. Edit the demonstration script:
   ```bash
   nano deployment/demo.py
   ```

3. Add code to demonstrate the real-time collaboration capabilities of the system.

4. Run the demonstration:
   ```bash
   python demo.py
   ```

## Troubleshooting

1. If you encounter permission issues:
   ```bash
   chmod -R 755 .
   ```

2. If you have issues with API connections, verify your API keys and network connectivity.

3. Check the logs for detailed error messages:
   ```bash
   cat deployment/deployment.log
   ```

4. If you encounter Python package conflicts, try creating a fresh virtual environment and reinstalling dependencies.

## Additional Configuration

1. To modify agent behaviors, edit the agent configuration files in the `app/agent` directory.

2. To adjust communication parameters, modify the `communication` section in the `deployment/config.json` file.

3. To add new agent roles, create new agent classes in the `app/agent` directory and update the configuration accordingly.
