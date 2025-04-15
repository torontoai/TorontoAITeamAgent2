# Common Issues and Solutions

This document provides solutions for common issues you might encounter when working with the TORONTO AI TEAM AGENT system.

## Installation Issues

### Python Environment Issues

**Issue**: Error when creating or activating virtual environment.

**Solution**:
```bash
# Remove existing virtual environment if corrupted
rm -rf venv

# Create a new virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Dependency Installation Failures

**Issue**: Errors when installing Python dependencies.

**Solution**:
```bash
# Update pip
pip install --upgrade pip

# Install dependencies with verbose output
pip install -e . -v

# If specific packages fail, try installing them individually
pip install <package-name>==<version>
```

### Node.js and npm Issues

**Issue**: Errors when installing frontend dependencies.

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install
```

## Backend Issues

### Backend Server Won't Start

**Issue**: The backend server fails to start.

**Solution**:
1. Check if the port is already in use:
   ```bash
   sudo lsof -i :8000
   ```
   If it is, terminate the process or use a different port.

2. Check for configuration errors:
   ```bash
   # Validate configuration file
   python -m app.deployment.config_validator
   ```

3. Check for missing API keys:
   ```bash
   # Verify API keys are properly set
   python -m app.deployment.api_key_validator
   ```

### Agent Initialization Failures

**Issue**: Agents fail to initialize properly.

**Solution**:
1. Check API key configuration:
   ```bash
   # Verify API keys
   cat config/api_keys.json
   ```

2. Check agent configuration:
   ```bash
   # Verify agent configuration
   cat deployment/config.json
   ```

3. Increase logging verbosity:
   ```bash
   # Set log level to DEBUG in config.json
   # Then restart the server
   python deploy.py
   ```

### Communication Framework Errors

**Issue**: Errors in the communication framework.

**Solution**:
1. Check event bus status:
   ```bash
   # Run event bus diagnostics
   python -m app.collaboration.event_bus_diagnostics
   ```

2. Reset communication channels:
   ```bash
   # Reset communication channels
   python -m app.collaboration.reset_channels
   ```

## Frontend Issues

### "Cannot find module './project_dashboard'" Error

**Issue**: Frontend fails to start with "Cannot find module './project_dashboard'" error.

**Solution**:
1. Verify the file exists:
   ```bash
   ls -la frontend/src/project_dashboard.jsx
   ```

2. If missing, restore it from the repository:
   ```bash
   git checkout origin/main -- frontend/src/project_dashboard.jsx
   ```

3. Check import paths in App.js:
   ```bash
   cat frontend/src/App.js
   ```
   Ensure the import path matches the actual file location.

### Frontend Loads But Cannot Connect to Backend

**Issue**: Frontend loads but cannot communicate with the backend.

**Solution**:
1. Check if backend is running:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. Verify proxy configuration in package.json:
   ```bash
   cat frontend/package.json
   ```
   Ensure the "proxy" field is set to the correct backend URL.

3. Check for CORS issues:
   ```bash
   # Enable CORS debugging in the backend
   # Edit deployment/config.json and set "debug_cors": true
   # Then restart the backend
   python deploy.py
   ```

### UI Rendering Issues

**Issue**: UI components don't render correctly.

**Solution**:
1. Clear browser cache and reload.

2. Check browser console for errors.

3. Verify all required dependencies are installed:
   ```bash
   cd frontend
   npm list @mui/material @emotion/react @emotion/styled
   ```

## Knowledge Integration Issues

### Vector Database Connection Failures

**Issue**: Cannot connect to vector database.

**Solution**:
1. Check vector database configuration:
   ```bash
   python -m app.training.cli config --show
   ```

2. Verify the vector database is running:
   ```bash
   # For ChromaDB
   docker ps | grep chroma
   ```

3. Reset vector database connection:
   ```bash
   python -m app.training.cli vector_db --reset
   ```

### Knowledge Extraction Failures

**Issue**: Knowledge extraction pipeline fails.

**Solution**:
1. Check file permissions:
   ```bash
   ls -la app/training/materials/
   ```

2. Verify file formats:
   ```bash
   file app/training/materials/*
   ```

3. Run extraction with debug logging:
   ```bash
   python -m app.training.cli extract --debug
   ```

## MCP and A2A Issues

### Protocol Compatibility Errors

**Issue**: Errors when communicating with external systems using MCP or A2A.

**Solution**:
1. Verify protocol version compatibility:
   ```bash
   python -m app.collaboration.tests.protocol_compatibility_test
   ```

2. Check external endpoint configuration:
   ```bash
   cat config/external_endpoints.json
   ```

3. Enable protocol debugging:
   ```bash
   # Edit config.json and set "protocol_debug": true
   # Then restart the system
   python deploy.py
   ```

### Authentication Failures

**Issue**: Authentication failures with external systems.

**Solution**:
1. Verify API keys for external systems:
   ```bash
   cat config/api_keys.json
   ```

2. Check token expiration:
   ```bash
   python -m app.collaboration.token_validator
   ```

3. Regenerate authentication tokens:
   ```bash
   python -m app.collaboration.regenerate_tokens
   ```

## Deployment Issues

### Docker Deployment Issues

**Issue**: Docker containers fail to start or communicate.

**Solution**:
1. Check Docker logs:
   ```bash
   docker logs <container-id>
   ```

2. Verify Docker network configuration:
   ```bash
   docker network inspect toronto-ai-network
   ```

3. Rebuild containers:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Kubernetes Deployment Issues

**Issue**: Kubernetes pods fail to start or communicate.

**Solution**:
1. Check pod status:
   ```bash
   kubectl get pods -n toronto-ai
   ```

2. Check pod logs:
   ```bash
   kubectl logs <pod-name> -n toronto-ai
   ```

3. Describe the pod for more details:
   ```bash
   kubectl describe pod <pod-name> -n toronto-ai
   ```

4. Verify ConfigMaps and Secrets:
   ```bash
   kubectl get configmaps -n toronto-ai
   kubectl get secrets -n toronto-ai
   ```

## Performance Issues

### Slow Response Times

**Issue**: System responds slowly to requests.

**Solution**:
1. Check system resource usage:
   ```bash
   top
   ```

2. Monitor API call latency:
   ```bash
   python -m app.monitoring.api_latency_monitor
   ```

3. Optimize vector database:
   ```bash
   python -m app.training.cli vector_db --optimize
   ```

### Memory Usage Issues

**Issue**: System uses excessive memory.

**Solution**:
1. Monitor memory usage:
   ```bash
   free -h
   ```

2. Check for memory leaks:
   ```bash
   python -m app.monitoring.memory_leak_detector
   ```

3. Adjust memory limits in configuration:
   ```bash
   # Edit deployment/config.json and adjust memory settings
   # Then restart the system
   python deploy.py
   ```

## Next Steps

- [Local Deployment Guide](../deployment/local-deployment.md) - For deploying the system locally
- [Production Deployment Guide](../deployment/production-deployment.md) - For deploying to a production environment
- [Knowledge Integration Framework](../features/knowledge-integration.md) - For understanding the knowledge integration system
