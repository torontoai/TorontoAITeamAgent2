"""
MaAS integration adapter for the AutoGen framework.

This module provides integration between the Multi-agent Architecture Search (MaAS)
system and the Microsoft AutoGen framework for agent orchestration.
"""

from typing import List, Dict, Any, Optional, Callable, Union, Type
import logging
import json
import os
import importlib

# Fix import paths to use local models instead of non-existent orchestration_models
from ..models import ArchitectureModel, AgentModel, ConnectionModel, TaskModel, AgentRole, AgentCapability
from ...adapters.autogen_adapter import AutoGenAdapter
from ..supernet.agentic_supernet import AgenticSupernet
from ..evaluation.evaluator import ArchitectureEvaluator

logger = logging.getLogger(__name__)

# Define AgentConfig and WorkflowConfig classes locally since orchestration_models doesn't exist
class AgentConfig:
    """Configuration for an agent in the workflow."""
    
    def __init__(self, id: str, name: str, agent_type: str, model: str, **kwargs):
        self.id = id
        self.name = name
        self.agent_type = agent_type
        self.model = model
        self.config = kwargs.get('config', {})
        self.role = kwargs.get('role', 'assistant')
        self.capabilities = kwargs.get('capabilities', [])

class WorkflowConfig:
    """Configuration for a workflow."""
    
    def __init__(self, workflow_type: str, graph: Dict[str, List[Dict[str, Any]]], entry_points: List[str]):
        self.workflow_type = workflow_type
        self.graph = graph
        self.entry_points = entry_points

class MaaSAutoGenAdapter:
    """Adapter for integrating MaAS with the AutoGen framework."""
    
    def __init__(self, supernet: AgenticSupernet, evaluator: Optional[ArchitectureEvaluator] = None):
        """Initialize the MaAS-AutoGen adapter.
        
        Args:
            supernet: AgenticSupernet instance for architecture sampling
            evaluator: Optional ArchitectureEvaluator for evaluating architectures
        """
        self.supernet = supernet
        self.evaluator = evaluator
        self.autogen_adapter = AutoGenAdapter()
        self.architecture_cache = {}  # Cache of task_id -> architecture
    
    def create_agent_team(self, task: TaskModel, architecture_id: Optional[str] = None, 
                         parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an AutoGen agent team based on a task using MaAS.
        
        Args:
            task: TaskModel describing the task requirements
            architecture_id: Optional ID of a specific architecture to use
            parameters: Optional parameters for team creation
            
        Returns:
            AutoGen configuration dictionary for the agent team
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
        
        # Convert the architecture to AutoGen configuration
        autogen_config = self._convert_to_autogen_config(architecture, task)
        
        logger.info(f"Created AutoGen team with {len(architecture.agents)} agents for task '{task.name}'")
        return autogen_config
    
    def execute_workflow(self, task: TaskModel, 
                        architecture_id: Optional[str] = None,
                        parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a workflow using an AutoGen team created with MaAS.
        
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
        autogen_config = self.create_agent_team(task, architecture_id, parameters)
        
        # Execute the workflow using the AutoGen adapter
        results = self.autogen_adapter.execute_workflow(
            config=autogen_config,
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
                    parameters=agent_config.get('config', {})
                )
                agents.append(agent)
        
        if 'workflow' in config and 'graph' in config['workflow']:
            for source_id, targets in config['workflow']['graph'].items():
                for target in targets:
                    connection = ConnectionModel(
                        source_id=source_id,
                        target_id=target['target'],
                        weight=target.get('weight', 1.0),
                        bidirectional=target.get('bidirectional', False)
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
    
    def _convert_to_autogen_config(self, architecture: ArchitectureModel, 
                                 task: TaskModel) -> Dict[str, Any]:
        """Convert a MaAS architecture to AutoGen configuration.
        
        Args:
            architecture: ArchitectureModel to convert
            task: TaskModel for context
            
        Returns:
            AutoGen configuration dictionary
        """
        # Create agent configurations
        agent_configs = []
        
        for agent in architecture.agents:
            # Convert MaAS agent to AutoGen agent config
            agent_config = self._convert_agent_to_autogen(agent, task)
            agent_configs.append(agent_config)
        
        # Create workflow configuration
        workflow_config = self._create_workflow_config(architecture, agent_configs)
        
        # Combine into final config
        autogen_config = {
            'agents': agent_configs,
            'workflow': workflow_config,
            'task': {
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'domain': task.domain
            }
        }
        
        return autogen_config
    
    def _convert_agent_to_autogen(self, agent: AgentModel, task: TaskModel) -> Dict[str, Any]:
        """Convert a MaAS agent to AutoGen agent configuration.
        
        Args:
            agent: AgentModel to convert
            task: TaskModel for context
            
        Returns:
            AutoGen agent configuration dictionary
        """
        # Map MaAS agent roles to AutoGen agent types
        role_to_type = {
            AgentRole.COORDINATOR: "assistant",
            AgentRole.EXECUTOR: "executor",
            AgentRole.PLANNER: "planner",
            AgentRole.RESEARCHER: "retriever",
            AgentRole.CRITIC: "critic",
            AgentRole.MEMORY: "memory",
            AgentRole.REASONER: "reasoner",
            AgentRole.GENERATOR: "generator",
            AgentRole.EVALUATOR: "evaluator",
            AgentRole.COMMUNICATOR: "communicator",
            AgentRole.SPECIALIST: "specialist",
            AgentRole.CUSTOM: "custom"
        }
        
        # Map capabilities to AutoGen agent configuration
        capability_config = self._map_capabilities_to_config(agent.capabilities)
        
        # Create the agent configuration
        agent_config = {
            'id': agent.id,
            'name': agent.name,
            'type': role_to_type.get(agent.role, "assistant"),
            'model': agent.model_name,
            'role': agent.role.value,
            'capabilities': [cap.value for cap in agent.capabilities] if agent.capabilities else [],
            'config': {
                **capability_config,
                **(agent.parameters or {})
            }
        }
        
        # Add task-specific context
        if task.description:
            agent_config['config']['task_description'] = task.description
        
        if task.domain:
            agent_config['config']['domain'] = task.domain
        
        return agent_config
    
    def _map_capabilities_to_config(self, capabilities: List[AgentCapability]) -> Dict[str, Any]:
        """Map agent capabilities to AutoGen configuration parameters.
        
        Args:
            capabilities: List of agent capabilities
            
        Returns:
            Configuration dictionary for AutoGen
        """
        config = {}
        
        if not capabilities:
            return config
        
        # Map specific capabilities to configuration
        capability_map = {
            AgentCapability.TOOL_USE: {'allow_tools': True},
            AgentCapability.CODE_EXECUTION: {'allow_code_execution': True},
            AgentCapability.ACTION_EXECUTION: {'allow_action_execution': True},
            AgentCapability.INFORMATION_RETRIEVAL: {'allow_retrieval': True},
            AgentCapability.PLANNING: {'allow_planning': True},
            AgentCapability.DELEGATION: {'allow_delegation': True},
            AgentCapability.MONITORING: {'allow_monitoring': True},
            AgentCapability.QUALITY_ASSESSMENT: {'allow_evaluation': True},  # Changed from EVALUATION
            AgentCapability.FEEDBACK: {'allow_feedback': True},
            AgentCapability.ERROR_DETECTION: {'allow_error_detection': True},
            AgentCapability.INFORMATION_STORAGE: {'allow_storage': True},
            AgentCapability.CONTEXT_MANAGEMENT: {'allow_context_management': True},
            AgentCapability.LOGICAL_REASONING: {'allow_reasoning': True},
            AgentCapability.PROBLEM_SOLVING: {'allow_problem_solving': True},
            AgentCapability.DECISION_MAKING: {'allow_decision_making': True},
            AgentCapability.CONTENT_GENERATION: {'allow_generation': True},
            AgentCapability.CREATIVITY: {'allow_creativity': True},
            AgentCapability.SUMMARIZATION: {'allow_summarization': True},
            AgentCapability.QUALITY_ASSESSMENT: {'allow_assessment': True},
            AgentCapability.PERFORMANCE_MONITORING: {'allow_performance_monitoring': True},
            AgentCapability.NATURAL_LANGUAGE_PROCESSING: {'allow_nlp': True},
            AgentCapability.DIALOGUE_MANAGEMENT: {'allow_dialogue': True},
            AgentCapability.EXPLANATION: {'allow_explanation': True},
            AgentCapability.DOMAIN_EXPERTISE: {'allow_domain_expertise': True},
            AgentCapability.SPECIALIZED_KNOWLEDGE: {'allow_specialized_knowledge': True},
            AgentCapability.TECHNICAL_SKILLS: {'allow_technical_skills': True},
            AgentCapability.GOAL_DECOMPOSITION: {'allow_goal_decomposition': True},
            AgentCapability.STRATEGY_FORMULATION: {'allow_strategy_formulation': True},
            AgentCapability.KNOWLEDGE_INTEGRATION: {'allow_knowledge_integration': True},
            AgentCapability.FACT_CHECKING: {'allow_fact_checking': True}
        }
        
        # Apply capability configurations
        for capability in capabilities:
            if capability in capability_map:
                config.update(capability_map[capability])
        
        return config
    
    def _create_workflow_config(self, architecture: ArchitectureModel, 
                              agent_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a workflow configuration from an architecture.
        
        Args:
            architecture: ArchitectureModel to convert
            agent_configs: List of agent configurations
            
        Returns:
            Workflow configuration dictionary
        """
        # Create a mapping from agent IDs to indices in the agent_configs list
        agent_indices = {config['id']: i for i, config in enumerate(agent_configs)}
        
        # Create the workflow graph
        workflow_graph = {}
        
        for agent_id in agent_indices:
            # Find all connections where this agent is the source
            outgoing_connections = [
                conn for conn in architecture.connections
                if conn.source_id == agent_id and conn.target_id in agent_indices
            ]
            
            # Add targets to the workflow graph
            if outgoing_connections:
                workflow_graph[agent_id] = [
                    {
                        'target': conn.target_id,
                        'weight': conn.weight,
                        'bidirectional': conn.bidirectional
                    }
                    for conn in outgoing_connections
                ]
        
        # Determine the entry point (coordinator or first agent)
        entry_points = [
            agent.id for agent in architecture.agents
            if agent.role == AgentRole.COORDINATOR
        ]
        
        if not entry_points and architecture.agents:
            entry_points = [architecture.agents[0].id]
        
        # Create the workflow configuration
        workflow_config = {
            'type': 'graph',
            'graph': workflow_graph,
            'entry_points': entry_points
        }
        
        return workflow_config
    
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
