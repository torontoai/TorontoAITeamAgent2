"""
Core algorithms for Multi-agent Architecture Search (MaAS).

This module provides the algorithms used for searching optimal agent architectures,
including evolutionary algorithms, neural architecture search, and other approaches.
"""

from typing import Dict, List, Any, Optional, Tuple, Callable, Set
import random
import time
import copy
import math
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..maas.models import (
    ArchitectureModel, AgentModel, ConnectionModel, SearchSpace,
    EvaluationResult, SearchResult, TaskModel, AgentRole, CommunicationPattern
)
from ..maas.config import get_config

logger = logging.getLogger(__name__)


class EvolutionarySearch:
    """Evolutionary algorithm for architecture search."""
    
    def __init__(
        self,
        search_space: SearchSpace,
        task: TaskModel,
        evaluation_function: Callable[[ArchitectureModel, TaskModel], EvaluationResult],
        population_size: Optional[int] = None,
        generations: Optional[int] = None,
        mutation_rate: Optional[float] = None,
        crossover_rate: Optional[float] = None,
        tournament_size: Optional[int] = None,
        elitism_count: Optional[int] = None,
        early_stopping_patience: Optional[int] = None,
        parallel_evaluations: Optional[int] = None
    ):
        """Initialize the evolutionary search algorithm.
        
        Args:
            search_space: The search space to explore
            task: The task for which to search architectures
            evaluation_function: Function to evaluate architectures
            population_size: Size of the population
            generations: Number of generations
            mutation_rate: Probability of mutation
            crossover_rate: Probability of crossover
            tournament_size: Size of tournament for selection
            elitism_count: Number of top individuals to preserve
            early_stopping_patience: Generations without improvement before stopping
            parallel_evaluations: Number of parallel evaluations to run
        """
        self.search_space = search_space
        self.task = task
        self.evaluation_function = evaluation_function
        
        # Get configuration
        config = get_config().search_parameters
        
        # Set parameters from arguments or config
        self.population_size = population_size or config.population_size
        self.generations = generations or config.generations
        self.mutation_rate = mutation_rate or config.mutation_rate
        self.crossover_rate = crossover_rate or config.crossover_rate
        self.tournament_size = tournament_size or config.tournament_size
        self.elitism_count = elitism_count or config.elitism_count
        self.early_stopping_patience = early_stopping_patience or config.early_stopping_patience
        self.parallel_evaluations = parallel_evaluations or config.parallel_evaluations
        
        # Initialize population and results
        self.population: List[ArchitectureModel] = []
        self.fitness_cache: Dict[str, float] = {}
        self.best_architecture: Optional[ArchitectureModel] = None
        self.best_fitness: float = float('-inf')
        self.generations_without_improvement: int = 0
    
    def initialize_population(self) -> None:
        """Initialize the population with random architectures."""
        self.population = []
        for i in range(self.population_size):
            architecture = self._generate_random_architecture(
                f"Architecture_{i}",
                f"Randomly generated architecture {i}"
            )
            self.population.append(architecture)
    
    def _generate_random_architecture(self, name: str, description: str) -> ArchitectureModel:
        """Generate a random architecture within the search space.
        
        Args:
            name: Name for the architecture
            description: Description for the architecture
            
        Returns:
            A randomly generated architecture
        """
        # Determine number of agents
        num_agents = random.randint(
            self.search_space.min_agents,
            self.search_space.max_agents
        )
        
        # Create agents
        agents = []
        for i in range(num_agents):
            # Ensure required roles are included
            if i < len(self.search_space.required_roles):
                role = self.search_space.required_roles[i]
            else:
                role = random.choice(self.search_space.allowed_agent_roles)
            
            # Random capabilities
            num_capabilities = random.randint(1, 5)
            capabilities = random.sample(
                self.search_space.allowed_agent_capabilities,
                min(num_capabilities, len(self.search_space.allowed_agent_capabilities))
            )
            
            agent = AgentModel(
                name=f"Agent_{i}",
                role=role,
                capabilities=capabilities,
                model_name=random.choice(["gpt-4", "llama-3", "claude-3", "gemini-pro"]),
                parameters={}
            )
            agents.append(agent)
        
        # Create connections
        connections = []
        agent_ids = [agent.id for agent in agents]
        
        # Determine number of connections
        max_possible_connections = num_agents * (num_agents - 1)
        num_connections = random.randint(
            min(self.search_space.min_connections, max_possible_connections),
            min(self.search_space.max_connections, max_possible_connections)
        )
        
        # Create random connections
        connection_pairs = set()
        for _ in range(num_connections):
            # Avoid duplicate connections
            for _ in range(100):  # Limit attempts to avoid infinite loop
                source_id = random.choice(agent_ids)
                target_id = random.choice(agent_ids)
                if source_id != target_id and (source_id, target_id) not in connection_pairs:
                    connection_pairs.add((source_id, target_id))
                    break
        
        for source_id, target_id in connection_pairs:
            bidirectional = random.random() < 0.3  # 30% chance of bidirectional
            connection = ConnectionModel(
                source_id=source_id,
                target_id=target_id,
                bidirectional=bidirectional,
                weight=random.uniform(0.1, 1.0),
                parameters={}
            )
            connections.append(connection)
        
        # Choose a communication pattern
        communication_pattern = random.choice(self.search_space.allowed_communication_patterns)
        
        # Create the architecture
        architecture = ArchitectureModel(
            name=name,
            description=description,
            agents=agents,
            connections=connections,
            communication_pattern=communication_pattern,
            parameters={}
        )
        
        return architecture
    
    def evaluate_population(self) -> List[Tuple[ArchitectureModel, float]]:
        """Evaluate all architectures in the population.
        
        Returns:
            List of (architecture, fitness) tuples
        """
        results = []
        
        # Use parallel evaluation if enabled
        if self.parallel_evaluations > 1:
            with ThreadPoolExecutor(max_workers=self.parallel_evaluations) as executor:
                future_to_arch = {
                    executor.submit(self._evaluate_architecture, arch): arch
                    for arch in self.population
                }
                for future in as_completed(future_to_arch):
                    arch = future_to_arch[future]
                    try:
                        fitness = future.result()
                        results.append((arch, fitness))
                    except Exception as e:
                        logger.error(f"Error evaluating architecture {arch.id}: {e}")
                        results.append((arch, float('-inf')))
        else:
            # Sequential evaluation
            for arch in self.population:
                try:
                    fitness = self._evaluate_architecture(arch)
                    results.append((arch, fitness))
                except Exception as e:
                    logger.error(f"Error evaluating architecture {arch.id}: {e}")
                    results.append((arch, float('-inf')))
        
        return results
    
    def _evaluate_architecture(self, architecture: ArchitectureModel) -> float:
        """Evaluate a single architecture.
        
        Args:
            architecture: The architecture to evaluate
            
        Returns:
            Fitness score for the architecture
        """
        # Check if architecture is valid
        is_valid, reason = self.search_space.is_valid_architecture(architecture)
        if not is_valid:
            logger.warning(f"Invalid architecture {architecture.id}: {reason}")
            return float('-inf')
        
        # Check if already evaluated
        if architecture.id in self.fitness_cache:
            return self.fitness_cache[architecture.id]
        
        # Evaluate the architecture
        evaluation_result = self.evaluation_function(architecture, self.task)
        fitness = evaluation_result.overall_fitness
        
        # Cache the result
        self.fitness_cache[architecture.id] = fitness
        
        return fitness
    
    def selection(self, evaluated_population: List[Tuple[ArchitectureModel, float]]) -> List[ArchitectureModel]:
        """Select architectures for reproduction using tournament selection.
        
        Args:
            evaluated_population: List of (architecture, fitness) tuples
            
        Returns:
            Selected architectures
        """
        selected = []
        
        # Elitism: preserve best individuals
        sorted_population = sorted(evaluated_population, key=lambda x: x[1], reverse=True)
        for i in range(min(self.elitism_count, len(sorted_population))):
            selected.append(sorted_population[i][0])
        
        # Tournament selection for the rest
        while len(selected) < self.population_size:
            tournament = random.sample(evaluated_population, min(self.tournament_size, len(evaluated_population)))
            winner = max(tournament, key=lambda x: x[1])[0]
            selected.append(copy.deepcopy(winner))
        
        return selected
    
    def crossover(self, parent1: ArchitectureModel, parent2: ArchitectureModel) -> Tuple[ArchitectureModel, ArchitectureModel]:
        """Perform crossover between two parent architectures.
        
        Args:
            parent1: First parent architecture
            parent2: Second parent architecture
            
        Returns:
            Two child architectures
        """
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        # Create child architectures
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # Generate new IDs for children
        child1.id = str(uuid.uuid4())
        child2.id = str(uuid.uuid4())
        child1.name = f"Child_of_{parent1.name}_{parent2.name}_1"
        child2.name = f"Child_of_{parent1.name}_{parent2.name}_2"
        
        # Agent crossover: exchange some agents
        if len(parent1.agents) > 0 and len(parent2.agents) > 0:
            # Create agent ID mapping for connections
            p1_to_c1 = {agent.id: agent.id for agent in child1.agents}
            p2_to_c2 = {agent.id: agent.id for agent in child2.agents}
            
            # Exchange a random subset of agents
            crossover_point = random.randint(1, min(len(parent1.agents), len(parent2.agents)) - 1)
            
            # Update child1 with agents from parent2
            for i in range(crossover_point):
                if i < len(parent2.agents):
                    new_agent = copy.deepcopy(parent2.agents[i])
                    old_id = new_agent.id
                    new_agent.id = str(uuid.uuid4())
                    p2_to_c1 = {old_id: new_agent.id}
                    
                    if i < len(child1.agents):
                        child1.agents[i] = new_agent
                    else:
                        child1.agents.append(new_agent)
            
            # Update child2 with agents from parent1
            for i in range(crossover_point):
                if i < len(parent1.agents):
                    new_agent = copy.deepcopy(parent1.agents[i])
                    old_id = new_agent.id
                    new_agent.id = str(uuid.uuid4())
                    p1_to_c2 = {old_id: new_agent.id}
                    
                    if i < len(child2.agents):
                        child2.agents[i] = new_agent
                    else:
                        child2.agents.append(new_agent)
            
            # Update connections to use new agent IDs
            self._update_connections(child1, p1_to_c1, p2_to_c1)
            self._update_connections(child2, p2_to_c2, p1_to_c2)
        
        # Connection crossover: exchange some connections
        if len(parent1.connections) > 0 and len(parent2.connections) > 0:
            # Exchange a random subset of connections
            crossover_point = random.randint(1, min(len(parent1.connections), len(parent2.connections)) - 1)
            
            # Get agent IDs in each child
            child1_agent_ids = {agent.id for agent in child1.agents}
            child2_agent_ids = {agent.id for agent in child2.agents}
            
            # Update child1 with connections from parent2
            valid_connections = []
            for i in range(crossover_point):
                if i < len(parent2.connections):
                    conn = copy.deepcopy(parent2.connections[i])
                    # Only add if both source and target agents exist in child1
                    if conn.source_id in child1_agent_ids and conn.target_id in child1_agent_ids:
                        conn.id = str(uuid.uuid4())
                        valid_connections.append(conn)
            
            # Replace connections in child1
            if valid_connections:
                if len(child1.connections) > len(valid_connections):
                    # Keep some original connections
                    keep_count = len(child1.connections) - len(valid_connections)
                    child1.connections = child1.connections[keep_count:] + valid_connections
                else:
                    child1.connections = valid_connections
            
            # Update child2 with connections from parent1
            valid_connections = []
            for i in range(crossover_point):
                if i < len(parent1.connections):
                    conn = copy.deepcopy(parent1.connections[i])
                    # Only add if both source and target agents exist in child2
                    if conn.source_id in child2_agent_ids and conn.target_id in child2_agent_ids:
                        conn.id = str(uuid.uuid4())
                        valid_connections.append(conn)
            
            # Replace connections in child2
            if valid_connections:
                if len(child2.connections) > len(valid_connections):
                    # Keep some original connections
                    keep_count = len(child2.connections) - len(valid_connections)
                    child2.connections = child2.connections[keep_count:] + valid_connections
                else:
                    child2.connections = valid_connections
        
        # Communication pattern crossover: randomly choose
        if random.random() < 0.5:
            child1.communication_pattern = parent2.communication_pattern
            child2.communication_pattern = parent1.communication_pattern
        
        return child1, child2
    
    def _update_connections(
        self,
        architecture: ArchitectureModel,
        primary_id_map: Dict[str, str],
        secondary_id_map: Dict[str, str]
    ) -> None:
        """Update connection IDs after agent crossover.
        
        Args:
            architecture: The architecture to update
            primary_id_map: Mapping from old to new IDs for primary parent
            secondary_id_map: Mapping from old to new IDs for secondary parent
        """
        agent_ids = {agent.id for agent in architecture.agents}
        valid_connections = []
        
        for conn in architecture.connections:
            new_conn = copy.deepcopy(conn)
            new_conn.id = str(uuid.uuid4())
            
            # Update source ID
            if conn.source_id in primary_id_map:
                new_conn.source_id = primary_id_map[conn.source_id]
            elif conn.source_id in secondary_id_map:
                new_conn.source_id = secondary_id_map[conn.source_id]
            
            # Update target ID
            if conn.target_id in primary_id_map:
                new_conn.target_id = primary_id_map[conn.target_id]
            elif conn.target_id in secondary_id_map:
                new_conn.target_id = secondary_id_map[conn.target_id]
            
            # Only keep connections between existing agents
            if new_conn.source_id in agent_ids and new_conn.target_id in agent_ids:
                valid_connections.append(new_conn)
        
        architecture.connections = valid_connections
    
    def mutation(self, architecture: ArchitectureModel) -> ArchitectureModel:
        """Mutate an architecture.
        
        Args:
            architecture: The architecture to mutate
            
        Returns:
            Mutated architecture
        """
        if random.random() > self.mutation_rate:
            return architecture
        
        # Create a copy for mutation
        mutated = copy.deepcopy(architecture)
        
        # Choose mutation type
        mutation_type = random.choice([
            "add_agent",
            "remove_agent",
            "modify_agent",
            "add_connection",
            "remove_connection",
            "modify_connection",
            "change_communication_pattern"
        ])
        
        if mutation_type == "add_agent" and len(mutated.agents) < self.search_space.max_agents:
            # Add a new agent
            role = random.choice(self.search_space.allowed_agent_roles)
            num_capabilities = random.randint(1, 5)
            capabilities = random.sample(
                self.search_space.allowed_agent_capabilities,
                min(num_capabilities, len(self.search_space.allowed_agent_capabilities))
            )
            
            new_agent = AgentModel(
                name=f"Agent_{len(mutated.agents)}",
                role=role,
                capabilities=capabilities,
                model_name=random.choice(["gpt-4", "llama-3", "claude-3", "gemini-pro"]),
                parameters={}
            )
            mutated.agents.append(new_agent)
            
            # Add some connections to the new agent
            existing_agent_ids = [agent.id for agent in mutated.agents[:-1]]
            if existing_agent_ids:
                # Add incoming connections
                num_incoming = random.randint(0, min(3, len(existing_agent_ids)))
                for _ in range(num_incoming):
                    source_id = random.choice(existing_agent_ids)
                    connection = ConnectionModel(
                        source_id=source_id,
                        target_id=new_agent.id,
                        bidirectional=random.random() < 0.3,
                        weight=random.uniform(0.1, 1.0),
                        parameters={}
                    )
                    mutated.connections.append(connection)
                
                # Add outgoing connections
                num_outgoing = random.randint(0, min(3, len(existing_agent_ids)))
                for _ in range(num_outgoing):
                    target_id = random.choice(existing_agent_ids)
                    connection = ConnectionModel(
                        source_id=new_agent.id,
                        target_id=target_id,
                        bidirectional=random.random() < 0.3,
                        weight=random.uniform(0.1, 1.0),
                        parameters={}
                    )
                    mutated.connections.append(connection)
        
        elif mutation_type == "remove_agent" and len(mutated.agents) > self.search_space.min_agents:
            # Check for required roles
            required_role_agents = []
            other_agents = []
            
            for agent in mutated.agents:
                if agent.role in self.search_space.required_roles:
                    required_role_agents.append(agent)
                else:
                    other_agents.append(agent)
            
            # Only remove if we have more than the minimum required agents
            if other_agents and len(required_role_agents) >= len(self.search_space.required_roles):
                # Remove a non-required agent
                agent_to_remove = random.choice(other_agents)
                mutated.remove_agent(agent_to_remove.id)
            elif len(required_role_agents) > len(self.search_space.required_roles):
                # Remove a required agent if we have extras
                role_counts = {}
                for agent in required_role_agents:
                    role_counts[agent.role] = role_counts.get(agent.role, 0) + 1
                
                # Find roles with more than one agent
                removable_agents = []
                for agent in required_role_agents:
                    if role_counts[agent.role] > 1:
                        removable_agents.append(agent)
                
                if removable_agents:
                    agent_to_remove = random.choice(removable_agents)
                    mutated.remove_agent(agent_to_remove.id)
        
        elif mutation_type == "modify_agent" and mutated.agents:
            # Modify an existing agent
            agent = random.choice(mutated.agents)
            
            # Don't modify required roles
            if agent.role in self.search_space.required_roles and len([a for a in mutated.agents if a.role == agent.role]) <= 1:
                # Only modify capabilities
                num_capabilities = random.randint(1, 5)
                agent.capabilities = random.sample(
                    self.search_space.allowed_agent_capabilities,
                    min(num_capabilities, len(self.search_space.allowed_agent_capabilities))
                )
            else:
                # Modify role and capabilities
                agent.role = random.choice(self.search_space.allowed_agent_roles)
                num_capabilities = random.randint(1, 5)
                agent.capabilities = random.sample(
                    self.search_space.allowed_agent_capabilities,
                    min(num_capabilities, len(self.search_space.allowed_agent_capabilities))
                )
            
            # Modify model
            agent.model_name = random.choice(["gpt-4", "llama-3", "claude-3", "gemini-pro"])
        
        elif mutation_type == "add_connection" and len(mutated.agents) >= 2:
            # Add a new connection
            agent_ids = [agent.id for agent in mutated.agents]
            
            # Track existing connections to avoid duplicates
            existing_connections = {(conn.source_id, conn.target_id) for conn in mutated.connections}
            
            # Try to find a new valid connection
            for _ in range(100):  # Limit attempts to avoid infinite loop
                source_id = random.choice(agent_ids)
                target_id = random.choice(agent_ids)
                if source_id != target_id and (source_id, target_id) not in existing_connections:
                    connection = ConnectionModel(
                        source_id=source_id,
                        target_id=target_id,
                        bidirectional=random.random() < 0.3,
                        weight=random.uniform(0.1, 1.0),
                        parameters={}
                    )
                    mutated.connections.append(connection)
                    break
        
        elif mutation_type == "remove_connection" and mutated.connections:
            # Remove a connection
            connection = random.choice(mutated.connections)
            mutated.remove_connection(connection.id)
        
        elif mutation_type == "modify_connection" and mutated.connections:
            # Modify a connection
            connection = random.choice(mutated.connections)
            connection.bidirectional = not connection.bidirectional
            connection.weight = random.uniform(0.1, 1.0)
        
        elif mutation_type == "change_communication_pattern":
            # Change communication pattern
            available_patterns = [
                pattern for pattern in self.search_space.allowed_communication_patterns
                if pattern != mutated.communication_pattern
            ]
            if available_patterns:
                mutated.communication_pattern = random.choice(available_patterns)
        
        return mutated
    
    def create_new_generation(self, selected: List[ArchitectureModel]) -> List[ArchitectureModel]:
        """Create a new generation through crossover and mutation.
        
        Args:
            selected: Selected architectures for reproduction
            
        Returns:
            New generation of architectures
        """
        new_generation = []
        
        # Elitism: preserve best individuals
        for i in range(min(self.elitism_count, len(selected))):
            new_generation.append(selected[i])
        
        # Create offspring through crossover and mutation
        while len(new_generation) < self.population_size:
            parent1 = random.choice(selected)
            parent2 = random.choice(selected)
            
            child1, child2 = self.crossover(parent1, parent2)
            child1 = self.mutation(child1)
            child2 = self.mutation(child2)
            
            new_generation.append(child1)
            if len(new_generation) < self.population_size:
                new_generation.append(child2)
        
        return new_generation
    
    def search(self) -> SearchResult:
        """Perform the architecture search.
        
        Returns:
            Search result containing the best architecture found
        """
        start_time = time.time()
        
        # Initialize population
        self.initialize_population()
        
        # Main evolutionary loop
        for generation in range(self.generations):
            logger.info(f"Generation {generation + 1}/{self.generations}")
            
            # Evaluate population
            evaluated_population = self.evaluate_population()
            
            # Update best architecture
            current_best = max(evaluated_population, key=lambda x: x[1])
            if current_best[1] > self.best_fitness:
                self.best_architecture = current_best[0]
                self.best_fitness = current_best[1]
                self.generations_without_improvement = 0
                logger.info(f"New best fitness: {self.best_fitness}")
            else:
                self.generations_without_improvement += 1
                logger.info(f"No improvement for {self.generations_without_improvement} generations")
            
            # Early stopping
            if self.generations_without_improvement >= self.early_stopping_patience:
                logger.info(f"Early stopping after {generation + 1} generations")
                break
            
            # Selection
            selected = self.selection(evaluated_population)
            
            # Create new generation
            self.population = self.create_new_generation(selected)
        
        # Final evaluation
        if not self.best_architecture:
            evaluated_population = self.evaluate_population()
            current_best = max(evaluated_population, key=lambda x: x[1])
            self.best_architecture = current_best[0]
            self.best_fitness = current_best[1]
        
        # Create search result
        search_time = time.time() - start_time
        result = SearchResult(
            task_id=self.task.id,
            search_space_id=self.search_space.id,
            best_architecture_id=self.best_architecture.id,
            best_fitness=self.best_fitness,
            architectures_evaluated=len(self.fitness_cache),
            search_time=search_time,
            algorithm_used="evolutionary",
            search_parameters={
                "population_size": self.population_size,
                "generations": self.generations,
                "mutation_rate": self.mutation_rate,
                "crossover_rate": self.crossover_rate,
                "tournament_size": self.tournament_size,
                "elitism_count": self.elitism_count,
                "early_stopping_patience": self.early_stopping_patience,
                "parallel_evaluations": self.parallel_evaluations
            }
        )
        
        logger.info(f"Search completed in {search_time:.2f} seconds")
        logger.info(f"Best fitness: {self.best_fitness}")
        logger.info(f"Architectures evaluated: {len(self.fitness_cache)}")
        
        return result


class TemplateBasedSearch:
    """Template-based algorithm for architecture search."""
    
    def __init__(
        self,
        search_space: SearchSpace,
        task: TaskModel,
        evaluation_function: Callable[[ArchitectureModel, TaskModel], EvaluationResult],
        templates: List[ArchitectureModel],
        variations_per_template: int = 10,
        parallel_evaluations: Optional[int] = None
    ):
        """Initialize the template-based search algorithm.
        
        Args:
            search_space: The search space to explore
            task: The task for which to search architectures
            evaluation_function: Function to evaluate architectures
            templates: List of template architectures
            variations_per_template: Number of variations to generate per template
            parallel_evaluations: Number of parallel evaluations to run
        """
        self.search_space = search_space
        self.task = task
        self.evaluation_function = evaluation_function
        self.templates = templates
        self.variations_per_template = variations_per_template
        
        # Get configuration
        config = get_config().search_parameters
        self.parallel_evaluations = parallel_evaluations or config.parallel_evaluations
        
        # Initialize results
        self.best_architecture: Optional[ArchitectureModel] = None
        self.best_fitness: float = float('-inf')
        self.fitness_cache: Dict[str, float] = {}
    
    def generate_variations(self, template: ArchitectureModel) -> List[ArchitectureModel]:
        """Generate variations of a template architecture.
        
        Args:
            template: Template architecture
            
        Returns:
            List of variations
        """
        variations = []
        
        for i in range(self.variations_per_template):
            # Create a copy of the template
            variation = copy.deepcopy(template)
            variation.id = str(uuid.uuid4())
            variation.name = f"{template.name}_Variation_{i}"
            variation.description = f"Variation {i} of {template.name}"
            
            # Apply random modifications
            num_modifications = random.randint(1, 5)
            for _ in range(num_modifications):
                modification_type = random.choice([
                    "add_agent",
                    "remove_agent",
                    "modify_agent",
                    "add_connection",
                    "remove_connection",
                    "modify_connection",
                    "change_communication_pattern"
                ])
                
                if modification_type == "add_agent" and len(variation.agents) < self.search_space.max_agents:
                    # Add a new agent
                    role = random.choice(self.search_space.allowed_agent_roles)
                    num_capabilities = random.randint(1, 5)
                    capabilities = random.sample(
                        self.search_space.allowed_agent_capabilities,
                        min(num_capabilities, len(self.search_space.allowed_agent_capabilities))
                    )
                    
                    new_agent = AgentModel(
                        name=f"Agent_{len(variation.agents)}",
                        role=role,
                        capabilities=capabilities,
                        model_name=random.choice(["gpt-4", "llama-3", "claude-3", "gemini-pro"]),
                        parameters={}
                    )
                    variation.agents.append(new_agent)
                    
                    # Add some connections to the new agent
                    existing_agent_ids = [agent.id for agent in variation.agents[:-1]]
                    if existing_agent_ids:
                        # Add incoming connections
                        num_incoming = random.randint(0, min(3, len(existing_agent_ids)))
                        for _ in range(num_incoming):
                            source_id = random.choice(existing_agent_ids)
                            connection = ConnectionModel(
                                source_id=source_id,
                                target_id=new_agent.id,
                                bidirectional=random.random() < 0.3,
                                weight=random.uniform(0.1, 1.0),
                                parameters={}
                            )
                            variation.connections.append(connection)
                        
                        # Add outgoing connections
                        num_outgoing = random.randint(0, min(3, len(existing_agent_ids)))
                        for _ in range(num_outgoing):
                            target_id = random.choice(existing_agent_ids)
                            connection = ConnectionModel(
                                source_id=new_agent.id,
                                target_id=target_id,
                                bidirectional=random.random() < 0.3,
                                weight=random.uniform(0.1, 1.0),
                                parameters={}
                            )
                            variation.connections.append(connection)
                
                elif modification_type == "remove_agent" and len(variation.agents) > self.search_space.min_agents:
                    # Check for required roles
                    required_role_agents = []
                    other_agents = []
                    
                    for agent in variation.agents:
                        if agent.role in self.search_space.required_roles:
                            required_role_agents.append(agent)
                        else:
                            other_agents.append(agent)
                    
                    # Only remove if we have more than the minimum required agents
                    if other_agents and len(required_role_agents) >= len(self.search_space.required_roles):
                        # Remove a non-required agent
                        agent_to_remove = random.choice(other_agents)
                        variation.remove_agent(agent_to_remove.id)
                    elif len(required_role_agents) > len(self.search_space.required_roles):
                        # Remove a required agent if we have extras
                        role_counts = {}
                        for agent in required_role_agents:
                            role_counts[agent.role] = role_counts.get(agent.role, 0) + 1
                        
                        # Find roles with more than one agent
                        removable_agents = []
                        for agent in required_role_agents:
                            if role_counts[agent.role] > 1:
                                removable_agents.append(agent)
                        
                        if removable_agents:
                            agent_to_remove = random.choice(removable_agents)
                            variation.remove_agent(agent_to_remove.id)
                
                elif modification_type == "modify_agent" and variation.agents:
                    # Modify an existing agent
                    agent = random.choice(variation.agents)
                    
                    # Don't modify required roles
                    if agent.role in self.search_space.required_roles and len([a for a in variation.agents if a.role == agent.role]) <= 1:
                        # Only modify capabilities
                        num_capabilities = random.randint(1, 5)
                        agent.capabilities = random.sample(
                            self.search_space.allowed_agent_capabilities,
                            min(num_capabilities, len(self.search_space.allowed_agent_capabilities))
                        )
                    else:
                        # Modify role and capabilities
                        agent.role = random.choice(self.search_space.allowed_agent_roles)
                        num_capabilities = random.randint(1, 5)
                        agent.capabilities = random.sample(
                            self.search_space.allowed_agent_capabilities,
                            min(num_capabilities, len(self.search_space.allowed_agent_capabilities))
                        )
                    
                    # Modify model
                    agent.model_name = random.choice(["gpt-4", "llama-3", "claude-3", "gemini-pro"])
                
                elif modification_type == "add_connection" and len(variation.agents) >= 2:
                    # Add a new connection
                    agent_ids = [agent.id for agent in variation.agents]
                    
                    # Track existing connections to avoid duplicates
                    existing_connections = {(conn.source_id, conn.target_id) for conn in variation.connections}
                    
                    # Try to find a new valid connection
                    for _ in range(100):  # Limit attempts to avoid infinite loop
                        source_id = random.choice(agent_ids)
                        target_id = random.choice(agent_ids)
                        if source_id != target_id and (source_id, target_id) not in existing_connections:
                            connection = ConnectionModel(
                                source_id=source_id,
                                target_id=target_id,
                                bidirectional=random.random() < 0.3,
                                weight=random.uniform(0.1, 1.0),
                                parameters={}
                            )
                            variation.connections.append(connection)
                            break
                
                elif modification_type == "remove_connection" and variation.connections:
                    # Remove a connection
                    connection = random.choice(variation.connections)
                    variation.remove_connection(connection.id)
                
                elif modification_type == "modify_connection" and variation.connections:
                    # Modify a connection
                    connection = random.choice(variation.connections)
                    connection.bidirectional = not connection.bidirectional
                    connection.weight = random.uniform(0.1, 1.0)
                
                elif modification_type == "change_communication_pattern":
                    # Change communication pattern
                    available_patterns = [
                        pattern for pattern in self.search_space.allowed_communication_patterns
                        if pattern != variation.communication_pattern
                    ]
                    if available_patterns:
                        variation.communication_pattern = random.choice(available_patterns)
            
            variations.append(variation)
        
        return variations
    
    def evaluate_architectures(self, architectures: List[ArchitectureModel]) -> List[Tuple[ArchitectureModel, float]]:
        """Evaluate a list of architectures.
        
        Args:
            architectures: List of architectures to evaluate
            
        Returns:
            List of (architecture, fitness) tuples
        """
        results = []
        
        # Use parallel evaluation if enabled
        if self.parallel_evaluations > 1:
            with ThreadPoolExecutor(max_workers=self.parallel_evaluations) as executor:
                future_to_arch = {
                    executor.submit(self._evaluate_architecture, arch): arch
                    for arch in architectures
                }
                for future in as_completed(future_to_arch):
                    arch = future_to_arch[future]
                    try:
                        fitness = future.result()
                        results.append((arch, fitness))
                    except Exception as e:
                        logger.error(f"Error evaluating architecture {arch.id}: {e}")
                        results.append((arch, float('-inf')))
        else:
            # Sequential evaluation
            for arch in architectures:
                try:
                    fitness = self._evaluate_architecture(arch)
                    results.append((arch, fitness))
                except Exception as e:
                    logger.error(f"Error evaluating architecture {arch.id}: {e}")
                    results.append((arch, float('-inf')))
        
        return results
    
    def _evaluate_architecture(self, architecture: ArchitectureModel) -> float:
        """Evaluate a single architecture.
        
        Args:
            architecture: The architecture to evaluate
            
        Returns:
            Fitness score for the architecture
        """
        # Check if architecture is valid
        is_valid, reason = self.search_space.is_valid_architecture(architecture)
        if not is_valid:
            logger.warning(f"Invalid architecture {architecture.id}: {reason}")
            return float('-inf')
        
        # Check if already evaluated
        if architecture.id in self.fitness_cache:
            return self.fitness_cache[architecture.id]
        
        # Evaluate the architecture
        evaluation_result = self.evaluation_function(architecture, self.task)
        fitness = evaluation_result.overall_fitness
        
        # Cache the result
        self.fitness_cache[architecture.id] = fitness
        
        return fitness
    
    def search(self) -> SearchResult:
        """Perform the architecture search.
        
        Returns:
            Search result containing the best architecture found
        """
        start_time = time.time()
        
        # Generate variations for each template
        all_architectures = []
        for template in self.templates:
            variations = self.generate_variations(template)
            all_architectures.extend(variations)
            all_architectures.append(template)  # Include the original template
        
        # Evaluate all architectures
        evaluated_architectures = self.evaluate_architectures(all_architectures)
        
        # Find the best architecture
        best = max(evaluated_architectures, key=lambda x: x[1])
        self.best_architecture = best[0]
        self.best_fitness = best[1]
        
        # Create search result
        search_time = time.time() - start_time
        result = SearchResult(
            task_id=self.task.id,
            search_space_id=self.search_space.id,
            best_architecture_id=self.best_architecture.id,
            best_fitness=self.best_fitness,
            architectures_evaluated=len(self.fitness_cache),
            search_time=search_time,
            algorithm_used="template_based",
            search_parameters={
                "templates_used": len(self.templates),
                "variations_per_template": self.variations_per_template,
                "parallel_evaluations": self.parallel_evaluations
            }
        )
        
        logger.info(f"Search completed in {search_time:.2f} seconds")
        logger.info(f"Best fitness: {self.best_fitness}")
        logger.info(f"Architectures evaluated: {len(self.fitness_cache)}")
        
        return result


def get_search_algorithm(
    algorithm_name: str,
    search_space: SearchSpace,
    task: TaskModel,
    evaluation_function: Callable[[ArchitectureModel, TaskModel], EvaluationResult],
    templates: Optional[List[ArchitectureModel]] = None,
    **kwargs
) -> Union[EvolutionarySearch, TemplateBasedSearch]:
    """Get a search algorithm by name.
    
    Args:
        algorithm_name: Name of the algorithm
        search_space: Search space to explore
        task: Task for which to search architectures
        evaluation_function: Function to evaluate architectures
        templates: List of template architectures (for template-based search)
        **kwargs: Additional parameters for the algorithm
        
    Returns:
        Search algorithm instance
        
    Raises:
        ValueError: If the algorithm name is not recognized
    """
    if algorithm_name == "evolutionary":
        return EvolutionarySearch(
            search_space=search_space,
            task=task,
            evaluation_function=evaluation_function,
            **kwargs
        )
    elif algorithm_name == "template_based":
        if not templates:
            raise ValueError("Templates must be provided for template-based search")
        return TemplateBasedSearch(
            search_space=search_space,
            task=task,
            evaluation_function=evaluation_function,
            templates=templates,
            **kwargs
        )
    else:
        raise ValueError(f"Unknown search algorithm: {algorithm_name}")
