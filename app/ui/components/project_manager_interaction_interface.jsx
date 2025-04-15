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
  Paper, 
  Typography, 
  Grid,
  Card,
  CardContent,
  Divider,
  Button,
  IconButton,
  TextField,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemAvatar,
  ListItemButton,
  Chip,
  Badge,
  Menu,
  MenuItem,
  Tooltip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Tabs,
  Tab,
  Drawer,
  AppBar,
  Toolbar,
  CircularProgress
} from '@mui/material';

import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  MoreVert as MoreVertIcon,
  FilterList as FilterIcon,
  Sort as SortIcon,
  Search as SearchIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Flag as FlagIcon,
  AccessTime as TimeIcon,
  PriorityHigh as PriorityHighIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  QuestionAnswer as QuestionAnswerIcon,
  Assignment as AssignmentIcon,
  Lightbulb as LightbulbIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';

/**
 * ProjectManagerInteractionInterface component
 * 
 * Provides an interface for users to interact with the Project Manager agent, including:
 * - Direct messaging with the Project Manager
 * - Viewing and responding to information requests from agents
 * - Decision points requiring human input
 * - Suggestion feed from Project Manager
 */
const ProjectManagerInteractionInterface = ({ 
  pmInteractionData,
  onSendMessage,
  onRespondToRequest,
  onApproveReject,
  onFilterChange,
  refreshData
}) => {
  // State for loading
  const [loading, setLoading] = useState(false);
  
  // State for message input
  const [messageInput, setMessageInput] = useState('');
  
  // State for active tab
  const [activeTab, setActiveTab] = useState(0);
  
  // State for filter menu
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  
  // State for sort menu
  const [sortAnchorEl, setSortAnchorEl] = useState(null);
  
  // State for request dialog
  const [requestDialogOpen, setRequestDialogOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [responseInput, setResponseInput] = useState('');
  
  // State for filters
  const [filters, setFilters] = useState({
    priority: 'all',
    type: 'all',
    status: 'all'
  });
  
  // State for sort
  const [sortBy, setSortBy] = useState('time');
  
  // Ref for message list
  const messageListRef = useRef(null);
  
  // Effect to scroll to bottom of message list when new messages arrive
  useEffect(() => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
    }
  }, [pmInteractionData?.recentMessages]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle message input change
  const handleMessageInputChange = (event) => {
    setMessageInput(event.target.value);
  };
  
  // Handle send message
  const handleSendMessage = () => {
    if (messageInput.trim() && onSendMessage) {
      onSendMessage(messageInput);
      setMessageInput('');
    }
  };
  
  // Handle key press in message input
  const handleMessageKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };
  
  // Handle filter menu open
  const handleFilterMenuOpen = (event) => {
    setFilterAnchorEl(event.currentTarget);
  };
  
  // Handle filter menu close
  const handleFilterMenuClose = () => {
    setFilterAnchorEl(null);
  };
  
  // Handle sort menu open
  const handleSortMenuOpen = (event) => {
    setSortAnchorEl(event.currentTarget);
  };
  
  // Handle sort menu close
  const handleSortMenuClose = () => {
    setSortAnchorEl(null);
  };
  
  // Handle filter change
  const handleFilterChange = (filterType, value) => {
    const newFilters = { ...filters, [filterType]: value };
    setFilters(newFilters);
    
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
    
    handleFilterMenuClose();
  };
  
  // Handle sort change
  const handleSortChange = (value) => {
    setSortBy(value);
    handleSortMenuClose();
  };
  
  // Handle open request dialog
  const handleOpenRequestDialog = (request) => {
    setSelectedRequest(request);
    setRequestDialogOpen(true);
    setResponseInput('');
  };
  
  // Handle close request dialog
  const handleCloseRequestDialog = () => {
    setRequestDialogOpen(false);
    setSelectedRequest(null);
  };
  
  // Handle response input change
  const handleResponseInputChange = (event) => {
    setResponseInput(event.target.value);
  };
  
  // Handle respond to request
  const handleRespondToRequest = () => {
    if (responseInput.trim() && selectedRequest && onRespondToRequest) {
      onRespondToRequest(selectedRequest.id, responseInput);
      handleCloseRequestDialog();
    }
  };
  
  // Handle approve/reject
  const handleApproveReject = (requestId, approved) => {
    if (onApproveReject) {
      onApproveReject(requestId, approved);
    }
  };
  
  // Handle refresh
  const handleRefresh = () => {
    setLoading(true);
    
    // Call the refresh function passed as prop
    if (refreshData) {
      refreshData().finally(() => {
        setLoading(false);
      });
    } else {
      // If no refresh function is provided, just simulate loading
      setTimeout(() => {
        setLoading(false);
      }, 1000);
    }
  };
  
  // Agent icon mapping
  const agentIcons = {
    project_manager: <Avatar sx={{ bgcolor: '#1976d2' }}>PM</Avatar>,
    product_manager: <Avatar sx={{ bgcolor: '#9c27b0' }}>PD</Avatar>,
    developer: <Avatar sx={{ bgcolor: '#4caf50' }}>DEV</Avatar>,
    system_architect: <Avatar sx={{ bgcolor: '#ff9800' }}>SA</Avatar>,
    qa_testing_specialist: <Avatar sx={{ bgcolor: '#f44336' }}>QA</Avatar>,
    devops_engineer: <Avatar sx={{ bgcolor: '#9c27b0' }}>DO</Avatar>,
    ui_ux_designer: <Avatar sx={{ bgcolor: '#2196f3' }}>UI</Avatar>,
    documentation_specialist: <Avatar sx={{ bgcolor: '#795548' }}>DOC</Avatar>,
    security_engineer: <Avatar sx={{ bgcolor: '#607d8b' }}>SE</Avatar>,
    database_engineer: <Avatar sx={{ bgcolor: '#009688' }}>DB</Avatar>,
    performance_engineer: <Avatar sx={{ bgcolor: '#673ab7' }}>PE</Avatar>,
    human: <Avatar sx={{ bgcolor: '#e91e63' }}>H</Avatar>
  };
  
  // Request type icon mapping
  const requestTypeIcons = {
    decision: <AssignmentIcon />,
    clarification: <QuestionAnswerIcon />,
    approval: <CheckCircleIcon />,
    information: <InfoIcon />
  };
  
  // Priority icon mapping
  const priorityIcons = {
    high: <ErrorIcon color="error" />,
    medium: <WarningIcon color="warning" />,
    low: <InfoIcon color="success" />
  };
  
  // If no interaction data is provided, show a placeholder
  if (!pmInteractionData) {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography variant="body1" color="textSecondary">No interaction data available</Typography>
      </Paper>
    );
  }
  
  // Filter and sort pending requests
  const filteredRequests = pmInteractionData.pendingRequests.filter(request => {
    if (filters.priority !== 'all' && request.priority !== filters.priority) return false;
    if (filters.type !== 'all' && request.type !== filters.type) return false;
    if (filters.status !== 'all' && request.status !== filters.status) return false;
    return true;
  }).sort((a, b) => {
    if (sortBy === 'priority') {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    } else if (sortBy === 'time') {
      // Simple string comparison for demo purposes
      // In a real app, you'd parse the time strings to Date objects
      return a.time > b.time ? -1 : 1;
    } else if (sortBy === 'type') {
      return a.type.localeCompare(b.type);
    } else if (sortBy === 'agent') {
      return a.from.localeCompare(b.from);
    }
    return 0;
  });
  
  // Render message list
  const renderMessageList = () => {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {agentIcons.project_manager}
            <Box sx={{ ml: 1 }}>
              <Typography variant="subtitle1">Project Manager</Typography>
              <Typography variant="body2" color="textSecondary">
                {pmInteractionData.pmStatus === 'online' ? 'Online' : 'Offline'}
              </Typography>
            </Box>
          </Box>
          <IconButton onClick={handleRefresh} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
        
        {/* Loading indicator */}
        {loading && (
          <LinearProgress />
        )}
        
        <List 
          sx={{ 
            flexGrow: 1, 
            overflow: 'auto', 
            p: 2,
            bgcolor: '#f5f5f5'
          }}
          ref={messageListRef}
        >
          {pmInteractionData.recentMessages.map((message, index) => (
            <ListItem 
              key={message.id} 
              sx={{ 
                mb: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: message.from === 'human' ? 'flex-end' : 'flex-start',
                p: 0
              }}
            >
              <Box 
                sx={{ 
                  display: 'flex', 
                  flexDirection: message.from === 'human' ? 'row-reverse' : 'row',
                  alignItems: 'flex-start',
                  maxWidth: '80%'
                }}
              >
                {message.from !== 'human' && (
                  <Box sx={{ mr: 1, mt: 0.5 }}>
                    {agentIcons[message.from] || <Avatar>A</Avatar>}
                  </Box>
                )}
                <Box 
                  sx={{ 
                    bgcolor: message.from === 'human' ? '#1976d2' : 'white',
                    color: message.from === 'human' ? 'white' : 'inherit',
                    p: 2,
                    borderRadius: 2,
                    boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                    maxWidth: '100%',
                    wordBreak: 'break-word'
                  }}
                >
                  <Typography variant="body1">{message.content}</Typography>
                </Box>
                {message.from === 'human' && (
                  <Box sx={{ ml: 1, mt: 0.5 }}>
                    {agentIcons.human}
                  </Box>
                )}
              </Box>
              <Typography 
                variant="caption" 
                color="textSecondary"
                sx={{ 
                  mt: 0.5,
                  ml: message.from === 'human' ? 0 : 5,
                  mr: message.from === 'human' ? 5 : 0
                }}
              >
                {message.time}
              </Typography>
            </ListItem>
          ))}
        </List>
        
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type a message..."
              value={messageInput}
              onChange={handleMessageInputChange}
              onKeyPress={handleMessageKeyPress}
              multiline
              maxRows={4}
              size="small"
              sx={{ mr: 1 }}
            />
            <Button
              variant="contained"
              color="primary"
              endIcon={<SendIcon />}
              onClick={handleSendMessage}
              disabled={!messageInput.trim()}
            >
              Send
            </Button>
          </Box>
        </Box>
      </Box>
    );
  };
  
  // Render pending requests
  const renderPendingRequests = () => {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle1">
            Pending Requests ({filteredRequests.length})
          </Typography>
          <Box>
            <IconButton onClick={handleFilterMenuOpen}>
              <FilterIcon />
            </IconButton>
            <Menu
              anchorEl={filterAnchorEl}
              open={Boolean(filterAnchorEl)}
              onClose={handleFilterMenuClose}
            >
              <Typography variant="subtitle2" sx={{ px: 2, py: 1 }}>Filter by Priority</Typography>
              <MenuItem 
                onClick={() => handleFilterChange('priority', 'all')}
                selected={filters.priority === 'all'}
              >
                All Priorities
              </MenuItem>
              <MenuItem 
                onClick={() => handleFilterChange('priority', 'high')}
                selected={filters.priority === 'high'}
              >
                <ListItemIcon>{priorityIcons.high}</ListItemIcon>
                High Priority
              </MenuItem>
              <MenuItem 
                onClick={() => handleFilterChange('priority', 'medium')}
                selected={filters.priority === 'medium'}
              >
                <ListItemIcon>{priorityIcons.medium}</ListItemIcon>
                Medium Priority
              </MenuItem>
              <MenuItem 
                onClick={() => handleFilterChange('priority', 'low')}
                selected={filters.priority === 'low'}
              >
                <ListItemIcon>{priorityIcons.low}</ListItemIcon>
                Low Priority
              </MenuItem>
              <Divider />
              <Typography variant="subtitle2" sx={{ px: 2, py: 1 }}>Filter by Type</Typography>
              <MenuItem 
                onClick={() => handleFilterChange('type', 'all')}
                selected={filters.type === 'all'}
              >
                All Types
              </MenuItem>
              <MenuItem 
                onClick={() => handleFilterChange('type', 'decision')}
                selected={filters.type === 'decision'}
              >
                <ListItemIcon>{requestTypeIcons.decision}</ListItemIcon>
                Decision
              </MenuItem>
              <MenuItem 
                onClick={() => handleFilterChange('type', 'clarification')}
                selected={filters.type === 'clarification'}
              >
                <ListItemIcon>{requestTypeIcons.clarification}</ListItemIcon>
                Clarification
              </MenuItem>
              <MenuItem 
                onClick={() => handleFilterChange('type', 'approval')}
                selected={filters.type === 'approval'}
              >
                <ListItemIcon>{requestTypeIcons.approval}</ListItemIcon>
                Approval
              </MenuItem>
              <MenuItem 
                onClick={() => handleFilterChange('type', 'information')}
                selected={filters.type === 'information'}
              >
                <ListItemIcon>{requestTypeIcons.information}</ListItemIcon>
                Information
              </MenuItem>
            </Menu>
            
            <IconButton onClick={handleSortMenuOpen}>
              <SortIcon />
            </IconButton>
            <Menu
              anchorEl={sortAnchorEl}
              open={Boolean(sortAnchorEl)}
              onClose={handleSortMenuClose}
            >
              <MenuItem 
                onClick={() => handleSortChange('priority')}
                selected={sortBy === 'priority'}
              >
                Sort by Priority
              </MenuItem>
              <MenuItem 
                onClick={() => handleSortChange('time')}
                selected={sortBy === 'time'}
              >
                Sort by Time
              </MenuItem>
              <MenuItem 
                onClick={() => handleSortChange('type')}
                selected={sortBy === 'type'}
              >
                Sort by Type
              </MenuItem>
              <MenuItem 
                onClick={() => handleSortChange('agent')}
                selected={sortBy === 'agent'}
              >
                Sort by Agent
              </MenuItem>
            </Menu>
            
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Box>
        </Box>
        
        {/* Loading indicator */}
        {loading && (
          <LinearProgress />
        )}
        
        <List sx={{ flexGrow: 1, overflow: 'auto', p: 0 }}>
          {filteredRequests.length > 0 ? (
            filteredRequests.map((request) => (
              <ListItem 
                key={request.id} 
                divider
                sx={{ px: 2, py: 1.5 }}
              >
                <ListItemAvatar>
                  {agentIcons[request.from] || <Avatar>A</Avatar>}
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Chip 
                        label={request.type} 
                        size="small"
                        icon={requestTypeIcons[request.type]}
                        sx={{ 
                          mr: 1, 
                          bgcolor: request.type === 'decision' ? '#1976d2' : request.type === 'clarification' ? '#ff9800' : request.type === 'approval' ? '#4caf50' : '#2196f3',
                          color: 'white',
                          '& .MuiChip-icon': {
                            color: 'white'
                          }
                        }} 
                      />
                      <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                        {request.title}
                      </Typography>
                      {priorityIcons[request.priority]}
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {request.description}
                      </Typography>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" color="textSecondary">
                          From: {request.from.replace('_', ' ')} • {request.time}
                        </Typography>
                        <Box>
                          {request.type === 'approval' ? (
                            <>
                              <Button 
                                variant="outlined" 
                                color="success" 
                                size="small" 
                                sx={{ mr: 1 }}
                                onClick={() => handleApproveReject(request.id, true)}
                              >
                                Approve
                              </Button>
                              <Button 
                                variant="outlined" 
                                color="error" 
                                size="small"
                                onClick={() => handleApproveReject(request.id, false)}
                              >
                                Reject
                              </Button>
                            </>
                          ) : (
                            <Button 
                              variant="contained" 
                              size="small"
                              onClick={() => handleOpenRequestDialog(request)}
                            >
                              Respond
                            </Button>
                          )}
                        </Box>
                      </Box>
                    </Box>
                  }
                />
              </ListItem>
            ))
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="textSecondary">
                No pending requests match your filters
              </Typography>
            </Box>
          )}
        </List>
      </Box>
    );
  };
  
  // Render PM suggestions
  const renderPMSuggestions = () => {
    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="subtitle1">
            Project Manager Suggestions
          </Typography>
          <IconButton onClick={handleRefresh} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
        
        {/* Loading indicator */}
        {loading && (
          <LinearProgress />
        )}
        
        <List sx={{ flexGrow: 1, overflow: 'auto', p: 2 }}>
          {pmInteractionData.suggestions.length > 0 ? (
            pmInteractionData.suggestions.map((suggestion) => (
              <Card key={suggestion.id} sx={{ mb: 2, boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                    <LightbulbIcon sx={{ color: '#ff9800', mr: 1 }} />
                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                          {suggestion.title}
                        </Typography>
                        <Chip 
                          label={suggestion.impact} 
                          size="small"
                          sx={{ 
                            bgcolor: suggestion.impact === 'high' ? '#f44336' : suggestion.impact === 'medium' ? '#ff9800' : '#4caf50',
                            color: 'white',
                            height: 24
                          }} 
                        />
                      </Box>
                      <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                        {suggestion.reason}
                      </Typography>
                    </Box>
                  </Box>
                  
                  {suggestion.benefits && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        Benefits:
                      </Typography>
                      <Typography variant="body2">
                        {suggestion.benefits}
                      </Typography>
                    </Box>
                  )}
                  
                  {suggestion.considerations && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        Considerations:
                      </Typography>
                      <Typography variant="body2">
                        {suggestion.considerations}
                      </Typography>
                    </Box>
                  )}
                  
                  <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button 
                      variant="outlined" 
                      size="small" 
                      sx={{ mr: 1 }}
                      onClick={() => {
                        setMessageInput(`Let's discuss your suggestion about "${suggestion.title}"`);
                        setActiveTab(0);
                      }}
                    >
                      Discuss
                    </Button>
                    <Button 
                      variant="contained" 
                      size="small"
                      onClick={() => {
                        setMessageInput(`I'd like to implement your suggestion about "${suggestion.title}". Please proceed with the necessary steps.`);
                        setActiveTab(0);
                      }}
                    >
                      Implement
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            ))
          ) : (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body1" color="textSecondary">
                No suggestions available at this time
              </Typography>
            </Box>
          )}
        </List>
      </Box>
    );
  };
  
  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 0:
        return renderMessageList();
      case 1:
        return renderPendingRequests();
      case 2:
        return renderPMSuggestions();
      default:
        return null;
    }
  };
  
  return (
    <Paper elevation={0} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        variant="fullWidth"
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab 
          icon={<QuestionAnswerIcon />} 
          label="Chat" 
          iconPosition="start"
        />
        <Tab 
          icon={
            <Badge 
              badgeContent={pmInteractionData.pendingRequests.length} 
              color="error"
              max={99}
            >
              <AssignmentIcon />
            </Badge>
          } 
          label="Requests" 
          iconPosition="start"
        />
        <Tab 
          icon={
            <Badge 
              badgeContent={pmInteractionData.suggestions.length} 
              color="primary"
              max={99}
            >
              <LightbulbIcon />
            </Badge>
          } 
          label="Suggestions" 
          iconPosition="start"
        />
      </Tabs>
      
      {/* Main content */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {renderContent()}
      </Box>
      
      {/* Request response dialog */}
      <Dialog
        open={requestDialogOpen}
        onClose={handleCloseRequestDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Respond to Request
        </DialogTitle>
        <DialogContent>
          {selectedRequest && (
            <>
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'flex-start' }}>
                <Box sx={{ mr: 2 }}>
                  {agentIcons[selectedRequest.from] || <Avatar>A</Avatar>}
                </Box>
                <Box>
                  <Typography variant="subtitle1">{selectedRequest.title}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    From: {selectedRequest.from.replace('_', ' ')} • {selectedRequest.time}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body1" sx={{ mb: 3 }}>
                {selectedRequest.description}
              </Typography>
              <TextField
                autoFocus
                label="Your Response"
                fullWidth
                multiline
                rows={4}
                variant="outlined"
                value={responseInput}
                onChange={handleResponseInputChange}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseRequestDialog}>Cancel</Button>
          <Button 
            onClick={handleRespondToRequest} 
            variant="contained"
            disabled={!responseInput.trim()}
          >
            Send Response
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default ProjectManagerInteractionInterface;
