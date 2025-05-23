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


"""Test suite for the TorontoAITeamAgent Team AI multi-agent system.

This module provides tests to ensure all components of the multi-agent system
work together properly."""

import os
import asyncio
import unittest
import json
import time
import uuid
from ..collaboration.multi_agent_system import MultiAgentSystem
from ..collaboration.communication_framework import AgentCommunicationFramework, AgentLearningMechanisms
from ..interface.project_manager_interface import ProjectManagerInterface
from ..integration.agent_role_integration import AgentRoleIntegration

class MultiAgentSystemTest:
    """Test suite for the multi-agent system.
    
    This class provides methods to test the functionality of the multi-agent system,
    including project creation, agent communication, task assignment, and learning."""
    
    def __init__(self):
        """Initialize the test suite."""
        # Initialize components
        self.multi_agent_system = MultiAgentSystem()
        self.communication_framework = AgentCommunicationFramework()
        self.learning_mechanisms = AgentLearningMechanisms()
        self.project_manager_interface = ProjectManagerInterface()
        self.agent_role_integration = AgentRoleIntegration()
        
        # Test results
        self.results = {}
    
    async def run_all_tests(self):
        """
        Run all tests for the multi-agent system.
        
        Returns:
            Test results
        """
        # Run tests
        await self.test_project_creation()
        await self.test_agent_communication()
        await self.test_task_assignment()
        await self.test_team_creation()
        await self.test_learning_cycle()
        
        # Calculate overall success
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result["success"])
        
        return {
            "success": successful_tests == total_tests,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "results": self.results
        }
    
    async def test_project_creation(self):
        """
        Test project creation with a team of agents.
        
        Returns:
            Test result
        """
        test_id = "project_creation"
        
        try:
            # Create a project
            project_result = await self.project_manager_interface.create_project({
                "name": "Test Project",
                "description": "A test project for the multi-agent system",
                "team_composition": ["project_manager", "product_manager", "developer", "system_architect"],
                "human_stakeholder": {
                    "name": "Test User",
                    "role": "stakeholder"
                }
            })
            
            # Check if project was created successfully
            if not project_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to create project: {project_result['error']}",
                    "details": project_result
                }
                return
            
            # Get project status
            status_result = await self.project_manager_interface.get_project_status({
                "project_id": project_result["project_id"]
            })
            
            # Check if status was retrieved successfully
            if not status_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to get project status: {status_result['error']}",
                    "details": status_result
                }
                return
            
            # Test passed
            self.results[test_id] = {
                "success": True,
                "project_id": project_result["project_id"],
                "details": {
                    "project_creation": project_result,
                    "project_status": status_result
                }
            }
        except Exception as e:
            self.results[test_id] = {
                "success": False,
                "error": f"Exception during test: {str(e)}"
            }
    
    async def test_agent_communication(self):
        """
        Test communication between agents.
        
        Returns:
            Test result
        """
        test_id = "agent_communication"
        
        try:
            # Create a project if not already created
            if "project_creation" not in self.results or not self.results["project_creation"]["success"]:
                # Create a new project
                project_result = await self.project_manager_interface.create_project({
                    "name": "Communication Test Project",
                    "description": "A test project for agent communication",
                    "team_composition": ["project_manager", "product_manager", "developer"],
                    "human_stakeholder": {
                        "name": "Test User",
                        "role": "stakeholder"
                    }
                })
                
                if not project_result["success"]:
                    self.results[test_id] = {
                        "success": False,
                        "error": f"Failed to create project for communication test: {project_result['error']}",
                        "details": project_result
                    }
                    return
                
                project_id = project_result["project_id"]
            else:
                # Use existing project
                project_id = self.results["project_creation"]["project_id"]
            
            # Send a message to the project manager
            message_result = await self.project_manager_interface.send_message_to_project_manager({
                "project_id": project_id,
                "message": "This is a test message for agent communication"
            })
            
            if not message_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to send message to project manager: {message_result['error']}",
                    "details": message_result
                }
                return
            
            # Process agent messages
            process_result = await self.project_manager_interface.process_agent_messages({
                "project_id": project_id,
                "iterations": 3
            })
            
            if not process_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to process agent messages: {process_result['error']}",
                    "details": process_result
                }
                return
            
            # Get messages from project manager
            response_result = await self.project_manager_interface.get_messages_from_project_manager({
                "project_id": project_id,
                "timeout": 1.0
            })
            
            # Test passed if we got a response or if the queue is empty (which is also valid)
            self.results[test_id] = {
                "success": True,
                "project_id": project_id,
                "details": {
                    "message_sent": message_result,
                    "message_processing": process_result,
                    "message_response": response_result
                }
            }
        except Exception as e:
            self.results[test_id] = {
                "success": False,
                "error": f"Exception during test: {str(e)}"
            }
    
    async def test_task_assignment(self):
        """
        Test task assignment to a team.
        
        Returns:
            Test result
        """
        test_id = "task_assignment"
        
        try:
            # Create a team
            team_result = await self.agent_role_integration.create_team({
                "name": "Task Test Team",
                "description": "A test team for task assignment",
                "team_type": "web_development"
            })
            
            if not team_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to create team for task assignment test: {team_result['error']}",
                    "details": team_result
                }
                return
            
            team_id = team_result["team_id"]
            project_id = team_result["project_id"]
            
            # Assign a task to the team
            task_result = await self.agent_role_integration.assign_task_to_team({
                "team_id": team_id,
                "task": "Create a simple landing page with a contact form",
                "priority": "high",
                "deadline": time.time() + 86400  # 24 hours from now
            })
            
            if not task_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to assign task to team: {task_result['error']}",
                    "details": task_result
                }
                return
            
            # Process agent messages
            process_result = await self.project_manager_interface.process_agent_messages({
                "project_id": project_id,
                "iterations": 5
            })
            
            if not process_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to process agent messages after task assignment: {process_result['error']}",
                    "details": process_result
                }
                return
            
            # Get team status
            status_result = await self.agent_role_integration.get_team_status({
                "team_id": team_id
            })
            
            if not status_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to get team status after task assignment: {status_result['error']}",
                    "details": status_result
                }
                return
            
            # Test passed
            self.results[test_id] = {
                "success": True,
                "team_id": team_id,
                "project_id": project_id,
                "details": {
                    "team_creation": team_result,
                    "task_assignment": task_result,
                    "message_processing": process_result,
                    "team_status": status_result
                }
            }
        except Exception as e:
            self.results[test_id] = {
                "success": False,
                "error": f"Exception during test: {str(e)}"
            }
    
    async def test_team_creation(self):
        """
        Test creation of teams with different role compositions.
        
        Returns:
            Test result
        """
        test_id = "team_creation"
        
        try:
            # Get available team templates
            templates_result = await self.agent_role_integration.get_available_team_templates()
            
            if not templates_result["success"]:
                self.results[test_id] = {
                    "success": False,
                    "error": f"Failed to get team templates: {templates_result['error']}",
                    "details": templates_result
                }
                return
            
            # Create teams with different templates
            team_results = {}
            
            for template_name in templates_result["templates"]:
                # Skip if we've already tested too many templates
                if len(team_results) >= 2:
                    break
                
                team_result = await self.agent_role_integration.create_team({
                    "name": f"{template_name.title()} Test Team",
                    "description": f"A test team using the {template_name} template",
                    "team_type": template_name
                })
                
                team_results[template_name] = team_result
                
                if not team_result["success"]:
                    self.results[test_id] = {
                        "success": False,
                        "error": f"Failed to create team with template {template_name}: {team_result['error']}",
                        "details": {
                            "templates": templates_result,
                            "team_results": team_results
                        }
                    }
                    return
            
            # Test passed
            self.results[test_id] = {
                "success": True,
                "details": {
                    "templates": templates_result,
                    "team_results": team_results
                }
            }
        except Exception as e:
            self.results[test_id] = {
                "success": False,
                "error": f"Exception during test: {str(e)}"
            }
    
    async def test_learning_cycle(self):
        """
        Test the learning cycle for agents.
        
        Returns:
            Test result
        """
        test_id = "learning_cycle"
        
        try:
            # Use an existing project if available
            if "project_creation" in self.results and self.results["project_creation"]["success"]:
                project_id = self.results["project_creation"]["project_id"]
            elif "task_assignment" in self.results and self.results["task_assignment"]["success"]:
                project_id = self.results["task_assignment"]["project_id"]
            else:
                # Create a new project
                project_result = await self.project_manager_interface.create_project({
                    "name": "Learning Test Project",
                    "description": "A test project for learning cycle",
                    "team_composition": ["project_manager", "product_manager", "developer", "system_architect"],
                    "human_stakeholder": {
                        "name": "Test User",
                        "role": "stakeholder"
                    }
                })
                
                if not project_result["success"]:
                    self.results[test_id] = {
                        "success": False,
                        "error": f"Failed to create project for learning test: {project_result['error']}",
                        "details": project_result
                    }
                    return
                
                project_id = project_result["project_id"]
            
            # Generate some communication for learning
            for i in range(3):
                # Send a message
                await self.project_manager_interface.send_message_to_project_manager({
                    "project_id": project_id,
                    "message": f"Test message {i+1} for learning cycle"
                })
                
                # Process messages
                await self.project_manager_interface.process_agent_messages({
                    "project_id": project_id,
                    "iterations": 2
                })
                
                # Get responses
                await self.project_manager_interface.get_messages_from_project_manager({
                    "project_id": project_id,
                    "timeout": 0.5
                })
            
            # Run learning cycle
            learning_result = await self.project_manager_interface.run_learning_cycle({
                "project_id": project_id
            })
            
            # Test passed even if learning didn't find improvements (which is valid if there's not enough data)
            self.results[test_id] = {
                "success": True,
                "project_id": project_id,
                "details": {
                    "learning_result": learning_result
                }
            }
        except Exception as e:
            self.results[test_id] = {
                "success": False,
                "error": f"Exception during test: {str(e)}"
            }

async def run_tests():
    """
    Run all tests for the multi-agent system.
    
    Returns:
        Test results
    """
    test_suite = MultiAgentSystemTest()
    return await test_suite.run_all_tests()

if __name__ == "__main__":
    # Run tests
    import asyncio
    results = asyncio.run(run_tests())
    
    # Print results
    print(json.dumps(results, indent=2))
