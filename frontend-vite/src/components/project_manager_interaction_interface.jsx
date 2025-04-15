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

import React, { useState } from 'react';
import { Box, Typography, Paper, Grid, TextField, Button, Divider, Chip, List, ListItem, ListItemText } from '@mui/material';

function ProjectManagerInteractionInterface() {
  const [message, setMessage] = useState('');
  
  const handleMessageChange = (event) => {
    setMessage(event.target.value);
  };
  
  const handleSendMessage = () => {
    // In a real implementation, this would send the message to the Project Manager
    console.log('Sending message to Project Manager:', message);
    setMessage('');
  };
  
  // Sample human input requests from agents
  const requests = [
    {
      id: 1,
      agent: 'project_manager',
      priority: 'high',
      category: 'decision',
      message: 'Should we implement additional operations like power or square root?',
      status: 'pending'
    },
    {
      id: 2,
      agent: 'developer',
      priority: 'medium',
      category: 'feedback',
      message: 'Please review the implementation of the calculator function',
      status: 'pending'
    }
  ];
  
  return (
    <>
      <Typography variant="h6" gutterBottom>
        Human Input Requests
      </Typography>
      
      {requests.map((request) => (
        <Paper key={request.id} sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight="bold">
              Request from {request.agent}
            </Typography>
            <Chip 
              label={request.status} 
              color={request.status === 'pending' ? 'warning' : 'success'} 
              size="small" 
            />
          </Box>
          
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Priority: {request.priority} | Category: {request.category}
          </Typography>
          
          <Typography variant="body1" paragraph>
            {request.message}
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button variant="outlined" color="inherit">
              Approve
            </Button>
            <Button variant="contained" color="primary">
              Respond
            </Button>
          </Box>
        </Paper>
      ))}
      
      <Divider sx={{ my: 3 }} />
      
      <Typography variant="h6" gutterBottom>
        Direct Communication with Project Manager
      </Typography>
      
      <Paper sx={{ p: 2 }}>
        <List sx={{ maxHeight: 200, overflow: 'auto', mb: 2 }}>
          <ListItem>
            <ListItemText 
              primary="Project Manager" 
              secondary="I've analyzed the requirements and created a plan for implementation. Do you have any specific priorities for this sprint?" 
            />
          </ListItem>
          <ListItem>
            <ListItemText 
              primary="You" 
              secondary="Let's focus on the core calculator functionality first, then add advanced features if time permits." 
              sx={{ textAlign: 'right' }}
            />
          </ListItem>
          <ListItem>
            <ListItemText 
              primary="Project Manager" 
              secondary="Understood. I'll coordinate with the team to prioritize core functionality." 
            />
          </ListItem>
        </List>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message to the Project Manager..."
            value={message}
            onChange={handleMessageChange}
          />
          <Button 
            variant="contained" 
            color="primary"
            onClick={handleSendMessage}
            disabled={!message.trim()}
          >
            Send
          </Button>
        </Box>
      </Paper>
    </>
  );
}

export default ProjectManagerInteractionInterface;
