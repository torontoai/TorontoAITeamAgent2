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


"""Test module for multi-agent collaboration functionality.

This module tests the enhanced communication framework and real-time collaboration
capabilities between multiple agent roles."""

import asyncio
import unittest
import logging
import json
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.collaboration.communication_framework import AgentCommunicationFramework
from app.collaboration.framework import RealTimeCollaborationFramework
from app.agent.project_manager import ProjectManagerAgent
from app.agent.product_manager import ProductManagerAgent
from app.agent.developer import DeveloperAgent
from app.agent.additional_roles import SystemArchitectAgent, QATestingSpecialistAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestMultiAgentCollaboration(unittest.TestCase):
    """Test case for multi-agent collaboration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create communication framework
        self.comm_framework = AgentCommunicationFramework()
        
        # Create real-time collaboration framework
        self.collab_framework = RealTimeCollaborationFramework(self.comm_framework)
        
        # Create test agents
        self.project_manager = ProjectManagerAgent({
            "id": "pm_test",
            "role": "project_manager",
            "project_id": "test_project"
        })
        
        self.product_manager = ProductManagerAgent({
            "id": "product_test",
            "role": "product_manager",
            "project_id": "test_project"
        })
        
        self.developer = DeveloperAgent({
            "id": "dev_test",
            "role": "developer",
            "project_id": "test_project"
        })
        
        self.architect = SystemArchitectAgent({
            "id": "arch_test",
            "role": "system_architect",
            "project_id": "test_project"
        })
        
        self.qa_specialist = QATestingSpecialistAgent({
            "id": "qa_test",
            "role": "qa_testing_specialist",
            "project_id": "test_project"
        })
        
        # Store test messages
        self.test_messages = []
    
    async def async_test_message_sending(self):
        """Test basic message sending between agents."""
        # Send a message from project manager to developer
        result = await self.comm_framework.send_message({
            "from": "pm_test",
            "to": "dev_test",
            "content": {
                "type": "task_assignment",
                "task": "Implement login functionality",
                "priority": "high"
            },
            "metadata": {
                "project_id": "test_project",
                "category": "task"
            }
        })
        
        self.assertTrue(result["success"])
        self.assertIn("message_id", result)
        
        # Store message ID for later tests
        self.test_messages.append(result["message_id"])
        
        # Send a message from developer to project manager
        result = await self.comm_framework.send_message({
            "from": "dev_test",
            "to": "pm_test",
            "content": {
                "type": "task_update",
                "task": "Implement login functionality",
                "status": "in_progress",
                "notes": "Started working on authentication flow"
            },
            "metadata": {
                "project_id": "test_project",
                "category": "update"
            }
        })
        
        self.assertTrue(result["success"])
        self.assertIn("message_id", result)
        
        # Store message ID for later tests
        self.test_messages.append(result["message_id"])
        
        # Test broadcast message
        result = await self.comm_framework.send_message({
            "from": "pm_test",
            "to": ["dev_test", "product_test", "arch_test", "qa_test"],
            "content": {
                "type": "announcement",
                "message": "Team meeting at 2pm today"
            },
            "pattern": "broadcast",
            "metadata": {
                "project_id": "test_project",
                "category": "announcement"
            }
        })
        
        self.assertTrue(result["success"])
        self.assertIn("message_id", result)
        
        # Store message ID for later tests
        self.test_messages.append(result["message_id"])
        
        # Get message history
        history_result = await self.comm_framework.get_message_history({
            "limit": 10
        })
        
        self.assertTrue(history_result["success"])
        self.assertEqual(len(history_result["history"]), 3)
    
    async def async_test_collaboration_session(self):
        """Test collaboration session creation and interaction."""
        # Create a collaboration session
        session_result = await self.collab_framework.create_collaboration_session({
            "name": "Login Feature Implementation",
            "description": "Collaborative session to design and implement the login feature",
            "participants": ["pm_test", "product_test", "dev_test", "arch_test"],
            "initiator": "pm_test",
            "context": {
                "feature": "login",
                "priority": "high",
                "deadline": (datetime.now() + timedelta(days=7)).isoformat()
            },
            "session_type": "feature_development"
        })
        
        self.assertTrue(session_result["success"])
        self.assertIn("session_id", session_result)
        
        session_id = session_result["session_id"]
        
        # Join session with QA specialist
        join_result = await self.collab_framework.join_collaboration_session({
            "session_id": session_id,
            "agent_id": "qa_test",
            "metadata": {
                "role": "qa_testing_specialist",
                "focus": "security testing"
            }
        })
        
        self.assertTrue(join_result["success"])
        self.assertEqual(len(join_result["session"]["participants"]), 5)
        
        # Send a collaboration message
        message_result = await self.collab_framework.send_collaboration_message({
            "session_id": session_id,
            "from": "arch_test",
            "content": {
                "type": "architecture_proposal",
                "auth_flow": "OAuth2 with JWT tokens",
                "components": ["AuthService", "UserRepository", "TokenManager"]
            },
            "message_type": "architecture",
            "metadata": {
                "importance": "high"
            }
        })
        
        self.assertTrue(message_result["success"])
        self.assertIn("message_id", message_result)
        
        # Update shared state
        state_result = await self.collab_framework.update_shared_state({
            "session_id": session_id,
            "agent_id": "product_test",
            "updates": {
                "requirements": {
                    "auth_methods": ["email", "google", "github"],
                    "security_level": "high",
                    "user_experience": "streamlined"
                }
            },
            "operation": "merge"
        })
        
        self.assertTrue(state_result["success"])
        self.assertIn("requirements", state_result["new_state"])
        
        # Add an artifact
        artifact_result = await self.collab_framework.add_collaboration_artifact({
            "session_id": session_id,
            "agent_id": "dev_test",
            "name": "auth_service.py",
            "type": "code",
            "content": "class AuthService:\n    def authenticate(self, credentials):\n        # Implementation\n        pass",
            "metadata": {
                "language": "python",
                "component": "AuthService"
            }
        })
        
        self.assertTrue(artifact_result["success"])
        self.assertIn("artifact_id", artifact_result)
        
        # Get session information
        session_info = await self.collab_framework.get_collaboration_session({
            "session_id": session_id,
            "include_messages": True,
            "include_artifacts": True,
            "include_state": True
        })
        
        self.assertTrue(session_info["success"])
        self.assertEqual(len(session_info["session"]["messages"]), 1)
        self.assertEqual(len(session_info["session"]["artifacts"]), 1)
        self.assertIn("requirements", session_info["session"]["shared_state"])
        
        # Leave session
        leave_result = await self.collab_framework.leave_collaboration_session({
            "session_id": session_id,
            "agent_id": "qa_test",
            "reason": "Testing complete"
        })
        
        self.assertTrue(leave_result["success"])
        self.assertEqual(leave_result["remaining_participants"], 4)
        
        # Close session
        close_result = await self.collab_framework.close_collaboration_session({
            "session_id": session_id,
            "agent_id": "pm_test",
            "reason": "Feature implementation complete"
        })
        
        self.assertTrue(close_result["success"])
    
    async def async_test_communication_analysis(self):
        """Test communication pattern analysis."""
        # Analyze communication patterns
        analysis_result = await self.comm_framework.analyze_communication_patterns({
            "project_id": "test_project"
        })
        
        self.assertTrue(analysis_result["success"])
        self.assertIn("insights", analysis_result)
        self.assertIn("recommendations", analysis_result)
        self.assertIn("metrics", analysis_result)
    
    def test_message_sending(self):
        """Run async test for message sending."""
        asyncio.run(self.async_test_message_sending())
    
    def test_collaboration_session(self):
        """Run async test for collaboration session."""
        asyncio.run(self.async_test_collaboration_session())
    
    def test_communication_analysis(self):
        """Run async test for communication analysis."""
        asyncio.run(self.async_test_communication_analysis())

if __name__ == '__main__':
    unittest.main()
