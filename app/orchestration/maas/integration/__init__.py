"""
Integration module for Multi-agent Architecture Search (MaAS).

This module provides integration adapters for connecting MaAS with
different agent orchestration frameworks.
"""

from typing import Dict, Any, Optional, List, Union
import logging

from ..models import TaskModel
from ..supernet.agentic_supernet import AgenticSupernet
from ..evaluation.evaluator import ArchitectureEvaluator
from .autogen_integration import MaaSAutoGenAdapter
from .a2a_integration import MaaSA2AAdapter

logger = logging.getLogger(__name__)


class MaaSIntegrationManager:
    """Manager for integrating MaAS with different agent orchestration frameworks.
    
    This class provides a unified interface for working with both AutoGen and A2A
    frameworks, abstracting away the differences between them.
    """
    
    def __init__(
        self, 
        supernet: AgenticSupernet,
        evaluator: ArchitectureEvaluator
    ):
        """Initialize the integration manager.
        
        Args:
            supernet: The agentic supernet for architecture sampling
            evaluator: The architecture evaluator for performance assessment
        """
        self.supernet = supernet
        self.evaluator = evaluator
        self.autogen_adapter = MaaSAutoGenAdapter(supernet, evaluator)
        self.a2a_adapter = MaaSA2AAdapter(supernet, evaluator)
        
        # Map framework names to adapters
        self.adapters = {
            "autogen": self.autogen_adapter,
            "a2a": self.a2a_adapter
        }
        
        logger.info("MaaSIntegrationManager initialized with AutoGen and A2A adapters")
    
    def create_agent_team(
        self,
        task: TaskModel,
        framework: str = "autogen",
        architecture_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an agent team for the given task using the specified framework.
        
        Args:
            task: The task to create an agent team for
            framework: The orchestration framework to use ("autogen" or "a2a")
            architecture_id: Optional ID of a specific architecture to use
            parameters: Optional parameters for team creation
            
        Returns:
            Configuration for the agent team in the specified framework
            
        Raises:
            ValueError: If the specified framework is not supported
        """
        if framework not in self.adapters:
            raise ValueError(f"Unsupported framework: {framework}. Supported frameworks: {list(self.adapters.keys())}")
        
        adapter = self.adapters[framework]
        config = adapter.create_agent_team(task, architecture_id, parameters)
        
        logger.info(f"Created agent team for task '{task.name}' using {framework} framework")
        return config
    
    def execute_workflow(
        self,
        task: TaskModel,
        framework: str = "autogen",
        architecture_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a workflow for the given task using the specified framework.
        
        Args:
            task: The task to execute
            framework: The orchestration framework to use ("autogen" or "a2a")
            architecture_id: Optional ID of a specific architecture to use
            parameters: Optional parameters for workflow execution
            
        Returns:
            Results of the workflow execution
            
        Raises:
            ValueError: If the specified framework is not supported
        """
        if framework not in self.adapters:
            raise ValueError(f"Unsupported framework: {framework}. Supported frameworks: {list(self.adapters.keys())}")
        
        adapter = self.adapters[framework]
        
        # Create agent team if architecture_id is not provided
        if not architecture_id:
            config = adapter.create_agent_team(task, parameters=parameters)
            architecture = adapter.get_architecture_from_config(config)
            architecture_id = architecture.id
        
        # Execute workflow
        results = adapter.execute_workflow(task, architecture_id, parameters)
        
        # Evaluate results and update supernet
        metrics = adapter.extract_metrics_from_results(results)
        evaluation_result = self.evaluator.evaluate_architecture(
            architecture_id=architecture_id,
            task=task,
            metrics=metrics
        )
        
        # Update supernet with feedback
        self.supernet.update_from_feedback(architecture_id, evaluation_result)
        
        logger.info(f"Executed workflow for task '{task.name}' using {framework} framework")
        return results
    
    def get_recommended_architecture(
        self,
        task: TaskModel,
        num_candidates: int = 5
    ) -> Dict[str, Any]:
        """Get the recommended architecture for the given task.
        
        Args:
            task: The task to get a recommended architecture for
            num_candidates: Number of candidate architectures to sample
            
        Returns:
            Information about the recommended architecture
        """
        # Sample multiple architectures
        architectures = [self.supernet.sample_architecture(task) for _ in range(num_candidates)]
        
        # Evaluate architectures using historical data or heuristics
        evaluations = []
        for architecture in architectures:
            # Use heuristic evaluation if no historical data
            evaluation = self.evaluator.evaluate_architecture_heuristically(architecture, task)
            evaluations.append(evaluation)
        
        # Find the best architecture
        best_idx = max(range(len(evaluations)), key=lambda i: evaluations[i].fitness)
        best_architecture = architectures[best_idx]
        best_evaluation = evaluations[best_idx]
        
        # Return information about the recommended architecture
        return {
            "architecture": best_architecture.to_dict(),
            "fitness": best_evaluation.fitness,
            "metrics": best_evaluation.metrics,
            "confidence": best_evaluation.confidence
        }
    
    def get_framework_capabilities(self) -> Dict[str, List[str]]:
        """Get the capabilities of each supported framework.
        
        Returns:
            Dictionary mapping framework names to lists of capabilities
        """
        return {
            "autogen": [
                "dynamic_team_formation",
                "hierarchical_workflows",
                "tool_augmentation",
                "memory_management"
            ],
            "a2a": [
                "standardized_communication",
                "cross_platform_compatibility",
                "interoperability",
                "extensibility"
            ]
        }
