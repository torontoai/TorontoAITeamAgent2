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
  Typography,
  CircularProgress
} from '@mui/material';

import ProjectOverviewPanel from './components/project_overview_panel';
import ProgressTrackingVisualizations from './components/progress_tracking_visualizations';
import ProjectManagerInteractionInterface from './components/project_manager_interaction_interface';
import AgentConversationMonitoringPanel from './agent_conversation_monitoring_panel';
import SprintTrackingVisualization from './sprint_tracking_visualization';
import HumanInputRequestSystem from './human_input_request_system';

// Import agent communication services
import { AgentCommunicationService } from '../collaboration/enhanced_communication_framework';
import { ProjectManagerService } from '../agent/project_manager';

/**
 * DashboardIntegration component
 * 
 * Integrates the dashboard UI components with the agent communication system
 */
const DashboardIntegration = () => {
  // State for project data
  const [projectData, setProjectData] = useState(null);
  
  // State for progress data
  const [progressData, setProgressData] = useState(null);
  
  // State for PM interaction data
  const [pmInteractionData, setPmInteractionData] = useState(null);
  
  // State for loading
  const [loading, setLoading] = useState(true);
  
  // State for error
  const [error, setError] = useState(null);
  
  // Initialize services
  const agentCommunicationService = new AgentCommunicationService();
  const projectManagerService = new ProjectManagerService(agentCommunicationService);
  
  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch project data
        const projectDataResponse = await projectManagerService.getProjectOverview();
        setProjectData(projectDataResponse);
        
        // Fetch progress data
        const progressDataResponse = await projectManagerService.getProgressData();
        setProgressData(progressDataResponse);
        
        // Fetch PM interaction data
        const pmInteractionDataResponse = await projectManagerService.getInteractionData();
        setPmInteractionData(pmInteractionDataResponse);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
        setLoading(false);
      }
    };
    
    fetchData();
    
    // Set up real-time updates
    const projectUpdateSubscription = agentCommunicationService.subscribeToTopic('project_updates', (data) => {
      setProjectData(prevData => ({...prevData, ...data}));
    });
    
    const progressUpdateSubscription = agentCommunicationService.subscribeToTopic('progress_updates', (data) => {
      setProgressData(prevData => ({...prevData, ...data}));
    });
    
    const interactionUpdateSubscription = agentCommunicationService.subscribeToTopic('interaction_updates', (data) => {
      setPmInteractionData(prevData => ({...prevData, ...data}));
    });
    
    // Clean up subscriptions
    return () => {
      agentCommunicationService.unsubscribe(projectUpdateSubscription);
      agentCommunicationService.unsubscribe(progressUpdateSubscription);
      agentCommunicationService.unsubscribe(interactionUpdateSubscription);
    };
  }, []);
  
  // Refresh project data
  const refreshProjectData = async () => {
    try {
      const projectDataResponse = await projectManagerService.getProjectOverview();
      setProjectData(projectDataResponse);
      return projectDataResponse;
    } catch (err) {
      console.error('Error refreshing project data:', err);
      throw err;
    }
  };
  
  // Refresh progress data
  const refreshProgressData = async () => {
    try {
      const progressDataResponse = await projectManagerService.getProgressData();
      setProgressData(progressDataResponse);
      return progressDataResponse;
    } catch (err) {
      console.error('Error refreshing progress data:', err);
      throw err;
    }
  };
  
  // Refresh PM interaction data
  const refreshPMInteractionData = async () => {
    try {
      const pmInteractionDataResponse = await projectManagerService.getInteractionData();
      setPmInteractionData(pmInteractionDataResponse);
      return pmInteractionDataResponse;
    } catch (err) {
      console.error('Error refreshing PM interaction data:', err);
      throw err;
    }
  };
  
  // Handle sending message to PM
  const handleSendMessageToPM = async (message) => {
    try {
      await projectManagerService.sendMessage(message);
      
      // Optimistically update the UI
      const newMessage = {
        id: `temp-${Date.now()}`,
        from: 'human',
        content: message,
        time: 'Just now'
      };
      
      setPmInteractionData(prevData => ({
        ...prevData,
        recentMessages: [...prevData.recentMessages, newMessage]
      }));
      
      // Refresh interaction data to get the actual response
      setTimeout(() => {
        refreshPMInteractionData();
      }, 1000);
    } catch (err) {
      console.error('Error sending message to PM:', err);
      // Handle error
    }
  };
  
  // Handle responding to request
  const handleRespondToRequest = async (requestId, response) => {
    try {
      await projectManagerService.respondToRequest(requestId, response);
      
      // Refresh interaction data to update the UI
      refreshPMInteractionData();
    } catch (err) {
      console.error('Error responding to request:', err);
      // Handle error
    }
  };
  
  // Handle approve/reject
  const handleApproveReject = async (requestId, approved) => {
    try {
      await projectManagerService.approveRejectRequest(requestId, approved);
      
      // Refresh interaction data to update the UI
      refreshPMInteractionData();
    } catch (err) {
      console.error('Error approving/rejecting request:', err);
      // Handle error
    }
  };
  
  // Handle filter change
  const handleFilterChange = async (filters) => {
    try {
      // In a real implementation, you might want to fetch filtered data from the server
      // For now, we'll just log the filters
      console.log('Filter changed:', filters);
    } catch (err) {
      console.error('Error applying filters:', err);
      // Handle error
    }
  };
  
  // Handle time range change
  const handleTimeRangeChange = async (timeRange) => {
    try {
      const progressDataResponse = await projectManagerService.getProgressData(timeRange);
      setProgressData(progressDataResponse);
    } catch (err) {
      console.error('Error changing time range:', err);
      // Handle error
    }
  };
  
  // If loading, show loading indicator
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  // If error, show error message
  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Typography variant="h6" color="error">{error}</Typography>
      </Box>
    );
  }
  
  return (
    <Box sx={{ height: '100%' }}>
      {/* Project Overview Panel */}
      <ProjectOverviewPanel 
        projectData={projectData}
        onViewAllActivity={() => console.log('View all activity')}
        onViewProjectDetails={() => console.log('View project details')}
        refreshData={refreshProjectData}
      />
      
      {/* Progress Tracking Visualizations */}
      <ProgressTrackingVisualizations 
        progressData={progressData}
        refreshData={refreshProgressData}
        timeRange="sprint"
        onTimeRangeChange={handleTimeRangeChange}
      />
      
      {/* Project Manager Interaction Interface */}
      <ProjectManagerInteractionInterface 
        pmInteractionData={pmInteractionData}
        onSendMessage={handleSendMessageToPM}
        onRespondToRequest={handleRespondToRequest}
        onApproveReject={handleApproveReject}
        onFilterChange={handleFilterChange}
        refreshData={refreshPMInteractionData}
      />
    </Box>
  );
};

export default DashboardIntegration;
