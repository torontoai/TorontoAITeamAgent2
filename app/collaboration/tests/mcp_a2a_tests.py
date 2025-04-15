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


"""MCP and A2A Integration Tests.

This module contains tests for the Multi-agent Conversational Protocols (MCP) and
Agent-to-Agent (A2A) frameworks and their integration with the existing system."""

import asyncio
import unittest
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.collaboration.communication_framework import Message, MessageType, EventBus
from app.collaboration.mcp_framework import (
    ConversationProtocol, ConversationContext, ConversationManager,
    InformationExchangeProtocol, NegotiationProtocol, TaskDelegationProtocol,
    CollaborativeProblemSolvingProtocol, ErrorHandlingProtocol
)
from app.collaboration.a2a_framework import (
    Capability, CapabilityRegistry, TrustManager, SecurityManager,
    AgentIdentity, A2AFramework
)
from app.collaboration.mcp_a2a_integration import (
    MCPAdapter, A2AAdapter, IntegratedCommunicationSystem
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMCPFramework(unittest.TestCase):
    """Tests for the MCP framework."""
    
    def setUp(self):
        """Set up test environment."""
        self.conversation_manager = ConversationManager()
        
        # Register standard protocols
        self.info_exchange = InformationExchangeProtocol()
        self.negotiation = NegotiationProtocol()
        self.task_delegation = TaskDelegationProtocol()
        self.problem_solving = CollaborativeProblemSolvingProtocol()
        self.error_handling = ErrorHandlingProtocol()
        
        self.conversation_manager.register_protocol(self.info_exchange)
        self.conversation_manager.register_protocol(self.negotiation)
        self.conversation_manager.register_protocol(self.task_delegation)
        self.conversation_manager.register_protocol(self.problem_solving)
        self.conversation_manager.register_protocol(self.error_handling)
        
    async def test_information_exchange_protocol(self):
        """Test information exchange protocol."""
        # Create conversation
        result = await self.conversation_manager.create_conversation(
            protocol_id="info_exchange",
            protocol_version="1.0",
            participants=[
                {"id": "agent1", "role": "requester"},
                {"id": "agent2", "role": "provider"}
            ]
        )
        
        self.assertTrue(result["success"])
        conversation_id = result["conversation_id"]
        
        # Send request message
        request_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "agent1", "role": "requester"},
            "content": {
                "type": "request",
                "subject": "Weather information",
                "body": "What's the weather like today?",
                "data": {}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, request_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "response")
        
        # Send response message
        response_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "agent2", "role": "provider"},
            "content": {
                "type": "response",
                "subject": "Re: Weather information",
                "body": "It's sunny with a high of 75°F.",
                "data": {"temperature": 75, "condition": "sunny"}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, response_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "completed")
        self.assertTrue(result["is_terminal"])
        
    async def test_negotiation_protocol(self):
        """Test negotiation protocol."""
        # Create conversation
        result = await self.conversation_manager.create_conversation(
            protocol_id="negotiation",
            protocol_version="1.0",
            participants=[
                {"id": "agent1", "role": "buyer"},
                {"id": "agent2", "role": "seller"}
            ]
        )
        
        self.assertTrue(result["success"])
        conversation_id = result["conversation_id"]
        
        # Send proposal message
        proposal_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "agent1", "role": "buyer"},
            "content": {
                "type": "proposal",
                "subject": "Purchase offer",
                "body": "I offer $100 for the item.",
                "data": {"price": 100}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, proposal_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "consideration")
        
        # Send counter-proposal message
        counter_proposal_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "agent2", "role": "seller"},
            "content": {
                "type": "counter_proposal",
                "subject": "Re: Purchase offer",
                "body": "I counter with $120 for the item.",
                "data": {"price": 120}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, counter_proposal_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "counter_proposal")
        
        # Send acceptance message
        accept_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "agent1", "role": "buyer"},
            "content": {
                "type": "accept",
                "subject": "Re: Purchase offer",
                "body": "I accept your counter-offer of $120.",
                "data": {"price": 120, "accepted": True}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, accept_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "accepted")
        self.assertTrue(result["is_terminal"])
        
    async def test_task_delegation_protocol(self):
        """Test task delegation protocol."""
        # Create conversation
        result = await self.conversation_manager.create_conversation(
            protocol_id="task_delegation",
            protocol_version="1.0",
            participants=[
                {"id": "manager", "role": "manager"},
                {"id": "worker", "role": "worker"}
            ]
        )
        
        self.assertTrue(result["success"])
        conversation_id = result["conversation_id"]
        
        # Send task assignment message
        assign_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "manager", "role": "manager"},
            "content": {
                "type": "assign_task",
                "subject": "Data analysis task",
                "body": "Please analyze the Q1 sales data and prepare a report.",
                "data": {"task_id": "T123", "deadline": "2025-04-15"}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "high"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, assign_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "acceptance")
        
        # Send acceptance message
        accept_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "worker", "role": "worker"},
            "content": {
                "type": "accept_task",
                "subject": "Re: Data analysis task",
                "body": "I accept the task and will complete it by the deadline.",
                "data": {"task_id": "T123", "accepted": True}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, accept_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "in_progress")
        
        # Send progress update message
        progress_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "worker", "role": "worker"},
            "content": {
                "type": "progress_update",
                "subject": "Re: Data analysis task",
                "body": "I've completed 50% of the analysis.",
                "data": {"task_id": "T123", "progress": 0.5}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, progress_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "in_progress")
        
        # Send task completed message
        completed_message = {
            "message_id": str(uuid.uuid4()),
            "sender": {"id": "worker", "role": "worker"},
            "content": {
                "type": "task_completed",
                "subject": "Re: Data analysis task",
                "body": "I've completed the analysis and attached the report.",
                "data": {"task_id": "T123", "report_url": "https://example.com/report.pdf"}
            },
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "priority": "normal"
            }
        }
        
        result = await self.conversation_manager.add_message(conversation_id, completed_message)
        self.assertTrue(result["success"])
        self.assertEqual(result["new_state"], "completed")

class TestA2AFramework(unittest.TestCase):
    """Tests for the A2A framework."""
    
    def setUp(self):
        """Set up test environment."""
        self.a2a_framework = A2AFramework()
        
    async def test_agent_registration(self):
        """Test agent registration."""
        # Register agents
        result = await self.a2a_framework.register_agent(
            agent_id="agent1",
            role="developer",
            name="Developer Agent",
            description="Agent that performs development tasks"
        )
        
        self.assertTrue(result["success"])
        self.assertIn("security_token", result)
        
        result = await self.a2a_framework.register_agent(
            agent_id="agent2",
            role="tester",
            name="Tester Agent",
            description="Agent that performs testing tasks"
        )
        
        self.assertTrue(result["success"])
        
    async def test_capability_registration(self):
        """Test capability registration."""
        # Register agents
        await self.a2a_framework.register_agent("agent1", "developer")
        await self.a2a_framework.register_agent("agent2", "tester")
        
        # Register capabilities
        result = await self.a2a_framework.register_capability(
            agent_id="agent1",
            capability={
                "name": "Python Development",
                "description": "Ability to write Python code",
                "parameters": {"languages": ["Python"], "experience_years": 5},
                "performance_metrics": {"code_quality": 0.9, "speed": 0.8},
                "semantic_tags": ["programming", "python", "development"]
            }
        )
        
        self.assertTrue(result["success"])
        
        result = await self.a2a_framework.register_capability(
            agent_id="agent2",
            capability={
                "name": "Automated Testing",
                "description": "Ability to write and run automated tests",
                "parameters": {"frameworks": ["pytest", "unittest"], "experience_years": 3},
                "performance_metrics": {"test_coverage": 0.95, "bug_detection": 0.85},
                "semantic_tags": ["testing", "automation", "quality"]
            }
        )
        
        self.assertTrue(result["success"])
        
    async def test_capability_discovery(self):
        """Test capability discovery."""
        # Register agents and capabilities
        await self.a2a_framework.register_agent("agent1", "developer")
        await self.a2a_framework.register_agent("agent2", "tester")
        await self.a2a_framework.register_agent("agent3", "designer")
        
        await self.a2a_framework.register_capability(
            agent_id="agent1",
            capability={
                "name": "Python Development",
                "description": "Ability to write Python code",
                "parameters": {"languages": ["Python"], "experience_years": 5},
                "semantic_tags": ["programming", "python", "development"]
            }
        )
        
        await self.a2a_framework.register_capability(
            agent_id="agent2",
            capability={
                "name": "Automated Testing",
                "description": "Ability to write and run automated tests",
                "parameters": {"frameworks": ["pytest", "unittest"], "experience_years": 3},
                "semantic_tags": ["testing", "automation", "quality"]
            }
        )
        
        await self.a2a_framework.register_capability(
            agent_id="agent3",
            capability={
                "name": "UI Design",
                "description": "Ability to design user interfaces",
                "parameters": {"tools": ["Figma", "Sketch"], "experience_years": 4},
                "semantic_tags": ["design", "ui", "ux"]
            }
        )
        
        # Search for Python developers
        result = await self.a2a_framework.find_capable_agents({
            "tags": ["python"],
            "description_keywords": ["code", "write"]
        })
        
        self.assertTrue(result["success"])
        self.assertIn("agent1", result["matching_agents"])
        self.assertNotIn("agent2", result["matching_agents"])
        self.assertNotIn("agent3", result["matching_agents"])
        
        # Search for testing capabilities
        result = await self.a2a_framework.find_capable_agents({
            "tags": ["testing", "automation"],
            "description_keywords": ["test"]
        })
        
        self.assertTrue(result["success"])
        self.assertIn("agent2", result["matching_agents"])
        self.assertNotIn("agent1", result["matching_agents"])
        self.assertNotIn("agent3", result["matching_agents"])
        
    async def test_trust_management(self):
        """Test trust management."""
        # Register agents
        await self.a2a_framework.register_agent("agent1", "developer")
        await self.a2a_framework.register_agent("agent2", "tester")
        
        # Record interactions
        await self.a2a_framework.trust_manager.record_interaction(
            source_agent="agent1",
            target_agent="agent2",
            interaction_type="task_completion",
            outcome="success"
        )
        
        await self.a2a_framework.trust_manager.record_interaction(
            source_agent="agent1",
            target_agent="agent2",
            interaction_type="code_review",
            outcome="partial"
        )
        
        # Get trust score
        result = await self.a2a_framework.get_agent_trust("agent1", "agent2")
        
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["trust_score"], 0.0)
        self.assertLessEqual(result["trust_score"], 1.0)
        self.assertEqual(result["interaction_count"], 2)
        
    async def test_secure_messaging(self):
        """Test secure messaging."""
        # Register agents
        agent1_result = await self.a2a_framework.register_agent("agent1", "developer")
        agent2_result = await self.a2a_framework.register_agent("agent2", "tester")
        
        # Send message
        message = {
            "subject": "Test message",
            "content": "This is a test message",
            "data": {"key": "value"},
            "type": "INFORMATION"
        }
        
        result = await self.a2a_framework.send_message(
            sender_id="agent1",
            recipient_id="agent2",
            message=message
        )
        
        self.assertTrue(result["success"])
        secured_message = result["secured_message"]
        
        # Receive message
        result = await self.a2a_framework.receive_message(
            recipient_id="agent2",
            secured_message=secured_message
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["sender"], "agent1")
        self.assertEqual(result["content"]["subject"], "Test message")
        self.assertEqual(result["content"]["content"], "This is a test message")
        self.assertEqual(result["content"]["data"]["key"], "value")

class TestIntegration(unittest.TestCase):
    """Tests for the integration of MCP and A2A with the existing system."""
    
    def setUp(self):
        """Set up test environment."""
        self.integrated_system = IntegratedCommunicationSystem()
        
    async def test_system_initialization(self):
        """Test system initialization."""
        await self.integrated_system.initialize()
        
        # Verify components are initialized
        self.assertIsNotNone(self.integrated_system.conversation_manager)
        self.assertIsNotNone(self.integrated_system.a2a_framework)
        self.assertIsNotNone(self.integrated_system.mcp_adapter)
        self.assertIsNotNone(self.integrated_system.a2a_adapter)
        
    async def test_agent_registration(self):
        """Test agent registration with the integrated system."""
        await self.integrated_system.initialize()
        
        # Register agents
        result = await self.integrated_system.register_agent(
            agent_id="developer1",
            role="developer",
            name="Developer Agent 1",
            description="Senior Python developer",
            capabilities=[
                {
                    "name": "Python Development",
                    "description": "Ability to write Python code",
                    "parameters": {"languages": ["Python"], "experience_years": 5},
                    "performance_metrics": {"code_quality": 0.9, "speed": 0.8},
                    "semantic_tags": ["programming", "python", "development"]
                }
            ]
        )
        
        self.assertTrue(result["success"])
        
        result = await self.integrated_system.register_agent(
            agent_id="tester1",
            role="tester",
            name="Tester Agent 1",
            description="QA automation specialist",
            capabilities=[
                {
                    "name": "Automated Testing",
                    "description": "Ability to write and run automated tests",
                    "parameters": {"frameworks": ["pytest", "unittest"], "experience_years": 3},
                    "performance_metrics": {"test_coverage": 0.95, "bug_detection": 0.85},
                    "semantic_tags": ["testing", "automation", "quality"]
                }
            ]
        )
        
        self.assertTrue(result["success"])
        
    async def test_agent_discovery(self):
        """Test agent discovery with the integrated system."""
        await self.integrated_system.initialize()
        
        # Register agents
        await self.integrated_system.register_agent(
            agent_id="developer1",
            role="developer",
            name="Developer Agent 1",
            description="Senior Python developer",
            capabilities=[
                {
                    "name": "Python Development",
                    "description": "Ability to write Python code",
                    "parameters": {"languages": ["Python"], "experience_years": 5},
                    "semantic_tags": ["programming", "python", "development"]
                }
            ]
        )
        
        await self.integrated_system.register_agent(
            agent_id="tester1",
            role="tester",
            name="Tester Agent 1",
            description="QA automation specialist",
            capabilities=[
                {
                    "name": "Automated Testing",
                    "description": "Ability to write and run automated tests",
                    "parameters": {"frameworks": ["pytest", "unittest"], "experience_years": 3},
                    "semantic_tags": ["testing", "automation", "quality"]
                }
            ]
        )
        
        # Find agents for a development task
        result = await self.integrated_system.find_agents_for_task(
            task_description="Need to write Python code for data analysis",
            required_capabilities=["python", "programming"]
        )
        
        self.assertTrue(result["success"])
        self.assertIn("developer1", result["matching_agents"])
        self.assertNotIn("tester1", result["matching_agents"])
        
        # Find agents for a testing task
        result = await self.integrated_system.find_agents_for_task(
            task_description="Need to create automated tests for the application",
            required_capabilities=["testing", "automation"]
        )
        
        self.assertTrue(result["success"])
        self.assertIn("tester1", result["matching_agents"])
        self.assertNotIn("developer1", result["matching_agents"])
        
    async def test_message_sending(self):
        """Test message sending with the integrated system."""
        await self.integrated_system.initialize()
        
        # Register agents
        await self.integrated_system.register_agent("sender", "manager")
        await self.integrated_system.register_agent("recipient", "worker")
        
        # Create and send a message
        message = Message(
            id=str(uuid.uuid4()),
            sender="sender",
            recipients=["recipient"],
            subject="Task Assignment",
            content="Please complete the data analysis task",
            type=MessageType.TASK,
            data={"task_id": "T123", "deadline": "2025-04-15"}
        )
        
        message.metadata = {
            "thread_id": str(uuid.uuid4()),
            "sender_role": "manager",
            "recipient_role_recipient": "worker"
        }
        
        result = await self.integrated_system.send_message(message, secure=True)
        
        self.assertTrue(result["success"])
        
    async def test_conversation_flow(self):
        """Test conversation flow with the integrated system."""
        await self.integrated_system.initialize()
        
        # Register agents
        await self.integrated_system.register_agent("manager", "manager")
        await self.integrated_system.register_agent("worker", "worker")
        
        # Start a conversation
        thread_id = str(uuid.uuid4())
        result = await self.integrated_system.start_conversation(
            thread_id=thread_id,
            protocol_type="task",
            participants=[
                {"id": "manager", "role": "manager"},
                {"id": "worker", "role": "worker"}
            ]
        )
        
        self.assertTrue(result["success"])
        conversation_id = result["conversation_id"]
        
        # Create and send task assignment message
        assign_message = Message(
            id=str(uuid.uuid4()),
            sender="manager",
            recipients=["worker"],
            subject="Data Analysis Task",
            content="Please analyze the Q1 sales data and prepare a report",
            type=MessageType.TASK,
            data={"task_id": "T123", "deadline": "2025-04-15"}
        )
        
        assign_message.metadata = {
            "thread_id": thread_id,
            "sender_role": "manager",
            "recipient_role_worker": "worker"
        }
        
        await self.integrated_system.send_message(assign_message, secure=False)
        
        # Create and send task acceptance message
        accept_message = Message(
            id=str(uuid.uuid4()),
            sender="worker",
            recipients=["manager"],
            subject="Re: Data Analysis Task",
            content="I accept the task and will complete it by the deadline",
            type=MessageType.RESPONSE,
            data={"task_id": "T123", "accepted": True}
        )
        
        accept_message.metadata = {
            "thread_id": thread_id,
            "sender_role": "worker",
            "recipient_role_manager": "manager"
        }
        
        await self.integrated_system.send_message(accept_message, secure=False)
        
    async def test_trust_updates(self):
        """Test trust updates with the integrated system."""
        await self.integrated_system.initialize()
        
        # Register agents
        await self.integrated_system.register_agent("manager", "manager")
        await self.integrated_system.register_agent("worker", "worker")
        
        # Update trust based on successful task completion
        result = await self.integrated_system.update_agent_trust(
            source_id="manager",
            target_id="worker",
            interaction_type="task_completion",
            outcome="success"
        )
        
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["trust_score"], 0.0)
        self.assertLessEqual(result["trust_score"], 1.0)
        
        # Get trust information
        result = await self.integrated_system.get_agent_trust("manager", "worker")
        
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["trust_score"], 0.0)
        self.assertLessEqual(result["trust_score"], 1.0)
        
    async def test_maintenance_tasks(self):
        """Test maintenance tasks with the integrated system."""
        await self.integrated_system.initialize()
        
        # Run maintenance tasks
        result = await self.integrated_system.maintenance_tasks()
        
        self.assertTrue(result["success"])
        self.assertIn("a2a_maintenance", result)
        self.assertIn("conversation_maintenance", result)

def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add MCP tests
    suite.addTest(unittest.makeSuite(TestMCPFramework))
    
    # Add A2A tests
    suite.addTest(unittest.makeSuite(TestA2AFramework))
    
    # Add integration tests
    suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    # Run tests using asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        *[test() for test in [
            TestMCPFramework().test_information_exchange_protocol,
            TestMCPFramework().test_negotiation_protocol,
            TestMCPFramework().test_task_delegation_protocol,
            TestA2AFramework().test_agent_registration,
            TestA2AFramework().test_capability_registration,
            TestA2AFramework().test_capability_discovery,
            TestA2AFramework().test_trust_management,
            TestA2AFramework().test_secure_messaging,
            TestIntegration().test_system_initialization,
            TestIntegration().test_agent_registration,
            TestIntegration().test_agent_discovery,
            TestIntegration().test_message_sending,
            TestIntegration().test_conversation_flow,
            TestIntegration().test_trust_updates,
            TestIntegration().test_maintenance_tasks
        ]]
    ))
