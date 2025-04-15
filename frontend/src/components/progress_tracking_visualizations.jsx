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

function ProgressTrackingVisualizations() {
  // Sample data for burndown chart
  const burndownData = {
    labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5'],
    datasets: [
      {
        label: 'Remaining Tasks',
        data: [10, 8, 6, 3, 0],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
      {
        label: 'Ideal Burndown',
        data: [10, 7.5, 5, 2.5, 0],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        borderDash: [5, 5],
      },
    ],
  };

  // Sample data for task completion by agent
  const taskCompletionData = {
    labels: ['Project Manager', 'Product Manager', 'Developer', 'System Architect'],
    datasets: [
      {
        label: 'Tasks Completed',
        data: [4, 3, 5, 2],
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
        text: 'Project Progress',
      },
    },
  };

  const barOptions = {
    ...options,
    plugins: {
      ...options.plugins,
      title: {
        display: true,
        text: 'Tasks Completed by Agent',
      },
    },
  };

  return (
    <>
      <Typography variant="h6" gutterBottom>
        Progress Tracking
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Line options={options} data={burndownData} />
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Bar options={barOptions} data={taskCompletionData} />
          </Box>
        </Grid>
      </Grid>
    </>
  );
}

export default ProgressTrackingVisualizations;
