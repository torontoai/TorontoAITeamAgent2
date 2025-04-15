"""
Architecture templates for Multi-agent Architecture Search (MaAS).

This module provides predefined architecture templates that can be used
as starting points for architecture search or as reference architectures.
"""

from typing import Dict, List, Any, Optional
import logging
import uuid

from ..models import (
    ArchitectureModel, AgentModel, ConnectionModel,
    AgentRole, AgentCapability
)

logger = logging.getLogger(__name__)


class ArchitectureTemplates:
    """Collection of predefined architecture templates."""
    
    @staticmethod
    def create_hierarchical_template(
        num_levels: int = 3,
        agents_per_level: Dict[int, int] = None,
        model_name: str = "gpt-4"
    ) -> ArchitectureModel:
        """Create a hierarchical architecture template.
        
        Args:
            num_levels: Number of hierarchy levels
            agents_per_level: Dictionary mapping level to number of agents
            model_name: Base model name for agents
            
        Returns:
            Hierarchical architecture model
        """
        if agents_per_level is None:
            agents_per_level = {
                0: 1,  # Top level (coordinator)
                1: 3,  # Middle level (managers)
                2: 6   # Bottom level (workers)
            }
        
        # Create architecture
        architecture = ArchitectureModel(
            id=str(uuid.uuid4()),
            name="Hierarchical Architecture",
            description="A hierarchical architecture with multiple levels",
            agents=[],
            connections=[]
        )
        
        # Create agents for each level
        agents_by_level = {}
        for level in range(num_levels):
            agents_by_level[level] = []
            num_agents = agents_per_level.get(level, 1)
            
            for i in range(num_agents):
                # Determine role based on level
                if level == 0:
                    role = AgentRole.COORDINATOR
                    capabilities = [
                        AgentCapability.PLANNING,
                        AgentCapability.DELEGATION,
                        AgentCapability.DECISION_MAKING
                    ]
                elif level == num_levels - 1:
                    role = AgentRole.WORKER
                    capabilities = [
                        AgentCapability.CODE_EXECUTION,  # Changed from TASK_EXECUTION
                        AgentCapability.INFORMATION_RETRIEVAL
                    ]
                else:
                    role = AgentRole.MANAGER
                    capabilities = [
                        AgentCapability.COORDINATION,
                        AgentCapability.MONITORING,
                        AgentCapability.REPORTING
                    ]
                
                # Create agent
                agent = AgentModel(
                    id=str(uuid.uuid4()),
                    name=f"{role.name.capitalize()} {level}.{i}",
                    description=f"Level {level} {role.name} agent",
                    role=role,
                    capabilities=capabilities,
                    model_name=model_name,
                    parameters={"temperature": 0.7, "max_tokens": 1000}
                )
                
                architecture.agents.append(agent)
                agents_by_level[level].append(agent)
        
        # Create connections between levels
        for level in range(num_levels - 1):
            for upper_agent in agents_by_level[level]:
                for lower_agent in agents_by_level[level + 1]:
                    # Create connection from upper to lower
                    connection = ConnectionModel(
                        id=str(uuid.uuid4()),
                        source_id=upper_agent.id,
                        target_id=lower_agent.id,
                        bidirectional=True,
                        weight=1.0
                    )
                    architecture.connections.append(connection)
        
        return architecture
    
    @staticmethod
    def create_star_template(
        num_specialists: int = 5,
        model_name: str = "gpt-4"
    ) -> ArchitectureModel:
        """Create a star architecture template with a central coordinator and specialists.
        
        Args:
            num_specialists: Number of specialist agents
            model_name: Base model name for agents
            
        Returns:
            Star architecture model
        """
        # Create architecture
        architecture = ArchitectureModel(
            id=str(uuid.uuid4()),
            name="Star Architecture",
            description="A star architecture with a central coordinator and specialists",
            agents=[],
            connections=[]
        )
        
        # Create coordinator agent
        coordinator = AgentModel(
            id=str(uuid.uuid4()),
            name="Central Coordinator",
            description="Central coordinator agent that manages specialists",
            role=AgentRole.COORDINATOR,
            capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.DELEGATION,
                AgentCapability.DECISION_MAKING,
                AgentCapability.COORDINATION
            ],
            model_name=model_name,
            parameters={"temperature": 0.7, "max_tokens": 1000}
        )
        architecture.agents.append(coordinator)
        
        # Create specialist roles and capabilities
        specialist_configs = [
            (AgentRole.RESEARCHER, [AgentCapability.INFORMATION_RETRIEVAL, AgentCapability.RESEARCH]),
            (AgentRole.CODER, [AgentCapability.CODE_GENERATION, AgentCapability.DEBUGGING]),
            (AgentRole.CRITIC, [AgentCapability.QUALITY_ASSESSMENT, AgentCapability.FEEDBACK]),  # Changed from EVALUATION
            (AgentRole.WRITER, [AgentCapability.CONTENT_GENERATION, AgentCapability.SUMMARIZATION]),
            (AgentRole.REASONER, [AgentCapability.REASONING, AgentCapability.PROBLEM_SOLVING]),
            (AgentRole.PLANNER, [AgentCapability.PLANNING, AgentCapability.GOAL_DECOMPOSITION]),  # Changed from SCHEDULING
            (AgentRole.MEMORY, [AgentCapability.MEMORY_MANAGEMENT, AgentCapability.INFORMATION_RETRIEVAL])
        ]
        
        # Create specialist agents
        for i in range(min(num_specialists, len(specialist_configs))):
            role, capabilities = specialist_configs[i]
            
            specialist = AgentModel(
                id=str(uuid.uuid4()),
                name=f"{role.name.capitalize()} Specialist",
                description=f"Specialist agent with {role.name} capabilities",
                role=role,
                capabilities=capabilities,
                model_name=model_name,
                parameters={"temperature": 0.7, "max_tokens": 1000}
            )
            architecture.agents.append(specialist)
            
            # Create bidirectional connection between coordinator and specialist
            connection = ConnectionModel(
                id=str(uuid.uuid4()),
                source_id=coordinator.id,
                target_id=specialist.id,
                bidirectional=True,
                weight=1.0
            )
            architecture.connections.append(connection)
        
        return architecture
    
    @staticmethod
    def create_mesh_template(
        num_agents: int = 5,
        connection_density: float = 0.7,
        model_name: str = "gpt-4"
    ) -> ArchitectureModel:
        """Create a mesh architecture template with densely connected agents.
        
        Args:
            num_agents: Number of agents in the mesh
            connection_density: Density of connections (0-1)
            model_name: Base model name for agents
            
        Returns:
            Mesh architecture model
        """
        # Create architecture
        architecture = ArchitectureModel(
            id=str(uuid.uuid4()),
            name="Mesh Architecture",
            description="A mesh architecture with densely connected agents",
            agents=[],
            connections=[]
        )
        
        # Create agent roles and capabilities
        agent_configs = [
            (AgentRole.COORDINATOR, [AgentCapability.COORDINATION, AgentCapability.DECISION_MAKING]),
            (AgentRole.RESEARCHER, [AgentCapability.INFORMATION_RETRIEVAL, AgentCapability.RESEARCH]),
            (AgentRole.CODER, [AgentCapability.CODE_GENERATION, AgentCapability.DEBUGGING]),
            (AgentRole.CRITIC, [AgentCapability.QUALITY_ASSESSMENT, AgentCapability.FEEDBACK]),  # Changed from EVALUATION
            (AgentRole.WRITER, [AgentCapability.CONTENT_GENERATION, AgentCapability.SUMMARIZATION]),
            (AgentRole.REASONER, [AgentCapability.REASONING, AgentCapability.PROBLEM_SOLVING]),
            (AgentRole.PLANNER, [AgentCapability.PLANNING, AgentCapability.GOAL_DECOMPOSITION])  # Changed from SCHEDULING
        ]
        
        # Create agents
        for i in range(min(num_agents, len(agent_configs))):
            role, capabilities = agent_configs[i]
            
            agent = AgentModel(
                id=str(uuid.uuid4()),
                name=f"{role.name.capitalize()} Agent",
                description=f"Agent with {role.name} capabilities",
                role=role,
                capabilities=capabilities,
                model_name=model_name,
                parameters={"temperature": 0.7, "max_tokens": 1000}
            )
            architecture.agents.append(agent)
        
        # Create connections based on density
        import random
        for i, agent1 in enumerate(architecture.agents):
            for j, agent2 in enumerate(architecture.agents):
                if i != j and random.random() < connection_density:
                    # Create bidirectional connection
                    connection = ConnectionModel(
                        id=str(uuid.uuid4()),
                        source_id=agent1.id,
                        target_id=agent2.id,
                        bidirectional=True,
                        weight=1.0
                    )
                    architecture.connections.append(connection)
        
        return architecture
    
    @staticmethod
    def create_pipeline_template(
        num_stages: int = 4,
        model_name: str = "gpt-4"
    ) -> ArchitectureModel:
        """Create a pipeline architecture template with sequential processing stages.
        
        Args:
            num_stages: Number of pipeline stages
            model_name: Base model name for agents
            
        Returns:
            Pipeline architecture model
        """
        # Create architecture
        architecture = ArchitectureModel(
            id=str(uuid.uuid4()),
            name="Pipeline Architecture",
            description="A pipeline architecture with sequential processing stages",
            agents=[],
            connections=[]
        )
        
        # Create stage roles and capabilities
        stage_configs = [
            (AgentRole.PLANNER, [AgentCapability.PLANNING, AgentCapability.REQUIREMENTS_ANALYSIS]),
            (AgentRole.RESEARCHER, [AgentCapability.INFORMATION_RETRIEVAL, AgentCapability.RESEARCH]),
            (AgentRole.CODER, [AgentCapability.CODE_GENERATION, AgentCapability.DEBUGGING]),
            (AgentRole.CRITIC, [AgentCapability.QUALITY_ASSESSMENT, AgentCapability.TESTING]),  # Changed from EVALUATION
            (AgentRole.WRITER, [AgentCapability.DOCUMENTATION, AgentCapability.CONTENT_GENERATION])
        ]
        
        # Create agents for each stage
        for i in range(min(num_stages, len(stage_configs))):
            role, capabilities = stage_configs[i]
            
            agent = AgentModel(
                id=str(uuid.uuid4()),
                name=f"Stage {i+1}: {role.name.capitalize()}",
                description=f"Pipeline stage {i+1} with {role.name} capabilities",
                role=role,
                capabilities=capabilities,
                model_name=model_name,
                parameters={"temperature": 0.7, "max_tokens": 1000}
            )
            architecture.agents.append(agent)
        
        # Create connections between adjacent stages
        for i in range(len(architecture.agents) - 1):
            # Create connection from current stage to next stage
            connection = ConnectionModel(
                id=str(uuid.uuid4()),
                source_id=architecture.agents[i].id,
                target_id=architecture.agents[i+1].id,
                bidirectional=False,  # Pipeline is unidirectional
                weight=1.0
            )
            architecture.connections.append(connection)
            
            # Create feedback connection from next stage to current stage
            feedback_connection = ConnectionModel(
                id=str(uuid.uuid4()),
                source_id=architecture.agents[i+1].id,
                target_id=architecture.agents[i].id,
                bidirectional=False,
                weight=0.5  # Lower weight for feedback
            )
            architecture.connections.append(feedback_connection)
        
        return architecture
    
    @staticmethod
    def create_hybrid_template(
        model_name: str = "gpt-4"
    ) -> ArchitectureModel:
        """Create a hybrid architecture template combining hierarchical and specialist patterns.
        
        Args:
            model_name: Base model name for agents
            
        Returns:
            Hybrid architecture model
        """
        # Create architecture
        architecture = ArchitectureModel(
            id=str(uuid.uuid4()),
            name="Hybrid Architecture",
            description="A hybrid architecture combining hierarchical and specialist patterns",
            agents=[],
            connections=[]
        )
        
        # Create coordinator agent
        coordinator = AgentModel(
            id=str(uuid.uuid4()),
            name="Project Coordinator",
            description="Top-level coordinator that manages the entire project",
            role=AgentRole.COORDINATOR,
            capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.DELEGATION,
                AgentCapability.DECISION_MAKING,
                AgentCapability.COORDINATION
            ],
            model_name=model_name,
            parameters={"temperature": 0.7, "max_tokens": 1000}
        )
        architecture.agents.append(coordinator)
        
        # Create department managers
        departments = [
            ("Research", AgentRole.MANAGER, [AgentCapability.RESEARCH, AgentCapability.COORDINATION]),
            ("Development", AgentRole.MANAGER, [AgentCapability.CODE_GENERATION, AgentCapability.COORDINATION]),
            ("Quality", AgentRole.MANAGER, [AgentCapability.QUALITY_ASSESSMENT, AgentCapability.COORDINATION])  # Changed from EVALUATION
        ]
        
        managers = []
        for dept_name, role, capabilities in departments:
            manager = AgentModel(
                id=str(uuid.uuid4()),
                name=f"{dept_name} Manager",
                description=f"Manager for the {dept_name} department",
                role=role,
                capabilities=capabilities,
                model_name=model_name,
                parameters={"temperature": 0.7, "max_tokens": 1000}
            )
            architecture.agents.append(manager)
            managers.append(manager)
            
            # Connect coordinator to manager
            connection = ConnectionModel(
                id=str(uuid.uuid4()),
                source_id=coordinator.id,
                target_id=manager.id,
                bidirectional=True,
                weight=1.0
            )
            architecture.connections.append(connection)
        
        # Create specialists under each manager
        specialists = [
            # Research department specialists
            (managers[0].id, "Information Retrieval", AgentRole.RESEARCHER, [AgentCapability.INFORMATION_RETRIEVAL]),
            (managers[0].id, "Domain Expert", AgentRole.SPECIALIST, [AgentCapability.DOMAIN_EXPERTISE]),
            
            # Development department specialists
            (managers[1].id, "Code Generator", AgentRole.CODER, [AgentCapability.CODE_GENERATION]),
            (managers[1].id, "Debugger", AgentRole.CODER, [AgentCapability.DEBUGGING]),
            
            # Quality department specialists
            (managers[2].id, "Tester", AgentRole.CRITIC, [AgentCapability.TESTING]),
            (managers[2].id, "Reviewer", AgentRole.CRITIC, [AgentCapability.FEEDBACK])
        ]
        
        for manager_id, name, role, capabilities in specialists:
            specialist = AgentModel(
                id=str(uuid.uuid4()),
                name=name,
                description=f"Specialist with {role.name} capabilities",
                role=role,
                capabilities=capabilities,
                model_name=model_name,
                parameters={"temperature": 0.7, "max_tokens": 1000}
            )
            architecture.agents.append(specialist)
            
            # Connect manager to specialist
            connection = ConnectionModel(
                id=str(uuid.uuid4()),
                source_id=manager_id,
                target_id=specialist.id,
                bidirectional=True,
                weight=1.0
            )
            architecture.connections.append(connection)
        
        return architecture
