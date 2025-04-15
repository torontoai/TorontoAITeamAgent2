/**
 * TORONTO AI TEAM AGENT - PROPRIETARY
 * 
 * Copyright (c) 2025 TORONTO AI
 * Creator: David Tadeusz Chudak
 * All Rights Reserved
 * 
 * This file is part of the TORONTO AI TEAM AGENT software.
 * 
 * This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
 * which is licensed under the MIT License. The original license is included
 * in the LICENSE file in the root directory of this project.
 * 
 * This software has been substantially modified with proprietary enhancements.
 */

// UI Mockup for Enhanced Project Manager Interface with Human Input Request System
// This file contains mockup code for the enhanced UI that integrates the human input request system

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Container, 
  Typography, 
  Paper, 
  Grid, 
  Button, 
  CircularProgress, 
  Divider, 
  Tabs, 
  Tab, 
  TextField,
  Badge,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Menu,
  MenuItem,
  Tooltip,
  Alert,
  Snackbar
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Timeline, TimelineItem, TimelineSeparator, TimelineConnector, TimelineContent, TimelineDot } from '@mui/lab';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

// Icons
import NotificationsIcon from '@mui/icons-material/Notifications';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import FeedbackIcon from '@mui/icons-material/Feedback';
import FilterListIcon from '@mui/icons-material/FilterList';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import InfoIcon from '@mui/icons-material/Info';
import AssignmentIcon from '@mui/icons-material/Assignment';
import DashboardIcon from '@mui/icons-material/Dashboard';
import GroupIcon from '@mui/icons-material/Group';
import BarChartIcon from '@mui/icons-material/BarChart';
import ChatIcon from '@mui/icons-material/Chat';

// Import Human Input Request System component
import HumanInputRequestSystem from './human_input_request_system';

// Theme configuration for Manus AI-like appearance
const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
    },
    secondary: {
      main: '#f50057',
    },
    background: {
      default: '#f5f5f7',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          borderRadius: 8,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

// Mock data for demonstration
const mockTasks = [
  { id: 1, name: 'Setup project structure', status: 'completed', progress: 100, assignedTo: 'Developer 1', eta: '2h ago' },
  { id: 2, name: 'Implement user authentication', status: 'in_progress', progress: 65, assignedTo: 'Developer 2', eta: '3h remaining' },
  { id: 3, name: 'Design database schema', status: 'in_progress', progress: 40, assignedTo: 'Developer 3', eta: '5h remaining' },
  { id: 4, name: 'Create API endpoints', status: 'pending', progress: 0, assignedTo: 'Developer 1', eta: 'Not started' },
  { id: 5, name: 'Implement frontend components', status: 'pending', progress: 0, assignedTo: 'Developer 2', eta: 'Not started' },
];

const mockTeamActivity = [
  { time: '09:15 AM', agent: 'Project Manager', action: 'Created project plan and assigned initial tasks' },
  { time: '09:30 AM', agent: 'Developer 1', action: 'Started working on project structure setup' },
  { time: '10:45 AM', agent: 'Developer 1', action: 'Completed project structure setup' },
  { time: '11:00 AM', agent: 'Developer 2', action: 'Started implementing user authentication' },
  { time: '11:30 AM', agent: 'Developer 3', action: 'Started designing database schema' },
];

const mockPerformanceData = [
  { name: 'Dev 1', tasks: 4, completion: 85, efficiency: 90 },
  { name: 'Dev 2', tasks: 3, completion: 65, efficiency: 75 },
  { name: 'Dev 3', tasks: 2, completion: 40, efficiency: 80 },
];

// Mock notifications
const mockNotifications = [
  { id: 1, title: 'New input request', message: 'Developer 2 needs clarification on authentication requirements', read: false, timestamp: '10 min ago' },
  { id: 2, title: 'Task completed', message: 'Developer 1 has completed project structure setup', read: true, timestamp: '1 hour ago' },
  { id: 3, title: 'Deadline approaching', message: 'Database schema design is due in 5 hours', read: true, timestamp: '2 hours ago' },
];

// Enhanced Project Manager Interface Component
const EnhancedProjectManagerInterface = () => {
  // State for tabs and communication
  const [activeTab, setActiveTab] = useState(0);
  const [message, setMessage] = useState('');
  const [thinking, setThinking] = useState(false);
  const [thinkingProcess, setThinkingProcess] = useState([]);
  const [conversations, setConversations] = useState([
    { sender: 'system', content: 'Welcome to the TORONTO AI Team Agent Team AI system. I am your Project Manager agent and will be your primary point of contact. How can I assist you with your project today?' }
  ]);
  
  // State for notifications
  const [notifications, setNotifications] = useState(mockNotifications);
  const [notificationDrawerOpen, setNotificationDrawerOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(mockNotifications.filter(n => !n.read).length);
  
  // State for human input requests
  const [inputRequestsOpen, setInputRequestsOpen] = useState(true);
  const [pendingRequestsCount, setPendingRequestsCount] = useState(0);
  
  // State for snackbar
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });
  
  // State for agent menu
  const [agentMenuAnchor, setAgentMenuAnchor] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  
  // Effect to update pending requests count
  useEffect(() => {
    // This would be an API call in a real implementation
    setPendingRequestsCount(3);
  }, []);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleMessageSend = () => {
    if (!message.trim()) return;
    
    // Add user message to conversation
    setConversations([...conversations, { sender: 'user', content: message }]);
    setMessage('');
    
    // Simulate thinking process
    setThinking(true);
    setThinkingProcess([]);
    
    // Simulate thinking steps with timeouts
    setTimeout(() => setThinkingProcess(prev => [...prev, 'Analyzing request context and intent...']), 500);
    setTimeout(() => setThinkingProcess(prev => [...prev, 'Identifying relevant project components...']), 1200);
    setTimeout(() => setThinkingProcess(prev => [...prev, 'Consulting with developer agents for technical feasibility...']), 2000);
    setTimeout(() => setThinkingProcess(prev => [...prev, 'Formulating comprehensive response...']), 3000);
    
    // Simulate response after "thinking"
    setTimeout(() => {
      setThinking(false);
      setConversations(prev => [...prev, { 
        sender: 'system', 
        content: 'I understand your request. I'll coordinate with the development team to implement this feature. Based on our current workload and complexity assessment, we estimate this will take approximately 8 hours of development time. Would you like me to prioritize this task in our current sprint?' 
      }]);
    }, 4000);
  };
  
  const handleNotificationClick = () => {
    setNotificationDrawerOpen(true);
  };
  
  const handleNotificationClose = () => {
    setNotificationDrawerOpen(false);
    
    // Mark all as read
    setNotifications(notifications.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };
  
  const handleAgentMenuOpen = (event, agent) => {
    setAgentMenuAnchor(event.currentTarget);
    setSelectedAgent(agent);
  };
  
  const handleAgentMenuClose = () => {
    setAgentMenuAnchor(null);
    setSelectedAgent(null);
  };
  
  const handleAgentAction = (action) => {
    // Handle agent actions (view details, message, etc.)
    setSnackbar({
      open: true,
      message: `Action "${action}" performed on ${selectedAgent}`,
      severity: 'info'
    });
    
    handleAgentMenuClose();
  };
  
  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };
  
  // Helper component for LinearProgress
  const LinearProgress = ({ value, ...props }) => {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
        <Box sx={{ width: '100%', mr: 1 }}>
          <Box
            sx={{
              height: props.sx?.height || 4,
              borderRadius: props.sx?.borderRadius || 2,
              bgcolor: props.sx?.bgcolor || '#e0e0e0',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                left: 0,
                top: 0,
                bottom: 0,
                width: `${value}%`,
                bgcolor: props.sx?.['& .MuiLinearProgress-bar']?.bgcolor || '#1976d2',
                transition: 'width 0.4s ease',
              }}
            />
          </Box>
        </Box>
      </Box>
    );
  };

  return (
    <ThemeProvider theme={theme}>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Header with notifications */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">
            TORONTO AI Team Agent Team AI - Project Manager
          </Typography>
          <Box>
            <Tooltip title="Notifications">
              <IconButton onClick={handleNotificationClick}>
                <Badge badgeContent={unreadCount} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        {/* Human Input Requests Panel */}
        <HumanInputRequestSystem projectId="project123" />
        
        {/* Main Tabs */}
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
          <Tab label="Dashboard" icon={<DashboardIcon />} iconPosition="start" />
          <Tab label="Task Progress" icon={<AssignmentIcon />} iconPosition="start" />
          <Tab label="Team Activity" icon={<GroupIcon />} iconPosition="start" />
          <Tab label="Performance" icon={<BarChartIcon />} iconPosition="start" />
        </Tabs>
        
        {/* Dashboard Tab */}
        {activeTab === 0 && (
          <Grid container spacing={3}>
            {/* Project Status Summary */}
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, height: '100%' }}>
                <Typography variant="h5" gutterBottom>Project Status</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: '#e3f2fd', textAlign: 'center' }}>
                      <Typography variant="h6">5</Typography>
                      <Typography variant="body2">Total Tasks</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={4}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: '#e8f5e9', textAlign: 'center' }}>
                      <Typography variant="h6">1</Typography>
                      <Typography variant="body2">Completed</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={4}>
                    <Paper elevation={0} sx={{ p: 2, bgcolor: '#fff8e1', textAlign: 'center' }}>
                      <Typography variant="h6">2</Typography>
                      <Typography variant="body2">In Progress</Typography>
                    </Paper>
                  </Grid>
                </Grid>
                
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>Overall Progress</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress variant="determinate" value={40} sx={{ height: 10, borderRadius: 5 }} />
                    </Box>
                    <Box sx={{ minWidth: 35 }}>
                      <Typography variant="body2" color="text.secondary">40%</Typography>
                    </Box>
                  </Box>
                </Box>
                
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>Team Members</Typography>
                  <List>
                    {mockPerformanceData.map((agent, index) => (
                      <ListItem key={index} sx={{ py: 1 }}>
                        <ListItemIcon>
                          <Avatar>{agent.name.charAt(0)}</Avatar>
                        </ListItemIcon>
                        <ListItemText 
                          primary={agent.name} 
                          secondary={`${agent.tasks} tasks assigned`} 
                        />
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Chip 
                            label={`${agent.completion}% complete`} 
                            size="small" 
                            sx={{ 
                              bgcolor: agent.completion > 75 ? '#e8f5e9' : agent.completion > 50 ? '#fff8e1' : '#ffebee',
                              mr: 1
                            }} 
                          />
                          <IconButton 
                            size="small"
                            onClick={(e) => handleAgentMenuOpen(e, agent.name)}
                          >
                            <MoreVertIcon />
                          </IconButton>
                        </Box>
                      </ListItem>
                    ))}
                  </List>
                </Box>
              </Paper>
            </Grid>
            
            {/* Communication Interface */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h5">Communication</Typography>
                  <Tooltip title="Chat with Project Manager">
                    <IconButton size="small">
                      <ChatIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
                <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2, maxHeight: 300 }}>
                  {conversations.map((msg, index) => (
                    <Box 
                      key={index} 
                      sx={{ 
                        mb: 1, 
                        p: 1.5, 
                        borderRadius: 2,
                        bgcolor: msg.sender === 'user' ? '#e3f2fd' : '#f5f5f5',
                        alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '80%',
                        ml: msg.sender === 'user' ? 'auto' : 0
                      }}
                    >
                      <Typography variant="body2">{msg.content}</Typography>
                    </Box>
                  ))}
                </Box>
                
                {thinking && (
                  <Paper elevation={0} sx={{ p: 2, mb: 2, bgcolor: '#f8f9fa', borderRadius: 2, border: '1px dashed #ccc' }}>
                    <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Thinking Process:
                    </Typography>
                    {thinkingProcess.map((step, index) => (
                      <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                        • {step}
                      </Typography>
                    ))}
                    {thinkingProcess.length > 0 && (
                      <Box sx={{ display: 'flex', alignItems: 'center', ml: 2, mt: 1 }}>
                        <CircularProgress size={16} sx={{ mr: 1 }} />
                        <Typography variant="body2">Processing...</Typography>
                      </Box>
                    )}
                  </Paper>
                )}
                
                <Box sx={{ display: 'flex', mt: 'auto' }}>
                  <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Type your message..."
                    size="small"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleMessageSend()}
                    disabled={thinking}
                  />
                  <Button 
                    variant="contained" 
                    color="primary" 
                    sx={{ ml: 1 }} 
                    onClick={handleMessageSend}
                    disabled={thinking}
                  >
                    Send
                  </Button>
                </Box>
              </Paper>
            </Grid>
            
            {/* Recent Activity */}
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>Recent Team Activity</Typography>
                <Timeline position="alternate">
                  {mockTeamActivity.slice(0, 3).map((activity, index) => (
                    <TimelineItem key={index}>
                      <TimelineSeparator>
                        <TimelineDot color={index === 0 ? "primary" : "grey"} />
                        {index < 2 && <TimelineConnector />}
                      </TimelineSeparator>
                      <TimelineContent>
                        <Typography variant="subtitle2">{activity.time}</Typography>
                        <Typography variant="body2"><strong>{activity.agent}</strong>: {activity.action}</Typography>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              </Paper>
            </Grid>
          </Grid>
        )}
        
        {/* Task Progress Tab */}
        {activeTab === 1 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Task Progress</Typography>
            <Grid container spacing={2}>
              {mockTasks.map((task) => (
                <Grid item xs={12} key={task.id}>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Grid container alignItems="center">
                      <Grid item xs={6}>
                        <Typography variant="subtitle1">{task.name}</Typography>
                        <Typography variant="body2" color="text.secondary">Assigned to: {task.assignedTo}</Typography>
                      </Grid>
                      <Grid item xs={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Box sx={{ width: '100%', mr: 1 }}>
                            <LinearProgress 
                              variant="determinate" 
                              value={task.progress} 
                              sx={{ 
                                height: 8, 
                                borderRadius: 5,
                                bgcolor: '#e0e0e0',
                                '& .MuiLinearProgress-bar': {
                                  bgcolor: task.status === 'completed' ? '#4caf50' : '#2196f3'
                                }
                              }} 
                            />
                          </Box>
                          <Box sx={{ minWidth: 35 }}>
                            <Typography variant="body2" color="text.secondary">{task.progress}%</Typography>
                          </Box>
                        </Box>
                      </Grid>
                      <Grid item xs={3} sx={{ textAlign: 'right' }}>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            display: 'inline-block',
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 1,
                            bgcolor: task.status === 'completed' ? '#e8f5e9' : task.status === 'in_progress' ? '#fff8e1' : '#f5f5f5',
                            color: task.status === 'completed' ? '#2e7d32' : task.status === 'in_progress' ? '#f57c00' : '#757575',
                          }}
                        >
                          ETA: {task.eta}
                        </Typography>
                      </Grid>
                    </Grid>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}
        
        {/* Team Activity Tab */}
        {activeTab === 2 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Team Activity Timeline</Typography>
            <Timeline position="alternate">
              {mockTeamActivity.map((activity, index) => (
                <TimelineItem key={index}>
                  <TimelineSeparator>
                    <TimelineDot color={index === 0 ? "primary" : "grey"} />
                    {index < mockTeamActivity.length - 1 && <TimelineConnector />}
                  </TimelineSeparator>
                  <TimelineContent>
                    <Paper elevation={1} sx={{ p: 2 }}>
                      <Typography variant="subtitle2">{activity.time}</Typography>
                      <Typography variant="body2"><strong>{activity.agent}</strong>: {activity.action}</Typography>
                    </Paper>
                  </TimelineContent>
                </TimelineItem>
              ))}
            </Timeline>
          </Paper>
        )}
        
        {/* Performance Tab */}
        {activeTab === 3 && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>Team Performance</Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart
                data={mockPerformanceData}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Bar dataKey="tasks" name="Tasks Assigned" fill="#8884d8" />
                <Bar dataKey="completion" name="Completion Rate (%)" fill="#82ca9d" />
                <Bar dataKey="efficiency" name="Efficiency Score" fill="#ffc658" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        )}
        
        {/* Notifications Drawer */}
        <Drawer
          anchor="right"
          open={notificationDrawerOpen}
          onClose={handleNotificationClose}
        >
          <Box sx={{ width: 320, p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Notifications</Typography>
              <Button size="small" onClick={handleNotificationClose}>
                Mark all as read
              </Button>
            </Box>
            <Divider sx={{ mb: 2 }} />
            <List>
              {notifications.length === 0 ? (
                <ListItem>
                  <ListItemText primary="No notifications" />
                </ListItem>
              ) : (
                notifications.map((notification) => (
                  <ListItem 
                    key={notification.id}
                    sx={{ 
                      bgcolor: notification.read ? 'transparent' : 'rgba(63, 81, 181, 0.08)',
                      borderRadius: 1,
                      mb: 1
                    }}
                  >
                    <ListItemText 
                      primary={
                        <Typography variant="subtitle2" sx={{ fontWeight: notification.read ? 400 : 600 }}>
                          {notification.title}
                        </Typography>
                      }
                      secondary={
                        <>
                          <Typography variant="body2" sx={{ mb: 0.5 }}>
                            {notification.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {notification.timestamp}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                ))
              )}
            </List>
          </Box>
        </Drawer>
        
        {/* Agent Menu */}
        <Menu
          anchorEl={agentMenuAnchor}
          open={Boolean(agentMenuAnchor)}
          onClose={handleAgentMenuClose}
        >
          <MenuItem onClick={() => handleAgentAction('view')}>View Details</MenuItem>
          <MenuItem onClick={() => handleAgentAction('message')}>Send Message</MenuItem>
          <MenuItem onClick={() => handleAgentAction('tasks')}>View Tasks</MenuItem>
        </Menu>
        
        {/* Snackbar for notifications */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={6000}
          onClose={handleSnackbarClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Container>
    </ThemeProvider>
  );
};

// Helper component for Avatar
const Avatar = ({ children, ...props }) => {
  return (
    <Box
      sx={{
        width: 36,
        height: 36,
        borderRadius: '50%',
        bgcolor: '#3f51b5',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 'bold',
        ...props.sx
      }}
    >
      {children}
    </Box>
  );
};

export default EnhancedProjectManagerInterface;
