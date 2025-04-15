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

import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  LinearProgress,
  Chip,
  Avatar,
  Tooltip,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { 
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import {
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  DonutLarge as DonutLargeIcon,
  Flag as FlagIcon,
  MoreVert as MoreVertIcon,
  Add as AddIcon,
  Code as CodeIcon,
  Architecture as ArchitectureIcon,
  Storage as StorageIcon,
  Security as SecurityIcon,
  DesignServices as DesignServicesIcon,
  Build as BuildIcon,
  BugReport as BugReportIcon,
  Info as InfoIcon,
  Timeline as TimelineIcon,
  CalendarToday as CalendarTodayIcon,
  BarChart as BarChartIcon,
  FilterList as FilterListIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

/**
 * Sprint Tracking Visualization Component
 * 
 * This component provides comprehensive visualization of sprint progress,
 * task assignments, and agent contributions to enable effective monitoring
 * of the multi-agent team's performance.
 */
const SprintTrackingVisualization = ({
  projectId,
  onClose,
  open = false
}) => {
  // State for sprint data
  const [sprintData, setSprintData] = useState({
    currentSprint: null,
    sprints: [],
    loading: true,
    error: null
  });
  
  // State for agent contributions
  const [agentContributions, setAgentContributions] = useState({
    byRole: {},
    byTask: {},
    loading: true,
    error: null
  });
  
  // State for task details
  const [taskDetails, setTaskDetails] = useState({
    selectedTask: null,
    showDialog: false,
    history: [],
    loading: false
  });
  
  // State for view options
  const [viewOptions, setViewOptions] = useState({
    sprintFilter: 'current',
    taskStatusFilter: 'all',
    groupBy: 'status'
  });
  
  // Auto-refresh interval reference
  const refreshIntervalRef = useRef(null);
  
  // Role icon mapping
  const roleIconMap = {
    'project_manager': <AssignmentIcon />,
    'product_manager': <TimelineIcon />,
    'developer': <CodeIcon />,
    'system_architect': <ArchitectureIcon />,
    'devops_engineer': <BuildIcon />,
    'qa_testing_specialist': <BugReportIcon />,
    'security_engineer': <SecurityIcon />,
    'database_engineer': <StorageIcon />,
    'ui_ux_designer': <DesignServicesIcon />
  };
  
  // Get role icon by role name
  const getRoleIcon = (role) => {
    return roleIconMap[role] || <InfoIcon />;
  };
  
  // Get color by agent role
  const getAgentColor = (role) => {
    const colorMap = {
      'project_manager': '#4caf50',
      'product_manager': '#2196f3',
      'developer': '#ff9800',
      'system_architect': '#9c27b0',
      'devops_engineer': '#f44336',
      'qa_testing_specialist': '#00bcd4',
      'security_engineer': '#607d8b',
      'database_engineer': '#795548',
      'ui_ux_designer': '#e91e63'
    };
    
    return colorMap[role] || '#757575';
  };
  
  // Get status color
  const getStatusColor = (status) => {
    const statusColorMap = {
      'not_started': '#9e9e9e',
      'in_progress': '#2196f3',
      'in_review': '#ff9800',
      'blocked': '#f44336',
      'completed': '#4caf50'
    };
    
    return statusColorMap[status] || '#757575';
  };
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  // Calculate days remaining
  const calculateDaysRemaining = (endDate) => {
    if (!endDate) return 0;
    const end = new Date(endDate);
    const today = new Date();
    const diffTime = end - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };
  
  // Handle view option change
  const handleViewOptionChange = (option, value) => {
    setViewOptions({
      ...viewOptions,
      [option]: value
    });
  };
  
  // Handle task selection
  const handleTaskSelect = async (task) => {
    setTaskDetails({
      ...taskDetails,
      selectedTask: task,
      showDialog: true,
      loading: true
    });
    
    try {
      // This would be replaced with an actual API call
      // For now, simulate a fetch with mock data
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock task history data
      const mockTaskHistory = [
        {
          id: 'event-1',
          timestamp: '2025-04-01T10:00:00.000Z',
          agent: 'project_manager',
          action: 'created',
          details: 'Task created and assigned to developer'
        },
        {
          id: 'event-2',
          timestamp: '2025-04-01T14:30:00.000Z',
          agent: 'developer',
          action: 'status_update',
          details: 'Started implementation, estimated completion in 2 days'
        },
        {
          id: 'event-3',
          timestamp: '2025-04-02T09:15:00.000Z',
          agent: 'system_architect',
          action: 'comment',
          details: 'Provided technical guidance on implementation approach'
        },
        {
          id: 'event-4',
          timestamp: '2025-04-02T16:45:00.000Z',
          agent: 'developer',
          action: 'status_update',
          details: 'Implementation 60% complete, on track for deadline'
        },
        {
          id: 'event-5',
          timestamp: '2025-04-03T11:20:00.000Z',
          agent: 'qa_testing_specialist',
          action: 'comment',
          details: 'Created test cases for this feature'
        }
      ];
      
      setTaskDetails({
        ...taskDetails,
        selectedTask: task,
        showDialog: true,
        history: mockTaskHistory,
        loading: false
      });
    } catch (error) {
      console.error('Error fetching task history:', error);
      setTaskDetails({
        ...taskDetails,
        loading: false,
        history: []
      });
    }
  };
  
  // Close task details dialog
  const handleCloseTaskDetails = () => {
    setTaskDetails({
      ...taskDetails,
      showDialog: false
    });
  };
  
  // Fetch sprint data
  const fetchSprintData = async () => {
    setSprintData({
      ...sprintData,
      loading: true,
      error: null
    });
    
    try {
      // This would be replaced with an actual API call
      // For now, simulate a fetch with mock data
      await new Promise(resolve => setTimeout(resolve, 700));
      
      // Mock sprint data
      const mockCurrentSprint = {
        id: 'sprint-1',
        name: 'Sprint 1',
        goal: 'Implement core authentication and user profile features',
        startDate: '2025-04-01',
        endDate: '2025-04-14',
        progress: 35,
        tasks: [
          {
            id: 'task-1',
            name: 'User Authentication Feature',
            description: 'Implement secure user authentication with JWT and OAuth2',
            assignedTo: 'developer',
            progress: 60,
            status: 'in_progress',
            priority: 'high',
            estimatedHours: 16,
            actualHours: 10,
            dependencies: []
          },
          {
            id: 'task-2',
            name: 'Authentication Architecture Design',
            description: 'Design the architecture for the authentication system',
            assignedTo: 'system_architect',
            progress: 100,
            status: 'completed',
            priority: 'high',
            estimatedHours: 8,
            actualHours: 6,
            dependencies: []
          },
          {
            id: 'task-3',
            name: 'Authentication Test Cases',
            description: 'Create comprehensive test cases for authentication features',
            assignedTo: 'qa_testing_specialist',
            progress: 100,
            status: 'completed',
            priority: 'medium',
            estimatedHours: 8,
            actualHours: 7,
            dependencies: ['task-2']
          },
          {
            id: 'task-4',
            name: 'User Profile UI Design',
            description: 'Create wireframes and design for user profile pages',
            assignedTo: 'ui_ux_designer',
            progress: 80,
            status: 'in_progress',
            priority: 'medium',
            estimatedHours: 12,
            actualHours: 10,
            dependencies: []
          },
          {
            id: 'task-5',
            name: 'Database Schema for User Data',
            description: 'Design and implement database schema for user profiles',
            assignedTo: 'database_engineer',
            progress: 90,
            status: 'in_review',
            priority: 'high',
            estimatedHours: 6,
            actualHours: 5,
            dependencies: []
          },
          {
            id: 'task-6',
            name: 'Security Review of Auth Implementation',
            description: 'Perform security review of authentication implementation',
            assignedTo: 'security_engineer',
            progress: 0,
            status: 'not_started',
            priority: 'high',
            estimatedHours: 8,
            actualHours: 0,
            dependencies: ['task-1']
          },
          {
            id: 'task-7',
            name: 'CI/CD Pipeline for Auth Service',
            description: 'Set up continuous integration and deployment for auth service',
            assignedTo: 'devops_engineer',
            progress: 30,
            status: 'in_progress',
            priority: 'low',
            estimatedHours: 6,
            actualHours: 2,
            dependencies: []
          },
          {
            id: 'task-8',
            name: 'User Profile API Endpoints',
            description: 'Implement API endpoints for user profile management',
            assignedTo: 'developer',
            progress: 20,
            status: 'in_progress',
            priority: 'medium',
            estimatedHours: 12,
            actualHours: 3,
            dependencies: ['task-5']
          }
        ]
      };
      
      const mockSprints = [
        {
          id: 'sprint-1',
          name: 'Sprint 1',
          startDate: '2025-04-01',
          endDate: '2025-04-14',
          progress: 35,
          taskCount: 8,
          completedTaskCount: 2
        },
        {
          id: 'sprint-2',
          name: 'Sprint 2',
          startDate: '2025-04-15',
          endDate: '2025-04-28',
          progress: 0,
          taskCount: 10,
          completedTaskCount: 0
        },
        {
          id: 'sprint-3',
          name: 'Sprint 3',
          startDate: '2025-04-29',
          endDate: '2025-05-12',
          progress: 0,
          taskCount: 12,
          completedTaskCount: 0
        }
      ];
      
      setSprintData({
        currentSprint: mockCurrentSprint,
        sprints: mockSprints,
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Error fetching sprint data:', error);
      setSprintData({
        ...sprintData,
        loading: false,
        error: 'Failed to load sprint data'
      });
    }
  };
  
  // Fetch agent contributions
  const fetchAgentContributions = async () => {
    setAgentContributions({
      ...agentContributions,
      loading: true,
      error: null
    });
    
    try {
      // This would be replaced with an actual API call
      // For now, simulate a fetch with mock data
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock agent contributions data
      const mockAgentContributions = {
        byRole: {
          'developer': {
            tasksAssigned: 2,
            tasksCompleted: 0,
            totalHours: 13,
            progress: 40
          },
          'system_architect': {
            tasksAssigned: 1,
            tasksCompleted: 1,
            totalHours: 6,
            progress: 100
          },
          'qa_testing_specialist': {
            tasksAssigned: 1,
            tasksCompleted: 1,
            totalHours: 7,
            progress: 100
          },
          'ui_ux_designer': {
            tasksAssigned: 1,
            tasksCompleted: 0,
            totalHours: 10,
            progress: 80
          },
          'database_engineer': {
            tasksAssigned: 1,
            tasksCompleted: 0,
            totalHours: 5,
            progress: 90
          },
          'security_engineer': {
            tasksAssigned: 1,
            tasksCompleted: 0,
            totalHours: 0,
            progress: 0
          },
          'devops_engineer': {
            tasksAssigned: 1,
            tasksCompleted: 0,
            totalHours: 2,
            progress: 30
          }
        },
        byTask: {
          'authentication': {
            totalTasks: 3,
            completedTasks: 2,
            progress: 87,
            agents: ['developer', 'system_architect', 'qa_testing_specialist']
          },
          'user_profile': {
            totalTasks: 3,
            completedTasks: 0,
            progress: 63,
            agents: ['ui_ux_designer', 'database_engineer', 'developer']
          },
          'security': {
            totalTasks: 1,
            completedTasks: 0,
            progress: 0,
            agents: ['security_engineer']
          },
          'infrastructure': {
            totalTasks: 1,
            completedTasks: 0,
            progress: 30,
            agents: ['devops_engineer']
          }
        }
      };
      
      setAgentContributions({
        byRole: mockAgentContributions.byRole,
        byTask: mockAgentContributions.byTask,
        loading: false,
        error: null
      });
    } catch (error) {
      console.error('Error fetching agent contributions:', error);
      setAgentContributions({
        ...agentContributions,
        loading: false,
        error: 'Failed to load agent contributions'
      });
    }
  };
  
  // Refresh all data
  const refreshData = () => {
    fetchSprintData();
    fetchAgentContributions();
  };
  
  // Set up auto-refresh
  useEffect(() => {
    if (open) {
      // Initial fetch
      refreshData();
      
      // Set up refresh interval
      refreshIntervalRef.current = setInterval(() => {
        refreshData();
      }, 60000); // Refresh every minute
    }
    
    // Cleanup
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [open, projectId]);
  
  // Filter tasks based on view options
  const getFilteredTasks = () => {
    if (!sprintData.currentSprint) return [];
    
    let tasks = [...sprintData.currentSprint.tasks];
    
    // Apply status filter
    if (viewOptions.taskStatusFilter !== 'all') {
      tasks = tasks.filter(task => task.status === viewOptions.taskStatusFilter);
    }
    
    return tasks;
  };
  
  // Group tasks based on view options
  const getGroupedTasks = () => {
    const tasks = getFilteredTasks();
    const groupedTasks = {};
    
    switch (viewOptions.groupBy) {
      case 'status':
        tasks.forEach(task => {
          if (!groupedTasks[task.status]) {
            groupedTasks[task.status] = [];
          }
          groupedTasks[task.status].push(task);
        });
        break;
      case 'assignee':
        tasks.forEach(task => {
          if (!groupedTasks[task.assignedTo]) {
            groupedTasks[task.assignedTo] = [];
          }
          groupedTasks[task.assignedTo].push(task);
        });
        break;
      case 'priority':
        tasks.forEach(task => {
          if (!groupedTasks[task.priority]) {
            groupedTasks[task.priority] = [];
          }
          groupedTasks[task.priority].push(task);
        });
        break;
      default:
        groupedTasks['all'] = tasks;
        break;
    }
    
    return groupedTasks;
  };
  
  // Prepare data for agent contribution chart
  const prepareAgentContributionChartData = () => {
    if (agentContributions.loading || !agentContributions.byRole) {
      return null;
    }
    
    const roles = Object.keys(agentContributions.byRole);
    const data = {
      labels: roles.map(role => role.replace('_', ' ')),
      datasets: [
        {
          label: 'Tasks Assigned',
          data: roles.map(role => agentContributions.byRole[role].tasksAssigned),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        {
          label: 'Tasks Completed',
          data: roles.map(role => agentContributions.byRole[role].tasksCompleted),
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        },
        {
          label: 'Hours Worked',
          data: roles.map(role => agentContributions.byRole[role].totalHours),
          backgroundColor: 'rgba(255, 159, 64, 0.5)',
          borderColor: 'rgba(255, 159, 64, 1)',
          borderWidth: 1,
          type: 'line',
          yAxisID: 'y1'
        }
      ]
    };
    
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Tasks'
          }
        },
        y1: {
          beginAtZero: true,
          position: 'right',
          title: {
            display: true,
            text: 'Hours'
          },
          grid: {
            drawOnChartArea: false
          }
        }
      }
    };
    
    return { data, options };
  };
  
  // Prepare data for task category progress chart
  const prepareTaskCategoryProgressChartData = () => {
    if (agentContributions.loading || !agentContributions.byTask) {
      return null;
    }
    
    const categories = Object.keys(agentContributions.byTask);
    const data = {
      labels: categories.map(category => category.replace('_', ' ')),
      datasets: [
        {
          label: 'Progress (%)',
          data: categories.map(category => agentContributions.byTask[category].progress),
          backgroundColor: categories.map((_, index) => `hsl(${index * 137.5}, 70%, 60%)`),
          borderWidth: 1
        }
      ]
    };
    
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Progress (%)'
          }
        }
      }
    };
    
    return { data, options };
  };
  
  // Render sprint overview section
  const renderSprintOverview = () => {
    if (sprintData.loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <LinearProgress sx={{ width: '100%' }} />
        </Box>
      );
    }
    
    if (sprintData.error) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error">{sprintData.error}</Typography>
          <Button 
            variant="outlined" 
            onClick={fetchSprintData} 
            sx={{ mt: 2 }}
          >
            Retry
          </Button>
        </Box>
      );
    }
    
    if (!sprintData.currentSprint) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography>No active sprint found</Typography>
        </Box>
      );
    }
    
    const { currentSprint } = sprintData;
    const daysRemaining = calculateDaysRemaining(currentSprint.endDate);
    
    return (
      <Card>
        <CardHeader
          title={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <DonutLargeIcon sx={{ mr: 1 }} />
              <Typography variant="h6">{currentSprint.name}</Typography>
            </Box>
          }
          subheader={`${formatDate(currentSprint.startDate)} - ${formatDate(currentSprint.endDate)}`}
          action={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Tooltip title="Refresh data">
                <IconButton onClick={refreshData} size="small">
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Sprint options">
                <IconButton size="small">
                  <MoreVertIcon />
                </IconButton>
              </Tooltip>
            </Box>
          }
        />
        <Divider />
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>Sprint Goal</Typography>
          <Typography variant="body2" paragraph>{currentSprint.goal}</Typography>
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="subtitle2" color="text.secondary">Progress</Typography>
                <Typography variant="h4">{currentSprint.progress}%</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={currentSprint.progress} 
                  sx={{ mt: 1, mb: 1 }}
                />
              </Paper>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="subtitle2" color="text.secondary">Days Remaining</Typography>
                <Typography variant="h4">{daysRemaining}</Typography>
                <Typography variant="caption" color={daysRemaining < 3 ? 'error' : 'text.secondary'}>
                  {daysRemaining < 0 ? 'Overdue' : `${Math.round((daysRemaining / 14) * 100)}% of time left`}
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="subtitle2" color="text.secondary">Tasks</Typography>
                <Typography variant="h4">
                  {currentSprint.tasks.filter(t => t.status === 'completed').length} / {currentSprint.tasks.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {Math.round((currentSprint.tasks.filter(t => t.status === 'completed').length / currentSprint.tasks.length) * 100)}% completed
                </Typography>
              </Paper>
            </Grid>
          </Grid>
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="subtitle1">Task Status Breakdown</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {['not_started', 'in_progress', 'in_review', 'blocked', 'completed'].map(status => {
                const count = currentSprint.tasks.filter(t => t.status === status).length;
                if (count === 0) return null;
                
                return (
                  <Chip 
                    key={status}
                    size="small"
                    label={`${status.replace('_', ' ')}: ${count}`}
                    sx={{ 
                      bgcolor: `${getStatusColor(status)}20`,
                      color: getStatusColor(status),
                      borderColor: getStatusColor(status)
                    }}
                    variant="outlined"
                  />
                );
              })}
            </Box>
          </Box>
          
          <Box sx={{ height: 200, mb: 2 }}>
            {prepareTaskCategoryProgressChartData() && (
              <Chart 
                type="bar" 
                data={prepareTaskCategoryProgressChartData().data}
                options={prepareTaskCategoryProgressChartData().options}
              />
            )}
          </Box>
        </CardContent>
      </Card>
    );
  };
  
  // Render task board section
  const renderTaskBoard = () => {
    if (sprintData.loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <LinearProgress sx={{ width: '100%' }} />
        </Box>
      );
    }
    
    if (!sprintData.currentSprint) {
      return null;
    }
    
    const groupedTasks = getGroupedTasks();
    const groupKeys = Object.keys(groupedTasks);
    
    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader
          title={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <AssignmentIcon sx={{ mr: 1 }} />
              <Typography variant="h6">Task Board</Typography>
            </Box>
          }
          action={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <FormControl size="small" sx={{ minWidth: 120, mr: 1 }}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={viewOptions.taskStatusFilter}
                  label="Status"
                  onChange={(e) => handleViewOptionChange('taskStatusFilter', e.target.value)}
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="not_started">Not Started</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="in_review">In Review</MenuItem>
                  <MenuItem value="blocked">Blocked</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Group By</InputLabel>
                <Select
                  value={viewOptions.groupBy}
                  label="Group By"
                  onChange={(e) => handleViewOptionChange('groupBy', e.target.value)}
                >
                  <MenuItem value="status">Status</MenuItem>
                  <MenuItem value="assignee">Assignee</MenuItem>
                  <MenuItem value="priority">Priority</MenuItem>
                </Select>
              </FormControl>
              
              <Tooltip title="Filter options">
                <IconButton size="small" sx={{ ml: 1 }}>
                  <FilterListIcon />
                </IconButton>
              </Tooltip>
            </Box>
          }
        />
        <Divider />
        <CardContent>
          <Grid container spacing={2}>
            {groupKeys.length === 0 ? (
              <Grid item xs={12}>
                <Box sx={{ p: 3, textAlign: 'center' }}>
                  <Typography>No tasks match the current filters</Typography>
                </Box>
              </Grid>
            ) : (
              groupKeys.map(groupKey => (
                <Grid item xs={12} md={viewOptions.groupBy === 'status' ? 6 : 12} lg={viewOptions.groupBy === 'status' ? 4 : 12} key={groupKey}>
                  <Paper sx={{ p: 2, height: '100%' }}>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      mb: 2,
                      pb: 1,
                      borderBottom: 1,
                      borderColor: 'divider'
                    }}>
                      {viewOptions.groupBy === 'status' && (
                        <Box 
                          sx={{ 
                            width: 12, 
                            height: 12, 
                            borderRadius: '50%', 
                            bgcolor: getStatusColor(groupKey),
                            mr: 1
                          }} 
                        />
                      )}
                      {viewOptions.groupBy === 'assignee' && (
                        <Avatar 
                          sx={{ 
                            width: 24, 
                            height: 24, 
                            bgcolor: getAgentColor(groupKey),
                            mr: 1
                          }}
                        >
                          {getRoleIcon(groupKey)}
                        </Avatar>
                      )}
                      {viewOptions.groupBy === 'priority' && (
                        <FlagIcon 
                          fontSize="small" 
                          color={
                            groupKey === 'high' ? 'error' :
                            groupKey === 'medium' ? 'warning' :
                            'action'
                          }
                          sx={{ mr: 1 }}
                        />
                      )}
                      <Typography variant="subtitle1">
                        {groupKey === 'all' ? 'All Tasks' : groupKey.replace('_', ' ')}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        ({groupedTasks[groupKey].length})
                      </Typography>
                    </Box>
                    
                    <List sx={{ 
                      maxHeight: 400, 
                      overflow: 'auto',
                      '& .MuiListItem-root': {
                        borderLeft: 3,
                        borderColor: 'transparent',
                        mb: 1,
                        bgcolor: 'background.default',
                        borderRadius: 1
                      }
                    }}>
                      {groupedTasks[groupKey].map(task => (
                        <ListItem 
                          key={task.id}
                          sx={{ 
                            borderLeftColor: getStatusColor(task.status),
                            cursor: 'pointer'
                          }}
                          onClick={() => handleTaskSelect(task)}
                        >
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Typography variant="body1">{task.name}</Typography>
                                {task.priority === 'high' && (
                                  <FlagIcon fontSize="small" color="error" sx={{ ml: 1 }} />
                                )}
                              </Box>
                            }
                            secondary={
                              <Box sx={{ mt: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                                  <Typography variant="caption" color="text.secondary">
                                    Progress: {task.progress}%
                                  </Typography>
                                  {task.status === 'completed' && (
                                    <CheckCircleIcon 
                                      fontSize="small" 
                                      color="success" 
                                      sx={{ ml: 1 }}
                                    />
                                  )}
                                </Box>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={task.progress} 
                                  sx={{ 
                                    mb: 1,
                                    bgcolor: 'background.paper',
                                    '& .MuiLinearProgress-bar': {
                                      bgcolor: task.progress === 100 ? 'success.main' : 'primary.main'
                                    }
                                  }}
                                />
                                <Box sx={{ 
                                  display: 'flex', 
                                  justifyContent: 'space-between',
                                  alignItems: 'center'
                                }}>
                                  {viewOptions.groupBy !== 'assignee' && (
                                    <Tooltip title={task.assignedTo.replace('_', ' ')}>
                                      <Avatar 
                                        sx={{ 
                                          width: 24, 
                                          height: 24, 
                                          bgcolor: getAgentColor(task.assignedTo)
                                        }}
                                      >
                                        {getRoleIcon(task.assignedTo)}
                                      </Avatar>
                                    </Tooltip>
                                  )}
                                  {viewOptions.groupBy !== 'status' && (
                                    <Chip 
                                      size="small"
                                      label={task.status.replace('_', ' ')}
                                      sx={{ 
                                        bgcolor: `${getStatusColor(task.status)}20`,
                                        color: getStatusColor(task.status),
                                        borderColor: getStatusColor(task.status)
                                      }}
                                      variant="outlined"
                                    />
                                  )}
                                </Box>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                </Grid>
              ))
            )}
          </Grid>
        </CardContent>
      </Card>
    );
  };
  
  // Render agent contributions section
  const renderAgentContributions = () => {
    if (agentContributions.loading) {
      return (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <LinearProgress sx={{ width: '100%' }} />
        </Box>
      );
    }
    
    if (agentContributions.error) {
      return (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error">{agentContributions.error}</Typography>
          <Button 
            variant="outlined" 
            onClick={fetchAgentContributions} 
            sx={{ mt: 2 }}
          >
            Retry
          </Button>
        </Box>
      );
    }
    
    const chartData = prepareAgentContributionChartData();
    
    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader
          title={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <BarChartIcon sx={{ mr: 1 }} />
              <Typography variant="h6">Agent Contributions</Typography>
            </Box>
          }
        />
        <Divider />
        <CardContent>
          <Box sx={{ height: 300, mb: 3 }}>
            {chartData && (
              <Chart 
                type="bar" 
                data={chartData.data}
                options={chartData.options}
              />
            )}
          </Box>
          
          <Typography variant="subtitle1" gutterBottom>Agent Performance</Typography>
          <Grid container spacing={2}>
            {Object.entries(agentContributions.byRole).map(([role, data]) => (
              <Grid item xs={12} sm={6} md={4} key={role}>
                <Paper sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Avatar 
                      sx={{ 
                        bgcolor: getAgentColor(role),
                        mr: 1
                      }}
                    >
                      {getRoleIcon(role)}
                    </Avatar>
                    <Typography variant="subtitle2">{role.replace('_', ' ')}</Typography>
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Tasks Assigned:</Typography>
                    <Typography variant="body2">{data.tasksAssigned}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Tasks Completed:</Typography>
                    <Typography variant="body2">{data.tasksCompleted}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Hours Worked:</Typography>
                    <Typography variant="body2">{data.totalHours}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Overall Progress:</Typography>
                    <Typography variant="body2">{data.progress}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={data.progress} 
                    sx={{ mt: 1 }}
                  />
                </Paper>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };
  
  // Render sprint timeline section
  const renderSprintTimeline = () => {
    if (sprintData.loading || !sprintData.sprints || sprintData.sprints.length === 0) {
      return null;
    }
    
    return (
      <Card sx={{ mt: 3 }}>
        <CardHeader
          title={
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CalendarTodayIcon sx={{ mr: 1 }} />
              <Typography variant="h6">Sprint Timeline</Typography>
            </Box>
          }
        />
        <Divider />
        <CardContent>
          <Timeline position="alternate">
            {sprintData.sprints.map((sprint, index) => (
              <TimelineItem key={sprint.id}>
                <TimelineOppositeContent color="text.secondary">
                  {formatDate(sprint.startDate)} - {formatDate(sprint.endDate)}
                </TimelineOppositeContent>
                <TimelineSeparator>
                  <TimelineDot 
                    color={
                      sprint.id === sprintData.currentSprint?.id ? 'primary' :
                      index < sprintData.sprints.findIndex(s => s.id === sprintData.currentSprint?.id) ? 'success' :
                      'grey'
                    }
                  >
                    {sprint.id === sprintData.currentSprint?.id ? (
                      <DonutLargeIcon />
                    ) : index < sprintData.sprints.findIndex(s => s.id === sprintData.currentSprint?.id) ? (
                      <CheckCircleIcon />
                    ) : (
                      <CalendarTodayIcon />
                    )}
                  </TimelineDot>
                  {index < sprintData.sprints.length - 1 && <TimelineConnector />}
                </TimelineSeparator>
                <TimelineContent>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle1">{sprint.name}</Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2">Tasks:</Typography>
                      <Typography variant="body2">
                        {sprint.completedTaskCount} / {sprint.taskCount}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2">Progress:</Typography>
                      <Typography variant="body2">{sprint.progress}%</Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={sprint.progress} 
                      sx={{ mt: 1 }}
                    />
                  </Paper>
                </TimelineContent>
              </TimelineItem>
            ))}
          </Timeline>
        </CardContent>
      </Card>
    );
  };
  
  // Render task details dialog
  const renderTaskDetailsDialog = () => {
    const { selectedTask, showDialog, history, loading } = taskDetails;
    
    if (!selectedTask) return null;
    
    return (
      <Dialog
        open={showDialog}
        onClose={handleCloseTaskDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="h6">{selectedTask.name}</Typography>
            <Chip 
              label={selectedTask.status.replace('_', ' ')}
              sx={{ 
                bgcolor: `${getStatusColor(selectedTask.status)}20`,
                color: getStatusColor(selectedTask.status),
                borderColor: getStatusColor(selectedTask.status)
              }}
              variant="outlined"
            />
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Typography variant="subtitle1" gutterBottom>Description</Typography>
              <Typography variant="body2" paragraph>
                {selectedTask.description}
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>Progress</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">{selectedTask.progress}% complete</Typography>
                  <Typography variant="body2">
                    {selectedTask.actualHours} / {selectedTask.estimatedHours} hours
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={selectedTask.progress} 
                  sx={{ height: 10, borderRadius: 5 }}
                />
              </Box>
              
              <Typography variant="subtitle1" gutterBottom>Activity History</Typography>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <LinearProgress sx={{ width: '100%' }} />
                </Box>
              ) : history.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No activity history available
                </Typography>
              ) : (
                <Timeline>
                  {history.map(event => (
                    <TimelineItem key={event.id}>
                      <TimelineOppositeContent color="text.secondary" sx={{ flex: 0.2 }}>
                        {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        <br />
                        {new Date(event.timestamp).toLocaleDateString()}
                      </TimelineOppositeContent>
                      <TimelineSeparator>
                        <TimelineDot sx={{ bgcolor: getAgentColor(event.agent) }}>
                          {getRoleIcon(event.agent)}
                        </TimelineDot>
                        <TimelineConnector />
                      </TimelineSeparator>
                      <TimelineContent sx={{ py: '12px', px: 2 }}>
                        <Typography variant="subtitle2">
                          {event.agent.replace('_', ' ')} {event.action.replace('_', ' ')}
                        </Typography>
                        <Typography variant="body2">{event.details}</Typography>
                      </TimelineContent>
                    </TimelineItem>
                  ))}
                </Timeline>
              )}
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>Details</Typography>
                <List dense disablePadding>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <AssignmentIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="ID"
                      secondary={selectedTask.id}
                    />
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Avatar 
                        sx={{ 
                          width: 24, 
                          height: 24, 
                          bgcolor: getAgentColor(selectedTask.assignedTo)
                        }}
                      >
                        {getRoleIcon(selectedTask.assignedTo)}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText 
                      primary="Assigned To"
                      secondary={selectedTask.assignedTo.replace('_', ' ')}
                    />
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <FlagIcon 
                        fontSize="small" 
                        color={
                          selectedTask.priority === 'high' ? 'error' :
                          selectedTask.priority === 'medium' ? 'warning' :
                          'action'
                        }
                      />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Priority"
                      secondary={selectedTask.priority}
                    />
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <TimelineIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Estimated Hours"
                      secondary={selectedTask.estimatedHours}
                    />
                  </ListItem>
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <TimelineIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="Actual Hours"
                      secondary={selectedTask.actualHours}
                    />
                  </ListItem>
                </List>
              </Paper>
              
              {selectedTask.dependencies.length > 0 && (
                <Paper sx={{ p: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>Dependencies</Typography>
                  <List dense disablePadding>
                    {selectedTask.dependencies.map(depId => {
                      const depTask = sprintData.currentSprint.tasks.find(t => t.id === depId);
                      if (!depTask) return null;
                      
                      return (
                        <ListItem 
                          key={depId}
                          sx={{ 
                            mb: 1,
                            borderLeft: 3,
                            borderColor: getStatusColor(depTask.status),
                            bgcolor: 'background.default',
                            borderRadius: 1
                          }}
                        >
                          <ListItemText
                            primary={depTask.name}
                            secondary={
                              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                <Typography variant="caption" sx={{ mr: 1 }}>
                                  {depTask.progress}% complete
                                </Typography>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={depTask.progress} 
                                  sx={{ width: 50 }}
                                />
                              </Box>
                            }
                          />
                        </ListItem>
                      );
                    })}
                  </List>
                </Paper>
              )}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseTaskDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  };
  
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5">Sprint Tracking</Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />}
          onClick={refreshData}
        >
          Refresh Data
        </Button>
      </Box>
      
      {renderSprintOverview()}
      {renderTaskBoard()}
      {renderAgentContributions()}
      {renderSprintTimeline()}
      {renderTaskDetailsDialog()}
    </Box>
  );
};

export default SprintTrackingVisualization;
