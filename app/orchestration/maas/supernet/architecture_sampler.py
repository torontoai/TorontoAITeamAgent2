"""
Architecture sampler for Multi-agent Architecture Search (MaAS).

This module provides functionality for sampling architectures from the search space
based on templates and constraints.
"""

from typing import List, Optional, Dict, Any, Tuple, Set
import random
import numpy as np
import logging

from ..models import (
    ArchitectureModel, AgentModel, ConnectionModel, SearchSpace, 
    TaskModel, AgentRole, AgentCapability
)

logger = logging.getLogger(__name__)

class ArchitectureSampler:
    """Samples architectures from the search space based on templates and constraints."""
    
    def __init__(self, search_space: SearchSpace):
        """Initialize the architecture sampler.
        
        Args:
            search_space: SearchSpace defining the architecture constraints
        """
        self.search_space = search_space
    
    def sample_from_template(self, template: ArchitectureModel, task: TaskModel, 
                            mutation_rate: float = 0.2) -> ArchitectureModel:
        """Sample an architecture by mutating a template.
        
        Args:
            template: Template architecture to base the sample on
            task: TaskModel describing the task requirements
            mutation_rate: Rate of mutation to apply (0.0 to 1.0)
            
        Returns:
            New ArchitectureModel sampled from the template
        """
        # Create a copy of the template
        architecture = self._copy_architecture(template)
        
        # Apply mutations based on mutation rate
        if random.random() < mutation_rate:
            self._mutate_agents(architecture, task)
        
        if random.random() < mutation_rate:
            self._mutate_connections(architecture)
        
        # Ensure the architecture meets the task requirements
        self._ensure_task_requirements(architecture, task)
        
        # Generate a new name for the architecture
        architecture.name = f"Sampled_{template.name}_{random.randint(1000, 9999)}"
        architecture.id = None  # Will be assigned when saved
        
        logger.debug(f"Sampled architecture '{architecture.name}' from template '{template.name}'")
        return architecture
    
    def sample_random(self, task: TaskModel, complexity: float = 0.5) -> ArchitectureModel:
        """Sample a completely random architecture.
        
        Args:
            task: TaskModel describing the task requirements
            complexity: Complexity factor (0.0 to 1.0) affecting the size and connectivity
            
        Returns:
            New random ArchitectureModel
        """
        # Determine number of agents based on complexity
        min_agents = max(1, self.search_space.min_agents)
        max_agents = self.search_space.max_agents  # Use exact max_agents from search space, don't cap at 20
        
        # Scale number of agents with complexity
        num_agents = int(min_agents + (max_agents - min_agents) * complexity)
        num_agents = max(min_agents, min(max_agents, num_agents))
        
        # Create architecture
        architecture = ArchitectureModel(
            name=f"Random_Architecture_{random.randint(1000, 9999)}",
            agents=[],
            connections=[]
        )
        
        # Add agents
        for i in range(num_agents):
            agent = self._create_random_agent(i, task)
            architecture.agents.append(agent)
        
        # Add connections based on complexity
        self._add_random_connections(architecture, complexity)
        
        # Ensure the architecture meets the task requirements
        self._ensure_task_requirements(architecture, task)
        
        logger.debug(f"Sampled random architecture '{architecture.name}' with {num_agents} agents")
        return architecture
    
    def crossover(self, parent1: ArchitectureModel, parent2: ArchitectureModel, 
                 task: TaskModel) -> ArchitectureModel:
        """Create a new architecture by crossing over two parent architectures.
        
        Args:
            parent1: First parent architecture
            parent2: Second parent architecture
            task: TaskModel describing the task requirements
            
        Returns:
            New ArchitectureModel created by crossover
        """
        # Create a new architecture
        child = ArchitectureModel(
            name=f"Crossover_{parent1.name}_{parent2.name}_{random.randint(1000, 9999)}",
            agents=[],
            connections=[]
        )
        
        # Determine which agents to inherit from each parent
        parent1_agents = {agent.id: agent for agent in parent1.agents}
        parent2_agents = {agent.id: agent for agent in parent2.agents}
        
        # Map from parent agent IDs to child agent IDs
        id_mapping = {}
        
        # Inherit agents from both parents, but respect max_agents limit
        max_agents = self.search_space.max_agents
        
        # First try to inherit from parent1
        for agent_id, agent in parent1_agents.items():
            if len(child.agents) >= max_agents:
                break
                
            if random.random() < 0.5:  # 50% chance to inherit from parent1
                new_agent = self._copy_agent(agent)
                new_agent.id = f"agent_{len(child.agents)}"
                child.agents.append(new_agent)
                id_mapping[agent_id] = new_agent.id
        
        # Then try to inherit from parent2
        for agent_id, agent in parent2_agents.items():
            if len(child.agents) >= max_agents:
                break
                
            if agent_id not in id_mapping:  # Only consider agents not already inherited
                if random.random() < 0.5:  # 50% chance to inherit from parent2
                    new_agent = self._copy_agent(agent)
                    new_agent.id = f"agent_{len(child.agents)}"
                    child.agents.append(new_agent)
                    id_mapping[agent_id] = new_agent.id
        
        # Ensure at least one agent
        if not child.agents:
            # Choose a random agent from either parent
            parent = random.choice([parent1, parent2])
            agent = random.choice(parent.agents)
            new_agent = self._copy_agent(agent)
            new_agent.id = "agent_0"
            child.agents.append(new_agent)
            id_mapping[agent.id] = new_agent.id
        
        # Inherit connections
        self._inherit_connections(child, parent1, parent2, id_mapping)
        
        # Ensure the architecture meets the task requirements
        self._ensure_task_requirements(child, task)
        
        logger.debug(f"Created crossover architecture '{child.name}' with {len(child.agents)} agents")
        return child
    
    def mutate(self, architecture: ArchitectureModel, task: TaskModel, 
              mutation_rate: float = 0.3) -> ArchitectureModel:
        """Create a new architecture by mutating an existing one.
        
        Args:
            architecture: Architecture to mutate
            task: TaskModel describing the task requirements
            mutation_rate: Rate of mutation to apply (0.0 to 1.0)
            
        Returns:
            New ArchitectureModel created by mutation
        """
        # Create a copy of the architecture
        mutated = self._copy_architecture(architecture)
        mutated.name = f"Mutated_{architecture.name}_{random.randint(1000, 9999)}"
        
        # Apply mutations based on mutation rate
        mutations_applied = 0
        
        # Potentially add a new agent
        if random.random() < mutation_rate and len(mutated.agents) < self.search_space.max_agents:
            new_agent = self._create_random_agent(len(mutated.agents), task)
            mutated.agents.append(new_agent)
            mutations_applied += 1
            
            # Add some connections to the new agent
            for agent in mutated.agents:
                if agent.id != new_agent.id and random.random() < 0.3:
                    connection = ConnectionModel(
                        source_id=agent.id,
                        target_id=new_agent.id,
                        weight=random.uniform(0.1, 1.0),
                        bidirectional=random.random() < 0.5
                    )
                    mutated.connections.append(connection)
                    mutations_applied += 1
        
        # Potentially remove an agent
        if random.random() < mutation_rate and len(mutated.agents) > self.search_space.min_agents:
            agent_to_remove = random.choice(mutated.agents)
            mutated.agents = [a for a in mutated.agents if a.id != agent_to_remove.id]
            mutated.connections = [c for c in mutated.connections 
                                  if c.source_id != agent_to_remove.id and c.target_id != agent_to_remove.id]
            mutations_applied += 1
        
        # Mutate existing agents
        for agent in mutated.agents:
            if random.random() < mutation_rate:
                self._mutate_agent(agent, task)
                mutations_applied += 1
        
        # Mutate connections
        self._mutate_connections(mutated, mutation_rate)
        mutations_applied += 1
        
        # If no mutations were applied, force at least one
        if mutations_applied == 0:
            if len(mutated.agents) > 0:
                agent = random.choice(mutated.agents)
                self._mutate_agent(agent, task)
            else:
                # Add a new agent if there are none
                new_agent = self._create_random_agent(0, task)
                mutated.agents.append(new_agent)
        
        # Ensure the architecture meets the task requirements
        self._ensure_task_requirements(mutated, task)
        
        logger.debug(f"Created mutated architecture '{mutated.name}' with {len(mutated.agents)} agents")
        return mutated
    
    def _copy_architecture(self, architecture: ArchitectureModel) -> ArchitectureModel:
        """Create a deep copy of an architecture.
        
        Args:
            architecture: Architecture to copy
            
        Returns:
            New copy of the architecture
        """
        return ArchitectureModel(
            name=architecture.name,
            description=architecture.description,
            agents=[self._copy_agent(agent) for agent in architecture.agents],
            connections=[self._copy_connection(conn) for conn in architecture.connections]
        )
    
    def _copy_agent(self, agent: AgentModel) -> AgentModel:
        """Create a deep copy of an agent.
        
        Args:
            agent: Agent to copy
            
        Returns:
            New copy of the agent
        """
        return AgentModel(
            id=agent.id,
            name=agent.name,
            role=agent.role,
            model_name=agent.model_name,
            capabilities=agent.capabilities.copy() if agent.capabilities else [],
            parameters=agent.parameters.copy() if agent.parameters else {}
        )
    
    def _copy_connection(self, connection: ConnectionModel) -> ConnectionModel:
        """Create a deep copy of a connection.
        
        Args:
            connection: Connection to copy
            
        Returns:
            New copy of the connection
        """
        return ConnectionModel(
            source_id=connection.source_id,
            target_id=connection.target_id,
            weight=connection.weight,
            bidirectional=connection.bidirectional,
            parameters=connection.parameters.copy() if connection.parameters else {}
        )
    
    def _create_random_agent(self, index: int, task: TaskModel) -> AgentModel:
        """Create a random agent.
        
        Args:
            index: Index of the agent in the architecture
            task: TaskModel describing the task requirements
            
        Returns:
            New random AgentModel
        """
        # Choose a random role
        role = random.choice(list(AgentRole))
        
        # Generate a name based on the role
        name = f"{role.value.capitalize()} Agent {index+1}"
        
        # Choose capabilities based on the role and task
        capabilities = self._select_capabilities_for_role(role, task)
        
        # Choose a model name based on the role
        model_name = self._select_model_for_role(role)
        
        return AgentModel(
            id=f"agent_{index}",
            name=name,
            role=role,
            model_name=model_name,
            capabilities=capabilities,
            parameters={}
        )
    
    def _select_capabilities_for_role(self, role: AgentRole, task: TaskModel) -> List[AgentCapability]:
        """Select appropriate capabilities for an agent based on its role and the task.
        
        Args:
            role: Role of the agent
            task: TaskModel describing the task requirements
            
        Returns:
            List of capabilities for the agent
        """
        # Define role-specific capabilities
        role_capabilities = {
            AgentRole.COORDINATOR: [
                AgentCapability.PLANNING,
                AgentCapability.DELEGATION,
                AgentCapability.MONITORING
            ],
            AgentRole.EXECUTOR: [
                AgentCapability.TOOL_USE,
                AgentCapability.CODE_EXECUTION,
                AgentCapability.ACTION_EXECUTION
            ],
            AgentRole.PLANNER: [
                AgentCapability.PLANNING,
                AgentCapability.GOAL_DECOMPOSITION,
                AgentCapability.STRATEGY_FORMULATION
            ],
            AgentRole.RESEARCHER: [
                AgentCapability.INFORMATION_RETRIEVAL,
                AgentCapability.KNOWLEDGE_INTEGRATION,
                AgentCapability.FACT_CHECKING
            ],
            AgentRole.CRITIC: [
                AgentCapability.QUALITY_ASSESSMENT,  # Changed from EVALUATION
                AgentCapability.FEEDBACK,
                AgentCapability.ERROR_DETECTION
            ],
            AgentRole.MEMORY: [
                AgentCapability.INFORMATION_STORAGE,
                AgentCapability.INFORMATION_RETRIEVAL,
                AgentCapability.CONTEXT_MANAGEMENT
            ],
            AgentRole.REASONER: [
                AgentCapability.LOGICAL_REASONING,
                AgentCapability.PROBLEM_SOLVING,
                AgentCapability.DECISION_MAKING
            ],
            AgentRole.GENERATOR: [
                AgentCapability.CONTENT_GENERATION,
                AgentCapability.CREATIVITY,
                AgentCapability.SUMMARIZATION
            ],
            AgentRole.EVALUATOR: [
                AgentCapability.QUALITY_ASSESSMENT,  # Changed from EVALUATION
                AgentCapability.QUALITY_ASSESSMENT,
                AgentCapability.PERFORMANCE_MONITORING
            ],
            AgentRole.COMMUNICATOR: [
                AgentCapability.NATURAL_LANGUAGE_PROCESSING,
                AgentCapability.DIALOGUE_MANAGEMENT,
                AgentCapability.EXPLANATION
            ],
            AgentRole.SPECIALIST: [
                AgentCapability.DOMAIN_EXPERTISE,
                AgentCapability.SPECIALIZED_KNOWLEDGE,
                AgentCapability.TECHNICAL_SKILLS
            ],
            AgentRole.CUSTOM: [
                random.choice(list(AgentCapability)),
                random.choice(list(AgentCapability)),
                random.choice(list(AgentCapability))
            ]
        }
        
        # Get base capabilities for the role
        capabilities = role_capabilities.get(role, [])
        
        # Add some task-specific capabilities if available
        if task.required_capabilities:
            for capability in task.required_capabilities:
                if capability not in capabilities and random.random() < 0.5:
                    capabilities.append(capability)
        
        # Ensure we don't exceed the maximum capabilities per agent
        max_capabilities = min(10, len(list(AgentCapability)))
        if len(capabilities) > max_capabilities:
            capabilities = random.sample(capabilities, max_capabilities)
        
        return capabilities
    
    def _select_model_for_role(self, role: AgentRole) -> str:
        """Select an appropriate model for an agent based on its role.
        
        Args:
            role: Role of the agent
            
        Returns:
            Model name for the agent
        """
        # Define role-specific models
        role_models = {
            AgentRole.COORDINATOR: ["gpt-4", "claude-3-opus", "gemini-pro"],
            AgentRole.EXECUTOR: ["gpt-3.5-turbo", "claude-3-haiku", "gemini-flash"],
            AgentRole.PLANNER: ["gpt-4", "claude-3-opus", "gemini-pro"],
            AgentRole.RESEARCHER: ["gpt-4", "claude-3-sonnet", "gemini-pro"],
            AgentRole.CRITIC: ["gpt-4", "claude-3-opus", "gemini-pro"],
            AgentRole.MEMORY: ["gpt-3.5-turbo", "claude-3-haiku", "gemini-flash"],
            AgentRole.REASONER: ["gpt-4", "claude-3-opus", "gemini-pro"],
            AgentRole.GENERATOR: ["gpt-3.5-turbo", "claude-3-sonnet", "gemini-pro"],
            AgentRole.EVALUATOR: ["gpt-4", "claude-3-opus", "gemini-pro"],
            AgentRole.COMMUNICATOR: ["gpt-3.5-turbo", "claude-3-haiku", "gemini-flash"],
            AgentRole.SPECIALIST: ["gpt-4", "claude-3-opus", "gemini-pro"],
            AgentRole.CUSTOM: ["gpt-3.5-turbo", "claude-3-haiku", "gemini-flash"]
        }
        
        # Get models for the role
        models = role_models.get(role, ["gpt-3.5-turbo"])
        
        # Choose a random model from the list
        return random.choice(models)
    
    def _mutate_agent(self, agent: AgentModel, task: TaskModel) -> None:
        """Mutate an agent's properties.
        
        Args:
            agent: Agent to mutate
            task: TaskModel describing the task requirements
        """
        # Choose a random mutation
        mutation_type = random.choice(["role", "model", "capabilities"])
        
        if mutation_type == "role":
            # Change the agent's role
            new_role = random.choice(list(AgentRole))
            agent.role = new_role
            
            # Update capabilities based on new role
            agent.capabilities = self._select_capabilities_for_role(new_role, task)
            
            # Update model based on new role
            agent.model_name = self._select_model_for_role(new_role)
            
            # Update name based on new role
            agent.name = f"{new_role.value.capitalize()} Agent"
            
        elif mutation_type == "model":
            # Change the agent's model
            agent.model_name = self._select_model_for_role(agent.role)
            
        elif mutation_type == "capabilities":
            # Modify the agent's capabilities
            if random.random() < 0.5 and agent.capabilities:
                # Remove a capability
                agent.capabilities.remove(random.choice(agent.capabilities))
            else:
                # Add a capability
                all_capabilities = list(AgentCapability)
                new_capability = random.choice(all_capabilities)
                if new_capability not in agent.capabilities:
                    agent.capabilities.append(new_capability)
    
    def _mutate_agents(self, architecture: ArchitectureModel, task: TaskModel) -> None:
        """Mutate agents in an architecture.
        
        Args:
            architecture: Architecture to mutate
            task: TaskModel describing the task requirements
        """
        # Potentially add a new agent
        if len(architecture.agents) < self.search_space.max_agents and random.random() < 0.3:
            new_agent = self._create_random_agent(len(architecture.agents), task)
            architecture.agents.append(new_agent)
            
            # Add some connections to the new agent
            for agent in architecture.agents:
                if agent.id != new_agent.id and random.random() < 0.3:
                    connection = ConnectionModel(
                        source_id=agent.id,
                        target_id=new_agent.id,
                        weight=random.uniform(0.1, 1.0),
                        bidirectional=random.random() < 0.5
                    )
                    architecture.connections.append(connection)
        
        # Potentially remove an agent
        if len(architecture.agents) > self.search_space.min_agents and random.random() < 0.2:
            agent_to_remove = random.choice(architecture.agents)
            architecture.agents = [a for a in architecture.agents if a.id != agent_to_remove.id]
            architecture.connections = [c for c in architecture.connections 
                                      if c.source_id != agent_to_remove.id and c.target_id != agent_to_remove.id]
        
        # Mutate existing agents
        for agent in architecture.agents:
            if random.random() < 0.3:
                self._mutate_agent(agent, task)
    
    def _mutate_connections(self, architecture: ArchitectureModel, mutation_rate: float = 0.3) -> None:
        """Mutate connections in an architecture.
        
        Args:
            architecture: Architecture to mutate
            mutation_rate: Rate of mutation to apply (0.0 to 1.0)
        """
        # Get all agent IDs
        agent_ids = [agent.id for agent in architecture.agents]
        
        # Potentially add a new connection
        if random.random() < mutation_rate:
            # Choose random source and target agents
            if len(agent_ids) >= 2:
                source_id = random.choice(agent_ids)
                target_id = random.choice([aid for aid in agent_ids if aid != source_id])
                
                # Check if connection already exists
                connection_exists = any(
                    c.source_id == source_id and c.target_id == target_id
                    for c in architecture.connections
                )
                
                if not connection_exists:
                    connection = ConnectionModel(
                        source_id=source_id,
                        target_id=target_id,
                        weight=random.uniform(0.1, 1.0),
                        bidirectional=random.random() < 0.5
                    )
                    architecture.connections.append(connection)
        
        # Potentially remove a connection
        if architecture.connections and random.random() < mutation_rate:
            connection_to_remove = random.choice(architecture.connections)
            architecture.connections = [c for c in architecture.connections if c != connection_to_remove]
        
        # Mutate existing connections
        for connection in architecture.connections:
            if random.random() < mutation_rate:
                # Modify weight
                connection.weight = random.uniform(0.1, 1.0)
                
                # Potentially flip bidirectionality
                if random.random() < 0.3:
                    connection.bidirectional = not connection.bidirectional
    
    def _add_random_connections(self, architecture: ArchitectureModel, complexity: float) -> None:
        """Add random connections to an architecture.
        
        Args:
            architecture: Architecture to add connections to
            complexity: Complexity factor (0.0 to 1.0) affecting the connectivity
        """
        # Get all agent IDs
        agent_ids = [agent.id for agent in architecture.agents]
        
        # Determine number of connections based on complexity
        max_connections = len(agent_ids) * (len(agent_ids) - 1)
        num_connections = int(max_connections * complexity * 0.5)  # Use 50% of max at full complexity
        
        # Add random connections
        for _ in range(num_connections):
            if len(agent_ids) < 2:
                break
                
            # Choose random source and target agents
            source_id = random.choice(agent_ids)
            target_id = random.choice([aid for aid in agent_ids if aid != source_id])
            
            # Check if connection already exists
            connection_exists = any(
                c.source_id == source_id and c.target_id == target_id
                for c in architecture.connections
            )
            
            if not connection_exists:
                connection = ConnectionModel(
                    source_id=source_id,
                    target_id=target_id,
                    weight=random.uniform(0.1, 1.0),
                    bidirectional=random.random() < 0.3  # 30% chance of bidirectional
                )
                architecture.connections.append(connection)
    
    def _inherit_connections(self, child: ArchitectureModel, parent1: ArchitectureModel, 
                           parent2: ArchitectureModel, id_mapping: Dict[str, str]) -> None:
        """Inherit connections from parent architectures.
        
        Args:
            child: Child architecture to add connections to
            parent1: First parent architecture
            parent2: Second parent architecture
            id_mapping: Mapping from parent agent IDs to child agent IDs
        """
        # Get all agent IDs in the child
        child_agent_ids = [agent.id for agent in child.agents]
        
        # Inherit connections from parent1
        for connection in parent1.connections:
            # Check if both source and target agents were inherited
            if connection.source_id in id_mapping and connection.target_id in id_mapping:
                child_source_id = id_mapping[connection.source_id]
                child_target_id = id_mapping[connection.target_id]
                
                # Create a new connection
                child_connection = ConnectionModel(
                    source_id=child_source_id,
                    target_id=child_target_id,
                    weight=connection.weight,
                    bidirectional=connection.bidirectional,
                    parameters=connection.parameters.copy() if connection.parameters else {}
                )
                
                child.connections.append(child_connection)
        
        # Inherit connections from parent2
        for connection in parent2.connections:
            # Check if both source and target agents were inherited
            if connection.source_id in id_mapping and connection.target_id in id_mapping:
                child_source_id = id_mapping[connection.source_id]
                child_target_id = id_mapping[connection.target_id]
                
                # Check if connection already exists
                connection_exists = any(
                    c.source_id == child_source_id and c.target_id == child_target_id
                    for c in child.connections
                )
                
                if not connection_exists:
                    # Create a new connection
                    child_connection = ConnectionModel(
                        source_id=child_source_id,
                        target_id=child_target_id,
                        weight=connection.weight,
                        bidirectional=connection.bidirectional,
                        parameters=connection.parameters.copy() if connection.parameters else {}
                    )
                    
                    child.connections.append(child_connection)
        
        # Ensure all agents have at least one connection
        for agent_id in child_agent_ids:
            has_connection = any(
                c.source_id == agent_id or c.target_id == agent_id
                for c in child.connections
            )
            
            if not has_connection and len(child_agent_ids) > 1:
                # Connect to a random other agent
                other_id = random.choice([aid for aid in child_agent_ids if aid != agent_id])
                
                connection = ConnectionModel(
                    source_id=agent_id,
                    target_id=other_id,
                    weight=random.uniform(0.1, 1.0),
                    bidirectional=random.random() < 0.5
                )
                
                child.connections.append(connection)
    
    def _ensure_task_requirements(self, architecture: ArchitectureModel, task: TaskModel) -> None:
        """Ensure the architecture meets the task requirements.
        
        Args:
            architecture: Architecture to check and modify
            task: TaskModel describing the task requirements
        """
        # Check for required roles (if task has this attribute)
        # TaskModel doesn't have required_roles attribute, so we need to check if it exists in parameters
        required_roles = []
        if hasattr(task, 'parameters') and task.parameters and 'required_roles' in task.parameters:
            required_roles = task.parameters.get('required_roles', [])
            
            existing_roles = {agent.role for agent in architecture.agents}
            
            for role_str in required_roles:
                try:
                    # Convert string to AgentRole enum if needed
                    role = role_str if isinstance(role_str, AgentRole) else AgentRole(role_str)
                    
                    if role not in existing_roles:
                        # Add an agent with the required role
                        new_agent = AgentModel(
                            id=f"agent_{len(architecture.agents)}",
                            name=f"{role.value.capitalize()} Agent",
                            role=role,
                            model_name=self._select_model_for_role(role),
                            capabilities=self._select_capabilities_for_role(role, task),
                            parameters={}
                        )
                        
                        architecture.agents.append(new_agent)
                        
                        # Connect to existing agents
                        for agent in architecture.agents:
                            if agent.id != new_agent.id and random.random() < 0.5:
                                connection = ConnectionModel(
                                    source_id=agent.id,
                                    target_id=new_agent.id,
                                    weight=random.uniform(0.1, 1.0),
                                    bidirectional=random.random() < 0.5
                                )
                                architecture.connections.append(connection)
                except (ValueError, KeyError):
                    # Skip invalid role values
                    logger.warning(f"Skipping invalid role value: {role_str}")
        
        # Ensure required capabilities are present
        if task.required_capabilities:
            existing_capabilities = set()
            for agent in architecture.agents:
                if agent.capabilities:
                    existing_capabilities.update(agent.capabilities)
            
            for capability in task.required_capabilities:
                if capability not in existing_capabilities:
                    # Add the capability to a random agent
                    if architecture.agents:
                        agent = random.choice(architecture.agents)
                        if not agent.capabilities:
                            agent.capabilities = []
                        agent.capabilities.append(capability)
        
        # Ensure the architecture has at least one agent
        if not architecture.agents:
            new_agent = self._create_random_agent(0, task)
            architecture.agents.append(new_agent)
        
        # Ensure the architecture doesn't exceed max_agents
        if len(architecture.agents) > self.search_space.max_agents:
            # Remove excess agents
            excess = len(architecture.agents) - self.search_space.max_agents
            agents_to_remove = random.sample(architecture.agents, excess)
            
            for agent in agents_to_remove:
                architecture.agents.remove(agent)
                architecture.connections = [c for c in architecture.connections 
                                          if c.source_id != agent.id and c.target_id != agent.id]
        
        # Ensure all agents have valid IDs
        for i, agent in enumerate(architecture.agents):
            agent.id = f"agent_{i}"
        
        # Update connection IDs to match agent IDs
        agent_ids = {agent.id for agent in architecture.agents}
        architecture.connections = [c for c in architecture.connections 
                                  if c.source_id in agent_ids and c.target_id in agent_ids]
