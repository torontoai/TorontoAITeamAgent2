# Frontend Configuration Guide

This guide provides detailed instructions for configuring the TORONTO AI TEAM AGENT frontend application after you've completed the setup process.

## Prerequisites

- Completed the [Frontend Setup](./setup.md)
- Backend services running (or configured for connection)

## API Connection Configuration

By default, the frontend expects the backend API to be running at `http://localhost:8000`. You can modify this in two ways:

### 1. Using the proxy setting in package.json

For development, the simplest approach is to add a proxy setting to your package.json file:

```bash
cd ~/toronto-ai-team-agent/frontend
```

Edit package.json and add the proxy field:

```json
{
  "name": "toronto-ai-team-agent-frontend",
  "version": "0.1.0",
  "private": true,
  "proxy": "http://localhost:8000",
  "dependencies": {
    // existing dependencies...
  },
  // rest of package.json...
}
```

This will proxy API requests from the frontend development server to your backend server.

### 2. Using environment variables

For more flexibility, you can use environment variables:

Create a `.env` file in the frontend directory:

```bash
cd ~/toronto-ai-team-agent/frontend
touch .env
```

Add the API URL to the .env file:

```
REACT_APP_API_URL=http://localhost:8000
```

Then update your API calls in the code to use this environment variable:

```javascript
const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
fetch(`${apiUrl}/api/endpoint`);
```

## Authentication Configuration

If your backend requires authentication:

1. Create an authentication service in the frontend:

```bash
mkdir -p src/services
touch src/services/auth.js
```

2. Implement authentication methods in this file:

```javascript
// Example auth.js
export const login = async (username, password) => {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  if (!response.ok) {
    throw new Error('Login failed');
  }
  
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data;
};

export const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};
```

3. Use these methods in your API calls:

```javascript
import { getAuthHeader } from '../services/auth';

const fetchData = async () => {
  const response = await fetch('http://localhost:8000/api/data', {
    headers: {
      ...getAuthHeader(),
    },
  });
  // Process response...
};
```

## WebSocket Configuration

For real-time updates from the backend:

1. Install the required package:

```bash
npm install socket.io-client
```

2. Create a WebSocket service:

```bash
touch src/services/socket.js
```

3. Implement the WebSocket connection:

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:8000', {
  autoConnect: false,
});

export const connectSocket = () => {
  socket.connect();
};

export const disconnectSocket = () => {
  socket.disconnect();
};

export const subscribeToEvent = (event, callback) => {
  socket.on(event, callback);
};

export const unsubscribeFromEvent = (event, callback) => {
  socket.off(event, callback);
};

export default socket;
```

4. Use this service in your components:

```javascript
import { useEffect } from 'react';
import { connectSocket, subscribeToEvent, disconnectSocket } from '../services/socket';

function YourComponent() {
  useEffect(() => {
    connectSocket();
    
    subscribeToEvent('agentMessage', (data) => {
      console.log('New message:', data);
      // Update state or UI based on the message
    });
    
    return () => {
      disconnectSocket();
    };
  }, []);
  
  // Component implementation...
}
```

## Environment-Specific Configuration

To support different environments (development, staging, production):

1. Create environment-specific .env files:

```bash
# Development (default)
touch .env.development

# Production
touch .env.production

# Staging
touch .env.staging
```

2. Add environment-specific variables to each file:

```
# .env.development
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
REACT_APP_LOG_LEVEL=debug

# .env.production
REACT_APP_API_URL=https://api.toronto-ai-team-agent.com
REACT_APP_ENV=production
REACT_APP_LOG_LEVEL=error

# .env.staging
REACT_APP_API_URL=https://staging-api.toronto-ai-team-agent.com
REACT_APP_ENV=staging
REACT_APP_LOG_LEVEL=info
```

3. Start or build the application with the specific environment:

```bash
# Development
npm start

# Production
npm run build

# Staging
REACT_APP_ENV=staging npm start
```

## Troubleshooting Configuration Issues

### API Connection Issues

If the frontend cannot connect to the backend:

1. Verify the backend is running: `curl http://localhost:8000/api/health`
2. Check for CORS issues in the browser console
3. Ensure the proxy setting in package.json is correct
4. Verify environment variables are properly set

### WebSocket Connection Issues

If real-time updates are not working:

1. Verify the WebSocket server is running
2. Check for WebSocket connection errors in the browser console
3. Ensure the WebSocket URL is correct
4. Verify that the WebSocket events match between frontend and backend

## Next Steps

- [Frontend Customization](./customization.md) - For customizing the UI components
- [Local Deployment Guide](../deployment/local-deployment.md) - For complete system deployment
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - For resolving common issues
