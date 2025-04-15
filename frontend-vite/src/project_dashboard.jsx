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
import { Box, Container, Typography, Paper, Grid, Tabs, Tab, AppBar } from '@mui/material';
import ProjectOverviewPanel from './components/project_overview_panel';
import ProgressTrackingVisualizations from './components/progress_tracking_visualizations';
import ProjectManagerInteractionInterface from './components/project_manager_interaction_interface';
import AgentConversationMonitoringPanel from './agent_conversation_monitoring_panel';
import SprintTrackingVisualization from './sprint_tracking_visualization';

function ProjectDashboard() {
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          TORONTO AI Team Agent Team AI - Project Dashboard
        </Typography>
        
        <AppBar position="static" color="default" sx={{ mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            variant="fullWidth"
          >
            <Tab label="Dashboard" />
            <Tab label="Agent Communications" />
            <Tab label="Artifacts" />
            <Tab label="Timeline" />
            <Tab label="Human Input" />
          </Tabs>
        </AppBar>
        
        {tabValue === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <ProjectOverviewPanel />
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Agent Status
                </Typography>
                <Typography variant="body2" paragraph>
                  Project Manager: Coordinating team activities
                </Typography>
                <Typography variant="body2" paragraph>
                  Product Manager: Analyzing requirements
                </Typography>
                <Typography variant="body2" paragraph>
                  Developer: Implementing features
                </Typography>
                <Typography variant="body2" paragraph>
                  System Architect: Reviewing code architecture
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Recent Communications
                </Typography>
                <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                  <Typography variant="subtitle2">project_manager to all:</Typography>
                  <Typography variant="body2" paragraph sx={{ pl: 2 }}>
                    I've analyzed the requirements. Let's break this down into subtasks.
                  </Typography>
                  <Typography variant="subtitle2">product_manager to all:</Typography>
                  <Typography variant="body2" paragraph sx={{ pl: 2 }}>
                    We need to ensure proper input validation and error handling.
                  </Typography>
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  Artifacts Summary
                </Typography>
                <Typography variant="subtitle2">calculator.py (code)</Typography>
                <Typography variant="body2" paragraph sx={{ pl: 2 }}>
                  Created by: developer
                </Typography>
                <Typography variant="subtitle2">requirements_analysis.md (document)</Typography>
                <Typography variant="body2" paragraph sx={{ pl: 2 }}>
                  Created by: product_manager
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2 }}>
                <ProgressTrackingVisualizations />
              </Paper>
            </Grid>
          </Grid>
        )}
        
        {tabValue === 1 && (
          <Paper sx={{ p: 2 }}>
            <AgentConversationMonitoringPanel />
          </Paper>
        )}
        
        {tabValue === 2 && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Project Artifacts
            </Typography>
            <Typography variant="body1">
              View and manage artifacts created by the team.
            </Typography>
          </Paper>
        )}
        
        {tabValue === 3 && (
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Project Timeline
            </Typography>
            <SprintTrackingVisualization />
          </Paper>
        )}
        
        {tabValue === 4 && (
          <Paper sx={{ p: 2 }}>
            <ProjectManagerInteractionInterface />
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default ProjectDashboard;
