"""
Agentic Supernet implementation for Multi-agent Architecture Search (MaAS).

This module provides the core implementation of the Agentic Supernet concept,
which enables dynamic architecture sampling based on task requirements.
"""

from typing import List, Optional, Dict, Any, Tuple
import numpy as np
import logging

from ..models import ArchitectureModel, AgentModel, ConnectionModel, SearchSpace, TaskModel, EvaluationResult
from .controller import SupernetController
from .architecture_sampler import ArchitectureSampler
from ..templates.architecture_templates import ArchitectureTemplates

logger = logging.getLogger(__name__)

class AgenticSupernet:
    """Implementation of the Agentic Supernet concept for MaAS.
    
    The Agentic Supernet is a probabilistic and continuous distribution of agent architectures
    that can be sampled based on task requirements. It learns to generate optimal architectures
    through feedback from architecture evaluations.
    """
    
    def __init__(self, search_space: SearchSpace, templates: Optional[List[ArchitectureModel]] = None):
        """Initialize the Agentic Supernet.
        
        Args:
            search_space: SearchSpace defining the architecture constraints
            templates: Optional list of template architectures to include
        """
        self.search_space = search_space
        self.templates = templates or self._load_default_templates()
        self.controller = SupernetController()
        self.sampler = ArchitectureSampler(search_space)
        
        # Initialize the controller with templates if provided
        if self.templates:
            for template in self.templates:
                self.controller.add_template(template)
    
    def sample_architecture(self, task: TaskModel, complexity: Optional[float] = None) -> ArchitectureModel:
        """Sample an architecture from the supernet based on task requirements.
        
        Args:
            task: TaskModel describing the task requirements
            complexity: Optional explicit complexity override (0.0 to 1.0)
                If not provided, complexity will be inferred from the task
                
        Returns:
            ArchitectureModel sampled from the supernet
        """
        # Infer complexity if not provided
        if complexity is None:
            complexity = self._infer_complexity(task)
        
        logger.info(f"Sampling architecture for task '{task.name}' with complexity {complexity:.2f}")
        
        # Use the controller to sample an architecture
        return self.controller.sample(task, self.search_space, complexity)
    
    def update_from_feedback(self, architecture: ArchitectureModel, evaluation_result: EvaluationResult) -> None:
        """Update the supernet based on architecture performance feedback.
        
        Args:
            architecture: ArchitectureModel that was evaluated
            evaluation_result: EvaluationResult from the evaluation
        """
        logger.info(f"Updating supernet with feedback for architecture '{architecture.name}' "
                   f"with fitness {evaluation_result.fitness:.4f}")
        
        # Update the controller based on feedback
        self.controller.update(architecture, evaluation_result)
    
    def get_architecture_distribution(self, task: TaskModel) -> Dict[str, float]:
        """Get the probability distribution over architecture templates for a given task.
        
        Args:
            task: TaskModel describing the task requirements
            
        Returns:
            Dictionary mapping template names to probabilities
        """
        return self.controller.get_template_distribution(task)
    
    def reset(self) -> None:
        """Reset the supernet to its initial state."""
        logger.info("Resetting Agentic Supernet")
        self.controller = SupernetController()
        
        # Re-initialize the controller with templates
        if self.templates:
            for template in self.templates:
                self.controller.add_template(template)
    
    def save_state(self, path: str) -> None:
        """Save the current state of the supernet to a file.
        
        Args:
            path: Path to save the state
        """
        import pickle
        import os
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        state = {
            'controller_state': self.controller.get_state(),
            'search_space': self.search_space,
            'templates': self.templates
        }
        
        with open(path, 'wb') as f:
            pickle.dump(state, f)
        
        logger.info(f"Saved Agentic Supernet state to {path}")
    
    def load_state(self, path: str) -> None:
        """Load the state of the supernet from a file.
        
        Args:
            path: Path to load the state from
        """
        import pickle
        
        with open(path, 'rb') as f:
            state = pickle.load(f)
        
        self.search_space = state['search_space']
        self.templates = state['templates']
        self.controller = SupernetController()
        self.controller.set_state(state['controller_state'])
        self.sampler = ArchitectureSampler(self.search_space)
        
        logger.info(f"Loaded Agentic Supernet state from {path}")
    
    def _load_default_templates(self) -> List[ArchitectureModel]:
        """Load default architecture templates.
        
        Returns:
            List of template ArchitectureModel objects
        """
        templates = [
            ArchitectureTemplates.create_hierarchical_template(),
            ArchitectureTemplates.create_star_template(),
            ArchitectureTemplates.create_mesh_template(),
            ArchitectureTemplates.create_pipeline_template(),
            ArchitectureTemplates.create_hybrid_template()
        ]
        
        logger.info(f"Loaded {len(templates)} default architecture templates")
        return templates
    
    def _infer_complexity(self, task: TaskModel) -> float:
        """Infer the complexity of a task.
        
        Args:
            task: TaskModel describing the task requirements
            
        Returns:
            Complexity value between 0.0 and 1.0
        """
        # Start with base complexity
        complexity = 0.5
        
        # Adjust based on task properties
        if task.complexity_score is not None:
            # If task has an explicit complexity score, use it
            return min(1.0, max(0.0, task.complexity_score))
        
        # Otherwise infer from task properties
        
        # Adjust based on required capabilities
        if task.required_capabilities:
            # More capabilities generally means more complex task
            capability_factor = min(1.0, len(task.required_capabilities) / 10)
            complexity += capability_factor * 0.2
        
        # Adjust based on expected steps
        if task.expected_steps:
            # More steps generally means more complex task
            steps_factor = min(1.0, task.expected_steps / 20)
            complexity += steps_factor * 0.2
        
        # Adjust based on domain
        if task.domain:
            # Some domains are inherently more complex
            complex_domains = ['research', 'coding', 'mathematics', 'reasoning', 'creative']
            domain_matches = sum(domain in task.domain.lower() for domain in complex_domains)
            domain_factor = min(1.0, domain_matches / len(complex_domains))
            complexity += domain_factor * 0.1
        
        # Ensure complexity is between 0 and 1
        return min(1.0, max(0.0, complexity))
