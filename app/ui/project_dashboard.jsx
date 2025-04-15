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

import React from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Divider,
  Button,
  IconButton,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  Menu,
  MenuItem,
  Badge,
  Avatar,
  Card,
  CardContent,
  CardHeader,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  CircularProgress
} from '@mui/material';

import {
  Dashboard as DashboardIcon,
  Assignment as AssignmentIcon,
  Timeline as TimelineIcon,
  Group as TeamIcon,
  Chat as ChatIcon,
  Assessment as MetricsIcon,
  BarChart as ResourcesIcon,
  Warning as RiskIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Search as SearchIcon,
  Help as HelpIcon,
  Menu as MenuIcon,
  MoreVert as MoreVertIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ArrowUpward as TrendUpIcon,
  ArrowDownward as TrendDownIcon,
  Flag as MilestoneIcon,
  AccessTime as TimeIcon,
  Code as CodeIcon,
  BugReport as BugIcon,
  Speed as PerformanceIcon,
  Security as SecurityIcon,
  Storage as DatabaseIcon,
  Brush as DesignIcon
} from '@mui/icons-material';

// Import chart components
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, 
  AreaChart, Area, ResponsiveContainer, XAxis, YAxis, 
  CartesianGrid, Tooltip as RechartsTooltip, Legend 
} from 'recharts';

// Import agent conversation panel
import AgentConversationMonitoringPanel from './agent_conversation_monitoring_panel';
import SprintTrackingVisualization from './sprint_tracking_visualization';
import HumanInputRequestSystem from './human_input_request_system';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
    subtitle1: {
      fontWeight: 400,
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 4,
        },
      },
    },
  },
});

// Mock data for project overview
const projectData = {
  name: 'E-Commerce Platform Redesign',
  progress: 68,
  status: 'on_track', // on_track, at_risk, behind
  startDate: '2025-03-15',
  endDate: '2025-06-30',
  nextMilestone: {
    name: 'Backend API Integration',
    dueDate: '2025-04-15',
    progress: 45
  },
  recentActivities: [
    { id: 1, agent: 'developer', action: 'completed', item: 'User Authentication Module', time: '2 hours ago' },
    { id: 2, agent: 'system_architect', action: 'updated', item: 'System Architecture Diagram', time: '4 hours ago' },
    { id: 3, agent: 'qa_testing_specialist', action: 'created', item: 'Test Cases for Payment Processing', time: '6 hours ago' },
    { id: 4, agent: 'project_manager', action: 'scheduled', item: 'Sprint Planning Meeting', time: '1 day ago' }
  ]
};

// Mock data for agent team status
const agentTeamData = {
  agents: [
    { id: 'pm-001', role: 'project_manager', name: 'Project Manager', status: 'active', tasks: 8, completion: 75 },
    { id: 'dev-001', role: 'developer', name: 'Developer', status: 'active', tasks: 12, completion: 60 },
    { id: 'arch-001', role: 'system_architect', name: 'System Architect', status: 'active', tasks: 6, completion: 80 },
    { id: 'qa-001', role: 'qa_testing_specialist', name: 'QA Testing Specialist', status: 'active', tasks: 9, completion: 55 },
    { id: 'devops-001', role: 'devops_engineer', name: 'DevOps Engineer', status: 'idle', tasks: 4, completion: 90 }
  ],
  roleDistribution: [
    { name: 'Development', value: 45 },
    { name: 'Architecture', value: 20 },
    { name: 'Testing', value: 15 },
    { name: 'Management', value: 10 },
    { name: 'DevOps', value: 10 }
  ]
};

// Mock data for tasks
const taskData = {
  columns: [
    { id: 'backlog', title: 'Backlog', tasks: [] },
    { id: 'todo', title: 'To Do', tasks: [] },
    { id: 'in_progress', title: 'In Progress', tasks: [] },
    { id: 'review', title: 'Review', tasks: [] },
    { id: 'done', title: 'Done', tasks: [] }
  ],
  tasks: [
    { id: 'task-1', title: 'Implement User Authentication', status: 'in_progress', priority: 'high', assignee: 'dev-001', dueDate: '2025-04-10', tags: ['frontend', 'security'] },
    { id: 'task-2', title: 'Design Database Schema', status: 'done', priority: 'high', assignee: 'arch-001', dueDate: '2025-04-05', tags: ['database', 'architecture'] },
    { id: 'task-3', title: 'Create API Documentation', status: 'review', priority: 'medium', assignee: 'arch-001', dueDate: '2025-04-12', tags: ['documentation', 'api'] },
    { id: 'task-4', title: 'Implement Payment Processing', status: 'todo', priority: 'high', assignee: 'dev-001', dueDate: '2025-04-18', tags: ['backend', 'payment'] },
    { id: 'task-5', title: 'Write Unit Tests for Auth Module', status: 'in_progress', priority: 'medium', assignee: 'qa-001', dueDate: '2025-04-11', tags: ['testing', 'security'] },
    { id: 'task-6', title: 'Set Up CI/CD Pipeline', status: 'todo', priority: 'medium', assignee: 'devops-001', dueDate: '2025-04-15', tags: ['devops', 'automation'] },
    { id: 'task-7', title: 'Design Product Listing UI', status: 'backlog', priority: 'medium', assignee: null, dueDate: '2025-04-20', tags: ['frontend', 'ui'] },
    { id: 'task-8', title: 'Implement Search Functionality', status: 'backlog', priority: 'low', assignee: null, dueDate: '2025-04-25', tags: ['frontend', 'search'] }
  ]
};

// Populate task columns
taskData.tasks.forEach(task => {
  const column = taskData.columns.find(col => col.id === task.status);
  if (column) {
    if (!column.tasks) column.tasks = [];
    column.tasks.push(task);
  }
});

// Mock data for timeline
const timelineData = {
  milestones: [
    { id: 1, name: 'Project Kickoff', date: '2025-03-15', completed: true },
    { id: 2, name: 'Requirements Gathering', date: '2025-03-30', completed: true },
    { id: 3, name: 'Backend API Integration', date: '2025-04-15', completed: false },
    { id: 4, name: 'Frontend Implementation', date: '2025-05-15', completed: false },
    { id: 5, name: 'Testing Phase', date: '2025-06-01', completed: false },
    { id: 6, name: 'Deployment', date: '2025-06-30', completed: false }
  ],
  dependencies: [
    { from: 1, to: 2 },
    { from: 2, to: 3 },
    { from: 3, to: 4 },
    { from: 4, to: 5 },
    { from: 5, to: 6 }
  ]
};

// Mock data for progress metrics
const progressMetricsData = {
  sprintBurndown: [
    { day: 'Day 1', planned: 100, actual: 100 },
    { day: 'Day 2', planned: 90, actual: 95 },
    { day: 'Day 3', planned: 80, actual: 85 },
    { day: 'Day 4', planned: 70, actual: 80 },
    { day: 'Day 5', planned: 60, actual: 70 },
    { day: 'Day 6', planned: 50, actual: 60 },
    { day: 'Day 7', planned: 40, actual: 50 },
    { day: 'Day 8', planned: 30, actual: 40 },
    { day: 'Day 9', planned: 20, actual: 30 },
    { day: 'Day 10', planned: 10, actual: 20 }
  ],
  velocity: [
    { sprint: 'Sprint 1', planned: 30, completed: 25 },
    { sprint: 'Sprint 2', planned: 35, completed: 30 },
    { sprint: 'Sprint 3', planned: 40, completed: 38 },
    { sprint: 'Current', planned: 45, completed: 30 }
  ],
  codeQuality: {
    coverage: 78,
    bugs: 12,
    vulnerabilities: 3,
    codeSmells: 24,
    duplications: 5
  }
};

// Mock data for resource allocation
const resourceAllocationData = {
  utilization: [
    { agent: 'Project Manager', allocated: 85, actual: 90 },
    { agent: 'Developer', allocated: 100, actual: 110 },
    { agent: 'System Architect', allocated: 70, actual: 65 },
    { agent: 'QA Testing Specialist', allocated: 60, actual: 55 },
    { agent: 'DevOps Engineer', allocated: 40, actual: 35 }
  ],
  skillCoverage: [
    { skill: 'Frontend Development', coverage: 90, demand: 85 },
    { skill: 'Backend Development', coverage: 85, demand: 90 },
    { skill: 'Database Design', coverage: 95, demand: 70 },
    { skill: 'Testing', coverage: 80, demand: 85 },
    { skill: 'DevOps', coverage: 75, demand: 60 }
  ],
  bottlenecks: [
    { area: 'Payment Integration', severity: 'high', impact: 'Schedule delay of 3 days' },
    { area: 'UI Testing Resources', severity: 'medium', impact: 'Potential quality issues' }
  ]
};

// Mock data for risk management
const riskManagementData = {
  risks: [
    { id: 1, name: 'API Integration Delay', probability: 'medium', impact: 'high', status: 'active', mitigation: 'Early prototype and testing' },
    { id: 2, name: 'Resource Shortage', probability: 'low', impact: 'high', status: 'mitigated', mitigation: 'Cross-training team members' },
    { id: 3, name: 'Security Vulnerabilities', probability: 'medium', impact: 'high', status: 'active', mitigation: 'Regular security audits' },
    { id: 4, name: 'Scope Creep', probability: 'high', impact: 'medium', status: 'active', mitigation: 'Strict change management process' }
  ],
  riskTrend: [
    { month: 'Jan', high: 4, medium: 3, low: 2 },
    { month: 'Feb', high: 3, medium: 4, low: 2 },
    { month: 'Mar', high: 3, medium: 3, low: 3 },
    { month: 'Apr', high: 2, medium: 3, low: 4 }
  ]
};

// Mock data for PM interaction
const pmInteractionData = {
  pendingRequests: [
    { id: 'req-1', type: 'decision', title: 'Authentication Method Selection', priority: 'high', from: 'system_architect', time: '2 hours ago', description: 'Need decision on whether to use OAuth or JWT for authentication.' },
    { id: 'req-2', type: 'clarification', title: 'Payment Gateway Requirements', priority: 'medium', from: 'developer', time: '5 hours ago', description: 'Need clarification on which payment gateways need to be supported.' },
    { id: 'req-3', type: 'approval', title: 'Sprint Plan Approval', priority: 'high', from: 'project_manager', time: '1 day ago', description: 'Sprint plan for next two weeks needs approval.' }
  ],
  recentMessages: [
    { id: 'msg-1', from: 'project_manager', content: 'The team has completed the database schema design ahead of schedule.', time: '3 hours ago' },
    { id: 'msg-2', from: 'project_manager', content: 'We need to schedule a review meeting for the API documentation.', time: '1 day ago' },
    { id: 'msg-3', from: 'project_manager', content: 'Risk assessment for the payment processing module has been updated.', time: '2 days ago' }
  ],
  suggestions: [
    { id: 'sug-1', title: 'Allocate more resources to payment processing', reason: 'Current velocity indicates potential delay', impact: 'high' },
    { id: 'sug-2', title: 'Consider third-party authentication service', reason: 'Would reduce development time by 40%', impact: 'medium' }
  ]
};

// Status color mapping
const statusColors = {
  on_track: '#4caf50',
  at_risk: '#ff9800',
  behind: '#f44336',
  high: '#f44336',
  medium: '#ff9800',
  low: '#4caf50',
  active: '#2196f3',
  mitigated: '#4caf50',
  completed: '#4caf50'
};

// Agent icon mapping
const agentIcons = {
  project_manager: <Avatar sx={{ bgcolor: '#1976d2' }}>PM</Avatar>,
  developer: <Avatar sx={{ bgcolor: '#4caf50' }}>DEV</Avatar>,
  system_architect: <Avatar sx={{ bgcolor: '#ff9800' }}>SA</Avatar>,
  qa_testing_specialist: <Avatar sx={{ bgcolor: '#f44336' }}>QA</Avatar>,
  devops_engineer: <Avatar sx={{ bgcolor: '#9c27b0' }}>DO</Avatar>
};

// Priority icon mapping
const priorityIcons = {
  high: <ErrorIcon color="error" />,
  medium: <WarningIcon color="warning" />,
  low: <InfoIcon color="success" />
};

/**
 * ProjectDashboard component
 * Main dashboard for the TORONTO AI Team Agent Team AI project management interface
 */
const ProjectDashboard = () => {
  // State for active tab
  const [activeTab, setActiveTab] = React.useState(0);
  
  // State for panels
  const [showConversations, setShowConversations] = React.useState(false);
  const [showSprints, setShowSprints] = React.useState(false);
  const [showRequests, setShowRequests] = React.useState(false);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Calculate days until next milestone
  const calculateDaysUntil = (dateString) => {
    const today = new Date();
    const targetDate = new Date(dateString);
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };
  
  // Render project overview panel
  const renderProjectOverview = () => {
    const daysUntilNextMilestone = calculateDaysUntil(projectData.nextMilestone.dueDate);
    
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5">{projectData.name}</Typography>
          <Chip 
            label={projectData.status === 'on_track' ? 'On Track' : projectData.status === 'at_risk' ? 'At Risk' : 'Behind'} 
            sx={{ 
              bgcolor: statusColors[projectData.status],
              color: 'white',
              fontWeight: 'bold'
            }} 
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="textSecondary" gutterBottom>Overall Progress</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress 
                variant="determinate" 
                value={projectData.progress} 
                sx={{ 
                  height: 10, 
                  borderRadius: 5,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: statusColors[projectData.status]
                  }
                }} 
              />
            </Box>
            <Typography variant="body2" color="textSecondary">{`${projectData.progress}%`}</Typography>
          </Box>
        </Box>
        
        <Box sx={{ mb: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <MilestoneIcon sx={{ mr: 1, color: '#1976d2' }} />
            <Typography variant="subtitle1">Next Milestone: {projectData.nextMilestone.name}</Typography>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" color="textSecondary">
              <TimeIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
              {daysUntilNextMilestone} days remaining
            </Typography>
            <Typography variant="body2" color="textSecondary">{`${projectData.nextMilestone.progress}% complete`}</Typography>
          </Box>
          <LinearProgress 
            variant="determinate" 
            value={projectData.nextMilestone.progress} 
            sx={{ 
              height: 6, 
              borderRadius: 3,
              backgroundColor: '#e0e0e0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: '#1976d2'
              }
            }} 
          />
        </Box>
        
        <Typography variant="subtitle1" gutterBottom>Recent Activity</Typography>
        <List sx={{ maxHeight: 240, overflow: 'auto' }}>
          {projectData.recentActivities.map((activity) => (
            <ListItem key={activity.id} sx={{ py: 1, px: 0 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                {agentIcons[activity.agent] || <Avatar>A</Avatar>}
              </ListItemIcon>
              <ListItemText 
                primary={
                  <Typography variant="body2">
                    <Typography component="span" sx={{ fontWeight: 'bold' }}>
                      {activity.agent.replace('_', ' ')}
                    </Typography>
                    {' '}
                    {activity.action}
                    {' '}
                    <Typography component="span" sx={{ fontWeight: 'medium' }}>
                      {activity.item}
                    </Typography>
                  </Typography>
                }
                secondary={activity.time}
              />
            </ListItem>
          ))}
        </List>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
          <Button variant="outlined" size="small">View All Activity</Button>
          <Button variant="contained" size="small">Project Details</Button>
        </Box>
      </Paper>
    );
  };
  
  // Render agent team status panel
  const renderAgentTeamStatus = () => {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>Agent Team Status</Typography>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Role Distribution</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={agentTeamData.roleDistribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                nameKey="name"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {agentTeamData.roleDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={['#1976d2', '#4caf50', '#ff9800', '#f44336', '#9c27b0'][index % 5]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Box>
        
        <Typography variant="subtitle2" gutterBottom>Agent Status</Typography>
        <List sx={{ maxHeight: 300, overflow: 'auto' }}>
          {agentTeamData.agents.map((agent) => (
            <ListItem key={agent.id} sx={{ py: 1, px: 0 }}>
              <ListItemIcon>
                {agentIcons[agent.role] || <Avatar>A</Avatar>}
              </ListItemIcon>
              <ListItemText 
                primary={
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {agent.name}
                    </Typography>
                    <Chip 
                      label={agent.status} 
                      size="small"
                      sx={{ 
                        bgcolor: agent.status === 'active' ? '#4caf50' : '#9e9e9e',
                        color: 'white',
                        height: 24
                      }} 
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                      <Typography variant="caption" color="textSecondary">
                        {agent.tasks} active tasks
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {agent.completion}% completion
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={agent.completion} 
                      sx={{ 
                        height: 4, 
                        borderRadius: 2,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: agent.completion > 75 ? '#4caf50' : agent.completion > 50 ? '#ff9800' : '#f44336'
                        }
                      }} 
                    />
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="outlined" 
            size="small" 
            onClick={() => setShowConversations(true)}
          >
            View Agent Conversations
          </Button>
        </Box>
      </Paper>
    );
  };
  
  // Render task management board
  const renderTaskManagementBoard = () => {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Task Management</Typography>
          <Box>
            <Button variant="outlined" size="small" sx={{ mr: 1 }}>Filter</Button>
            <Button variant="contained" size="small">Add Task</Button>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', overflowX: 'auto', pb: 2 }}>
          {taskData.columns.map((column) => (
            <Box 
              key={column.id} 
              sx={{ 
                minWidth: 280, 
                maxWidth: 280, 
                mr: 2, 
                bgcolor: '#f5f5f5', 
                borderRadius: 2,
                p: 2,
                height: 'fit-content'
              }}
            >
              <Typography 
                variant="subtitle2" 
                sx={{ 
                  mb: 2, 
                  pb: 1, 
                  borderBottom: '2px solid #e0e0e0',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                {column.title}
                <Chip 
                  label={column.tasks ? column.tasks.length : 0} 
                  size="small"
                  sx={{ height: 20, minWidth: 20 }}
                />
              </Typography>
              
              {column.tasks && column.tasks.map((task) => (
                <Card key={task.id} sx={{ mb: 2, boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'medium', flex: 1 }}>
                        {task.title}
                      </Typography>
                      {priorityIcons[task.priority]}
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Typography variant="caption" color="textSecondary" sx={{ mr: 1 }}>
                        Due: {task.dueDate}
                      </Typography>
                      {task.assignee && (
                        <Tooltip title={task.assignee.replace('_', ' ')}>
                          <Box sx={{ display: 'inline-flex' }}>
                            {agentIcons[agentTeamData.agents.find(a => a.id === task.assignee)?.role] || <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>A</Avatar>}
                          </Box>
                        </Tooltip>
                      )}
                    </Box>
                    
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {task.tags.map((tag) => (
                        <Chip 
                          key={tag} 
                          label={tag} 
                          size="small"
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              ))}
              
              {(!column.tasks || column.tasks.length === 0) && (
                <Box sx={{ p: 2, textAlign: 'center', color: 'text.secondary' }}>
                  <Typography variant="body2">No tasks</Typography>
                </Box>
              )}
            </Box>
          ))}
        </Box>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button 
            variant="outlined" 
            size="small" 
            onClick={() => setShowSprints(true)}
          >
            View Sprint Details
          </Button>
        </Box>
      </Paper>
    );
  };
  
  // Render timeline visualization
  const renderTimelineVisualization = () => {
    const today = new Date();
    const startDate = new Date(projectData.startDate);
    const endDate = new Date(projectData.endDate);
    const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
    
    // Calculate position percentage for each milestone
    const milestones = timelineData.milestones.map(milestone => {
      const milestoneDate = new Date(milestone.date);
      const daysSinceStart = Math.ceil((milestoneDate - startDate) / (1000 * 60 * 60 * 24));
      const position = (daysSinceStart / totalDays) * 100;
      return {
        ...milestone,
        position,
        isPast: milestoneDate < today
      };
    });
    
    // Calculate position percentage for today
    const daysSinceStart = Math.ceil((today - startDate) / (1000 * 60 * 60 * 24));
    const todayPosition = (daysSinceStart / totalDays) * 100;
    
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>Project Timeline</Typography>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            {projectData.startDate} to {projectData.endDate}
          </Typography>
          
          {/* Timeline bar */}
          <Box sx={{ position: 'relative', height: 200, mt: 4 }}>
            {/* Main timeline line */}
            <Box 
              sx={{ 
                position: 'absolute', 
                top: 80, 
                left: 0, 
                right: 0, 
                height: 4, 
                bgcolor: '#e0e0e0',
                borderRadius: 2
              }} 
            />
            
            {/* Today marker */}
            <Box 
              sx={{ 
                position: 'absolute', 
                top: 70, 
                left: `${todayPosition}%`, 
                width: 2, 
                height: 24, 
                bgcolor: '#f44336',
                zIndex: 2
              }} 
            />
            <Box 
              sx={{ 
                position: 'absolute', 
                top: 60, 
                left: `${todayPosition}%`, 
                transform: 'translateX(-50%)',
                bgcolor: '#f44336',
                color: 'white',
                px: 1,
                py: 0.5,
                borderRadius: 1,
                fontSize: '0.75rem',
                fontWeight: 'bold',
                zIndex: 2
              }} 
            >
              TODAY
            </Box>
            
            {/* Milestones */}
            {milestones.map((milestone, index) => (
              <React.Fragment key={milestone.id}>
                {/* Milestone marker */}
                <Box 
                  sx={{ 
                    position: 'absolute', 
                    top: 72, 
                    left: `${milestone.position}%`, 
                    width: 20, 
                    height: 20, 
                    borderRadius: '50%',
                    bgcolor: milestone.completed ? '#4caf50' : '#1976d2',
                    border: '3px solid white',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 1
                  }} 
                />
                
                {/* Milestone label - alternate top and bottom */}
                <Box 
                  sx={{ 
                    position: 'absolute', 
                    [index % 2 === 0 ? 'bottom' : 'top']: 100,
                    left: `${milestone.position}%`, 
                    transform: 'translateX(-50%)',
                    width: 150,
                    textAlign: 'center'
                  }} 
                >
                  <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                    {milestone.name}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    {milestone.date}
                  </Typography>
                  {milestone.completed && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                      <CheckCircleIcon sx={{ color: '#4caf50', fontSize: 14, mr: 0.5 }} />
                      <Typography variant="caption" sx={{ color: '#4caf50' }}>
                        Completed
                      </Typography>
                    </Box>
                  )}
                </Box>
              </React.Fragment>
            ))}
          </Box>
        </Box>
        
        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle2" gutterBottom>Critical Path</Typography>
          <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
            <Typography variant="body2">
              The critical path includes: Project Kickoff → Requirements Gathering → Backend API Integration → Frontend Implementation → Testing Phase → Deployment
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Timeline Comparison</Typography>
          <ResponsiveContainer width="100%" height={100}>
            <BarChart
              data={[
                { name: 'Planned', value: 100 },
                { name: 'Actual', value: 68 }
              ]}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis type="category" dataKey="name" />
              <Bar dataKey="value" fill="#1976d2" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      </Paper>
    );
  };
  
  // Render project manager interaction hub
  const renderPMInteractionHub = () => {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Project Manager Interaction</Typography>
          <Button 
            variant="outlined" 
            size="small"
            onClick={() => setShowRequests(true)}
          >
            View All Requests
          </Button>
        </Box>
        
        <Typography variant="subtitle2" gutterBottom>Pending Requests</Typography>
        <List sx={{ mb: 3 }}>
          {pmInteractionData.pendingRequests.map((request) => (
            <Card key={request.id} sx={{ mb: 2, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={request.type} 
                      size="small"
                      sx={{ 
                        mr: 1, 
                        bgcolor: request.type === 'decision' ? '#1976d2' : request.type === 'clarification' ? '#ff9800' : '#4caf50',
                        color: 'white',
                        height: 24
                      }} 
                    />
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {request.title}
                    </Typography>
                  </Box>
                  {priorityIcons[request.priority]}
                </Box>
                
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {request.description}
                </Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="caption" color="textSecondary" sx={{ mr: 1 }}>
                      From: {request.from.replace('_', ' ')}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {request.time}
                    </Typography>
                  </Box>
                  <Button variant="contained" size="small">Respond</Button>
                </Box>
              </CardContent>
            </Card>
          ))}
        </List>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle2" gutterBottom>Recent Messages</Typography>
        <List sx={{ mb: 3 }}>
          {pmInteractionData.recentMessages.map((message) => (
            <ListItem key={message.id} sx={{ px: 0, py: 1 }}>
              <ListItemIcon sx={{ minWidth: 40 }}>
                {agentIcons[message.from] || <Avatar>A</Avatar>}
              </ListItemIcon>
              <ListItemText 
                primary={message.content}
                secondary={message.time}
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
          ))}
        </List>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle2" gutterBottom>PM Suggestions</Typography>
        <List>
          {pmInteractionData.suggestions.map((suggestion) => (
            <Card key={suggestion.id} sx={{ mb: 2, bgcolor: '#f5f5f5', boxShadow: 'none' }}>
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                    {suggestion.title}
                  </Typography>
                  <Chip 
                    label={suggestion.impact} 
                    size="small"
                    sx={{ 
                      bgcolor: statusColors[suggestion.impact],
                      color: 'white',
                      height: 24
                    }} 
                  />
                </Box>
                <Typography variant="body2" color="textSecondary">
                  {suggestion.reason}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </List>
      </Paper>
    );
  };
  
  // Render progress metrics dashboard
  const renderProgressMetricsDashboard = () => {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>Progress Metrics</Typography>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>Sprint Burndown</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={progressMetricsData.sprintBurndown}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="planned" stroke="#1976d2" strokeWidth={2} />
              <Line type="monotone" dataKey="actual" stroke="#f44336" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>Velocity Tracking</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={progressMetricsData.velocity}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="sprint" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="planned" fill="#1976d2" />
              <Bar dataKey="completed" fill="#4caf50" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
        
        <Box>
          <Typography variant="subtitle2" gutterBottom>Code Quality Metrics</Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} md={4}>
              <Card sx={{ bgcolor: '#f5f5f5', boxShadow: 'none' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Test Coverage
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CircularProgress 
                      variant="determinate" 
                      value={progressMetricsData.codeQuality.coverage} 
                      sx={{ 
                        color: progressMetricsData.codeQuality.coverage > 75 ? '#4caf50' : progressMetricsData.codeQuality.coverage > 50 ? '#ff9800' : '#f44336',
                        mr: 1
                      }} 
                    />
                    <Typography variant="h6">
                      {progressMetricsData.codeQuality.coverage}%
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card sx={{ bgcolor: '#f5f5f5', boxShadow: 'none' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Bugs
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <BugIcon sx={{ color: '#f44336', mr: 1 }} />
                    <Typography variant="h6">
                      {progressMetricsData.codeQuality.bugs}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card sx={{ bgcolor: '#f5f5f5', boxShadow: 'none' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Vulnerabilities
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <SecurityIcon sx={{ color: '#ff9800', mr: 1 }} />
                    <Typography variant="h6">
                      {progressMetricsData.codeQuality.vulnerabilities}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card sx={{ bgcolor: '#f5f5f5', boxShadow: 'none' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Code Smells
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <CodeIcon sx={{ color: '#9c27b0', mr: 1 }} />
                    <Typography variant="h6">
                      {progressMetricsData.codeQuality.codeSmells}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} md={4}>
              <Card sx={{ bgcolor: '#f5f5f5', boxShadow: 'none' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Duplications
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <ContentCopyIcon sx={{ color: '#607d8b', mr: 1 }} />
                    <Typography variant="h6">
                      {progressMetricsData.codeQuality.duplications}%
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    );
  };
  
  // Render resource allocation view
  const renderResourceAllocationView = () => {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>Resource Allocation</Typography>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>Agent Utilization</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={resourceAllocationData.utilization}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" />
              <YAxis type="category" dataKey="agent" />
              <Tooltip />
              <Legend />
              <Bar dataKey="allocated" name="Allocated %" fill="#1976d2" />
              <Bar dataKey="actual" name="Actual %" fill="#f44336" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>Skill Coverage vs. Demand</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={resourceAllocationData.skillCoverage}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="coverage" name="Coverage %" fill="#4caf50" />
              <Bar dataKey="demand" name="Demand %" fill="#ff9800" />
            </BarChart>
          </ResponsiveContainer>
        </Box>
        
        <Box>
          <Typography variant="subtitle2" gutterBottom>Bottlenecks</Typography>
          <List>
            {resourceAllocationData.bottlenecks.map((bottleneck, index) => (
              <Card key={index} sx={{ mb: 2, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {bottleneck.area}
                    </Typography>
                    <Chip 
                      label={bottleneck.severity} 
                      size="small"
                      sx={{ 
                        bgcolor: statusColors[bottleneck.severity],
                        color: 'white',
                        height: 24
                      }} 
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    Impact: {bottleneck.impact}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </List>
        </Box>
      </Paper>
    );
  };
  
  // Render risk management panel
  const renderRiskManagementPanel = () => {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
        <Typography variant="h6" gutterBottom>Risk Management</Typography>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>Active Risks</Typography>
          <List>
            {riskManagementData.risks.filter(risk => risk.status === 'active').map((risk) => (
              <Card key={risk.id} sx={{ mb: 2, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {risk.name}
                    </Typography>
                    <Box sx={{ display: 'flex' }}>
                      <Chip 
                        label={`P: ${risk.probability}`} 
                        size="small"
                        sx={{ 
                          mr: 0.5,
                          bgcolor: statusColors[risk.probability],
                          color: 'white',
                          height: 24
                        }} 
                      />
                      <Chip 
                        label={`I: ${risk.impact}`} 
                        size="small"
                        sx={{ 
                          bgcolor: statusColors[risk.impact],
                          color: 'white',
                          height: 24
                        }} 
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    Mitigation: {risk.mitigation}
                  </Typography>
                </CardContent>
              </Card>
            ))}
          </List>
        </Box>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="subtitle2" gutterBottom>Risk Trend</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={riskManagementData.riskTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="high" stackId="1" stroke="#f44336" fill="#f44336" fillOpacity={0.6} />
              <Area type="monotone" dataKey="medium" stackId="1" stroke="#ff9800" fill="#ff9800" fillOpacity={0.6} />
              <Area type="monotone" dataKey="low" stackId="1" stroke="#4caf50" fill="#4caf50" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
        
        <Box>
          <Typography variant="subtitle2" gutterBottom>Early Warning Indicators</Typography>
          <List>
            <ListItem sx={{ px: 0, py: 1 }}>
              <ListItemIcon>
                <TrendUpIcon sx={{ color: '#f44336' }} />
              </ListItemIcon>
              <ListItemText 
                primary="API response times increasing by 15% over past week"
                secondary="May impact performance and user experience"
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
            <ListItem sx={{ px: 0, py: 1 }}>
              <ListItemIcon>
                <TrendUpIcon sx={{ color: '#ff9800' }} />
              </ListItemIcon>
              <ListItemText 
                primary="Test failure rate increased to 8% in payment module"
                secondary="May indicate integration issues with payment gateway"
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
            </ListItem>
          </List>
        </Box>
      </Paper>
    );
  };
  
  // Render dashboard content based on active tab
  const renderDashboardContent = () => {
    switch (activeTab) {
      case 0: // Overview
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={4}>
              {renderProjectOverview()}
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              {renderAgentTeamStatus()}
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              {renderPMInteractionHub()}
            </Grid>
            <Grid item xs={12}>
              {renderTaskManagementBoard()}
            </Grid>
            <Grid item xs={12}>
              {renderTimelineVisualization()}
            </Grid>
          </Grid>
        );
      case 1: // Tasks
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {renderTaskManagementBoard()}
            </Grid>
          </Grid>
        );
      case 2: // Timeline
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {renderTimelineVisualization()}
            </Grid>
          </Grid>
        );
      case 3: // Team
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              {renderAgentTeamStatus()}
            </Grid>
            <Grid item xs={12} md={6}>
              {renderResourceAllocationView()}
            </Grid>
          </Grid>
        );
      case 4: // PM Chat
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {renderPMInteractionHub()}
            </Grid>
          </Grid>
        );
      case 5: // Metrics
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {renderProgressMetricsDashboard()}
            </Grid>
          </Grid>
        );
      case 6: // Resources
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {renderResourceAllocationView()}
            </Grid>
          </Grid>
        );
      case 7: // Risks
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {renderRiskManagementPanel()}
            </Grid>
          </Grid>
        );
      default:
        return null;
    }
  };
  
  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        {/* App Bar */}
        <AppBar position="static">
          <Toolbar>
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              TORONTO AI Team Agent Team AI
            </Typography>
            <IconButton color="inherit">
              <Badge badgeContent={4} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <IconButton color="inherit">
              <SearchIcon />
            </IconButton>
            <IconButton color="inherit">
              <HelpIcon />
            </IconButton>
            <IconButton color="inherit">
              <SettingsIcon />
            </IconButton>
            <Avatar sx={{ ml: 2 }}>U</Avatar>
          </Toolbar>
        </AppBar>
        
        {/* Tabs */}
        <Box sx={{ bgcolor: 'background.paper', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ px: 2 }}
          >
            <Tab icon={<DashboardIcon />} label="Overview" />
            <Tab icon={<AssignmentIcon />} label="Tasks" />
            <Tab icon={<TimelineIcon />} label="Timeline" />
            <Tab icon={<TeamIcon />} label="Team" />
            <Tab icon={<ChatIcon />} label="PM Chat" />
            <Tab icon={<MetricsIcon />} label="Metrics" />
            <Tab icon={<ResourcesIcon />} label="Resources" />
            <Tab icon={<RiskIcon />} label="Risks" />
          </Tabs>
        </Box>
        
        {/* Main Content */}
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 3, bgcolor: 'background.default' }}>
          {renderDashboardContent()}
        </Box>
        
        {/* Agent Conversation Monitoring Panel */}
        <AgentConversationMonitoringPanel 
          open={showConversations} 
          onClose={() => setShowConversations(false)} 
        />
        
        {/* Sprint Tracking Visualization */}
        <SprintTrackingVisualization 
          open={showSprints} 
          onClose={() => setShowSprints(false)} 
        />
        
        {/* Human Input Request System */}
        <HumanInputRequestSystem 
          open={showRequests} 
          onClose={() => setShowRequests(false)} 
        />
      </Box>
    </ThemeProvider>
  );
};

export default ProjectDashboard;
