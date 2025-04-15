# Frontend Configuration Guide

This guide provides detailed instructions for configuring the TORONTO AI Team Agent Team AI frontend application after you've completed the environment setup.

## Prerequisites

- Completed the [Environment Setup](./environment_setup.md)
- Backend services running (or configured for connection)

## Frontend Configuration Options

The TORONTO AI Team Agent Team AI frontend can be configured in several ways to connect with backend services and customize its behavior.

### API Connection Configuration

By default, the frontend expects the backend API to be running at `http://localhost:8000`. You can modify this in two ways:

#### 1. Using the proxy setting in package.json

For development, the simplest approach is to add a proxy setting to your package.json file:

```bash
cd ~/toronto-ai-team-agent-team-ai/frontend
```

Edit package.json and add the proxy field:

```json
{
  "name": "toronto-ai-team-agent-team-ai-frontend",
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

#### 2. Using environment variables

For more flexibility, you can use environment variables:

Create a `.env` file in the frontend directory:

```bash
cd ~/toronto-ai-team-agent-team-ai/frontend
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

### Theme Customization

The application uses Material UI with a default theme. You can customize the theme by editing the theme configuration in `src/App.js`:

```javascript
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // Change to your preferred primary color
    },
    secondary: {
      main: '#dc004e', // Change to your preferred secondary color
    },
    background: {
      default: '#f5f5f5', // Change to your preferred background color
    },
  },
});
```

### Component Configuration

Each component in the dashboard can be configured or customized:

1. **Project Overview Panel**: Edit `src/components/project_overview_panel.jsx`
2. **Progress Tracking Visualizations**: Edit `src/components/progress_tracking_visualizations.jsx`
3. **Project Manager Interaction Interface**: Edit `src/components/project_manager_interaction_interface.jsx`

## Backend Integration

The frontend communicates with the backend through RESTful API calls. Ensure your backend is properly configured and running before starting the frontend.

### Authentication Configuration

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

## Advanced Configuration

### WebSocket Configuration

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

## Troubleshooting Configuration Issues

### API Connection Issues

If the frontend cannot connect to the backend:

1. Verify the backend is running: `curl http://localhost:8000/api/health`
2. Check for CORS issues in the browser console
3. Ensure the proxy setting in package.json is correct
4. Verify environment variables are properly set

### Component Loading Issues

If components fail to load:

1. Check import paths in each component file
2. Verify all required files exist in the correct locations
3. Check for JavaScript errors in the browser console

## Next Steps

After configuring the frontend, you can:

1. Start developing new features
2. Customize the UI to match your requirements
3. Connect to additional backend services

For more information on deployment, refer to the [Local Deployment Guide](../local_deployment_guide.md).
