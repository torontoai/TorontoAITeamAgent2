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
import { Box, Typography, Paper, Grid } from '@mui/material';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function SprintTrackingVisualization() {
  // Sample data for sprint timeline
  const sprintTimelineData = {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Planned Story Points',
        data: [10, 15, 12, 8],
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Completed Story Points',
        data: [10, 14, 11, 8],
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  };

  // Sample data for agent contributions
  const agentContributionsData = {
    labels: ['Project Manager', 'Product Manager', 'Developer', 'System Architect'],
    datasets: [
      {
        label: 'Tasks Assigned',
        data: [5, 4, 8, 3],
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
      {
        label: 'Tasks Completed',
        data: [5, 4, 7, 3],
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Sprint Progress by Week',
      },
    },
  };

  const barOptions = {
    ...options,
    plugins: {
      ...options.plugins,
      title: {
        display: true,
        text: 'Agent Contributions to Sprint',
      },
    },
  };

  return (
    <>
      <Typography variant="h6" gutterBottom>
        Sprint Tracking
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Current Sprint: Sprint 1 (Calculator Implementation)
            </Typography>
            <Typography variant="body2">
              Start Date: March 25, 2025 | End Date: April 8, 2025
            </Typography>
            <Typography variant="body2">
              Status: Completed | Progress: 100% | Velocity: 43 story points
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Bar options={options} data={sprintTimelineData} />
          </Box>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Bar options={barOptions} data={agentContributionsData} />
          </Box>
        </Grid>
        
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Sprint Highlights
            </Typography>
            <Typography variant="body2" paragraph>
              • All core functionality implemented and tested
            </Typography>
            <Typography variant="body2" paragraph>
              • Input validation and error handling completed
            </Typography>
            <Typography variant="body2" paragraph>
              • Documentation created for all components
            </Typography>
            <Typography variant="body2" paragraph>
              • Code review completed by System Architect
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </>
  );
}

export default SprintTrackingVisualization;
