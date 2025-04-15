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
  Grid,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Button,
  IconButton,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  LinearProgress
} from '@mui/material';

import {
  Timeline as TimelineIcon,
  ShowChart as ChartIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Refresh as RefreshIcon,
  DateRange as DateRangeIcon,
  FilterList as FilterIcon,
  GetApp as DownloadIcon,
  Info as InfoIcon
} from '@mui/icons-material';

import { 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  AreaChart, 
  Area, 
  ResponsiveContainer, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend,
  Cell
} from 'recharts';

/**
 * ProgressTrackingVisualizations component
 * 
 * Displays various visualizations for tracking project progress including:
 * - Sprint burndown charts
 * - Velocity tracking
 * - Task completion metrics
 * - Code quality metrics
 * - Trend analysis
 */
const ProgressTrackingVisualizations = ({ 
  progressData, 
  refreshData,
  timeRange = 'sprint',
  onTimeRangeChange
}) => {
  // State for loading
  const [loading, setLoading] = useState(false);
  
  // State for active tab
  const [activeTab, setActiveTab] = useState(0);
  
  // State for selected chart type
  const [chartType, setChartType] = useState('burndown');
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // Handle chart type change
  const handleChartTypeChange = (event) => {
    setChartType(event.target.value);
  };
  
  // Handle time range change
  const handleTimeRangeChange = (event) => {
    if (onTimeRangeChange) {
      onTimeRangeChange(event.target.value);
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
  
  // If no progress data is provided, show a placeholder
  if (!progressData) {
    return (
      <Paper elevation={0} sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography variant="body1" color="textSecondary">No progress data available</Typography>
      </Paper>
    );
  }
  
  // Render sprint burndown chart
  const renderBurndownChart = () => {
    const burndownData = progressData.sprintBurndown || [];
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Sprint Burndown</Typography>
          <Tooltip title="The burndown chart shows the amount of work remaining in the sprint over time. The ideal burndown is represented by the planned line, while the actual progress is shown by the actual line.">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={burndownData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="day" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="planned" 
              stroke="#1976d2" 
              strokeWidth={2} 
              name="Planned Remaining"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line 
              type="monotone" 
              dataKey="actual" 
              stroke="#f44336" 
              strokeWidth={2} 
              name="Actual Remaining"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            Sprint Progress: {progressData.sprintProgress || 0}%
          </Typography>
          <Typography variant="body2" color={progressData.sprintStatus === 'on_track' ? 'success.main' : progressData.sprintStatus === 'at_risk' ? 'warning.main' : 'error.main'}>
            Status: {progressData.sprintStatus === 'on_track' ? 'On Track' : progressData.sprintStatus === 'at_risk' ? 'At Risk' : 'Behind'}
          </Typography>
        </Box>
      </Box>
    );
  };
  
  // Render velocity chart
  const renderVelocityChart = () => {
    const velocityData = progressData.velocity || [];
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Team Velocity</Typography>
          <Tooltip title="The velocity chart shows the amount of work completed in each sprint. This helps in predicting how much work the team can complete in future sprints.">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={velocityData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="sprint" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            <Bar 
              dataKey="planned" 
              fill="#1976d2" 
              name="Planned Points"
              radius={[4, 4, 0, 0]}
            />
            <Bar 
              dataKey="completed" 
              fill="#4caf50" 
              name="Completed Points"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            Average Velocity: {progressData.averageVelocity || 0} points/sprint
          </Typography>
          <Typography variant="body2" color={progressData.velocityTrend === 'increasing' ? 'success.main' : progressData.velocityTrend === 'stable' ? 'info.main' : 'error.main'}>
            Trend: {progressData.velocityTrend === 'increasing' ? 'Increasing' : progressData.velocityTrend === 'stable' ? 'Stable' : 'Decreasing'}
          </Typography>
        </Box>
      </Box>
    );
  };
  
  // Render task completion chart
  const renderTaskCompletionChart = () => {
    const taskCompletionData = progressData.taskCompletion || [];
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Task Completion</Typography>
          <Tooltip title="The task completion chart shows the number of tasks completed over time, categorized by priority.">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={taskCompletionData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <RechartsTooltip />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="high" 
              stackId="1" 
              stroke="#f44336" 
              fill="#f44336" 
              fillOpacity={0.6} 
              name="High Priority"
            />
            <Area 
              type="monotone" 
              dataKey="medium" 
              stackId="1" 
              stroke="#ff9800" 
              fill="#ff9800" 
              fillOpacity={0.6} 
              name="Medium Priority"
            />
            <Area 
              type="monotone" 
              dataKey="low" 
              stackId="1" 
              stroke="#4caf50" 
              fill="#4caf50" 
              fillOpacity={0.6} 
              name="Low Priority"
            />
          </AreaChart>
        </ResponsiveContainer>
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            Total Tasks Completed: {progressData.totalTasksCompleted || 0}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Completion Rate: {progressData.taskCompletionRate || 0}%
          </Typography>
        </Box>
      </Box>
    );
  };
  
  // Render code quality metrics
  const renderCodeQualityMetrics = () => {
    const codeQuality = progressData.codeQuality || {};
    
    // Prepare data for the chart
    const codeQualityData = [
      { name: 'Test Coverage', value: codeQuality.coverage || 0, color: '#4caf50' },
      { name: 'Code Smells', value: codeQuality.codeSmells || 0, color: '#ff9800' },
      { name: 'Bugs', value: codeQuality.bugs || 0, color: '#f44336' },
      { name: 'Vulnerabilities', value: codeQuality.vulnerabilities || 0, color: '#9c27b0' },
      { name: 'Duplications', value: codeQuality.duplications || 0, color: '#607d8b' }
    ];
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Code Quality Metrics</Typography>
          <Tooltip title="Code quality metrics provide insights into the health of the codebase, including test coverage, bugs, vulnerabilities, code smells, and duplications.">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart 
                data={codeQualityData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" />
                <YAxis type="category" dataKey="name" />
                <RechartsTooltip />
                <Bar dataKey="value">
                  {codeQualityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card variant="outlined" sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>Quality Gate Status</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {codeQuality.qualityGateStatus === 'passed' ? (
                    <Box sx={{ color: '#4caf50', display: 'flex', alignItems: 'center' }}>
                      <CheckCircleIcon sx={{ mr: 1 }} />
                      <Typography variant="body1">Passed</Typography>
                    </Box>
                  ) : (
                    <Box sx={{ color: '#f44336', display: 'flex', alignItems: 'center' }}>
                      <ErrorIcon sx={{ mr: 1 }} />
                      <Typography variant="body1">Failed</Typography>
                    </Box>
                  )}
                </Box>
                
                <Typography variant="subtitle2" gutterBottom>Test Coverage</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={codeQuality.coverage || 0} 
                      sx={{ 
                        height: 10, 
                        borderRadius: 5,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: (codeQuality.coverage || 0) > 80 ? '#4caf50' : (codeQuality.coverage || 0) > 60 ? '#ff9800' : '#f44336'
                        }
                      }} 
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">{`${codeQuality.coverage || 0}%`}</Typography>
                </Box>
                
                <Typography variant="subtitle2" gutterBottom>Issues</Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="error.main">Bugs: {codeQuality.bugs || 0}</Typography>
                  <Typography variant="body2" color="warning.main">Vulnerabilities: {codeQuality.vulnerabilities || 0}</Typography>
                  <Typography variant="body2" color="info.main">Code Smells: {codeQuality.codeSmells || 0}</Typography>
                </Box>
                
                <Typography variant="subtitle2" gutterBottom>Trend</Typography>
                <Typography variant="body2" color={codeQuality.trend === 'improving' ? 'success.main' : codeQuality.trend === 'stable' ? 'info.main' : 'error.main'}>
                  {codeQuality.trend === 'improving' ? 'Improving' : codeQuality.trend === 'stable' ? 'Stable' : 'Declining'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };
  
  // Render trend analysis
  const renderTrendAnalysis = () => {
    const trendData = progressData.trends || [];
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Trend Analysis</Typography>
          <Tooltip title="Trend analysis shows how key project metrics have changed over time, helping to identify patterns and potential issues.">
            <IconButton size="small">
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" orientation="left" />
            <YAxis yAxisId="right" orientation="right" />
            <RechartsTooltip />
            <Legend />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="velocity" 
              stroke="#1976d2" 
              name="Velocity"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="taskCompletion" 
              stroke="#4caf50" 
              name="Task Completion"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="bugCount" 
              stroke="#f44336" 
              name="Bug Count"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="testCoverage" 
              stroke="#ff9800" 
              name="Test Coverage"
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Key Insights</Typography>
          <Grid container spacing={2}>
            {(progressData.insights || []).map((insight, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card variant="outlined" sx={{ bgcolor: '#f5f5f5' }}>
                  <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                    <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                      {insight.title}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {insight.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Box>
    );
  };
  
  // Render content based on active tab and chart type
  const renderContent = () => {
    if (activeTab === 0) {
      // Sprint Progress tab
      switch (chartType) {
        case 'burndown':
          return renderBurndownChart();
        case 'velocity':
          return renderVelocityChart();
        case 'taskCompletion':
          return renderTaskCompletionChart();
        default:
          return renderBurndownChart();
      }
    } else if (activeTab === 1) {
      // Code Quality tab
      return renderCodeQualityMetrics();
    } else if (activeTab === 2) {
      // Trend Analysis tab
      return renderTrendAnalysis();
    }
    
    return null;
  };
  
  return (
    <Paper elevation={0} sx={{ p: 3, height: '100%' }}>
      {/* Header with controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Progress Tracking</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120, mr: 1 }}>
            <InputLabel id="time-range-label">Time Range</InputLabel>
            <Select
              labelId="time-range-label"
              id="time-range-select"
              value={timeRange}
              label="Time Range"
              onChange={handleTimeRangeChange}
              size="small"
            >
              <MenuItem value="sprint">Current Sprint</MenuItem>
              <MenuItem value="month">Last Month</MenuItem>
              <MenuItem value="quarter">Last Quarter</MenuItem>
              <MenuItem value="year">Last Year</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={handleRefresh} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>
      
      {/* Loading indicator */}
      {loading && (
        <LinearProgress sx={{ mb: 2 }} />
      )}
      
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab icon={<ChartIcon />} label="Sprint Progress" />
        <Tab icon={<BarChartIcon />} label="Code Quality" />
        <Tab icon={<TimelineIcon />} label="Trend Analysis" />
      </Tabs>
      
      {/* Chart type selector (only for Sprint Progress tab) */}
      {activeTab === 0 && (
        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ mr: 2 }}>Chart Type:</Typography>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <Select
              id="chart-type-select"
              value={chartType}
              onChange={handleChartTypeChange}
              size="small"
            >
              <MenuItem value="burndown">Burndown Chart</MenuItem>
              <MenuItem value="velocity">Velocity Chart</MenuItem>
              <MenuItem value="taskCompletion">Task Completion</MenuItem>
            </Select>
          </FormControl>
        </Box>
      )}
      
      {/* Main content */}
      <Box sx={{ flexGrow: 1 }}>
        {renderContent()}
      </Box>
      
      {/* Footer with actions */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          size="small"
        >
          Export Data
        </Button>
      </Box>
    </Paper>
  );
};

export default ProgressTrackingVisualizations;
