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
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import DashboardIntegration from '../ui/dashboard_integration';
import { AgentCommunicationService } from '../collaboration/enhanced_communication_framework';
import { ProjectManagerService } from '../agent/project_manager';

// Mock the services
jest.mock('../collaboration/enhanced_communication_framework');
jest.mock('../agent/project_manager');

describe('Dashboard Integration Tests', () => {
  // Mock data
  const mockProjectData = {
    name: 'Test Project',
    progress: 65,
    status: 'on_track',
    startDate: '2025-03-01',
    endDate: '2025-06-30',
    nextMilestone: {
      name: 'Feature Implementation',
      dueDate: '2025-04-15',
      progress: 40
    },
    recentActivities: [
      { id: 1, agent: 'developer', action: 'completed', item: 'Authentication Module', time: '2 hours ago' }
    ],
    teamAllocation: [
      { name: 'Development', value: 40 },
      { name: 'Design', value: 20 },
      { name: 'Testing', value: 20 },
      { name: 'Management', value: 20 }
    ]
  };

  const mockProgressData = {
    sprintBurndown: [
      { day: 'Day 1', planned: 100, actual: 100 },
      { day: 'Day 2', planned: 90, actual: 95 }
    ],
    velocity: [
      { sprint: 'Sprint 1', planned: 30, completed: 25 },
      { sprint: 'Sprint 2', planned: 35, completed: 30 }
    ],
    sprintProgress: 45,
    sprintStatus: 'on_track',
    codeQuality: {
      coverage: 78,
      bugs: 5,
      vulnerabilities: 2,
      codeSmells: 15,
      qualityGateStatus: 'passed'
    }
  };

  const mockPMInteractionData = {
    pendingRequests: [
      { 
        id: 'req-1', 
        type: 'decision', 
        title: 'Database Selection', 
        priority: 'high', 
        from: 'system_architect', 
        time: '3 hours ago',
        description: 'Need to decide between PostgreSQL and MongoDB for the user data storage.'
      }
    ],
    recentMessages: [
      { id: 'msg-1', from: 'project_manager', content: 'Sprint planning is scheduled for tomorrow.', time: '1 day ago' }
    ],
    suggestions: [
      { 
        id: 'sug-1', 
        title: 'Add more resources to the frontend team', 
        impact: 'medium', 
        reason: 'Current velocity indicates potential delay in UI implementation.' 
      }
    ],
    pmStatus: 'online'
  };

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Setup mock implementations
    AgentCommunicationService.mockImplementation(() => ({
      subscribeToTopic: jest.fn((topic, callback) => {
        return `subscription-${topic}`;
      }),
      unsubscribe: jest.fn(),
      sendMessage: jest.fn()
    }));
    
    ProjectManagerService.mockImplementation(() => ({
      getProjectOverview: jest.fn().mockResolvedValue(mockProjectData),
      getProgressData: jest.fn().mockResolvedValue(mockProgressData),
      getInteractionData: jest.fn().mockResolvedValue(mockPMInteractionData),
      sendMessage: jest.fn().mockResolvedValue({}),
      respondToRequest: jest.fn().mockResolvedValue({}),
      approveRejectRequest: jest.fn().mockResolvedValue({})
    }));
  });

  test('renders dashboard with loading state initially', () => {
    render(<DashboardIntegration />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('loads and displays project data', async () => {
    render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check if project data is displayed
    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('Feature Implementation')).toBeInTheDocument();
  });

  test('handles sending message to project manager', async () => {
    const { getByPlaceholderText, getByText } = render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Find input field and send button
    const inputField = getByPlaceholderText('Type a message...');
    fireEvent.change(inputField, { target: { value: 'Hello Project Manager' } });
    
    const sendButton = getByText('Send');
    fireEvent.click(sendButton);
    
    // Check if the message was sent
    expect(ProjectManagerService.mock.instances[0].sendMessage).toHaveBeenCalledWith('Hello Project Manager');
  });

  test('handles responding to requests', async () => {
    render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Find and click on the Requests tab
    const requestsTab = screen.getByText('Requests');
    fireEvent.click(requestsTab);
    
    // Find and click on the Respond button
    const respondButton = screen.getByText('Respond');
    fireEvent.click(respondButton);
    
    // Dialog should open
    expect(screen.getByText('Respond to Request')).toBeInTheDocument();
    
    // Enter response and submit
    const responseField = screen.getByLabelText('Your Response');
    fireEvent.change(responseField, { target: { value: 'Let\'s use PostgreSQL for better relational data support.' } });
    
    const sendResponseButton = screen.getByText('Send Response');
    fireEvent.click(sendResponseButton);
    
    // Check if the response was sent
    expect(ProjectManagerService.mock.instances[0].respondToRequest).toHaveBeenCalledWith(
      'req-1', 
      'Let\'s use PostgreSQL for better relational data support.'
    );
  });

  test('handles approving requests', async () => {
    // Mock an approval request
    const approvalRequestData = {
      ...mockPMInteractionData,
      pendingRequests: [
        { 
          id: 'req-2', 
          type: 'approval', 
          title: 'Sprint Plan Approval', 
          priority: 'high', 
          from: 'project_manager', 
          time: '1 day ago',
          description: 'Need approval for the sprint plan for next two weeks.'
        }
      ]
    };
    
    ProjectManagerService.mockImplementation(() => ({
      getProjectOverview: jest.fn().mockResolvedValue(mockProjectData),
      getProgressData: jest.fn().mockResolvedValue(mockProgressData),
      getInteractionData: jest.fn().mockResolvedValue(approvalRequestData),
      sendMessage: jest.fn().mockResolvedValue({}),
      respondToRequest: jest.fn().mockResolvedValue({}),
      approveRejectRequest: jest.fn().mockResolvedValue({})
    }));
    
    render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Find and click on the Requests tab
    const requestsTab = screen.getByText('Requests');
    fireEvent.click(requestsTab);
    
    // Find and click on the Approve button
    const approveButton = screen.getByText('Approve');
    fireEvent.click(approveButton);
    
    // Check if the approval was sent
    expect(ProjectManagerService.mock.instances[0].approveRejectRequest).toHaveBeenCalledWith('req-2', true);
  });

  test('handles refreshing data', async () => {
    render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Find and click refresh buttons
    const refreshButtons = screen.getAllByRole('button', { name: '' }); // Refresh buttons don't have text
    
    // Click the first refresh button (project overview)
    fireEvent.click(refreshButtons[0]);
    
    // Check if refresh was called
    expect(ProjectManagerService.mock.instances[0].getProjectOverview).toHaveBeenCalledTimes(2); // Once on load, once on refresh
  });

  test('handles time range changes for progress data', async () => {
    render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Find and click on the Progress Tracking tab
    const progressTab = screen.getByText('Progress Tracking');
    fireEvent.click(progressTab);
    
    // Find and change the time range selector
    const timeRangeSelect = screen.getByLabelText('Time Range');
    fireEvent.mouseDown(timeRangeSelect);
    
    // Select a different time range
    const monthOption = screen.getByText('Last Month');
    fireEvent.click(monthOption);
    
    // Check if getProgressData was called with the new time range
    expect(ProjectManagerService.mock.instances[0].getProgressData).toHaveBeenCalledWith('month');
  });

  test('subscribes to real-time updates', async () => {
    render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Check if subscriptions were created
    const communicationService = AgentCommunicationService.mock.instances[0];
    expect(communicationService.subscribeToTopic).toHaveBeenCalledWith('project_updates', expect.any(Function));
    expect(communicationService.subscribeToTopic).toHaveBeenCalledWith('progress_updates', expect.any(Function));
    expect(communicationService.subscribeToTopic).toHaveBeenCalledWith('interaction_updates', expect.any(Function));
  });

  test('unsubscribes when component unmounts', async () => {
    const { unmount } = render(<DashboardIntegration />);
    
    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
    
    // Unmount the component
    unmount();
    
    // Check if unsubscribe was called
    const communicationService = AgentCommunicationService.mock.instances[0];
    expect(communicationService.unsubscribe).toHaveBeenCalledTimes(3); // Once for each subscription
  });
});
