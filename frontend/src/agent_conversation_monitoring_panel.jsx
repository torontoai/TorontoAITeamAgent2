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
import { Box, Typography, Paper, Grid, TextField, Button, Divider, Chip, List, ListItem, ListItemText, FormControl, InputLabel, Select, MenuItem } from '@mui/material';

function AgentConversationMonitoringPanel() {
  const [filter, setFilter] = useState({
    agent: 'all',
    pattern: 'all',
    search: ''
  });
  
  const handleFilterChange = (event) => {
    setFilter({
      ...filter,
      [event.target.name]: event.target.value
    });
  };
  
  // Sample conversation data
  const conversations = [
    {
      id: 1,
      from: 'project_manager',
      to: 'all',
      time: '02:21:41',
      message: "I've analyzed the requirements. Let's break this down into subtasks."
    },
    {
      id: 2,
      from: 'product_manager',
      to: 'all',
      time: '02:21:42',
      message: "I've analyzed the requirements. We need to ensure proper input validation and error handling."
    },
    {
      id: 3,
      from: 'system_architect',
      to: 'developer',
      time: '02:21:43',
      message: "I recommend using a dictionary for mapping operations to functions for cleaner code."
    },
    {
      id: 4,
      from: 'developer',
      to: 'all',
      time: '02:21:44',
      message: "I'm starting implementation now. Will focus on core functionality first, then add validation and error handling."
    }
  ];
  
  // Filter conversations based on current filter settings
  const filteredConversations = conversations.filter(conv => {
    const agentMatch = filter.agent === 'all' || conv.from === filter.agent || conv.to === filter.agent;
    const patternMatch = filter.pattern === 'all' || 
                         (filter.pattern === 'broadcast' && conv.to === 'all') ||
                         (filter.pattern === 'direct' && conv.to !== 'all');
    const searchMatch = !filter.search || 
                        conv.message.toLowerCase().includes(filter.search.toLowerCase()) ||
                        conv.from.toLowerCase().includes(filter.search.toLowerCase()) ||
                        conv.to.toLowerCase().includes(filter.search.toLowerCase());
    
    return agentMatch && patternMatch && searchMatch;
  });
  
  return (
    <>
      <Typography variant="h6" gutterBottom>
        Agent Conversations
      </Typography>
      
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth size="small">
            <InputLabel id="agent-filter-label">Agent</InputLabel>
            <Select
              labelId="agent-filter-label"
              name="agent"
              value={filter.agent}
              label="Agent"
              onChange={handleFilterChange}
            >
              <MenuItem value="all">All Agents</MenuItem>
              <MenuItem value="project_manager">Project Manager</MenuItem>
              <MenuItem value="product_manager">Product Manager</MenuItem>
              <MenuItem value="developer">Developer</MenuItem>
              <MenuItem value="system_architect">System Architect</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={3}>
          <FormControl fullWidth size="small">
            <InputLabel id="pattern-filter-label">Pattern</InputLabel>
            <Select
              labelId="pattern-filter-label"
              name="pattern"
              value={filter.pattern}
              label="Pattern"
              onChange={handleFilterChange}
            >
              <MenuItem value="all">All Patterns</MenuItem>
              <MenuItem value="broadcast">Broadcast</MenuItem>
              <MenuItem value="direct">Direct Message</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            size="small"
            name="search"
            label="Search"
            variant="outlined"
            value={filter.search}
            onChange={handleFilterChange}
          />
        </Grid>
      </Grid>
      
      {filteredConversations.map((conv) => (
        <Paper key={conv.id} sx={{ p: 2, mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight="bold">
              From: {conv.from} To: {conv.to}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Time: {conv.time}
            </Typography>
          </Box>
          
          <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'background.paper' }}>
            <Typography variant="body1">
              {conv.message}
            </Typography>
          </Paper>
        </Paper>
      ))}
      
      {filteredConversations.length === 0 && (
        <Paper sx={{ p: 2, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No conversations match your filter criteria.
          </Typography>
        </Paper>
      )}
    </>
  );
}

export default AgentConversationMonitoringPanel;
