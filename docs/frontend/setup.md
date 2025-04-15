# Frontend Setup Guide

This guide provides detailed instructions for setting up the TORONTO AI TEAM AGENT frontend application.

## Prerequisites

Before proceeding, ensure you have:
- Completed the [Installation](../getting-started/installation.md) process
- Node.js 18+ and npm 8+
- At least 2GB of free disk space for frontend dependencies

## Repository Structure

The React application has the following key files and directories:

```
frontend/
├── node_modules/        # Dependencies (created after npm install)
├── public/
│   └── index.html       # HTML template
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── project_overview_panel.jsx
│   │   ├── progress_tracking_visualizations.jsx
│   │   └── project_manager_interaction_interface.jsx
│   ├── agent_conversation_monitoring_panel.jsx
│   ├── sprint_tracking_visualization.jsx
│   ├── project_dashboard.jsx  # Main dashboard component
│   ├── App.js                 # Main application component
│   ├── index.js               # Application entry point
│   └── index.css              # Global styles
└── package.json               # Dependencies and scripts
```

**Important**: All these files must be present for the application to work correctly. The error "Cannot find module './project_dashboard'" occurs when the `project_dashboard.jsx` file is missing or not in the correct location.

## Installation Steps

### 1. Navigate to the Frontend Directory

```bash
cd ~/toronto-ai-team-agent/frontend
```

### 2. Install Dependencies

```bash
npm install
```

This process may take several minutes as it downloads and installs all required packages.

**Important Notes**:
- The frontend dependencies require significant disk space (approximately 800MB-1GB).
- If you encounter "ENOSPC: no space left on device" errors, free up disk space or deploy on a system with more available storage.
- Modern React applications have many dependencies, so be patient during installation.

### 3. Verify Installation

After installation, verify that all React components are properly structured:

```bash
# Check the main components
ls -la src/App.js src/project_dashboard.jsx

# Check imported components
ls -la src/components/
ls -la src/agent_conversation_monitoring_panel.jsx src/sprint_tracking_visualization.jsx
```

### 4. Configure Environment

Create a `.env` file in the frontend directory:

```bash
touch .env
```

Add the following content to the `.env` file:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

### 5. Start the Development Server

Once all dependencies are installed and files are verified, start the development server:

```bash
npm start
```

This will:
1. Compile the React application
2. Start a development server on port 3000
3. Open your default web browser to http://localhost:3000

If the browser doesn't open automatically, you can manually navigate to http://localhost:3000.

## Building for Production

When you're ready to deploy to production:

```bash
# Create an optimized production build
npm run build
```

This will create a production-ready build in the `build` directory that can be served by any static file server.

## Troubleshooting

### Module Not Found Error

If you encounter the error "Cannot find module './project_dashboard'":

1. Verify all required component files are present in the correct locations
2. Check the import paths in App.js and other components
3. Pull the latest changes from the repository: `git pull`

### Disk Space Issues

If you encounter disk space errors:

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

## Next Steps

- [Frontend Configuration](./configuration.md) - For configuring the frontend application
- [Frontend Customization](./customization.md) - For customizing the UI components
- [Local Deployment Guide](../deployment/local-deployment.md) - For complete system deployment
