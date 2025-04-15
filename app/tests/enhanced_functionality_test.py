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


import unittest
import asyncio
import json
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collaboration.enhanced_communication_framework import EnhancedAgentCommunicationFramework
from agent.optimized_role_specialization import OptimizedAgentRoleSpecialization
from collaboration.project_manager_communication_flow import ProjectManagerCommunicationFlow
from collaboration.request_prioritization_mechanism import RequestPrioritizationMechanism


class TestEnhancedFunctionality(unittest.TestCase):
    """Test suite for the enhanced multi-agent team functionality."""

    def setUp(self):
        """Set up test environment."""
        # Initialize the communication framework
        self.communication_framework = EnhancedAgentCommunicationFramework()
        
        # Initialize the role specialization system
        self.role_specialization = OptimizedAgentRoleSpecialization()
        
        # Initialize the project manager communication flow
        self.pm_communication_flow = ProjectManagerCommunicationFlow()
        
        # Initialize the request prioritization mechanism
        self.request_prioritization = RequestPrioritizationMechanism()
        
        # Set up test agents
        self.test_agents = {
            "project_manager": {
                "id": "pm-001",
                "role": "project_manager",
                "capabilities": ["project_planning", "task_coordination", "risk_management"],
                "expertise_areas": ["agile_methodology", "resource_allocation"]
            },
            "developer": {
                "id": "dev-001",
                "role": "developer",
                "capabilities": ["coding", "debugging", "testing"],
                "expertise_areas": ["python", "javascript", "api_development"]
            },
            "system_architect": {
                "id": "arch-001",
                "role": "system_architect",
                "capabilities": ["architecture_design", "system_modeling", "technology_selection"],
                "expertise_areas": ["microservices", "cloud_architecture", "security_design"]
            },
            "qa_testing_specialist": {
                "id": "qa-001",
                "role": "qa_testing_specialist",
                "capabilities": ["test_planning", "test_automation", "defect_reporting"],
                "expertise_areas": ["integration_testing", "performance_testing", "security_testing"]
            }
        }

    def test_agent_registration(self):
        """Test agent registration with the communication framework and role specialization system."""
        # Test registering agents with the communication framework
        async def test_comm_registration():
            for agent_id, agent_data in self.test_agents.items():
                result = await self.communication_framework.register_agent(agent_data)
                self.assertTrue(result["success"])
                self.assertEqual(result["agent_id"], agent_data["id"])
                self.assertEqual(result["role"], agent_data["role"])
        
        # Test registering agents with the role specialization system
        async def test_role_registration():
            for agent_id, agent_data in self.test_agents.items():
                result = await self.role_specialization.register_agent(agent_data)
                self.assertTrue(result["success"])
                self.assertEqual(result["agent_id"], agent_data["id"])
                self.assertEqual(result["role"], agent_data["role"])
        
        # Run the async tests
        asyncio.run(test_comm_registration())
        asyncio.run(test_role_registration())

    def test_message_sending(self):
        """Test sending messages between agents."""
        async def test_messaging():
            # Register agents
            for agent_id, agent_data in self.test_agents.items():
                await self.communication_framework.register_agent(agent_data)
            
            # Test direct message
            direct_message = {
                "from": "pm-001",
                "to": "dev-001",
                "content": "Can you provide an update on the authentication feature?",
                "pattern": "request_response",
                "priority": "high"
            }
            
            result = await self.communication_framework.send_message(direct_message)
            self.assertTrue(result["success"])
            self.assertEqual(result["result"]["pattern"], "request_response")
            self.assertEqual(result["result"]["status"], "delivered")
            
            # Test group discussion
            group_message = {
                "from": "pm-001",
                "to": ["dev-001", "arch-001", "qa-001"],
                "content": "Let's discuss the implementation approach for the new feature.",
                "pattern": "group_discussion",
                "priority": "medium",
                "topic": "Feature Implementation"
            }
            
            result = await self.communication_framework.send_message(group_message)
            self.assertTrue(result["success"])
            self.assertEqual(result["result"]["pattern"], "group_discussion")
            self.assertEqual(result["result"]["status"], "delivered")
            
            # Test task delegation
            task_message = {
                "from": "pm-001",
                "to": "dev-001",
                "content": "Please implement the authentication service by Friday.",
                "pattern": "task_delegation",
                "priority": "high",
                "task": {
                    "title": "Implement Authentication Service",
                    "description": "Create a JWT-based authentication service with refresh token support.",
                    "due_date": (datetime.now().isoformat().split("T")[0]) + "T17:00:00Z",
                    "priority": "high"
                }
            }
            
            result = await self.communication_framework.send_message(task_message)
            self.assertTrue(result["success"])
            self.assertEqual(result["result"]["pattern"], "task_delegation")
            self.assertEqual(result["result"]["status"], "delivered")
        
        # Run the async test
        asyncio.run(test_messaging())

    def test_message_response(self):
        """Test responding to messages."""
        async def test_response():
            # Register agents
            for agent_id, agent_data in self.test_agents.items():
                await self.communication_framework.register_agent(agent_data)
            
            # Send a request message
            request_message = {
                "from": "pm-001",
                "to": "dev-001",
                "content": "Can you provide an estimate for implementing the authentication service?",
                "pattern": "request_response",
                "priority": "high"
            }
            
            send_result = await self.communication_framework.send_message(request_message)
            self.assertTrue(send_result["success"])
            request_id = send_result["message_id"]
            
            # Respond to the message
            response_params = {
                "request_id": request_id,
                "from": "dev-001",
                "content": "I estimate it will take approximately 3 days to implement the core authentication service."
            }
            
            response_result = await self.communication_framework.respond_to_message(response_params)
            self.assertTrue(response_result["success"])
            self.assertEqual(response_result["request_id"], request_id)
        
        # Run the async test
        asyncio.run(test_response())

    def test_communication_analysis(self):
        """Test analyzing communication patterns."""
        async def test_analysis():
            # Register agents and send messages
            for agent_id, agent_data in self.test_agents.items():
                await self.communication_framework.register_agent(agent_data)
            
            # Send several messages to generate data for analysis
            messages = [
                {
                    "from": "pm-001",
                    "to": "dev-001",
                    "content": "Can you provide an update on the authentication feature?",
                    "pattern": "request_response",
                    "priority": "high"
                },
                {
                    "from": "dev-001",
                    "to": "pm-001",
                    "content": "I've completed the core functionality and am now working on the refresh token mechanism.",
                    "pattern": "status_update",
                    "priority": "medium"
                },
                {
                    "from": "pm-001",
                    "to": ["dev-001", "arch-001", "qa-001"],
                    "content": "Let's discuss the implementation approach for the new feature.",
                    "pattern": "group_discussion",
                    "priority": "medium"
                },
                {
                    "from": "arch-001",
                    "to": ["pm-001", "dev-001", "qa-001"],
                    "content": "I recommend using a microservices approach for this feature.",
                    "pattern": "group_discussion",
                    "priority": "medium"
                },
                {
                    "from": "qa-001",
                    "to": ["pm-001", "dev-001", "arch-001"],
                    "content": "I'll prepare test cases based on the requirements and architecture.",
                    "pattern": "group_discussion",
                    "priority": "medium"
                }
            ]
            
            for message in messages:
                await self.communication_framework.send_message(message)
            
            # Analyze communication patterns
            analysis_params = {
                "time_period": "all"
            }
            
            analysis_result = await self.communication_framework.analyze_communication_patterns(analysis_params)
            self.assertTrue(analysis_result["success"])
            
            # Verify that we have insights and recommendations
            self.assertGreater(len(analysis_result["insights"]), 0)
            self.assertGreater(len(analysis_result["recommendations"]), 0)
            
            # Verify that we have data for agents and patterns
            self.assertGreaterEqual(len(analysis_result["metrics"]["by_agent"]), 1)
            self.assertGreaterEqual(len(analysis_result["metrics"]["by_pattern"]), 1)
        
        # Run the async test
        asyncio.run(test_analysis())

    def test_role_optimization(self):
        """Test optimizing agent roles based on performance."""
        async def test_optimization():
            # Register agents with the role specialization system
            for agent_id, agent_data in self.test_agents.items():
                await self.role_specialization.register_agent(agent_data)
            
            # Update performance for an agent
            performance_params = {
                "agent_id": "dev-001",
                "task_id": "task-001",
                "success": True,
                "quality": 8,
                "time_taken": 7200,  # 2 hours
                "skills_used": ["coding", "debugging"],
                "collaboration_score": 7,
                "tools_used": ["git", "vscode"],
                "tool_effectiveness": {
                    "git": 0.9,
                    "vscode": 0.8
                },
                "expertise_used": ["python", "api_development"],
                "expertise_effectiveness": {
                    "python": 0.9,
                    "api_development": 0.7
                }
            }
            
            update_result = await self.role_specialization.update_agent_performance(performance_params)
            self.assertTrue(update_result["success"])
            
            # Optimize the agent's role
            optimization_params = {
                "agent_id": "dev-001",
                "optimization_level": 2
            }
            
            optimization_result = await self.role_specialization.optimize_agent_role(optimization_params)
            self.assertTrue(optimization_result["success"])
            self.assertEqual(optimization_result["optimization_level"], 2)
            self.assertGreater(len(optimization_result["changes"]), 0)
            
            # Get recommendations for the agent
            recommendation_params = {
                "agent_id": "dev-001",
                "recommendation_type": "all"
            }
            
            recommendation_result = await self.role_specialization.get_agent_recommendations(recommendation_params)
            self.assertTrue(recommendation_result["success"])
            self.assertGreater(len(recommendation_result["recommendations"]), 0)
        
        # Run the async test
        asyncio.run(test_optimization())

    def test_team_composition_analysis(self):
        """Test analyzing team composition."""
        async def test_team_analysis():
            # Register agents with the role specialization system
            for agent_id, agent_data in self.test_agents.items():
                await self.role_specialization.register_agent(agent_data)
            
            # Update performance for agents
            for agent_id, agent_data in self.test_agents.items():
                performance_params = {
                    "agent_id": agent_data["id"],
                    "task_id": f"task-{agent_id}",
                    "success": True,
                    "quality": 7 + (hash(agent_id) % 3),  # Vary quality between 7-9
                    "time_taken": 3600 + (hash(agent_id) % 3600),  # Vary time between 1-2 hours
                    "skills_used": agent_data["capabilities"][:2],
                    "collaboration_score": 6 + (hash(agent_id) % 4)  # Vary score between 6-9
                }
                
                await self.role_specialization.update_agent_performance(performance_params)
            
            # Analyze team composition
            team_analysis_params = {
                "team_ids": [agent_data["id"] for agent_data in self.test_agents.values()],
                "project_type": "development"
            }
            
            analysis_result = await self.role_specialization.analyze_team_composition(team_analysis_params)
            self.assertTrue(analysis_result["success"])
            
            # Verify team analysis data
            self.assertEqual(analysis_result["team_size"], len(self.test_agents))
            self.assertGreaterEqual(len(analysis_result["roles_present"]), 1)
            self.assertGreaterEqual(len(analysis_result["team_members"]), 1)
            self.assertGreaterEqual(len(analysis_result["recommendations"]), 0)
        
        # Run the async test
        asyncio.run(test_team_analysis())

    def test_project_manager_communication_flow(self):
        """Test the project manager communication flow."""
        async def test_pm_flow():
            # Initialize the PM communication flow with agents
            for agent_id, agent_data in self.test_agents.items():
                await self.pm_communication_flow.register_agent(agent_data)
            
            # Create a human input request from a developer
            request_params = {
                "from_agent": "dev-001",
                "to_agent": "pm-001",
                "request_type": "clarification",
                "content": "Need clarification on the authentication requirements. Should we support social login?",
                "priority": "medium",
                "context": {
                    "feature": "authentication",
                    "current_task": "implementation_planning"
                }
            }
            
            request_result = await self.pm_communication_flow.submit_human_input_request(request_params)
            self.assertTrue(request_result["success"])
            self.assertIsNotNone(request_result["request_id"])
            
            # Get pending human input requests
            pending_result = await self.pm_communication_flow.get_pending_human_input_requests({})
            self.assertTrue(pending_result["success"])
            self.assertGreaterEqual(len(pending_result["requests"]), 1)
            
            # Prioritize requests
            prioritization_result = await self.pm_communication_flow.prioritize_human_input_requests({})
            self.assertTrue(prioritization_result["success"])
            self.assertGreaterEqual(len(prioritization_result["prioritized_requests"]), 1)
            
            # Submit human response
            response_params = {
                "request_id": request_result["request_id"],
                "response": "Yes, please implement social login with Google and GitHub options.",
                "from_human": True
            }
            
            response_result = await self.pm_communication_flow.submit_human_response(response_params)
            self.assertTrue(response_result["success"])
            
            # Verify request is marked as resolved
            pending_result = await self.pm_communication_flow.get_pending_human_input_requests({})
            request_ids = [req["id"] for req in pending_result["requests"]]
            self.assertNotIn(request_result["request_id"], request_ids)
        
        # Run the async test
        asyncio.run(test_pm_flow())

    def test_request_prioritization(self):
        """Test the request prioritization mechanism."""
        async def test_prioritization():
            # Create test requests
            test_requests = [
                {
                    "id": "req-001",
                    "from_agent": "dev-001",
                    "to_agent": "pm-001",
                    "request_type": "clarification",
                    "content": "Need clarification on authentication requirements.",
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "context": {
                        "feature": "authentication",
                        "current_task": "implementation_planning"
                    }
                },
                {
                    "id": "req-002",
                    "from_agent": "qa-001",
                    "to_agent": "pm-001",
                    "request_type": "approval",
                    "content": "Need approval for the test plan.",
                    "priority": "high",
                    "timestamp": datetime.now().isoformat(),
                    "context": {
                        "feature": "authentication",
                        "current_task": "test_planning"
                    }
                },
                {
                    "id": "req-003",
                    "from_agent": "arch-001",
                    "to_agent": "pm-001",
                    "request_type": "decision",
                    "content": "Need decision on the authentication service architecture.",
                    "priority": "critical",
                    "timestamp": datetime.now().isoformat(),
                    "context": {
                        "feature": "authentication",
                        "current_task": "architecture_design"
                    }
                }
            ]
            
            # Add requests to the prioritization mechanism
            for request in test_requests:
                await self.request_prioritization.add_request(request)
            
            # Get prioritized requests
            prioritization_params = {
                "max_requests": 10
            }
            
            prioritization_result = await self.request_prioritization.get_prioritized_requests(prioritization_params)
            self.assertTrue(prioritization_result["success"])
            self.assertEqual(len(prioritization_result["requests"]), len(test_requests))
            
            # Verify prioritization order (critical > high > medium)
            self.assertEqual(prioritization_result["requests"][0]["id"], "req-003")  # Critical priority
            self.assertEqual(prioritization_result["requests"][1]["id"], "req-002")  # High priority
            self.assertEqual(prioritization_result["requests"][2]["id"], "req-001")  # Medium priority
            
            # Mark a request as resolved
            resolve_params = {
                "request_id": "req-002",
                "resolution": "Approved test plan.",
                "resolved_by": "pm-001"
            }
            
            resolve_result = await self.request_prioritization.mark_request_resolved(resolve_params)
            self.assertTrue(resolve_result["success"])
            
            # Verify request is marked as resolved
            prioritization_result = await self.request_prioritization.get_prioritized_requests(prioritization_params)
            request_ids = [req["id"] for req in prioritization_result["requests"]]
            self.assertNotIn("req-002", request_ids)
            self.assertEqual(len(prioritization_result["requests"]), len(test_requests) - 1)
        
        # Run the async test
        asyncio.run(test_prioritization())

    def test_optimized_prompt_generation(self):
        """Test generating optimized prompts for agents."""
        async def test_prompt_generation():
            # Register agents with the role specialization system
            for agent_id, agent_data in self.test_agents.items():
                await self.role_specialization.register_agent(agent_data)
            
            # Generate optimized prompt for developer
            prompt_params = {
                "agent_id": "dev-001",
                "task_type": "development",
                "context": {
                    "feature": "authentication",
                    "requirements": ["JWT support", "refresh tokens", "password reset"]
                }
            }
            
            prompt_result = await self.role_specialization.generate_optimized_prompt(prompt_params)
            self.assertTrue(prompt_result["success"])
            self.assertIsNotNone(prompt_result["optimized_prompt"])
            self.assertGreater(len(prompt_result["optimized_prompt"]), 100)  # Ensure we have a substantial prompt
            
            # Generate optimized prompt for project manager
            prompt_params = {
                "agent_id": "pm-001",
                "task_type": "planning",
                "context": {
                    "project": "authentication_service",
                    "timeline": "2 weeks",
                    "team_size": 4
                }
            }
            
            prompt_result = await self.role_specialization.generate_optimized_prompt(prompt_params)
            self.assertTrue(prompt_result["success"])
            self.assertIsNotNone(prompt_result["optimized_prompt"])
            self.assertGreater(len(prompt_result["optimized_prompt"]), 100)  # Ensure we have a substantial prompt
        
        # Run the async test
        asyncio.run(test_prompt_generation())

    def test_find_optimal_collaborators(self):
        """Test finding optimal collaborators for a task."""
        async def test_find_collaborators():
            # Register agents with the communication framework
            for agent_id, agent_data in self.test_agents.items():
                await self.communication_framework.register_agent(agent_data)
            
            # Find optimal collaborators for a development task
            collaborator_params = {
                "task_type": "development",
                "required_skills": ["coding", "api_development", "security_design"],
                "team_size": 3
            }
            
            collaborator_result = await self.communication_framework.find_optimal_collaborators(collaborator_params)
            self.assertTrue(collaborator_result["success"])
            self.assertEqual(len(collaborator_result["recommended_team"]), 3)
            
            # Verify that the developer is in the recommended team (highest match for coding and api_development)
            dev_in_team = False
            for member in collaborator_result["recommended_team"]:
                if member["agent_id"] == "dev-001":
                    dev_in_team = True
                    break
            
            self.assertTrue(dev_in_team, "Developer should be in the recommended team for a development task")
        
        # Run the async test
        asyncio.run(test_find_collaborators())


if __name__ == "__main__":
    unittest.main()
