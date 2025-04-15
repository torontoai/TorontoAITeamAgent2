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

import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Collapse, IconButton, List, ListItem, ListItemText, ListItemIcon, Chip, Divider, Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField, Select, FormControl, InputLabel, MenuItem, Badge, Grid } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import PriorityHighIcon from '@mui/icons-material/PriorityHigh';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import FeedbackIcon from '@mui/icons-material/Feedback';
import EditIcon from '@mui/icons-material/Edit';
import FilterListIcon from '@mui/icons-material/FilterList';

/**
 * Human Input Request System Component
 * 
 * A collapsible panel that displays and manages human input requests from various agents.
 * The Project Manager acts as the central point for all requests, prioritizing and reformulating
 * them before presenting to the human user.
 * 
 * Features:
 * - Collapsible panel that can be minimized by the user
 * - Prioritized list of requests with status tracking
 * - Filtering by status, priority, and category
 * - Detailed view of each request
 * - Ability to edit and update requests
 * - Status tracking (pending, in progress, completed)
 */
const HumanInputRequestSystem = ({ projectId }) => {
  // State for panel expansion
  const [expanded, setExpanded] = useState(true);
  
  // State for input requests
  const [inputRequests, setInputRequests] = useState([]);
  
  // State for request detail dialog
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  
  // State for edit dialog
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editedRequest, setEditedRequest] = useState(null);
  
  // State for filter dialog
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    category: 'all'
  });
  
  // Mock data for demonstration - would be fetched from backend in real implementation
  useEffect(() => {
    // Simulate fetching data from backend
    const mockRequests = [
      {
        id: 'req_001',
        title: 'Confirm authentication requirements',
        description: 'We need clarification on the authentication methods required for the application. Developer has suggested OAuth2 with JWT tokens. Please confirm if this meets your security requirements.',
        status: 'pending',
        priority: 'high',
        category: 'decision',
        requestedBy: 'Developer',
        createdAt: '2025-04-01T10:30:00Z',
        dueBy: '2025-04-03T16:00:00Z',
        originalRequest: 'What authentication methods should we implement for user login?',
        notes: 'This is blocking progress on the user authentication module.'
      },
      {
        id: 'req_002',
        title: 'Review database schema design',
        description: 'The System Architect has completed the initial database schema design. Please review the attached ER diagram and provide feedback on whether it meets the project requirements.',
        status: 'pending',
        priority: 'medium',
        category: 'feedback',
        requestedBy: 'System Architect',
        createdAt: '2025-04-01T14:15:00Z',
        dueBy: '2025-04-04T16:00:00Z',
        originalRequest: 'Please review the database schema design for the project.',
        notes: 'This will impact data storage and retrieval performance.'
      },
      {
        id: 'req_003',
        title: 'Provide API endpoint specifications',
        description: 'The development team needs detailed specifications for the API endpoints. Please provide the required endpoints, parameters, and expected responses.',
        status: 'in_progress',
        priority: 'medium',
        category: 'information',
        requestedBy: 'Developer',
        createdAt: '2025-04-02T09:45:00Z',
        dueBy: '2025-04-05T16:00:00Z',
        originalRequest: 'What API endpoints should we implement for the frontend to communicate with the backend?',
        notes: 'This information is needed to proceed with backend development.'
      },
      {
        id: 'req_004',
        title: 'Approve UI color scheme',
        description: 'The UI/UX Designer has proposed a color scheme for the application. Please review and approve the color palette to proceed with UI implementation.',
        status: 'completed',
        priority: 'low',
        category: 'approval',
        requestedBy: 'UI/UX Designer',
        createdAt: '2025-04-02T11:20:00Z',
        completedAt: '2025-04-02T15:45:00Z',
        originalRequest: 'Please approve the color scheme for the application UI.',
        notes: 'Color scheme has been approved with minor adjustments to the secondary color.'
      }
    ];
    
    setInputRequests(mockRequests);
  }, [projectId]);
  
  // Filter requests based on current filters
  const filteredRequests = inputRequests.filter(request => {
    if (filters.status !== 'all' && request.status !== filters.status) return false;
    if (filters.priority !== 'all' && request.priority !== filters.priority) return false;
    if (filters.category !== 'all' && request.category !== filters.category) return false;
    return true;
  });
  
  // Count pending requests
  const pendingCount = inputRequests.filter(req => req.status === 'pending').length;
  
  // Handle opening request detail dialog
  const handleOpenDetail = (request) => {
    setSelectedRequest(request);
    setDetailDialogOpen(true);
  };
  
  // Handle opening edit dialog
  const handleOpenEdit = (request) => {
    setEditedRequest({...request});
    setEditDialogOpen(true);
  };
  
  // Handle saving edited request
  const handleSaveEdit = () => {
    if (!editedRequest) return;
    
    // Update the request in the list
    setInputRequests(inputRequests.map(req => 
      req.id === editedRequest.id ? editedRequest : req
    ));
    
    // Close the dialog
    setEditDialogOpen(false);
    setEditedRequest(null);
  };
  
  // Handle updating request status
  const handleUpdateStatus = (requestId, newStatus) => {
    setInputRequests(inputRequests.map(req => {
      if (req.id === requestId) {
        const updatedReq = {...req, status: newStatus};
        if (newStatus === 'completed') {
          updatedReq.completedAt = new Date().toISOString();
        }
        return updatedReq;
      }
      return req;
    }));
    
    // Close the detail dialog if open
    setDetailDialogOpen(false);
  };
  
  // Handle applying filters
  const handleApplyFilters = () => {
    // Filters are already applied through the filteredRequests variable
    setFilterDialogOpen(false);
  };
  
  // Helper function to get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#ff9800'; // Orange
      case 'in_progress': return '#2196f3'; // Blue
      case 'completed': return '#4caf50'; // Green
      default: return '#757575'; // Grey
    }
  };
  
  // Helper function to get priority icon
  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return <PriorityHighIcon sx={{ color: '#f44336' }} />;
      case 'medium': return <PriorityHighIcon sx={{ color: '#ff9800' }} />;
      case 'low': return <PriorityHighIcon sx={{ color: '#4caf50' }} />;
      default: return <PriorityHighIcon sx={{ color: '#757575' }} />;
    }
  };
  
  // Helper function to get category icon
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'decision': return <HelpOutlineIcon />;
      case 'feedback': return <FeedbackIcon />;
      case 'approval': return <CheckCircleOutlineIcon />;
      case 'information': return <HelpOutlineIcon />;
      default: return <HelpOutlineIcon />;
    }
  };
  
  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Calculate time remaining or overdue
  const getTimeStatus = (dueBy) => {
    if (!dueBy) return '';
    
    const now = new Date();
    const due = new Date(dueBy);
    const diffMs = due - now;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (diffMs < 0) {
      return `Overdue by ${Math.abs(diffDays)} days ${Math.abs(diffHours)} hours`;
    } else if (diffDays === 0 && diffHours < 24) {
      return `Due in ${diffHours} hours`;
    } else {
      return `Due in ${diffDays} days ${diffHours} hours`;
    }
  };
  
  return (
    <Paper sx={{ mb: 3, overflow: 'hidden' }}>
      {/* Header with expand/collapse functionality */}
      <Box 
        sx={{ 
          p: 2, 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          bgcolor: '#f5f5f7',
          borderBottom: '1px solid #e0e0e0',
          cursor: 'pointer'
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="h6" component="div">
            Human Input Requests
          </Typography>
          <Badge 
            badgeContent={pendingCount} 
            color="error" 
            sx={{ ml: 2 }}
          />
        </Box>
        <Box>
          <IconButton 
            onClick={(e) => {
              e.stopPropagation();
              setFilterDialogOpen(true);
            }}
            size="small"
            sx={{ mr: 1 }}
          >
            <FilterListIcon />
          </IconButton>
          <IconButton size="small">
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
      </Box>
      
      {/* Collapsible content */}
      <Collapse in={expanded}>
        <List sx={{ p: 0 }}>
          {filteredRequests.length === 0 ? (
            <ListItem>
              <ListItemText primary="No input requests found" />
            </ListItem>
          ) : (
            filteredRequests.map((request) => (
              <React.Fragment key={request.id}>
                <ListItem 
                  sx={{ 
                    py: 1.5,
                    cursor: 'pointer',
                    '&:hover': { bgcolor: '#f9f9f9' }
                  }}
                  onClick={() => handleOpenDetail(request)}
                >
                  <ListItemIcon>
                    {getCategoryIcon(request.category)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {getPriorityIcon(request.priority)}
                        <Typography 
                          variant="subtitle1" 
                          sx={{ ml: 1, fontWeight: request.status === 'pending' ? 600 : 400 }}
                        >
                          {request.title}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                        <Chip 
                          label={request.status} 
                          size="small" 
                          sx={{ 
                            bgcolor: getStatusColor(request.status) + '20',
                            color: getStatusColor(request.status),
                            fontWeight: 500,
                            mr: 1
                          }} 
                        />
                        <Chip 
                          label={request.category} 
                          size="small" 
                          variant="outlined"
                          sx={{ mr: 1 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          From: {request.requestedBy}
                        </Typography>
                      </Box>
                    }
                  />
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(request.createdAt)}
                    </Typography>
                    {request.status !== 'completed' && (
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          color: new Date(request.dueBy) < new Date() ? '#f44336' : '#757575',
                          display: 'flex',
                          alignItems: 'center'
                        }}
                      >
                        <AccessTimeIcon sx={{ fontSize: 14, mr: 0.5 }} />
                        {getTimeStatus(request.dueBy)}
                      </Typography>
                    )}
                  </Box>
                </ListItem>
                <Divider />
              </React.Fragment>
            ))
          )}
        </List>
      </Collapse>
      
      {/* Request Detail Dialog */}
      <Dialog 
        open={detailDialogOpen} 
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedRequest && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6">{selectedRequest.title}</Typography>
                <Box>
                  <IconButton 
                    size="small" 
                    onClick={() => handleOpenEdit(selectedRequest)}
                    sx={{ mr: 1 }}
                  >
                    <EditIcon />
                  </IconButton>
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Description
                </Typography>
                <Typography variant="body1">
                  {selectedRequest.description}
                </Typography>
              </Box>
              
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Status
                  </Typography>
                  <Chip 
                    label={selectedRequest.status} 
                    sx={{ 
                      bgcolor: getStatusColor(selectedRequest.status) + '20',
                      color: getStatusColor(selectedRequest.status),
                      fontWeight: 500
                    }} 
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Priority
                  </Typography>
                  <Chip 
                    label={selectedRequest.priority} 
                    icon={getPriorityIcon(selectedRequest.priority)}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Category
                  </Typography>
                  <Chip 
                    label={selectedRequest.category} 
                    icon={getCategoryIcon(selectedRequest.category)}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Requested By
                  </Typography>
                  <Typography variant="body1">
                    {selectedRequest.requestedBy}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Created At
                  </Typography>
                  <Typography variant="body1">
                    {formatDate(selectedRequest.createdAt)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Due By
                  </Typography>
                  <Typography 
                    variant="body1" 
                    sx={{ 
                      color: selectedRequest.status !== 'completed' && 
                             new Date(selectedRequest.dueBy) < new Date() ? 
                             '#f44336' : 'inherit'
                    }}
                  >
                    {formatDate(selectedRequest.dueBy)}
                    {selectedRequest.status !== 'completed' && (
                      <Typography 
                        component="span" 
                        variant="caption" 
                        sx={{ ml: 1, fontStyle: 'italic' }}
                      >
                        ({getTimeStatus(selectedRequest.dueBy)})
                      </Typography>
                    )}
                  </Typography>
                </Grid>
                {selectedRequest.completedAt && (
                  <Grid item xs={6}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Completed At
                    </Typography>
                    <Typography variant="body1">
                      {formatDate(selectedRequest.completedAt)}
                    </Typography>
                  </Grid>
                )}
              </Grid>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Original Request
                </Typography>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f9f9f9' }}>
                  <Typography variant="body1" sx={{ fontStyle: 'italic' }}>
                    "{selectedRequest.originalRequest}"
                  </Typography>
                </Paper>
              </Box>
              
              {selectedRequest.notes && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Notes
                  </Typography>
                  <Typography variant="body1">
                    {selectedRequest.notes}
                  </Typography>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              {selectedRequest.status === 'pending' && (
                <Button 
                  onClick={() => handleUpdateStatus(selectedRequest.id, 'in_progress')}
                  color="primary"
                >
                  Mark In Progress
                </Button>
              )}
              {(selectedRequest.status === 'pending' || selectedRequest.status === 'in_progress') && (
                <Button 
                  onClick={() => handleUpdateStatus(selectedRequest.id, 'completed')}
                  color="success"
                  variant="contained"
                >
                  Mark Completed
                </Button>
              )}
              <Button onClick={() => setDetailDialogOpen(false)}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
      
      {/* Edit Request Dialog */}
      <Dialog 
        open={editDialogOpen} 
        onClose={() => setEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {editedRequest && (
          <>
            <DialogTitle>Edit Request</DialogTitle>
            <DialogContent dividers>
              <TextField
                label="Title"
                fullWidth
                value={editedRequest.title}
                onChange={(e) => setEditedRequest({...editedRequest, title: e.target.value})}
                margin="normal"
              />
              
              <TextField
                label="Description"
                fullWidth
                multiline
                rows={4}
                value={editedRequest.description}
                onChange={(e) => setEditedRequest({...editedRequest, description: e.target.value})}
                margin="normal"
              />
              
              <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={editedRequest.status}
                    onChange={(e) => setEditedRequest({...editedRequest, status: e.target.value})}
                    label="Status"
                  >
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="in_progress">In Progress</MenuItem>
                    <MenuItem value="completed">Completed</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth margin="normal">
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={editedRequest.priority}
                    onChange={(e) => setEditedRequest({...editedRequest, priority: e.target.value})}
                    label="Priority"
                  >
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth margin="normal">
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={editedRequest.category}
                    onChange={(e) => setEditedRequest({...editedRequest, category: e.target.value})}
                    label="Category"
                  >
                    <MenuItem value="decision">Decision</MenuItem>
                    <MenuItem value="feedback">Feedback</MenuItem>
                    <MenuItem value="approval">Approval</MenuItem>
                    <MenuItem value="information">Information</MenuItem>
                  </Select>
                </FormControl>
              </Box>
              
              <TextField
                label="Notes"
                fullWidth
                multiline
                rows={3}
                value={editedRequest.notes}
                onChange={(e) => setEditedRequest({...editedRequest, notes: e.target.value})}
                margin="normal"
              />
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setEditDialogOpen(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleSaveEdit}
                variant="contained"
                color="primary"
              >
                Save Changes
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
      
      {/* Filter Dialog */}
      <Dialog 
        open={filterDialogOpen} 
        onClose={() => setFilterDialogOpen(false)}
      >
        <DialogTitle>Filter Requests</DialogTitle>
        <DialogContent dividers>
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              label="Status"
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Priority</InputLabel>
            <Select
              value={filters.priority}
              onChange={(e) => setFilters({...filters, priority: e.target.value})}
              label="Priority"
            >
              <MenuItem value="all">All Priorities</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth margin="normal">
            <InputLabel>Category</InputLabel>
            <Select
              value={filters.category}
              onChange={(e) => setFilters({...filters, category: e.target.value})}
              label="Category"
            >
              <MenuItem value="all">All Categories</MenuItem>
              <MenuItem value="decision">Decision</MenuItem>
              <MenuItem value="feedback">Feedback</MenuItem>
              <MenuItem value="approval">Approval</MenuItem>
              <MenuItem value="information">Information</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setFilters({status: 'all', priority: 'all', category: 'all'})}
          >
            Reset
          </Button>
          <Button 
            onClick={handleApplyFilters}
            variant="contained"
            color="primary"
          >
            Apply Filters
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default HumanInputRequestSystem;
