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
  Drawer, 
  IconButton, 
  Typography, 
  Tabs, 
  Tab, 
  Paper, 
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Badge,
  Button,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Collapse,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  CircularProgress,
  LinearProgress
} from '@mui/material';
import { 
  Message as MessageIcon,
  Group as GroupIcon,
  Assignment as AssignmentIcon,
  Timeline as TimelineIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  FilterList as FilterListIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Person as PersonIcon,
  Code as CodeIcon,
  Build as BuildIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Brush as BrushIcon,
  Description as DescriptionIcon,
  Speed as SpeedIcon,
  DeviceHub as DeviceHubIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material';
import { Line, Bar, Pie } from 'react-chartjs-2';
import { format, formatDistance } from 'date-fns';

// Agent icon mapping
const AGENT_ICONS = {
  'project_manager': <PersonIcon />,
  'product_manager': <AssignmentIcon />,
  'developer': <CodeIcon />,
  'system_architect': <DeviceHubIcon />,
  'devops_engineer': <BuildIcon />,
  'qa_testing_specialist': <BugReportIcon />,
  'security_engineer': <SecurityIcon />,
  'database_engineer': <StorageIcon />,
  'ui_ux_designer': <BrushIcon />,
  'documentation_specialist': <DescriptionIcon />,
  'performance_engineer': <SpeedIcon />
};

// Priority color mapping
const PRIORITY_COLORS = {
  'critical': '#d32f2f',
  'high': '#f57c00',
  'medium': '#0288d1',
  'low': '#388e3c'
};

// Message pattern icons
const PATTERN_ICONS = {
  'request_response': <MessageIcon fontSize="small" />,
  'broadcast': <GroupIcon fontSize="small" />,
  'direct_message': <PersonIcon fontSize="small" />,
  'group_discussion': <GroupIcon fontSize="small" />,
  'task_delegation': <AssignmentIcon fontSize="small" />,
  'status_update': <InfoIcon fontSize="small" />
};

/**
 * AgentConversationMonitoringPanel component
 * 
 * A collapsible panel that allows users to monitor conversations between agents,
 * view message history, and track agent activities in real-time.
 */
const AgentConversationMonitoringPanel = ({ 
  open, 
  onClose, 
  width = 800,
  height = '80vh',
  position = 'right'
}) => {
  // State for tab management
  const [activeTab, setActiveTab] = useState(0);
  
  // State for conversation data
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // State for filters
  const [filters, setFilters] = useState({
    agent: '',
    pattern: '',
    priority: '',
    timeRange: 'all',
    searchTerm: ''
  });
  
  // State for agent activity
  const [agentActivity, setAgentActivity] = useState({});
  const [agentMetrics, setAgentMetrics] = useState({});
  
  // State for expanded sections
  const [expandedSections, setExpandedSections] = useState({
    filters: false,
    conversationDetails: true,
    agentMetrics: false
  });
  
  // Ref for message container to auto-scroll
  const messageContainerRef = useRef(null);
  
  // Mock data for development - would be replaced with actual API calls
  useEffect(() => {
    if (open) {
      fetchData();
    }
  }, [open, filters]);
  
  // Auto-scroll to bottom of messages when new messages arrive
  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages]);
  
  // Fetch conversation data based on filters
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // In a real implementation, these would be API calls
      // For now, we'll simulate with mock data
      
      // Fetch conversations
      const mockConversations = generateMockConversations();
      setConversations(mockConversations);
      
      // Set selected conversation if none is selected
      if (!selectedConversation && mockConversations.length > 0) {
        setSelectedConversation(mockConversations[0].id);
        
        // Fetch messages for the selected conversation
        const mockMessages = generateMockMessages(mockConversations[0].id);
        setMessages(mockMessages);
      } else if (selectedConversation) {
        // Fetch messages for the selected conversation
        const mockMessages = generateMockMessages(selectedConversation);
        setMessages(mockMessages);
      }
      
      // Fetch agent activity
      const mockAgentActivity = generateMockAgentActivity();
      setAgentActivity(mockAgentActivity);
      
      // Fetch agent metrics
      const mockAgentMetrics = generateMockAgentMetrics();
      setAgentMetrics(mockAgentMetrics);
      
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load conversation data. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle conversation selection
  const handleConversationSelect = (conversationId) => {
    setSelectedConversation(conversationId);
    
    // Fetch messages for the selected conversation
    const mockMessages = generateMockMessages(conversationId);
    setMessages(mockMessages);
  };
  
  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };
  
  // Toggle expanded sections
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  // Refresh data
  const handleRefresh = () => {
    fetchData();
  };
  
  // Generate mock conversations for development
  const generateMockConversations = () => {
    return [
      {
        id: 'conv-1',
        title: 'Feature Implementation Planning',
        participants: ['project_manager', 'developer', 'system_architect'],
        lastActivity: new Date().toISOString(),
        messageCount: 12,
        status: 'active'
      },
      {
        id: 'conv-2',
        title: 'API Design Discussion',
        participants: ['system_architect', 'developer', 'product_manager'],
        lastActivity: new Date(Date.now() - 30 * 60000).toISOString(),
        messageCount: 8,
        status: 'active'
      },
      {
        id: 'conv-3',
        title: 'Testing Strategy',
        participants: ['qa_testing_specialist', 'developer', 'project_manager'],
        lastActivity: new Date(Date.now() - 2 * 3600000).toISOString(),
        messageCount: 5,
        status: 'active'
      },
      {
        id: 'conv-4',
        title: 'Deployment Planning',
        participants: ['devops_engineer', 'system_architect', 'project_manager'],
        lastActivity: new Date(Date.now() - 5 * 3600000).toISOString(),
        messageCount: 7,
        status: 'completed'
      }
    ].filter(conv => {
      // Apply filters
      if (filters.agent && !conv.participants.includes(filters.agent)) {
        return false;
      }
      
      // Apply search term
      if (filters.searchTerm && !conv.title.toLowerCase().includes(filters.searchTerm.toLowerCase())) {
        return false;
      }
      
      return true;
    });
  };
  
  // Generate mock messages for development
  const generateMockMessages = (conversationId) => {
    const baseTime = new Date(Date.now() - 3600000);
    
    const messagesByConversation = {
      'conv-1': [
        {
          id: 'msg-1-1',
          conversationId: 'conv-1',
          from: 'project_manager',
          to: ['developer', 'system_architect'],
          content: 'We need to implement the user authentication feature by the end of this sprint. Let\'s discuss the approach.',
          timestamp: new Date(baseTime.getTime() + 5 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'high'
        },
        {
          id: 'msg-1-2',
          conversationId: 'conv-1',
          from: 'system_architect',
          to: ['project_manager', 'developer'],
          content: 'I recommend using JWT for authentication. We should also consider implementing refresh tokens for better security.',
          timestamp: new Date(baseTime.getTime() + 10 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'medium'
        },
        {
          id: 'msg-1-3',
          conversationId: 'conv-1',
          from: 'developer',
          to: ['project_manager', 'system_architect'],
          content: 'I agree with the JWT approach. I can implement this using our existing user service. How should we handle password reset functionality?',
          timestamp: new Date(baseTime.getTime() + 15 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'medium'
        },
        {
          id: 'msg-1-4',
          conversationId: 'conv-1',
          from: 'project_manager',
          to: 'developer',
          content: 'Can you provide an estimate for implementing the authentication service?',
          timestamp: new Date(baseTime.getTime() + 20 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'high'
        },
        {
          id: 'msg-1-5',
          conversationId: 'conv-1',
          from: 'developer',
          to: 'project_manager',
          content: 'I estimate it will take approximately 3 days to implement the core authentication service with JWT support.',
          timestamp: new Date(baseTime.getTime() + 25 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'high'
        },
        {
          id: 'msg-1-6',
          conversationId: 'conv-1',
          from: 'system_architect',
          to: 'developer',
          content: 'Here\'s a diagram of the authentication flow I\'m proposing. Let me know if you have any questions.',
          timestamp: new Date(baseTime.getTime() + 30 * 60000).toISOString(),
          pattern: 'direct_message',
          priority: 'medium'
        },
        {
          id: 'msg-1-7',
          conversationId: 'conv-1',
          from: 'developer',
          to: 'system_architect',
          content: 'Thanks for the diagram. This helps clarify the flow. I\'ll start implementing this tomorrow.',
          timestamp: new Date(baseTime.getTime() + 35 * 60000).toISOString(),
          pattern: 'direct_message',
          priority: 'medium'
        },
        {
          id: 'msg-1-8',
          conversationId: 'conv-1',
          from: 'project_manager',
          to: ['developer', 'system_architect'],
          content: 'Let\'s schedule a review of the authentication implementation for Friday. Does that work for everyone?',
          timestamp: new Date(baseTime.getTime() + 40 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'medium'
        },
        {
          id: 'msg-1-9',
          conversationId: 'conv-1',
          from: 'system_architect',
          to: 'project_manager',
          content: 'Friday works for me. I\'ll prepare some test cases to validate the implementation.',
          timestamp: new Date(baseTime.getTime() + 45 * 60000).toISOString(),
          pattern: 'direct_message',
          priority: 'low'
        },
        {
          id: 'msg-1-10',
          conversationId: 'conv-1',
          from: 'developer',
          to: 'project_manager',
          content: 'Friday is good. I should have a working implementation by then.',
          timestamp: new Date(baseTime.getTime() + 50 * 60000).toISOString(),
          pattern: 'direct_message',
          priority: 'low'
        },
        {
          id: 'msg-1-11',
          conversationId: 'conv-1',
          from: 'project_manager',
          to: 'qa_testing_specialist',
          content: 'We\'re implementing the authentication service this week. Can you prepare test cases for it?',
          timestamp: new Date(baseTime.getTime() + 55 * 60000).toISOString(),
          pattern: 'task_delegation',
          priority: 'medium'
        },
        {
          id: 'msg-1-12',
          conversationId: 'conv-1',
          from: 'qa_testing_specialist',
          to: 'project_manager',
          content: 'I\'ll prepare comprehensive test cases for the authentication service, including edge cases and security scenarios.',
          timestamp: new Date(baseTime.getTime() + 60 * 60000).toISOString(),
          pattern: 'status_update',
          priority: 'medium'
        }
      ],
      'conv-2': [
        {
          id: 'msg-2-1',
          conversationId: 'conv-2',
          from: 'system_architect',
          to: ['developer', 'product_manager'],
          content: 'Let\'s discuss the API design for the new feature. We need to ensure it\'s RESTful and follows our standards.',
          timestamp: new Date(baseTime.getTime() - 30 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'medium'
        },
        {
          id: 'msg-2-2',
          conversationId: 'conv-2',
          from: 'product_manager',
          to: ['system_architect', 'developer'],
          content: 'The API needs to support filtering, pagination, and sorting. These are critical for the frontend team.',
          timestamp: new Date(baseTime.getTime() - 25 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'high'
        },
        {
          id: 'msg-2-3',
          conversationId: 'conv-2',
          from: 'developer',
          to: ['system_architect', 'product_manager'],
          content: 'I suggest we use GraphQL instead of REST for this feature. It would give the frontend more flexibility.',
          timestamp: new Date(baseTime.getTime() - 20 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'medium'
        },
        {
          id: 'msg-2-4',
          conversationId: 'conv-2',
          from: 'system_architect',
          to: 'developer',
          content: 'Interesting suggestion. Can you elaborate on the benefits of GraphQL for this specific feature?',
          timestamp: new Date(baseTime.getTime() - 15 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'medium'
        },
        {
          id: 'msg-2-5',
          conversationId: 'conv-2',
          from: 'developer',
          to: 'system_architect',
          content: 'GraphQL would allow the frontend to request exactly the data it needs, reducing over-fetching. It also simplifies handling related resources.',
          timestamp: new Date(baseTime.getTime() - 10 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'medium'
        },
        {
          id: 'msg-2-6',
          conversationId: 'conv-2',
          from: 'product_manager',
          to: ['system_architect', 'developer'],
          content: 'I\'m concerned about the learning curve for GraphQL. Would it delay our timeline?',
          timestamp: new Date(baseTime.getTime() - 5 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'high'
        },
        {
          id: 'msg-2-7',
          conversationId: 'conv-2',
          from: 'system_architect',
          to: ['product_manager', 'developer'],
          content: 'Let\'s stick with REST for now since the team is familiar with it. We can explore GraphQL for future features.',
          timestamp: new Date(baseTime.getTime()).toISOString(),
          pattern: 'group_discussion',
          priority: 'high'
        },
        {
          id: 'msg-2-8',
          conversationId: 'conv-2',
          from: 'developer',
          to: ['system_architect', 'product_manager'],
          content: 'Understood. I\'ll draft the REST API design with support for filtering, pagination, and sorting.',
          timestamp: new Date(baseTime.getTime() + 5 * 60000).toISOString(),
          pattern: 'status_update',
          priority: 'medium'
        }
      ],
      'conv-3': [
        {
          id: 'msg-3-1',
          conversationId: 'conv-3',
          from: 'qa_testing_specialist',
          to: ['developer', 'project_manager'],
          content: 'We need to develop a comprehensive testing strategy for the new features. Let\'s discuss approach and coverage.',
          timestamp: new Date(baseTime.getTime() - 120 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'high'
        },
        {
          id: 'msg-3-2',
          conversationId: 'conv-3',
          from: 'developer',
          to: ['qa_testing_specialist', 'project_manager'],
          content: 'I\'ve already written unit tests for the core functionality. We should focus on integration and end-to-end tests.',
          timestamp: new Date(baseTime.getTime() - 115 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'medium'
        },
        {
          id: 'msg-3-3',
          conversationId: 'conv-3',
          from: 'project_manager',
          to: ['qa_testing_specialist', 'developer'],
          content: 'What\'s our current test coverage percentage? We should aim for at least 80% coverage.',
          timestamp: new Date(baseTime.getTime() - 110 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'medium'
        },
        {
          id: 'msg-3-4',
          conversationId: 'conv-3',
          from: 'developer',
          to: ['project_manager', 'qa_testing_specialist'],
          content: 'Current unit test coverage is at 75%. I\'ll work on increasing it to 85% by the end of the week.',
          timestamp: new Date(baseTime.getTime() - 105 * 60000).toISOString(),
          pattern: 'status_update',
          priority: 'medium'
        },
        {
          id: 'msg-3-5',
          conversationId: 'conv-3',
          from: 'qa_testing_specialist',
          to: ['developer', 'project_manager'],
          content: 'I\'ll create a test plan document with all test scenarios and edge cases. Should be ready by tomorrow.',
          timestamp: new Date(baseTime.getTime() - 100 * 60000).toISOString(),
          pattern: 'status_update',
          priority: 'high'
        }
      ],
      'conv-4': [
        {
          id: 'msg-4-1',
          conversationId: 'conv-4',
          from: 'devops_engineer',
          to: ['system_architect', 'project_manager'],
          content: 'We need to plan the deployment strategy for the new features. Let\'s discuss infrastructure requirements.',
          timestamp: new Date(baseTime.getTime() - 300 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'high'
        },
        {
          id: 'msg-4-2',
          conversationId: 'conv-4',
          from: 'system_architect',
          to: ['devops_engineer', 'project_manager'],
          content: 'The new features will require additional database capacity and a new microservice.',
          timestamp: new Date(baseTime.getTime() - 295 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'medium'
        },
        {
          id: 'msg-4-3',
          conversationId: 'conv-4',
          from: 'project_manager',
          to: ['devops_engineer', 'system_architect'],
          content: 'What\'s the estimated cost increase for the new infrastructure?',
          timestamp: new Date(baseTime.getTime() - 290 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'high'
        },
        {
          id: 'msg-4-4',
          conversationId: 'conv-4',
          from: 'devops_engineer',
          to: ['project_manager', 'system_architect'],
          content: 'I estimate a 15% increase in infrastructure costs. I\'ll prepare a detailed breakdown.',
          timestamp: new Date(baseTime.getTime() - 285 * 60000).toISOString(),
          pattern: 'status_update',
          priority: 'high'
        },
        {
          id: 'msg-4-5',
          conversationId: 'conv-4',
          from: 'system_architect',
          to: 'devops_engineer',
          content: 'Can we use containerization to optimize resource usage and potentially reduce costs?',
          timestamp: new Date(baseTime.getTime() - 280 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'medium'
        },
        {
          id: 'msg-4-6',
          conversationId: 'conv-4',
          from: 'devops_engineer',
          to: 'system_architect',
          content: 'Yes, I\'ll implement Kubernetes for container orchestration. This should improve resource utilization by about 20%.',
          timestamp: new Date(baseTime.getTime() - 275 * 60000).toISOString(),
          pattern: 'request_response',
          priority: 'medium'
        },
        {
          id: 'msg-4-7',
          conversationId: 'conv-4',
          from: 'project_manager',
          to: ['devops_engineer', 'system_architect'],
          content: 'Great work! Let\'s finalize the deployment plan by Friday.',
          timestamp: new Date(baseTime.getTime() - 270 * 60000).toISOString(),
          pattern: 'group_discussion',
          priority: 'low'
        }
      ]
    };
    
    return (messagesByConversation[conversationId] || []).filter(msg => {
      // Apply filters
      if (filters.agent && msg.from !== filters.agent && 
          !(Array.isArray(msg.to) && msg.to.includes(filters.agent)) && 
          msg.to !== filters.agent) {
        return false;
      }
      
      if (filters.pattern && msg.pattern !== filters.pattern) {
        return false;
      }
      
      if (filters.priority && msg.priority !== filters.priority) {
        return false;
      }
      
      if (filters.searchTerm && !msg.content.toLowerCase().includes(filters.searchTerm.toLowerCase())) {
        return false;
      }
      
      return true;
    });
  };
  
  // Generate mock agent activity
  const generateMockAgentActivity = () => {
    return {
      'project_manager': {
        messagesSent: 42,
        messagesReceived: 38,
        activeConversations: 5,
        lastActive: new Date().toISOString(),
        currentTasks: [
          { id: 'task-1', title: 'Sprint Planning', status: 'in_progress', priority: 'high' },
          { id: 'task-2', title: 'Resource Allocation', status: 'pending', priority: 'medium' }
        ]
      },
      'developer': {
        messagesSent: 36,
        messagesReceived: 41,
        activeConversations: 3,
        lastActive: new Date(Date.now() - 15 * 60000).toISOString(),
        currentTasks: [
          { id: 'task-3', title: 'Implement Authentication', status: 'in_progress', priority: 'high' },
          { id: 'task-4', title: 'Fix Pagination Bug', status: 'completed', priority: 'medium' }
        ]
      },
      'system_architect': {
        messagesSent: 28,
        messagesReceived: 32,
        activeConversations: 4,
        lastActive: new Date(Date.now() - 5 * 60000).toISOString(),
        currentTasks: [
          { id: 'task-5', title: 'API Design Review', status: 'in_progress', priority: 'high' },
          { id: 'task-6', title: 'Architecture Documentation', status: 'pending', priority: 'medium' }
        ]
      },
      'qa_testing_specialist': {
        messagesSent: 18,
        messagesReceived: 22,
        activeConversations: 2,
        lastActive: new Date(Date.now() - 45 * 60000).toISOString(),
        currentTasks: [
          { id: 'task-7', title: 'Test Plan Creation', status: 'in_progress', priority: 'high' },
          { id: 'task-8', title: 'Regression Testing', status: 'pending', priority: 'medium' }
        ]
      },
      'devops_engineer': {
        messagesSent: 15,
        messagesReceived: 19,
        activeConversations: 2,
        lastActive: new Date(Date.now() - 120 * 60000).toISOString(),
        currentTasks: [
          { id: 'task-9', title: 'CI/CD Pipeline Update', status: 'in_progress', priority: 'medium' },
          { id: 'task-10', title: 'Kubernetes Configuration', status: 'pending', priority: 'high' }
        ]
      }
    };
  };
  
  // Generate mock agent metrics
  const generateMockAgentMetrics = () => {
    return {
      messagesByAgent: {
        'project_manager': 42,
        'developer': 36,
        'system_architect': 28,
        'qa_testing_specialist': 18,
        'devops_engineer': 15,
        'product_manager': 22
      },
      messagesByPattern: {
        'request_response': 45,
        'group_discussion': 38,
        'direct_message': 32,
        'task_delegation': 15,
        'status_update': 20,
        'broadcast': 10
      },
      messagesByPriority: {
        'critical': 8,
        'high': 42,
        'medium': 85,
        'low': 25
      },
      responseTimesByAgent: {
        'project_manager': 5.2,
        'developer': 8.7,
        'system_architect': 6.3,
        'qa_testing_specialist': 12.1,
        'devops_engineer': 9.5,
        'product_manager': 7.8
      },
      collaborationScores: {
        'project_manager': 9.2,
        'developer': 8.5,
        'system_architect': 8.8,
        'qa_testing_specialist': 7.9,
        'devops_engineer': 8.1,
        'product_manager': 8.4
      }
    };
  };
  
  // Render message item
  const renderMessageItem = (message) => {
    const isFromCurrentAgent = filters.agent === message.from;
    const isToCurrentAgent = filters.agent === message.to || 
                            (Array.isArray(message.to) && message.to.includes(filters.agent));
    
    return (
      <Box
        key={message.id}
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: isFromCurrentAgent ? 'flex-end' : 'flex-start',
          mb: 2,
          maxWidth: '80%',
          alignSelf: isFromCurrentAgent ? 'flex-end' : 'flex-start'
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            mb: 0.5
          }}
        >
          <ListItemIcon sx={{ minWidth: 30 }}>
            {AGENT_ICONS[message.from] || <PersonIcon fontSize="small" />}
          </ListItemIcon>
          <Typography variant="caption" color="textSecondary">
            {message.from.replace('_', ' ')}
          </Typography>
          <Typography variant="caption" color="textSecondary" sx={{ ml: 1 }}>
            {format(new Date(message.timestamp), 'HH:mm')}
          </Typography>
          <Tooltip title={message.pattern}>
            <Box sx={{ ml: 1 }}>
              {PATTERN_ICONS[message.pattern] || <MessageIcon fontSize="small" />}
            </Box>
          </Tooltip>
          <Chip 
            label={message.priority} 
            size="small" 
            sx={{ 
              ml: 1, 
              height: 20, 
              fontSize: '0.6rem',
              backgroundColor: PRIORITY_COLORS[message.priority] || '#757575',
              color: 'white'
            }} 
          />
        </Box>
        <Paper
          elevation={1}
          sx={{
            p: 1.5,
            borderRadius: 2,
            backgroundColor: isFromCurrentAgent ? '#e3f2fd' : '#f5f5f5',
            maxWidth: '100%'
          }}
        >
          <Typography variant="body2">{message.content}</Typography>
        </Paper>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            mt: 0.5
          }}
        >
          <Typography variant="caption" color="textSecondary">
            To: {Array.isArray(message.to) 
              ? message.to.join(', ').replace(/_/g, ' ')
              : message.to.replace(/_/g, ' ')}
          </Typography>
        </Box>
      </Box>
    );
  };
  
  // Render conversation list item
  const renderConversationItem = (conversation) => {
    const isSelected = selectedConversation === conversation.id;
    const lastActivityDate = new Date(conversation.lastActivity);
    
    return (
      <ListItem
        key={conversation.id}
        button
        selected={isSelected}
        onClick={() => handleConversationSelect(conversation.id)}
        sx={{
          borderLeft: isSelected ? `4px solid #1976d2` : '4px solid transparent',
          backgroundColor: isSelected ? 'rgba(25, 118, 210, 0.08)' : 'transparent'
        }}
      >
        <ListItemIcon>
          <Badge badgeContent={conversation.messageCount} color="primary">
            <GroupIcon />
          </Badge>
        </ListItemIcon>
        <ListItemText
          primary={conversation.title}
          secondary={
            <React.Fragment>
              <Typography variant="caption" component="span" color="textSecondary">
                {conversation.participants.length} participants • {' '}
                {formatDistance(lastActivityDate, new Date(), { addSuffix: true })}
              </Typography>
              <Chip
                label={conversation.status}
                size="small"
                color={conversation.status === 'active' ? 'success' : 'default'}
                sx={{ ml: 1, height: 20, fontSize: '0.6rem' }}
              />
            </React.Fragment>
          }
        />
      </ListItem>
    );
  };
  
  // Render agent activity
  const renderAgentActivity = () => {
    return (
      <Grid container spacing={2}>
        {Object.entries(agentActivity).map(([agentId, activity]) => (
          <Grid item xs={12} md={6} key={agentId}>
            <Card variant="outlined">
              <CardHeader
                avatar={AGENT_ICONS[agentId] || <PersonIcon />}
                title={agentId.replace('_', ' ')}
                subheader={`Last active: ${formatDistance(new Date(activity.lastActive), new Date(), { addSuffix: true })}`}
                titleTypographyProps={{ variant: 'subtitle1' }}
                subheaderTypographyProps={{ variant: 'caption' }}
              />
              <CardContent sx={{ pt: 0 }}>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">Messages Sent</Typography>
                    <Typography variant="body2">{activity.messagesSent}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" color="textSecondary">Messages Received</Typography>
                    <Typography variant="body2">{activity.messagesReceived}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">Current Tasks</Typography>
                    {activity.currentTasks.map(task => (
                      <Box key={task.id} sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                        <Box sx={{ width: 10, height: 10, borderRadius: '50%', mr: 1, backgroundColor: PRIORITY_COLORS[task.priority] || '#757575' }} />
                        <Typography variant="body2">{task.title}</Typography>
                        <Chip 
                          label={task.status.replace('_', ' ')} 
                          size="small" 
                          color={task.status === 'completed' ? 'success' : task.status === 'in_progress' ? 'primary' : 'default'}
                          sx={{ ml: 1, height: 20, fontSize: '0.6rem' }} 
                        />
                      </Box>
                    ))}
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };
  
  // Render agent metrics charts
  const renderAgentMetricsCharts = () => {
    // Chart data for messages by agent
    const messagesByAgentData = {
      labels: Object.keys(agentMetrics.messagesByAgent).map(agent => agent.replace('_', ' ')),
      datasets: [
        {
          label: 'Messages',
          data: Object.values(agentMetrics.messagesByAgent),
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }
      ]
    };
    
    // Chart data for messages by pattern
    const messagesByPatternData = {
      labels: Object.keys(agentMetrics.messagesByPattern).map(pattern => pattern.replace('_', ' ')),
      datasets: [
        {
          label: 'Messages',
          data: Object.values(agentMetrics.messagesByPattern),
          backgroundColor: [
            'rgba(255, 99, 132, 0.5)',
            'rgba(54, 162, 235, 0.5)',
            'rgba(255, 206, 86, 0.5)',
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)',
            'rgba(255, 159, 64, 0.5)'
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
          ],
          borderWidth: 1
        }
      ]
    };
    
    // Chart data for response times
    const responseTimesData = {
      labels: Object.keys(agentMetrics.responseTimesByAgent).map(agent => agent.replace('_', ' ')),
      datasets: [
        {
          label: 'Response Time (minutes)',
          data: Object.values(agentMetrics.responseTimesByAgent),
          backgroundColor: 'rgba(75, 192, 192, 0.5)',
          borderColor: 'rgba(75, 192, 192, 1)',
          borderWidth: 1
        }
      ]
    };
    
    // Chart data for collaboration scores
    const collaborationScoresData = {
      labels: Object.keys(agentMetrics.collaborationScores).map(agent => agent.replace('_', ' ')),
      datasets: [
        {
          label: 'Collaboration Score',
          data: Object.values(agentMetrics.collaborationScores),
          backgroundColor: 'rgba(153, 102, 255, 0.5)',
          borderColor: 'rgba(153, 102, 255, 1)',
          borderWidth: 1
        }
      ]
    };
    
    return (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle2" gutterBottom>Messages by Agent</Typography>
          <Paper sx={{ p: 2, height: 300 }}>
            <Bar 
              data={messagesByAgentData} 
              options={{ 
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true
                  }
                }
              }} 
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle2" gutterBottom>Messages by Pattern</Typography>
          <Paper sx={{ p: 2, height: 300 }}>
            <Pie 
              data={messagesByPatternData} 
              options={{ 
                maintainAspectRatio: false
              }} 
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle2" gutterBottom>Response Times by Agent</Typography>
          <Paper sx={{ p: 2, height: 300 }}>
            <Bar 
              data={responseTimesData} 
              options={{ 
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true
                  }
                }
              }} 
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle2" gutterBottom>Collaboration Scores</Typography>
          <Paper sx={{ p: 2, height: 300 }}>
            <Bar 
              data={collaborationScoresData} 
              options={{ 
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true,
                    max: 10
                  }
                }
              }} 
            />
          </Paper>
        </Grid>
      </Grid>
    );
  };
  
  return (
    <Drawer
      anchor={position}
      open={open}
      onClose={onClose}
      sx={{
        width: width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: width,
          boxSizing: 'border-box',
          height: height,
          top: 'auto',
          bottom: 'auto',
          position: 'absolute'
        },
      }}
    >
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Agent Conversations</Typography>
          <Box>
            <IconButton onClick={handleRefresh} size="small" sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
            <IconButton onClick={onClose} size="small">
              <ExpandMoreIcon />
            </IconButton>
          </Box>
        </Box>
        
        {/* Tabs */}
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Conversations" icon={<MessageIcon />} iconPosition="start" />
          <Tab label="Agent Activity" icon={<PersonIcon />} iconPosition="start" />
          <Tab label="Metrics" icon={<TimelineIcon />} iconPosition="start" />
        </Tabs>
        
        {/* Content */}
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          {/* Conversations Tab */}
          {activeTab === 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
              {/* Filters */}
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2">Filters</Typography>
                  <IconButton size="small" onClick={() => toggleSection('filters')}>
                    {expandedSections.filters ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>
                <Collapse in={expandedSections.filters}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Agent</InputLabel>
                        <Select
                          value={filters.agent}
                          label="Agent"
                          onChange={(e) => handleFilterChange('agent', e.target.value)}
                        >
                          <MenuItem value="">All Agents</MenuItem>
                          <MenuItem value="project_manager">Project Manager</MenuItem>
                          <MenuItem value="product_manager">Product Manager</MenuItem>
                          <MenuItem value="developer">Developer</MenuItem>
                          <MenuItem value="system_architect">System Architect</MenuItem>
                          <MenuItem value="qa_testing_specialist">QA Testing Specialist</MenuItem>
                          <MenuItem value="devops_engineer">DevOps Engineer</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Pattern</InputLabel>
                        <Select
                          value={filters.pattern}
                          label="Pattern"
                          onChange={(e) => handleFilterChange('pattern', e.target.value)}
                        >
                          <MenuItem value="">All Patterns</MenuItem>
                          <MenuItem value="request_response">Request-Response</MenuItem>
                          <MenuItem value="broadcast">Broadcast</MenuItem>
                          <MenuItem value="direct_message">Direct Message</MenuItem>
                          <MenuItem value="group_discussion">Group Discussion</MenuItem>
                          <MenuItem value="task_delegation">Task Delegation</MenuItem>
                          <MenuItem value="status_update">Status Update</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Priority</InputLabel>
                        <Select
                          value={filters.priority}
                          label="Priority"
                          onChange={(e) => handleFilterChange('priority', e.target.value)}
                        >
                          <MenuItem value="">All Priorities</MenuItem>
                          <MenuItem value="critical">Critical</MenuItem>
                          <MenuItem value="high">High</MenuItem>
                          <MenuItem value="medium">Medium</MenuItem>
                          <MenuItem value="low">Low</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Search"
                        value={filters.searchTerm}
                        onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
                        InputProps={{
                          endAdornment: (
                            <IconButton size="small">
                              <SearchIcon />
                            </IconButton>
                          )
                        }}
                      />
                    </Grid>
                  </Grid>
                </Collapse>
              </Box>
              
              {/* Conversation List and Messages */}
              <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
                {/* Conversation List */}
                <Box sx={{ width: 300, borderRight: 1, borderColor: 'divider', overflow: 'auto' }}>
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : error ? (
                    <Box sx={{ p: 2 }}>
                      <Typography color="error">{error}</Typography>
                    </Box>
                  ) : conversations.length === 0 ? (
                    <Box sx={{ p: 2 }}>
                      <Typography>No conversations found.</Typography>
                    </Box>
                  ) : (
                    <List>
                      {conversations.map(renderConversationItem)}
                    </List>
                  )}
                </Box>
                
                {/* Messages */}
                <Box sx={{ flexGrow: 1, ml: 2, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                  {selectedConversation ? (
                    <>
                      {/* Conversation Details */}
                      <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="subtitle2">Conversation Details</Typography>
                          <IconButton size="small" onClick={() => toggleSection('conversationDetails')}>
                            {expandedSections.conversationDetails ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                          </IconButton>
                        </Box>
                        <Collapse in={expandedSections.conversationDetails}>
                          {conversations.find(c => c.id === selectedConversation) && (
                            <Box sx={{ p: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
                              <Typography variant="subtitle1">
                                {conversations.find(c => c.id === selectedConversation).title}
                              </Typography>
                              <Typography variant="caption" display="block">
                                Participants: {conversations.find(c => c.id === selectedConversation).participants.map(p => p.replace('_', ' ')).join(', ')}
                              </Typography>
                              <Typography variant="caption" display="block">
                                Last Activity: {format(new Date(conversations.find(c => c.id === selectedConversation).lastActivity), 'PPpp')}
                              </Typography>
                              <Typography variant="caption" display="block">
                                Messages: {conversations.find(c => c.id === selectedConversation).messageCount}
                              </Typography>
                              <Typography variant="caption" display="block">
                                Status: {conversations.find(c => c.id === selectedConversation).status}
                              </Typography>
                            </Box>
                          )}
                        </Collapse>
                      </Box>
                      
                      {/* Message List */}
                      <Box 
                        ref={messageContainerRef}
                        sx={{ 
                          flexGrow: 1, 
                          overflow: 'auto',
                          display: 'flex',
                          flexDirection: 'column',
                          p: 2,
                          bgcolor: 'background.default',
                          borderRadius: 1
                        }}
                      >
                        {loading ? (
                          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                            <CircularProgress size={24} />
                          </Box>
                        ) : error ? (
                          <Box sx={{ p: 2 }}>
                            <Typography color="error">{error}</Typography>
                          </Box>
                        ) : messages.length === 0 ? (
                          <Box sx={{ p: 2 }}>
                            <Typography>No messages found.</Typography>
                          </Box>
                        ) : (
                          messages.map(renderMessageItem)
                        )}
                      </Box>
                    </>
                  ) : (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                      <Typography color="textSecondary">Select a conversation to view messages</Typography>
                    </Box>
                  )}
                </Box>
              </Box>
            </Box>
          )}
          
          {/* Agent Activity Tab */}
          {activeTab === 1 && (
            <Box>
              {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              ) : error ? (
                <Box sx={{ p: 2 }}>
                  <Typography color="error">{error}</Typography>
                </Box>
              ) : (
                renderAgentActivity()
              )}
            </Box>
          )}
          
          {/* Metrics Tab */}
          {activeTab === 2 && (
            <Box>
              {/* Agent Metrics */}
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2">Agent Metrics</Typography>
                  <IconButton size="small" onClick={() => toggleSection('agentMetrics')}>
                    {expandedSections.agentMetrics ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>
                <Collapse in={expandedSections.agentMetrics}>
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : error ? (
                    <Box sx={{ p: 2 }}>
                      <Typography color="error">{error}</Typography>
                    </Box>
                  ) : (
                    renderAgentMetricsCharts()
                  )}
                </Collapse>
              </Box>
              
              {/* Communication Analysis */}
              <Box>
                <Typography variant="subtitle2" gutterBottom>Communication Analysis</Typography>
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Metric</TableCell>
                        <TableCell align="right">Value</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Total Messages</TableCell>
                        <TableCell align="right">
                          {Object.values(agentMetrics.messagesByAgent || {}).reduce((sum, val) => sum + val, 0)}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Most Active Agent</TableCell>
                        <TableCell align="right">
                          {Object.entries(agentMetrics.messagesByAgent || {})
                            .sort((a, b) => b[1] - a[1])
                            .slice(0, 1)
                            .map(([agent, count]) => `${agent.replace('_', ' ')} (${count})`)
                          }
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Most Common Pattern</TableCell>
                        <TableCell align="right">
                          {Object.entries(agentMetrics.messagesByPattern || {})
                            .sort((a, b) => b[1] - a[1])
                            .slice(0, 1)
                            .map(([pattern, count]) => `${pattern.replace('_', ' ')} (${count})`)
                          }
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Average Response Time</TableCell>
                        <TableCell align="right">
                          {Object.values(agentMetrics.responseTimesByAgent || {}).length > 0
                            ? `${(Object.values(agentMetrics.responseTimesByAgent).reduce((sum, val) => sum + val, 0) / 
                                Object.values(agentMetrics.responseTimesByAgent).length).toFixed(2)} minutes`
                            : 'N/A'
                          }
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Average Collaboration Score</TableCell>
                        <TableCell align="right">
                          {Object.values(agentMetrics.collaborationScores || {}).length > 0
                            ? `${(Object.values(agentMetrics.collaborationScores).reduce((sum, val) => sum + val, 0) / 
                                Object.values(agentMetrics.collaborationScores).length).toFixed(2)} / 10`
                            : 'N/A'
                          }
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    </Drawer>
  );
};

export default AgentConversationMonitoringPanel;
