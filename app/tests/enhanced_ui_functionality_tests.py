# TORONTO AI TEAM AGENT - PROPRIETARY
#
# Copyright (c) 2025 TORONTO AI
# Creator: David Tadeusz Chudak
# All Rights Reserved
#
# This file is part of the TORONTO AI TEAM AGENT software.
#
# This software is based on OpenManus (Copyright (c) 2025 manna_and_poem),
# which is licensed under the MIT License. The original license is included
# in the LICENSE file in the root directory of this project.
#
# This software has been substantially modified with proprietary enhancements.


"""Integration tests for the enhanced UI functionality with human input request system.

This module provides tests to verify that the UI components work correctly with
the backend communication and prioritization mechanisms."""

import unittest
import asyncio
import json
import os
from datetime import datetime, timedelta

from ..interface.project_manager_interface import ProjectManagerInterface
from ..collaboration.project_manager_communication_flow import ProjectManagerCommunicationFlow
from ..collaboration.request_prioritization_mechanism import RequestPrioritizationMechanism

class EnhancedUIFunctionalityTests(unittest.TestCase):
    """Test suite for the enhanced UI functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_manager_interface = ProjectManagerInterface()
        self.communication_flow = ProjectManagerCommunicationFlow(self.project_manager_interface)
        self.prioritization_mechanism = RequestPrioritizationMechanism()
        
        # Create a test project
        self.project_id = f"test_project_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Set up the event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests."""
        self.loop.close()
    
    def test_create_input_request(self):
        """Test creating a human input request."""
        # Create a test request
        request_params = {
            "project_id": self.project_id,
            "title": "Test Request",
            "description": "This is a test request for UI functionality testing.",
            "priority": "high",
            "category": "decision",
            "requested_by": "Developer",
            "original_request": "What should we do about this test?",
            "notes": "This is a test note."
        }
        
        # Execute the async test
        result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.create_input_request(request_params)
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertIn("request_id", result)
        self.assertIn("request", result)
        
        # Store the request ID for later tests
        self.request_id = result["request_id"]
    
    def test_get_input_requests(self):
        """Test retrieving human input requests."""
        # First create a test request if not already created
        if not hasattr(self, 'request_id'):
            self.test_create_input_request()
        
        # Get requests for the project
        result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.get_input_requests({
                "project_id": self.project_id
            })
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertIn("requests", result)
        self.assertGreaterEqual(len(result["requests"]), 1)
        
        # Test prioritization
        prioritized_requests = self.prioritization_mechanism.prioritize_requests(result["requests"])
        self.assertEqual(len(prioritized_requests), len(result["requests"]))
        self.assertIn("priority_score", prioritized_requests[0])
    
    def test_get_input_request_detail(self):
        """Test retrieving details of a specific human input request."""
        # First create a test request if not already created
        if not hasattr(self, 'request_id'):
            self.test_create_input_request()
        
        # Get request details
        result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.get_input_request({
                "request_id": self.request_id
            })
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertIn("request", result)
        self.assertEqual(result["request"]["id"], self.request_id)
    
    def test_update_input_request(self):
        """Test updating a human input request."""
        # First create a test request if not already created
        if not hasattr(self, 'request_id'):
            self.test_create_input_request()
        
        # Update the request
        update_params = {
            "request_id": self.request_id,
            "title": "Updated Test Request",
            "status": "in_progress",
            "notes": "This request has been updated for testing."
        }
        
        result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.update_input_request(update_params)
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertIn("request", result)
        self.assertEqual(result["request"]["title"], "Updated Test Request")
        self.assertEqual(result["request"]["status"], "in_progress")
    
    def test_agent_to_human_request(self):
        """Test processing a request from an agent that needs human input."""
        # Create a test agent request
        request_params = {
            "project_id": self.project_id,
            "agent_role": "Developer",
            "request_content": {
                "title": "Agent Request",
                "description": "This is a test request from an agent.",
                "priority": "medium",
                "category": "information",
                "original_request": "I need some information for testing."
            }
        }
        
        # Process the agent request
        result = self.loop.run_until_complete(
            self.communication_flow.handle_agent_to_human_request(request_params)
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertIn("request_id", result)
    
    def test_human_to_agent_response(self):
        """Test processing a response from a human to an agent request."""
        # First create a test agent request
        self.test_agent_to_human_request()
        
        # Get the latest request for the project
        result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.get_input_requests({
                "project_id": self.project_id
            })
        )
        
        # Get the latest request ID
        latest_request_id = result["requests"][0]["id"]
        
        # Create a test response
        response_params = {
            "project_id": self.project_id,
            "request_id": latest_request_id,
            "response_content": {
                "answer": "This is a test response to the agent request.",
                "additional_info": "Here is some additional information for testing."
            }
        }
        
        # Process the human response
        result = self.loop.run_until_complete(
            self.communication_flow.handle_human_to_agent_response(response_params)
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        
        # Verify the request was marked as completed
        request_result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.get_input_request({
                "request_id": latest_request_id
            })
        )
        
        self.assertEqual(request_result["request"]["status"], "completed")
    
    def test_pending_requests_count(self):
        """Test getting the count of pending human input requests."""
        # Create a few test requests with different statuses
        for i in range(3):
            request_params = {
                "project_id": self.project_id,
                "title": f"Pending Request {i}",
                "description": f"This is pending request {i} for testing.",
                "priority": "medium",
                "category": "information",
                "requested_by": "Developer",
                "status": "pending"
            }
            
            self.loop.run_until_complete(
                self.communication_flow.input_request_manager.create_input_request(request_params)
            )
        
        # Get the pending count
        result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.get_pending_requests_count({
                "project_id": self.project_id
            })
        )
        
        # Verify the result
        self.assertTrue(result.get("success", False))
        self.assertIn("count", result)
        self.assertGreaterEqual(result["count"], 3)
    
    def test_request_pattern_analysis(self):
        """Test analyzing patterns in human input requests."""
        # Create a few more test requests with different properties
        for i in range(2):
            request_params = {
                "project_id": self.project_id,
                "title": f"Feedback Request {i}",
                "description": f"This is feedback request {i} for testing.",
                "priority": "low",
                "category": "feedback",
                "requested_by": "UI/UX Designer",
                "status": "pending"
            }
            
            self.loop.run_until_complete(
                self.communication_flow.input_request_manager.create_input_request(request_params)
            )
        
        # Get all requests for the project
        result = self.loop.run_until_complete(
            self.communication_flow.input_request_manager.get_input_requests({
                "project_id": self.project_id
            })
        )
        
        # Analyze request patterns
        analysis = self.prioritization_mechanism.analyze_request_patterns(result["requests"])
        
        # Verify the analysis
        self.assertIn("total_requests", analysis)
        self.assertIn("by_agent", analysis)
        self.assertIn("by_category", analysis)
        self.assertIn("by_priority", analysis)
        self.assertIn("by_status", analysis)
        
        # Verify that we have data for agents and categories
        self.assertGreaterEqual(len(analysis["by_agent"]), 1)
        self.assertGreaterEqual(len(analysis["by_category"]), 1)

if __name__ == '__main__':
    unittest.main()
