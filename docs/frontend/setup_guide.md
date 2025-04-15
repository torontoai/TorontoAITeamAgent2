# Comprehensive Frontend Setup and Deployment Guide

This guide provides detailed instructions for setting up and deploying the TORONTO AI Team Agent Team AI frontend application, with specific attention to the initial setup process and resolving common deployment issues.

## Prerequisites

- Node.js (v14.0.0 or higher)
- npm (v6.0.0 or higher)
- Git
- At least 1GB of free disk space (important for npm dependencies)

## Initial Frontend Setup

### 1. Clone the Repository

```bash
# Using HTTPS with token
git clone https://[YOUR_GITHUB_TOKEN]@github.com/torontoai/TorontoAITeamAgent.git

# Or using SSH if you have it configured
git clone git@github.com:torontoai/TorontoAITeamAgent.git

cd TorontoAITeamAgent
```

### 2. Create Frontend Directory Structure (if not exists)

The repository should already contain the frontend directory structure. If for any reason it's missing or incomplete, ensure you have the following structure:

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── project_overview_panel.jsx
│   │   ├── progress_tracking_visualizations.jsx
│   │   └── project_manager_interaction_interface.jsx
│   ├── agent_conversation_monitoring_panel.jsx
│   ├── sprint_tracking_visualization.jsx
│   ├── project_dashboard.jsx
│   ├── App.js
│   ├── index.js
│   └── index.css
└── package.json
```

### 3. Configure Frontend Environment

Create a `.env` file in the frontend directory to configure environment variables:

```bash
cd frontend
touch .env
```

Add the following content to the `.env` file:

```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_ENV=development
```

Adjust the API URL if your backend is running on a different port or host.

### 4. Install Frontend Dependencies

```bash
# Make sure you're in the frontend directory
cd frontend

# Install all dependencies defined in package.json
npm install
```

> **Important Note**: The frontend dependencies require significant disk space (approximately 800MB). If you encounter "ENOSPC: no space left on device" errors during installation, free up disk space or deploy on a system with more available storage.

## Frontend Development and Testing

### 1. Start the Development Server

```bash
# Make sure you're in the frontend directory
cd frontend

# Start the development server
npm start
```

This will start the React development server and automatically open the application in your default browser at http://localhost:3000.

### 2. Testing the Frontend

The frontend includes several key components:

- Project Dashboard: The main interface showing project overview, agent status, and progress
- Agent Conversation Monitoring: View and filter conversations between agents
- Sprint Tracking: Visualize sprint progress and agent contributions
- Human Input Requests: Interface for responding to agent requests for information

Verify that all these components load correctly and that there are no console errors.

### 3. Build for Production

When you're ready to deploy to production:

```bash
# Create an optimized production build
npm run build
```

This will create a production-ready build in the `build` directory that can be served by any static file server.

## Serving the Production Build

### Option 1: Using serve (Quick Method)

```bash
# Install serve globally
npm install -g serve

# Serve the build directory
serve -s build
```

### Option 2: Using nginx (Production Method)

1. Install nginx:
```bash
sudo apt update
sudo apt install nginx
```

2. Configure nginx:
```bash
sudo nano /etc/nginx/sites-available/toronto-ai-team-agent
```

Add the following configuration:
```
server {
    listen 80;
    server_name your_domain.com;  # Replace with your domain or IP

    root /path/to/TorontoAITeamAgent/frontend/build;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

3. Enable the site and restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/toronto-ai-team-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Connecting Frontend to Backend

The frontend is configured to connect to the backend API at the URL specified in the `.env` file. Ensure your backend is running and accessible at this URL.

## Troubleshooting

### Module Not Found Error

If you encounter the error "Cannot find module './project_dashboard'", ensure you have the latest code from the repository. We've recently fixed this issue by adding all missing component files.

### Disk Space Issues

The React application has substantial dependencies. If you encounter disk space errors:

1. Clear npm cache: `npm cache clean --force`
2. Remove node_modules: `rm -rf node_modules`
3. Free up disk space on your system
4. Try installation again: `npm install`

### Other Common Issues

1. **Port already in use**: If port 3000 is already in use, React will prompt you to use a different port.

2. **Dependency conflicts**: If you encounter dependency conflicts, try:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Blank screen after deployment**: Check browser console for errors. This is often caused by missing dependencies or incorrect import paths.

4. **CORS issues**: If you see CORS errors in the console, ensure your backend is configured to allow requests from your frontend origin.

## Need Help?

If you continue to experience issues with deployment, please open an issue on the GitHub repository with details about the error and your environment.
