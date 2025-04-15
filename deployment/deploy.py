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


"""
Deployment script for TORONTO AI Team Agent Team AI multi-agent system.

This script deploys multiple agent instances based on the configuration
and sets up the communication framework for inter-agent collaboration.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent.project_manager import ProjectManagerAgent
from app.agent.product_manager import ProductManagerAgent
from app.agent.developer import DeveloperAgent
from app.agent.additional_roles import SystemArchitectAgent, QATestingSpecialistAgent
from app.collaboration.communication_framework import AgentCommunicationFramework
from app.collaboration.framework import RealTimeCollaborationFramework

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'deployment.log'))
    ]
)
logger = logging.getLogger(__name__)

class MultiAgentDeployment:
    """
    Deployment manager for the multi-agent system.
    """
    
    def __init__(self, config_path):
        """
        Initialize the deployment manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.agents = {}
        self.comm_framework = AgentCommunicationFramework()
        self.collab_framework = RealTimeCollaborationFramework(self.comm_framework)
        
        logger.info(f"Initialized deployment manager with config from {config_path}")
    
    def _load_config(self):
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Loaded configuration: {config['system']['name']} v{config['system']['version']}")
        return config
    
    async def deploy_agents(self):
        """
        Deploy agent instances based on configuration.
        
        Returns:
            Dictionary of deployed agents
        """
        agent_configs = self.config['agents']
        
        # Create agent instances
        for role, agent_config in agent_configs.items():
            if not agent_config.get('enabled', True):
                logger.info(f"Agent {agent_config['id']} ({role}) is disabled, skipping")
                continue
            
            try:
                agent = self._create_agent_instance(role, agent_config)
                self.agents[agent_config['id']] = agent
                logger.info(f"Deployed agent {agent_config['id']} with role {role}")
            except Exception as e:
                logger.error(f"Error deploying agent {agent_config['id']}: {str(e)}")
        
        logger.info(f"Deployed {len(self.agents)} agents")
        return self.agents
    
    def _create_agent_instance(self, role, config):
        """
        Create an agent instance based on role.
        
        Args:
            role: Agent role
            config: Agent configuration
            
        Returns:
            Agent instance
        """
        agent_classes = {
            "project_manager": ProjectManagerAgent,
            "product_manager": ProductManagerAgent,
            "developer": DeveloperAgent,
            "system_architect": SystemArchitectAgent,
            "qa_testing_specialist": QATestingSpecialistAgent
        }
        
        if role not in agent_classes:
            raise ValueError(f"Unknown agent role: {role}")
        
        agent_class = agent_classes[role]
        return agent_class(config)
    
    async def create_collaboration_session(self, name, description, participants):
        """
        Create a collaboration session between agents.
        
        Args:
            name: Session name
            description: Session description
            participants: List of agent IDs to include
            
        Returns:
            Session creation result
        """
        if not participants:
            participants = list(self.agents.keys())
        
        # Use the project manager as the initiator if available
        initiator = next((agent_id for agent_id, agent in self.agents.items() 
                         if agent.__class__.__name__ == "ProjectManagerAgent"), participants[0])
        
        result = await self.collab_framework.create_collaboration_session({
            "name": name,
            "description": description,
            "participants": participants,
            "initiator": initiator,
            "context": {
                "deployment_id": f"deploy_{os.getpid()}",
                "environment": self.config['system']['environment']
            },
            "session_type": self.config['collaboration'].get('default_session_type', 'general')
        })
        
        logger.info(f"Created collaboration session: {result.get('session_id')} - {name}")
        return result
    
    async def run_test_scenario(self, scenario_name):
        """
        Run a test scenario with the deployed agents.
        
        Args:
            scenario_name: Name of the scenario to run
            
        Returns:
            Scenario result
        """
        logger.info(f"Running test scenario: {scenario_name}")
        
        if scenario_name == "basic_communication":
            return await self._run_basic_communication_test()
        elif scenario_name == "collaboration_session":
            return await self._run_collaboration_session_test()
        else:
            return {
                "success": False,
                "message": f"Unknown test scenario: {scenario_name}"
            }
    
    async def _run_basic_communication_test(self):
        """
        Run a basic communication test between agents.
        
        Returns:
            Test result
        """
        # Get project manager and developer agents
        pm_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                           if agent.__class__.__name__ == "ProjectManagerAgent"), None)
        dev_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                            if agent.__class__.__name__ == "DeveloperAgent"), None)
        
        if not pm_agent_id or not dev_agent_id:
            return {
                "success": False,
                "message": "Project Manager or Developer agent not found"
            }
        
        # Send a message from project manager to developer
        result1 = await self.comm_framework.send_message({
            "from": pm_agent_id,
            "to": dev_agent_id,
            "content": {
                "type": "task_assignment",
                "task": "Implement login functionality",
                "priority": "high"
            },
            "metadata": {
                "category": "task"
            }
        })
        
        # Send a message from developer to project manager
        result2 = await self.comm_framework.send_message({
            "from": dev_agent_id,
            "to": pm_agent_id,
            "content": {
                "type": "task_update",
                "task": "Implement login functionality",
                "status": "in_progress",
                "notes": "Started working on authentication flow"
            },
            "metadata": {
                "category": "update"
            }
        })
        
        # Get message history
        history_result = await self.comm_framework.get_message_history({
            "limit": 10
        })
        
        return {
            "success": True,
            "message": "Basic communication test completed successfully",
            "results": {
                "pm_to_dev": result1,
                "dev_to_pm": result2,
                "history": history_result
            }
        }
    
    async def _run_collaboration_session_test(self):
        """
        Run a collaboration session test between agents.
        
        Returns:
            Test result
        """
        # Create a collaboration session with all agents
        session_result = await self.create_collaboration_session(
            "Test Feature Implementation",
            "Collaborative session to design and implement a test feature",
            list(self.agents.keys())
        )
        
        if not session_result.get("success"):
            return session_result
        
        session_id = session_result["session_id"]
        
        # Get agent IDs by role
        arch_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                             if agent.__class__.__name__ == "SystemArchitectAgent"), None)
        product_agent_id = next((agent_id for agent_id, agent in self.agents.items() 
                                if agent.__class__.__name__ == "ProductManagerAgent"), None)
        
        if not arch_agent_id or not product_agent_id:
            return {
                "success": False,
                "message": "System Architect or Product Manager agent not found"
            }
        
        # Send a collaboration message from architect
        message_result = await self.collab_framework.send_collaboration_message({
            "session_id": session_id,
            "from": arch_agent_id,
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
        
        # Update shared state from product manager
        state_result = await self.collab_framework.update_shared_state({
            "session_id": session_id,
            "agent_id": product_agent_id,
            "updates": {
                "requirements": {
                    "auth_methods": ["email", "google", "github"],
                    "security_level": "high",
                    "user_experience": "streamlined"
                }
            },
            "operation": "merge"
        })
        
        # Get session information
        session_info = await self.collab_framework.get_collaboration_session({
            "session_id": session_id,
            "include_messages": True,
            "include_artifacts": True,
            "include_state": True
        })
        
        return {
            "success": True,
            "message": "Collaboration session test completed successfully",
            "results": {
                "session_creation": session_result,
                "message_sending": message_result,
                "state_update": state_result,
                "session_info": session_info
            }
        }
    
    async def shutdown(self):
        """
        Shutdown the deployment and clean up resources.
        """
        logger.info("Shutting down deployment")
        # Clean up resources if needed
        self.agents = {}

async def main():
    """
    Main entry point for deployment.
    """
    # Get config path
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    # Create deployment manager
    deployment = MultiAgentDeployment(config_path)
    
    try:
        # Deploy agents
        await deployment.deploy_agents()
        
        # Run test scenarios
        basic_result = await deployment.run_test_scenario("basic_communication")
        logger.info(f"Basic communication test result: {basic_result['success']}")
        
        collab_result = await deployment.run_test_scenario("collaboration_session")
        logger.info(f"Collaboration session test result: {collab_result['success']}")
        
        # Save test results
        with open(os.path.join(os.path.dirname(__file__), 'test_results.json'), 'w') as f:
            json.dump({
                "basic_communication": basic_result,
                "collaboration_session": collab_result
            }, f, indent=2)
        
        logger.info("Deployment and testing completed successfully")
    
    except Exception as e:
        logger.error(f"Error during deployment: {str(e)}")
    
    finally:
        # Shutdown deployment
        await deployment.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
