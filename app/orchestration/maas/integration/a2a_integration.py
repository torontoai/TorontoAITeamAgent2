"""
MaAS integration adapter for the A2A protocol.

This module provides integration between the Multi-agent Architecture Search (MaAS)
system and the Google A2A protocol for agent orchestration.
"""

from typing import List, Dict, Any, Optional, Callable, Union, Type
import logging
import json
import os
import importlib

# Fix import paths to use local models instead of non-existent orchestration_models
from ..models import ArchitectureModel, AgentModel, ConnectionModel, TaskModel, AgentRole, AgentCapability
from ...adapters.a2a_adapter import A2AAdapter
from ..supernet.agentic_supernet import AgenticSupernet
from ..evaluation.evaluator import ArchitectureEvaluator

logger = logging.getLogger(__name__)

class MaaSA2AAdapter:
    """Adapter for integrating MaAS with the A2A protocol."""
    
    def __init__(self, supernet: AgenticSupernet, evaluator: Optional[ArchitectureEvaluator] = None):
        """Initialize the MaAS-A2A adapter.
        
        Args:
            supernet: AgenticSupernet instance for architecture sampling
            evaluator: Optional ArchitectureEvaluator for evaluating architectures
        """
        self.supernet = supernet
        self.evaluator = evaluator
        self.a2a_adapter = A2AAdapter()
        self.architecture_cache = {}  # Cache of task_id -> architecture
    
    def create_agent_team(self, task: TaskModel, architecture_id: Optional[str] = None, 
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an A2A agent team based on a task using MaAS.
        
        Args:
            task: TaskModel describing the task requirements
            architecture_id: Optional ID of a specific architecture to use
            parameters: Optional parameters for team creation
            
        Returns:
            A2A configuration dictionary for the agent team
        """
        # Extract complexity from parameters if provided
        complexity = None
        if parameters and 'complexity' in parameters:
            complexity = parameters.get('complexity')
        
        # Sample an architecture from the supernet
        architecture = self.supernet.sample_architecture(task, complexity)
        
        # Cache the architecture for this task
        if task.id:
            self.architecture_cache[task.id] = architecture
        
        # Convert the architecture to A2A configuration
        a2a_config = self._convert_to_a2a_config(architecture, task)
        
        logger.info(f"Created A2A team with {len(architecture.agents)} agents for task '{task.name}'")
        return a2a_config
    
    def execute_workflow(self, task: TaskModel, 
                        architecture_id: Optional[str] = None,
                        parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a workflow using an A2A team created with MaAS.
        
        Args:
            task: TaskModel describing the task requirements
            architecture_id: Optional ID of a specific architecture to use
            parameters: Optional parameters for workflow execution
            
        Returns:
            Results from the workflow execution
        """
        # Extract execution parameters
        max_iterations = 10
        user_input = None
        callbacks = None
        
        if parameters:
            if 'max_iterations' in parameters:
                max_iterations = parameters.get('max_iterations')
            if 'user_input' in parameters:
                user_input = parameters.get('user_input')
            if 'callbacks' in parameters:
                callbacks = parameters.get('callbacks')
        
        # Create the agent team
        a2a_config = self.create_agent_team(task, architecture_id, parameters)
        
        # Execute the workflow using the A2A adapter
        results = self.a2a_adapter.execute_workflow(
            config=a2a_config,
            max_iterations=max_iterations,
            user_input=user_input,
            callbacks=callbacks
        )
        
        # If we have an evaluator and a cached architecture, evaluate it
        if self.evaluator and task.id and task.id in self.architecture_cache:
            architecture = self.architecture_cache[task.id]
            
            # Extract metrics from results
            metrics = self._extract_metrics_from_results(results)
            
            # Evaluate the architecture
            evaluation_result = self.evaluator.evaluate_architecture(
                architecture=architecture,
                task=task,
                metrics=metrics
            )
            
            # Update the supernet with feedback
            self.supernet.update_from_feedback(architecture, evaluation_result)
            
            # Add evaluation to results
            results['evaluation'] = {
                'fitness': evaluation_result.fitness,
                'metrics': evaluation_result.metrics
            }
        
        return results
    
    def get_architecture_from_config(self, config: Dict[str, Any]) -> ArchitectureModel:
        """Extract architecture information from a configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            ArchitectureModel extracted from the configuration
        """
        # This is a placeholder implementation
        # In a real implementation, we would extract the architecture from the config
        if 'task' in config and 'id' in config['task'] and config['task']['id'] in self.architecture_cache:
            return self.architecture_cache[config['task']['id']]
        
        # If we can't find the architecture, create a dummy one
        agents = []
        connections = []
        
        if 'agents' in config:
            for i, agent_config in enumerate(config['agents']):
                agent = AgentModel(
                    id=agent_config.get('id', f"agent_{i}"),
                    name=agent_config.get('name', f"Agent {i}"),
                    role=AgentRole(agent_config.get('role', 'assistant')),
                    model_name=agent_config.get('model', 'gpt-3.5-turbo'),
                    capabilities=[],
                    parameters=agent_config.get('parameters', {})
                )
                agents.append(agent)
        
        if 'graph' in config and 'edges' in config['graph']:
            for edge in config['graph']['edges']:
                connection = ConnectionModel(
                    source_id=edge['source'],
                    target_id=edge['target'],
                    weight=edge.get('weight', 1.0),
                    bidirectional=edge.get('bidirectional', False)
                )
                connections.append(connection)
        
        return ArchitectureModel(
            name="Extracted Architecture",
            agents=agents,
            connections=connections
        )
    
    def extract_metrics_from_results(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract metrics from workflow execution results.
        
        Args:
            results: Results from workflow execution
            
        Returns:
            Dictionary of metrics
        """
        return self._extract_metrics_from_results(results)
    
    def _convert_to_a2a_config(self, architecture: ArchitectureModel, 
                             task: TaskModel) -> Dict[str, Any]:
        """Convert a MaAS architecture to A2A configuration.
        
        Args:
            architecture: ArchitectureModel to convert
            task: TaskModel for context
            
        Returns:
            A2A configuration dictionary
        """
        # Create agent configurations
        agents = []
        
        for agent in architecture.agents:
            # Convert MaAS agent to A2A agent config
            agent_config = self._convert_agent_to_a2a(agent, task)
            agents.append(agent_config)
        
        # Create graph configuration
        graph = self._create_graph_config(architecture)
        
        # Combine into final config
        a2a_config = {
            'agents': agents,
            'graph': graph,
            'task': {
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'domain': task.domain
            }
        }
        
        return a2a_config
    
    def _convert_agent_to_a2a(self, agent: AgentModel, task: TaskModel) -> Dict[str, Any]:
        """Convert a MaAS agent to A2A agent configuration.
        
        Args:
            agent: AgentModel to convert
            task: TaskModel for context
            
        Returns:
            A2A agent configuration dictionary
        """
        # Map MaAS agent roles to A2A agent types
        role_to_type = {
            AgentRole.COORDINATOR: "coordinator",
            AgentRole.EXECUTOR: "executor",
            AgentRole.PLANNER: "planner",
            AgentRole.RESEARCHER: "researcher",
            AgentRole.CRITIC: "critic",
            AgentRole.MEMORY: "memory",
            AgentRole.REASONER: "reasoner",
            AgentRole.GENERATOR: "generator",
            AgentRole.EVALUATOR: "evaluator",
            AgentRole.COMMUNICATOR: "communicator",
            AgentRole.SPECIALIST: "specialist",
            AgentRole.CUSTOM: "custom"
        }
        
        # Create the agent configuration
        agent_config = {
            'id': agent.id,
            'name': agent.name,
            'type': role_to_type.get(agent.role, "assistant"),
            'model': agent.model_name,
            'role': agent.role.value,
            'capabilities': [cap.value for cap in agent.capabilities] if agent.capabilities else [],
            'parameters': agent.parameters or {}
        }
        
        # Add task-specific context
        if task.description:
            agent_config['parameters']['task_description'] = task.description
        
        if task.domain:
            agent_config['parameters']['domain'] = task.domain
        
        return agent_config
    
    def _create_graph_config(self, architecture: ArchitectureModel) -> Dict[str, Any]:
        """Create a graph configuration from an architecture.
        
        Args:
            architecture: ArchitectureModel to convert
            
        Returns:
            Graph configuration dictionary
        """
        # Create nodes
        nodes = [
            {
                'id': agent.id,
                'type': agent.role.value
            }
            for agent in architecture.agents
        ]
        
        # Create edges
        edges = [
            {
                'source': conn.source_id,
                'target': conn.target_id,
                'weight': conn.weight,
                'bidirectional': conn.bidirectional
            }
            for conn in architecture.connections
        ]
        
        # Create the graph configuration
        graph_config = {
            'nodes': nodes,
            'edges': edges
        }
        
        return graph_config
    
    def _extract_metrics_from_results(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Extract metrics from workflow execution results.
        
        Args:
            results: Results from workflow execution
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        # Extract basic metrics
        if 'execution_time' in results:
            metrics['execution_time'] = float(results['execution_time'])
        
        if 'iterations' in results:
            metrics['iterations'] = float(results['iterations'])
        
        if 'token_usage' in results:
            metrics['token_usage'] = float(results['token_usage'])
        
        if 'cost' in results:
            metrics['cost'] = float(results['cost'])
        
        # Extract success metrics if available
        if 'success' in results:
            metrics['success'] = 1.0 if results['success'] else 0.0
        
        if 'quality_score' in results:
            metrics['quality_score'] = float(results['quality_score'])
        
        # Extract agent-specific metrics
        if 'agent_metrics' in results:
            agent_metrics = results['agent_metrics']
            for agent_id, agent_data in agent_metrics.items():
                for metric_name, metric_value in agent_data.items():
                    if isinstance(metric_value, (int, float)):
                        metrics[f"{agent_id}_{metric_name}"] = float(metric_value)
        
        return metrics
