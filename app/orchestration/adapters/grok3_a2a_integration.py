"""
Grok 3 A2A integration module.

This module provides integration between Grok 3 and the Agent-to-Agent (A2A) communication protocol.
"""

import logging
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple

from app.models.adapters.model_adapter import Grok3Adapter
from app.models.adapters.reasoning_adapters import ReasoningGrok3Adapter
from app.code_execution.code_execution import CodeExecutionGrok3Adapter

# Set up logging
logger = logging.getLogger(__name__)

class Grok3A2AIntegration:
    """
    Integration class for Grok 3 and the Agent-to-Agent (A2A) communication protocol.
    
    This class provides methods for creating and managing teams of Grok 3-powered agents
    that can communicate using the A2A protocol.
    """
    
    def __init__(
        self,
        grok3_adapter: Optional[Grok3Adapter] = None,
        reasoning_adapter: Optional[ReasoningGrok3Adapter] = None,
        code_execution_adapter: Optional[CodeExecutionGrok3Adapter] = None,
        a2a_adapter = None
    ):
        """
        Initialize the Grok3A2AIntegration.
        
        Args:
            grok3_adapter: Optional Grok3Adapter instance.
            reasoning_adapter: Optional ReasoningGrok3Adapter instance.
            code_execution_adapter: Optional CodeExecutionGrok3Adapter instance.
            a2a_adapter: Optional A2AAdapter instance.
        """
        self.grok3_adapter = grok3_adapter or Grok3Adapter()
        self.reasoning_adapter = reasoning_adapter or ReasoningGrok3Adapter(self.grok3_adapter)
        self.code_execution_adapter = code_execution_adapter or CodeExecutionGrok3Adapter(self.grok3_adapter, self.reasoning_adapter)
        
        # Store A2A adapter
        self.a2a_adapter = a2a_adapter
        
        # Store active agent teams
        self.agent_teams = {}
        
        logger.info("Initialized Grok3A2AIntegration")
    
    def create_agent_team(
        self,
        team_name: str,
        agent_roles: List[Dict[str, str]],
        team_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a team of Grok 3-powered agents.
        
        Args:
            team_name: Name of the team.
            agent_roles: List of agent roles (each with role and name).
            team_config: Optional team configuration.
        
        Returns:
            Team configuration as a dictionary.
        """
        if not self.a2a_adapter:
            logger.warning("A2AAdapter not provided, creating basic team configuration")
            return self._create_basic_team(
                team_name=team_name,
                agent_roles=agent_roles,
                team_config=team_config
            )
        
        # Use the A2A adapter to create a team
        team_id = str(uuid.uuid4())
        
        # Create agents
        agents = []
        for role_config in agent_roles:
            agent_id = str(uuid.uuid4())
            role = role_config.get("role", "general")
            name = role_config.get("name", f"Agent {len(agents) + 1}")
            
            agent = {
                "id": agent_id,
                "name": name,
                "role": role,
                "model": "grok-3",
                "capabilities": self._get_capabilities_for_role(role)
            }
            
            agents.append(agent)
        
        # Create team configuration
        team = {
            "id": team_id,
            "name": team_name,
            "agents": agents,
            "config": team_config or {}
        }
        
        # Store the team
        self.agent_teams[team_id] = team
        
        # Register the team with the A2A adapter
        if self.a2a_adapter:
            self.a2a_adapter.register_team(team)
        
        return team
    
    def request_reasoning(
        self,
        from_agent_id: str,
        to_agent_id: str,
        prompt: str,
        reasoning_mode: str = "auto",
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request reasoning from one agent to another.
        
        Args:
            from_agent_id: ID of the requesting agent.
            to_agent_id: ID of the agent to perform reasoning.
            prompt: Prompt for reasoning.
            reasoning_mode: Reasoning mode to use (auto, think, big_brain).
            system_message: Optional system message for context.
        
        Returns:
            Reasoning result as a dictionary.
        """
        # Validate agent IDs
        if not self._validate_agent_ids(from_agent_id, to_agent_id):
            return {
                "success": False,
                "error": "Invalid agent IDs",
                "result": ""
            }
        
        # Create A2A message if adapter is available
        if self.a2a_adapter:
            message = {
                "from": from_agent_id,
                "to": to_agent_id,
                "type": "reasoning_request",
                "content": {
                    "prompt": prompt,
                    "reasoning_mode": reasoning_mode,
                    "system_message": system_message
                }
            }
            
            # Send the message through A2A
            self.a2a_adapter.send_message(message)
        
        # Perform reasoning
        result = self.reasoning_adapter.generate_text(
            prompt=prompt,
            reasoning_mode=reasoning_mode,
            system_message=system_message
        )
        
        # Create response
        response = {
            "success": True,
            "from": to_agent_id,
            "to": from_agent_id,
            "result": result
        }
        
        # Send response through A2A if available
        if self.a2a_adapter:
            response_message = {
                "from": to_agent_id,
                "to": from_agent_id,
                "type": "reasoning_response",
                "content": response
            }
            
            self.a2a_adapter.send_message(response_message)
        
        return response
    
    def request_code_execution(
        self,
        from_agent_id: str,
        to_agent_id: str,
        prompt: str,
        language: str = "python",
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request code execution from one agent to another.
        
        Args:
            from_agent_id: ID of the requesting agent.
            to_agent_id: ID of the agent to perform code execution.
            prompt: Prompt describing the code to generate.
            language: Target programming language.
            system_message: Optional system message for context.
        
        Returns:
            Code execution result as a dictionary.
        """
        # Validate agent IDs
        if not self._validate_agent_ids(from_agent_id, to_agent_id):
            return {
                "success": False,
                "error": "Invalid agent IDs",
                "result": {}
            }
        
        # Create A2A message if adapter is available
        if self.a2a_adapter:
            message = {
                "from": from_agent_id,
                "to": to_agent_id,
                "type": "code_execution_request",
                "content": {
                    "prompt": prompt,
                    "language": language,
                    "system_message": system_message
                }
            }
            
            # Send the message through A2A
            self.a2a_adapter.send_message(message)
        
        # Perform code generation and execution
        result = self.code_execution_adapter.generate_and_execute_code(
            prompt=prompt,
            language=language,
            system_message=system_message
        )
        
        # Create response
        response = {
            "success": True,
            "from": to_agent_id,
            "to": from_agent_id,
            "result": result
        }
        
        # Send response through A2A if available
        if self.a2a_adapter:
            response_message = {
                "from": to_agent_id,
                "to": from_agent_id,
                "type": "code_execution_response",
                "content": response
            }
            
            self.a2a_adapter.send_message(response_message)
        
        return response
    
    def send_message(
        self,
        from_agent_id: str,
        to_agent_id: str,
        message_type: str,
        content: Any
    ) -> Dict[str, Any]:
        """
        Send a message from one agent to another.
        
        Args:
            from_agent_id: ID of the sending agent.
            to_agent_id: ID of the receiving agent.
            message_type: Type of message.
            content: Message content.
        
        Returns:
            Message status as a dictionary.
        """
        # Validate agent IDs
        if not self._validate_agent_ids(from_agent_id, to_agent_id):
            return {
                "success": False,
                "error": "Invalid agent IDs"
            }
        
        # Create A2A message
        message = {
            "from": from_agent_id,
            "to": to_agent_id,
            "type": message_type,
            "content": content
        }
        
        # Send the message through A2A if available
        if self.a2a_adapter:
            self.a2a_adapter.send_message(message)
            return {
                "success": True,
                "message_id": str(uuid.uuid4())
            }
        else:
            logger.warning("A2AAdapter not provided, message not sent")
            return {
                "success": False,
                "error": "A2AAdapter not provided"
            }
    
    def _create_basic_team(
        self,
        team_name: str,
        agent_roles: List[Dict[str, str]],
        team_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a basic team configuration without using the A2A adapter.
        
        Args:
            team_name: Name of the team.
            agent_roles: List of agent roles (each with role and name).
            team_config: Optional team configuration.
        
        Returns:
            Team configuration as a dictionary.
        """
        team_id = str(uuid.uuid4())
        
        # Create agents
        agents = []
        for role_config in agent_roles:
            agent_id = str(uuid.uuid4())
            role = role_config.get("role", "general")
            name = role_config.get("name", f"Agent {len(agents) + 1}")
            
            agent = {
                "id": agent_id,
                "name": name,
                "role": role,
                "model": "grok-3",
                "capabilities": self._get_capabilities_for_role(role)
            }
            
            agents.append(agent)
        
        # Create team configuration
        team = {
            "id": team_id,
            "name": team_name,
            "agents": agents,
            "config": team_config or {}
        }
        
        # Store the team
        self.agent_teams[team_id] = team
        
        return team
    
    def _get_capabilities_for_role(self, role: str) -> List[str]:
        """
        Get capabilities for a specific role.
        
        Args:
            role: Agent role.
        
        Returns:
            List of capabilities.
        """
        role_capabilities = {
            "coordinator": ["planning", "coordination", "oversight"],
            "developer": ["coding", "testing", "debugging"],
            "analyst": ["analysis", "research", "evaluation"],
            "researcher": ["research", "information_gathering", "summarization"],
            "designer": ["design", "creativity", "visualization"],
            "tester": ["testing", "quality_assurance", "validation"],
            "project_manager": ["planning", "coordination", "resource_management"],
            "product_manager": ["requirements", "prioritization", "user_focus"]
        }
        
        return role_capabilities.get(role, ["general_task"])
    
    def _validate_agent_ids(self, from_agent_id: str, to_agent_id: str) -> bool:
        """
        Validate that agent IDs exist in the teams.
        
        Args:
            from_agent_id: ID of the sending agent.
            to_agent_id: ID of the receiving agent.
        
        Returns:
            True if both agent IDs are valid, False otherwise.
        """
        # If no teams are registered, assume IDs are valid
        if not self.agent_teams:
            return True
        
        from_valid = False
        to_valid = False
        
        # Check all teams for the agent IDs
        for team in self.agent_teams.values():
            for agent in team.get("agents", []):
                if agent.get("id") == from_agent_id:
                    from_valid = True
                if agent.get("id") == to_agent_id:
                    to_valid = True
                
                if from_valid and to_valid:
                    return True
        
        if not from_valid:
            logger.warning(f"Agent ID not found: {from_agent_id}")
        if not to_valid:
            logger.warning(f"Agent ID not found: {to_agent_id}")
        
        return False
