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
import { 
  Box, 
  Paper, 
  Typography, 
  LinearProgress, 
  Chip, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Avatar, 
  Button,
  Card,
  CardContent,
  Grid,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';

import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Flag as MilestoneIcon,
  AccessTime as TimeIcon,
  ArrowUpward as TrendUpIcon,
  ArrowDownward as TrendDownIcon,
  Info as InfoIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip as RechartsTooltip } from 'recharts';

/**
 * ProjectOverviewPanel component
 * 
 * Displays high-level project information including:
 * - Project name and status
 * - Overall progress
 * - Next milestone information
 * - Recent activity feed
 * - Key metrics and indicators
 */
const ProjectOverviewPanel = ({ 
  projectData, 
  onViewAllActivity, 
  onViewProjectDetails,
  refreshData
}) => {
  // State for loading
  const [loading, setLoading] = useState(false);
  
  // Status color mapping
  const statusColors = {
    on_track: '#4caf50',
    at_risk: '#ff9800',
    behind: '#f44336',
    completed: '#4caf50'
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
    performance_engineer: <Avatar sx={{ bgcolor: '#673ab7' }}>PE</Avatar>
  };
  
  // Calculate days until next milestone
  const calculateDaysUntil = (dateString) => {
    const today = new Date();
    const targetDate = new Date(dateString);
    const diffTime = targetDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
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
  
  // Calculate key metrics
  const calculateKeyMetrics = () => {
    if (!projectData) return [];
    
    return [
      {
        label: 'Tasks',
        value: projectData.taskMetrics?.total || 0,
        completed: projectData.taskMetrics?.completed || 0,
        color: '#1976d2'
      },
      {
        label: 'Issues',
        value: projectData.issueMetrics?.total || 0,
        resolved: projectData.issueMetrics?.resolved || 0,
        color: '#f44336'
      },
      {
        label: 'Milestones',
        value: projectData.milestoneMetrics?.total || 0,
        completed: projectData.milestoneMetrics?.completed || 0,
        color: '#4caf50'
      }
    ];
  };
  
  // If no project data is provided, show a placeholder
  if (!projectData) {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography variant="body1" color="textSecondary">No project data available</Typography>
      </Paper>
    );
  }
  
  const daysUntilNextMilestone = calculateDaysUntil(projectData.nextMilestone?.dueDate);
  const keyMetrics = calculateKeyMetrics();
  
  return (
    <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
      {/* Header with refresh button */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="h5">{projectData.name}</Typography>
          <Chip 
            label={projectData.status === 'on_track' ? 'On Track' : projectData.status === 'at_risk' ? 'At Risk' : 'Behind'} 
            sx={{ 
              ml: 2,
              bgcolor: statusColors[projectData.status],
              color: 'white',
              fontWeight: 'bold'
            }} 
          />
        </Box>
        <IconButton onClick={handleRefresh} disabled={loading}>
          <RefreshIcon />
        </IconButton>
      </Box>
      
      {/* Loading indicator */}
      {loading && (
        <LinearProgress sx={{ mb: 2 }} />
      )}
      
      {/* Project dates */}
      <Typography variant="body2" color="textSecondary" gutterBottom>
        {projectData.startDate} to {projectData.endDate}
      </Typography>
      
      {/* Overall progress */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
          <Typography variant="body2" color="textSecondary">Overall Progress</Typography>
          <Typography variant="body2" color="textSecondary">{`${projectData.progress}%`}</Typography>
        </Box>
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
      
      {/* Key metrics */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {keyMetrics.map((metric, index) => (
          <Grid item xs={4} key={index}>
            <Card variant="outlined" sx={{ borderColor: 'transparent', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
              <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="caption" color="textSecondary" gutterBottom>
                  {metric.label}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'baseline' }}>
                  <Typography variant="h6" sx={{ mr: 1 }}>
                    {metric.value}
                  </Typography>
                  {metric.completed !== undefined && (
                    <Typography variant="caption" color="success.main">
                      {metric.completed} completed
                    </Typography>
                  )}
                  {metric.resolved !== undefined && (
                    <Typography variant="caption" color="success.main">
                      {metric.resolved} resolved
                    </Typography>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      
      {/* Next milestone */}
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
      
      {/* Team allocation */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>Team Allocation</Typography>
        <ResponsiveContainer width="100%" height={120}>
          <PieChart>
            <Pie
              data={projectData.teamAllocation || []}
              cx="50%"
              cy="50%"
              innerRadius={30}
              outerRadius={50}
              paddingAngle={2}
              dataKey="value"
              nameKey="name"
            >
              {(projectData.teamAllocation || []).map((entry, index) => (
                <Cell key={`cell-${index}`} fill={['#1976d2', '#4caf50', '#ff9800', '#f44336', '#9c27b0'][index % 5]} />
              ))}
            </Pie>
            <RechartsTooltip formatter={(value, name) => [`${value}%`, name]} />
          </PieChart>
        </ResponsiveContainer>
      </Box>
      
      {/* Recent activity */}
      <Box>
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
              {activity.trend && (
                <Box>
                  {activity.trend === 'up' ? (
                    <TrendUpIcon sx={{ color: activity.trendColor || '#4caf50' }} />
                  ) : (
                    <TrendDownIcon sx={{ color: activity.trendColor || '#f44336' }} />
                  )}
                </Box>
              )}
            </ListItem>
          ))}
        </List>
      </Box>
      
      {/* Action buttons */}
      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
        <Button 
          variant="outlined" 
          size="small"
          onClick={onViewAllActivity}
        >
          View All Activity
        </Button>
        <Button 
          variant="contained" 
          size="small"
          onClick={onViewProjectDetails}
        >
          Project Details
        </Button>
      </Box>
    </Paper>
  );
};

export default ProjectOverviewPanel;
