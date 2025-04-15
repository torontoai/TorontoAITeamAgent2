# Prerequisites

This document outlines the prerequisites for installing and running the TORONTO AI TEAM AGENT system.

## Hardware Requirements

### Minimum Requirements (Development Environment)
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 10GB free space (2GB for frontend dependencies)
- Network: Broadband internet connection

### Recommended Requirements (Production Environment)
- CPU: 16+ cores
- RAM: 64GB+
- Storage: 500GB SSD
- Network: 10Gbps connectivity

## Software Requirements

### Operating System
- Ubuntu 22.04 LTS or newer (recommended)
- Other Linux distributions may work but are not officially supported

### Runtime Environment
- Python 3.10 or newer
- Node.js 18+ and npm 8+
- Git

### Optional Components
- Docker 24+ and Docker Compose (for containerized deployment)
- Kubernetes 1.26+ (for orchestrated deployment)
- Nginx (for production deployment)

## API Keys

The TORONTO AI TEAM AGENT system requires API keys for external services:

### Required
- OpenAI API key (for GPT-4o model access)

### Optional
- Anthropic API key (for Claude models)
- Pinecone API key (for vector database)
- Weaviate API key (for vector database)
- GitHub API token (for repository analysis)

## Network Requirements

- Outbound internet access to OpenAI API endpoints
- Outbound internet access to GitHub (if using repository analysis features)
- For production deployment: Firewall rules allowing inbound traffic to web server ports

## Browser Requirements

For accessing the frontend application:
- Chrome 90+ (recommended)
- Firefox 90+
- Edge 90+
- Safari 15+

## Next Steps

After ensuring you meet all prerequisites:
- Proceed to [Installation](./installation.md)
- Review the [Local Deployment Guide](../deployment/local-deployment.md) for development setup
- Review the [Production Deployment Guide](../deployment/production-deployment.md) for production setup
