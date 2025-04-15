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


"""Integration of all agent roles for TorontoAITeamAgent Team AI.

This module integrates all agent roles into the multi-agent system,
ensuring they work together effectively as a team."""

from typing import Dict, Any, List, Optional, Union
import os
import asyncio
import logging
import uuid
import time
import json
from ..agent.base_agent import BaseAgent
from ..agent.project_manager import ProjectManagerAgent
from ..agent.product_manager import ProductManagerAgent
from ..agent.developer import DeveloperAgent
from ..agent.additional_roles import (
    SystemArchitectAgent,
    DevOpsEngineerAgent,
    QATestingSpecialistAgent,
    SecurityEngineerAgent,
    DatabaseEngineerAgent,
    UIUXDesignerAgent,
    DocumentationSpecialistAgent,
    PerformanceEngineerAgent
)
from ..collaboration.multi_agent_system import MultiAgentSystem
from ..collaboration.communication_framework import AgentCommunicationFramework, AgentLearningMechanisms
from ..interface.project_manager_interface import ProjectManagerInterface

logger = logging.getLogger(__name__)

class AgentRoleIntegration:
    """Integration of all agent roles into a cohesive team.
    
    This class provides methods for creating teams with different role compositions,
    defining role interactions, and ensuring effective collaboration."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Agent Role Integration.
        
        Args:
            config: Integration configuration with optional settings"""
        self.config = config or {}
        
        # Initialize components
        self.multi_agent_system = MultiAgentSystem(self.config.get("multi_agent_system"))
        self.communication_framework = AgentCommunicationFramework(self.config.get("communication_framework"))
        self.learning_mechanisms = AgentLearningMechanisms(self.config.get("learning_mechanisms"))
        self.project_manager_interface = ProjectManagerInterface(self.config.get("project_manager_interface"))
        
        # Default configuration
        self.default_config = {
            "default_team_composition": ["project_manager", "product_manager", "developer"],
            "specialized_teams": {
                "web_development": [
                    "project_manager", 
                    "product_manager", 
                    "developer", 
                    "ui_ux_designer", 
                    "qa_testing_specialist"
                ],
                "enterprise_system": [
                    "project_manager", 
                    "product_manager", 
                    "developer", 
                    "system_architect", 
                    "database_engineer", 
                    "security_engineer", 
                    "devops_engineer"
                ],
                "data_science": [
                    "project_manager", 
                    "product_manager", 
                    "developer", 
                    "database_engineer", 
                    "performance_engineer"
                ],
                "full_stack": [
                    "project_manager", 
                    "product_manager", 
                    "developer", 
                    "system_architect", 
                    "ui_ux_designer", 
                    "database_engineer", 
                    "qa_testing_specialist", 
                    "security_engineer", 
                    "devops_engineer", 
                    "documentation_specialist"
                ]
            },
            "role_interactions": {
                "project_manager": ["*"],  # Can interact with all roles
                "product_manager": ["project_manager", "developer", "ui_ux_designer", "system_architect"],
                "developer": ["project_manager", "product_manager", "system_architect", "database_engineer", "qa_testing_specialist"],
                "system_architect": ["project_manager", "product_manager", "developer", "database_engineer", "security_engineer", "devops_engineer"],
                "devops_engineer": ["project_manager", "system_architect", "developer", "security_engineer"],
                "qa_testing_specialist": ["project_manager", "developer", "product_manager"],
                "security_engineer": ["project_manager", "system_architect", "developer", "devops_engineer"],
                "database_engineer": ["project_manager", "system_architect", "developer", "performance_engineer"],
                "ui_ux_designer": ["project_manager", "product_manager", "developer"],
                "documentation_specialist": ["project_manager", "product_manager", "developer", "system_architect"],
                "performance_engineer": ["project_manager", "developer", "database_engineer", "system_architect"]
            }
        }
        
        # Merge default config with provided config
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Available agent roles
        self.available_roles = {
            "project_manager": ProjectManagerAgent,
            "product_manager": ProductManagerAgent,
            "developer": DeveloperAgent,
            "system_architect": SystemArchitectAgent,
            "devops_engineer": DevOpsEngineerAgent,
            "qa_testing_specialist": QATestingSpecialistAgent,
            "security_engineer": SecurityEngineerAgent,
            "database_engineer": DatabaseEngineerAgent,
            "ui_ux_designer": UIUXDesignerAgent,
            "documentation_specialist": DocumentationSpecialistAgent,
            "performance_engineer": PerformanceEngineerAgent
        }
        
        # Active teams
        self.active_teams = {}
    
    async def create_team(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new team with specified roles.
        
        Args:
            params: Team parameters including:
                - name: Team name
                - description: Team description
                - team_type: Type of team (default, web_development, enterprise_system, etc.)
                - custom_roles: Custom list of roles (overrides team_type)
                - project_id: Optional project ID to associate with the team
                
        Returns:
            Team creation result
        """
        name = params.get("name")
        description = params.get("description", "")
        team_type = params.get("team_type", "default")
        custom_roles = params.get("custom_roles")
        project_id = params.get("project_id")
        
        if not name:
            return {
                "success": False,
                "error": "Team name is required"
            }
        
        # Determine team composition
        if custom_roles:
            # Use custom roles
            team_composition = custom_roles
        elif team_type in self.config["specialized_teams"]:
            # Use specialized team composition
            team_composition = self.config["specialized_teams"][team_type]
        else:
            # Use default team composition
            team_composition = self.config["default_team_composition"]
        
        # Validate roles
        for role in team_composition:
            if role not in self.available_roles:
                return {
                    "success": False,
                    "error": f"Unknown role: {role}"
                }
        
        # Ensure project manager is included
        if "project_manager" not in team_composition:
            team_composition.insert(0, "project_manager")
        
        # Generate team ID
        team_id = str(uuid.uuid4())
        
        # Create project if not provided
        if not project_id:
            project_result = await self.project_manager_interface.create_project({
                "name": name,
                "description": description,
                "team_composition": team_composition,
                "human_stakeholder": {
                    "name": "Human Stakeholder",
                    "role": "stakeholder"
                }
            })
            
            if not project_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create project: {project_result['error']}"
                }
            
            project_id = project_result["project_id"]
        
        # Store team
        self.active_teams[team_id] = {
            "id": team_id,
            "name": name,
            "description": description,
            "team_type": team_type,
            "composition": team_composition,
            "project_id": project_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "status": "active"
        }
        
        return {
            "success": True,
            "team_id": team_id,
            "name": name,
            "team_type": team_type,
            "composition": team_composition,
            "project_id": project_id,
            "message": f"Team '{name}' created successfully with {len(team_composition)} roles"
        }
    
    async def get_team_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about a team.
        
        Args:
            params: Parameters including:
                - team_id: Team ID
                
        Returns:
            Team information
        """
        team_id = params.get("team_id")
        
        if not team_id:
            return {
                "success": False,
                "error": "Team ID is required"
            }
        
        # Check if team exists
        if team_id not in self.active_teams:
            return {
                "success": False,
                "error": f"Team with ID '{team_id}' does not exist"
            }
        
        team = self.active_teams[team_id]
        
        return {
            "success": True,
            "team": team
        }
    
    async def get_role_interactions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the interaction matrix for roles in a team.
        
        Args:
            params: Parameters including:
                - team_id: Team ID
                
        Returns:
            Role interaction matrix
        """
        team_id = params.get("team_id")
        
        if not team_id:
            return {
                "success": False,
                "error": "Team ID is required"
            }
        
        # Check if team exists
        if team_id not in self.active_teams:
            return {
                "success": False,
                "error": f"Team with ID '{team_id}' does not exist"
            }
        
        team = self.active_teams[team_id]
        
        # Build interaction matrix
        interaction_matrix = {}
        
        for role in team["composition"]:
            allowed_interactions = self.config["role_interactions"].get(role, [])
            
            # If "*" is in allowed interactions, can interact with all roles
            if "*" in allowed_interactions:
                interaction_matrix[role] = [r for r in team["composition"] if r != role]
            else:
                # Filter allowed interactions to only include roles in the team
                interaction_matrix[role] = [r for r in allowed_interactions if r in team["composition"] and r != role]
        
        return {
            "success": True,
            "team_id": team_id,
            "interaction_matrix": interaction_matrix
        }
    
    async def assign_task_to_team(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign a task to a team through the project manager.
        
        Args:
            params: Task parameters including:
                - team_id: Team ID
                - task: Task description
                - priority: Task priority
                - deadline: Optional deadline
                - attachments: Optional attachments
                
        Returns:
            Task assignment result
        """
        team_id = params.get("team_id")
        task = params.get("task")
        priority = params.get("priority", "normal")
        deadline = params.get("deadline")
        attachments = params.get("attachments", [])
        
        if not team_id:
            return {
                "success": False,
                "error": "Team ID is required"
            }
            
        if not task:
            return {
                "success": False,
                "error": "Task description is required"
            }
        
        # Check if team exists
        if team_id not in self.active_teams:
            return {
                "success": False,
                "error": f"Team with ID '{team_id}' does not exist"
            }
        
        team = self.active_teams[team_id]
        project_id = team["project_id"]
        
        # Create task message
        task_message = {
            "type": "task_assignment",
            "task": task,
            "priority": priority,
            "deadline": deadline,
            "timestamp": time.time()
        }
        
        # Send task to project manager
        result = await self.project_manager_interface.send_message_to_project_manager({
            "project_id": project_id,
            "message": json.dumps(task_message),
            "attachments": attachments
        })
        
        if not result["success"]:
            return {
                "success": False,
                "error": f"Failed to assign task: {result['error']}"
            }
        
        # Update team timestamp
        team["updated_at"] = time.time()
        
        return {
            "success": True,
            "team_id": team_id,
            "project_id": project_id,
            "message_id": result["message_id"],
            "message": "Task assigned to team successfully"
        }
    
    async def get_team_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the status of a team.
        
        Args:
            params: Parameters including:
                - team_id: Team ID
                
        Returns:
            Team status
        """
        team_id = params.get("team_id")
        
        if not team_id:
            return {
                "success": False,
                "error": "Team ID is required"
            }
        
        # Check if team exists
        if team_id not in self.active_teams:
            return {
                "success": False,
                "error": f"Team with ID '{team_id}' does not exist"
            }
        
        team = self.active_teams[team_id]
        project_id = team["project_id"]
        
        # Get project status
        result = await self.project_manager_interface.get_project_status({
            "project_id": project_id
        })
        
        if not result["success"]:
            return {
                "success": False,
                "error": f"Failed to get team status: {result['error']}"
            }
        
        return {
            "success": True,
            "team_id": team_id,
            "team_name": team["name"],
            "team_composition": team["composition"],
            "project_id": project_id,
            "status": result["status"],
            "progress": result["progress"],
            "tasks": result["tasks"],
            "updated_at": result["updated_at"]
        }
    
    async def get_team_communication(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the communication history for a team.
        
        Args:
            params: Parameters including:
                - team_id: Team ID
                - limit: Maximum number of messages to return
                - filter: Optional filter for messages
                
        Returns:
            Team communication history
        """
        team_id = params.get("team_id")
        limit = params.get("limit", 100)
        filter_params = params.get("filter", {})
        
        if not team_id:
            return {
                "success": False,
                "error": "Team ID is required"
            }
        
        # Check if team exists
        if team_id not in self.active_teams:
            return {
                "success": False,
                "error": f"Team with ID '{team_id}' does not exist"
            }
        
        team = self.active_teams[team_id]
        project_id = team["project_id"]
        
        # Get communication log
        result = await self.multi_agent_system.get_communication_log({
            "project_id": project_id,
            "limit": limit,
            "filter": filter_params
        })
        
        return result
    
    async def run_team_learning_cycle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a learning cycle for a team to improve their communication.
        
        Args:
            params: Parameters including:
                - team_id: Team ID
                
        Returns:
            Learning cycle result
        """
        team_id = params.get("team_id")
        
        if not team_id:
            return {
                "success": False,
                "error": "Team ID is required"
            }
        
        # Check if team exists
        if team_id not in self.active_teams:
            return {
                "success": False,
                "error": f"Team with ID '{team_id}' does not exist"
            }
        
        team = self.active_teams[team_id]
        project_id = team["project_id"]
        
        # Run learning cycle
        result = await self.multi_agent_system.run_learning_cycle({
            "project_id": project_id
        })
        
        return result
    
    async def get_available_team_templates(self) -> Dict[str, Any]:
        """
        Get the available team templates.
        
        Returns:
            Available team templates
        """
        templates = {
            "default": {
                "name": "Default Team",
                "description": "Basic team with project manager, product manager, and developer",
                "roles": self.config["default_team_composition"]
            }
        }
        
        # Add specialized teams
        for team_type, roles in self.config["specialized_teams"].items():
            templates[team_type] = {
                "name": team_type.replace("_", " ").title() + " Team",
                "description": f"Specialized team for {team_type.replace('_', ' ')} projects",
                "roles": roles
            }
        
        return {
            "success": True,
            "templates": templates
        }
    
    async def get_available_roles(self) -> Dict[str, Any]:
        """
        Get the available agent roles.
        
        Returns:
            Available agent roles
        """
        roles = {}
        
        for role_name, role_class in self.available_roles.items():
            roles[role_name] = {
                "name": role_name,
                "description": role_class.description if hasattr(role_class, "description") else "",
                "capabilities": role_class().capabilities if hasattr(role_class(), "capabilities") else []
            }
        
        return {
            "success": True,
            "roles": roles
        }
