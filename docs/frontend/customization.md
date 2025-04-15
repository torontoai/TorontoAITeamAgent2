# Frontend Customization Guide

This guide provides instructions for customizing the TORONTO AI TEAM AGENT frontend application to match your specific requirements and branding.

## Prerequisites

- Completed the [Frontend Setup](./setup.md)
- Configured the frontend as described in [Frontend Configuration](./configuration.md)

## Theme Customization

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
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    // Add more typography customizations as needed
  },
});
```

## Component Customization

Each component in the dashboard can be customized to match your requirements:

### Project Overview Panel

Edit `src/components/project_overview_panel.jsx` to customize:
- Project information display
- Status indicators
- Progress metrics
- Team member listings

Example customization:

```javascript
// Customize the project status display
const getStatusColor = (status) => {
  switch (status.toLowerCase()) {
    case 'completed':
      return '#4caf50'; // Green
    case 'in progress':
      return '#2196f3'; // Blue
    case 'blocked':
      return '#f44336'; // Red
    case 'planning':
      return '#ff9800'; // Orange
    default:
      return '#9e9e9e'; // Grey
  }
};
```

### Progress Tracking Visualizations

Edit `src/components/progress_tracking_visualizations.jsx` to customize:
- Chart types (bar, line, pie)
- Data visualization options
- Time period selections
- Metric calculations

Example customization:

```javascript
// Customize chart colors
const chartColors = {
  completed: '#4caf50',
  inProgress: '#2196f3',
  blocked: '#f44336',
  planning: '#ff9800',
};
```

### Project Manager Interaction Interface

Edit `src/components/project_manager_interaction_interface.jsx` to customize:
- Message display format
- Input controls
- Attachment handling
- Response formatting

Example customization:

```javascript
// Customize message display
const MessageBubble = ({ message, isUser }) => (
  <div className={`message-bubble ${isUser ? 'user-message' : 'agent-message'}`}>
    <div className="message-header">
      <span className="sender">{isUser ? 'You' : message.sender}</span>
      <span className="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
    </div>
    <div className="message-content">{message.content}</div>
  </div>
);
```

## Layout Customization

### Dashboard Layout

Edit `src/project_dashboard.jsx` to customize:
- Component arrangement
- Grid layout
- Responsive behavior
- Panel sizes

Example customization:

```javascript
// Customize dashboard layout
<Grid container spacing={3}>
  <Grid item xs={12} md={8}>
    <ProjectOverviewPanel project={currentProject} />
  </Grid>
  <Grid item xs={12} md={4}>
    <ProgressTrackingVisualizations projectId={currentProject.id} />
  </Grid>
  <Grid item xs={12}>
    <ProjectManagerInteractionInterface projectId={currentProject.id} />
  </Grid>
</Grid>
```

### Navigation

Edit `src/App.js` to customize:
- Navigation menu items
- Routing configuration
- Page transitions
- Header and footer content

Example customization:

```javascript
// Customize navigation menu
const navigationItems = [
  { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
  { label: 'Projects', path: '/projects', icon: <FolderIcon /> },
  { label: 'Team', path: '/team', icon: <PeopleIcon /> },
  { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
];
```

## Styling Customization

### CSS Customization

Create or edit CSS files to customize styles:

```bash
# Create a custom styles file
touch src/custom-styles.css
```

Add your custom styles:

```css
/* Custom styles */
.dashboard-container {
  padding: 24px;
  background-color: #f9f9f9;
}

.project-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-in-out;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

Import your custom styles in the appropriate component:

```javascript
import './custom-styles.css';
```

### Styled Components

For component-specific styling, you can use styled-components:

```bash
# Install styled-components
npm install styled-components
```

Create styled components:

```javascript
import styled from 'styled-components';

const StyledCard = styled.div`
  padding: 16px;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  h2 {
    color: ${props => props.theme.primary || '#1976d2'};
    margin-top: 0;
  }
`;
```

## Logo and Branding

### Replacing the Logo

1. Prepare your logo file (SVG or PNG recommended)
2. Place it in the `public` directory
3. Update the logo reference in your components:

```javascript
// Example logo replacement in a header component
<img 
  src="/your-logo.svg" 
  alt="TORONTO AI TEAM AGENT" 
  className="header-logo" 
/>
```

### Updating Favicon

1. Generate favicon files using a tool like [favicon.io](https://favicon.io/)
2. Replace the favicon files in the `public` directory
3. Update the references in `public/index.html` if needed

## Advanced Customization

### Custom Components

Create new custom components to extend functionality:

```bash
# Create a new component
touch src/components/custom_dashboard_widget.jsx
```

Implement your custom component:

```javascript
import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography } from '@mui/material';

const CustomDashboardWidget = ({ title, dataSource }) => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // Fetch data or process input
    const fetchData = async () => {
      // Implementation details
    };
    
    fetchData();
  }, [dataSource]);
  
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{title}</Typography>
        {/* Widget content */}
      </CardContent>
    </Card>
  );
};

export default CustomDashboardWidget;
```

### Custom Hooks

Create reusable hooks for common functionality:

```bash
# Create a custom hook
touch src/hooks/useProjectData.js
```

Implement your custom hook:

```javascript
import { useState, useEffect } from 'react';

const useProjectData = (projectId) => {
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        // Fetch project data
        const response = await fetch(`/api/projects/${projectId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch project');
        }
        const data = await response.json();
        setProject(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProject();
  }, [projectId]);
  
  return { project, loading, error };
};

export default useProjectData;
```

## Next Steps

- [Frontend Configuration](./configuration.md) - For configuring the frontend application
- [Local Deployment Guide](../deployment/local-deployment.md) - For complete system deployment
- [Troubleshooting Guide](../troubleshooting/common-issues.md) - For resolving common issues
