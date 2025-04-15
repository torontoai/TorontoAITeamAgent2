"""
Supernet Controller for Multi-agent Architecture Search (MaAS).

This module provides the controller for the Agentic Supernet, which learns to sample
architectures based on task requirements and performance feedback.
"""

from typing import List, Optional, Dict, Any, Tuple, Union
import numpy as np
import random
import logging
import json
from collections import defaultdict

from ..models import ArchitectureModel, TaskModel, EvaluationResult, SearchSpace
from .architecture_sampler import ArchitectureSampler

logger = logging.getLogger(__name__)

class SupernetController:
    """Controller for the Agentic Supernet that learns to sample architectures."""
    
    def __init__(self):
        """Initialize the supernet controller."""
        # Templates are stored as (template, performance_history) pairs
        self.templates = []
        self.template_performance = {}  # Maps template_id to performance metrics
        self.task_history = {}  # Maps task_id to list of (template_id, performance) pairs
        self.learning_rate = 0.1
        self.exploration_rate = 0.2  # Probability of random exploration
        self.temperature = 1.0  # Temperature for softmax sampling
        
        # Task similarity model (simple TF-IDF for now)
        self.task_features = {}  # Maps task_id to feature vector
        
        # Performance history for online learning
        self.performance_history = []
    
    def sample(self, task: TaskModel, search_space: SearchSpace, 
              complexity: float = 0.5) -> ArchitectureModel:
        """Sample an architecture based on task requirements.
        
        Args:
            task: TaskModel describing the task requirements
            search_space: SearchSpace defining the architecture constraints
            complexity: Complexity factor (0.0 to 1.0) affecting the architecture
            
        Returns:
            ArchitectureModel sampled from the supernet
        """
        # Extract task features
        task_features = self._extract_task_features(task)
        
        # If no trained model exists or with some probability, use exploration
        if not self.templates or random.random() < self.exploration_rate:
            return self._exploration_sampling(task, search_space, complexity)
        
        # Otherwise, use the trained model to sample
        return self._exploitation_sampling(task, search_space, complexity)
    
    def update(self, architecture: ArchitectureModel, evaluation_result: EvaluationResult) -> None:
        """Update the controller based on architecture performance.
        
        Args:
            architecture: ArchitectureModel that was evaluated
            evaluation_result: EvaluationResult from the evaluation
        """
        # Store the performance result
        self.performance_history.append((architecture, evaluation_result))
        
        # If this is a template, update its performance history
        for template, _ in self.templates:
            if template.id == architecture.id:
                if template.id not in self.template_performance:
                    self.template_performance[template.id] = []
                self.template_performance[template.id].append(evaluation_result.fitness)
                break
        
        # Update task history if task_id is available
        if evaluation_result.task_id:
            if evaluation_result.task_id not in self.task_history:
                self.task_history[evaluation_result.task_id] = []
            
            # Store the template_id and performance
            template_id = self._find_closest_template(architecture)
            if template_id:
                self.task_history[evaluation_result.task_id].append(
                    (template_id, evaluation_result.fitness))
        
        # Update the model based on the new data
        self._update_model()
    
    def add_template(self, template: ArchitectureModel) -> None:
        """Add a template architecture to the controller.
        
        Args:
            template: Template architecture to add
        """
        # Check if template already exists
        for existing_template, _ in self.templates:
            if existing_template.id == template.id:
                logger.warning(f"Template {template.id} already exists, skipping")
                return
        
        # Add the template with initial weight
        self.templates.append((template, 1.0))
        logger.info(f"Added template {template.name} to controller")
    
    def get_template_distribution(self, task: TaskModel) -> Dict[str, float]:
        """Get the probability distribution over architecture templates for a given task.
        
        Args:
            task: TaskModel describing the task requirements
            
        Returns:
            Dictionary mapping template names to probabilities
        """
        if not self.templates:
            return {}
        
        # Extract task features
        task_features = self._extract_task_features(task)
        
        # Calculate template scores based on task similarity and performance
        template_scores = {}
        for template, weight in self.templates:
            # Calculate score based on template weight and task similarity
            template_score = weight
            
            # Adjust score based on task similarity if we have history
            if task.id in self.task_history:
                similarity_bonus = self._calculate_task_template_similarity(task, template)
                template_score *= (1.0 + similarity_bonus)
            
            template_scores[template.name] = template_score
        
        # Normalize scores to probabilities
        total_score = sum(template_scores.values())
        if total_score > 0:
            template_probs = {name: score / total_score 
                             for name, score in template_scores.items()}
        else:
            # Equal probabilities if no scores
            template_probs = {template.name: 1.0 / len(self.templates) 
                             for template, _ in self.templates}
        
        return template_probs
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the controller for serialization.
        
        Returns:
            Dictionary containing the controller state
        """
        state = {
            'templates': [(template.id, weight) for template, weight in self.templates],
            'template_performance': self.template_performance,
            'task_history': self.task_history,
            'learning_rate': self.learning_rate,
            'exploration_rate': self.exploration_rate,
            'temperature': self.temperature,
            'task_features': self.task_features
        }
        return state
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the controller state from a serialized state.
        
        Args:
            state: Dictionary containing the controller state
        """
        # We need to reconstruct templates from IDs
        template_weights = state.get('templates', [])
        self.templates = []
        
        # Other state variables
        self.template_performance = state.get('template_performance', {})
        self.task_history = state.get('task_history', {})
        self.learning_rate = state.get('learning_rate', 0.1)
        self.exploration_rate = state.get('exploration_rate', 0.2)
        self.temperature = state.get('temperature', 1.0)
        self.task_features = state.get('task_features', {})
    
    def _exploration_sampling(self, task: TaskModel, search_space: SearchSpace, 
                             complexity: float) -> ArchitectureModel:
        """Sample an architecture using exploration strategies.
        
        Args:
            task: TaskModel describing the task requirements
            search_space: SearchSpace defining the architecture constraints
            complexity: Complexity factor (0.0 to 1.0)
            
        Returns:
            ArchitectureModel sampled from exploration
        """
        # Create a sampler
        sampler = ArchitectureSampler(search_space)
        
        # With some probability, use a template if available
        if self.templates and random.random() < 0.7:
            # Choose a random template
            template, _ = random.choice(self.templates)
            
            # Sample from the template with mutation
            return sampler.sample_from_template(template, task, mutation_rate=0.3)
        else:
            # Generate a completely random architecture
            return sampler.sample_random(task, complexity)
    
    def _exploitation_sampling(self, task: TaskModel, search_space: SearchSpace, 
                              complexity: float) -> ArchitectureModel:
        """Sample an architecture using the learned model.
        
        Args:
            task: TaskModel describing the task requirements
            search_space: SearchSpace defining the architecture constraints
            complexity: Complexity factor (0.0 to 1.0)
            
        Returns:
            ArchitectureModel sampled based on learned patterns
        """
        # Get template distribution for this task
        template_probs = self.get_template_distribution(task)
        
        # Create a sampler
        sampler = ArchitectureSampler(search_space)
        
        # Choose a template based on probabilities
        if template_probs:
            templates = [template for template, _ in self.templates]
            template_names = [template.name for template in templates]
            probs = [template_probs.get(name, 0.0) for name in template_names]
            
            # Apply temperature to probabilities
            if self.temperature != 1.0:
                probs = np.array(probs) ** (1.0 / self.temperature)
                probs = probs / np.sum(probs)
            
            # Sample a template
            template_idx = np.random.choice(len(templates), p=probs)
            template = templates[template_idx]
            
            # Sample from the template with mutation rate based on complexity
            mutation_rate = 0.1 + complexity * 0.4  # 0.1 to 0.5
            return sampler.sample_from_template(template, task, mutation_rate=mutation_rate)
        else:
            # Fallback to random sampling
            return sampler.sample_random(task, complexity)
    
    def _extract_task_features(self, task: TaskModel) -> np.ndarray:
        """Extract features from a task for similarity comparison.
        
        Args:
            task: TaskModel to extract features from
            
        Returns:
            Feature vector for the task
        """
        # Simple feature extraction based on task properties
        features = []
        
        # Required capabilities (one-hot encoding)
        capability_features = np.zeros(len(task.required_capabilities) if task.required_capabilities else 0)
        if task.required_capabilities:
            for i, capability in enumerate(task.required_capabilities):
                capability_features[i] = 1.0
        features.extend(capability_features)
        
        # Complexity score
        if task.complexity_score is not None:
            features.append(task.complexity_score)
        else:
            features.append(0.5)  # Default complexity
        
        # Expected steps (normalized)
        if task.expected_steps:
            features.append(min(1.0, task.expected_steps / 20.0))
        else:
            features.append(0.0)
        
        # Domain (simple bag of words)
        domain_features = np.zeros(5)  # Fixed size for simplicity
        if task.domain:
            domains = ['research', 'coding', 'mathematics', 'reasoning', 'creative']
            for i, domain in enumerate(domains):
                if domain in task.domain.lower():
                    domain_features[i] = 1.0
        features.extend(domain_features)
        
        # Store features for this task
        if task.id:
            self.task_features[task.id] = features
        
        return np.array(features)
    
    def _calculate_task_similarity(self, task1_id: str, task2_id: str) -> float:
        """Calculate similarity between two tasks.
        
        Args:
            task1_id: ID of the first task
            task2_id: ID of the second task
            
        Returns:
            Similarity score between 0 and 1
        """
        if task1_id not in self.task_features or task2_id not in self.task_features:
            return 0.0
        
        features1 = self.task_features[task1_id]
        features2 = self.task_features[task2_id]
        
        # Calculate cosine similarity
        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _calculate_task_template_similarity(self, task: TaskModel, template: ArchitectureModel) -> float:
        """Calculate how well a template matches a task based on historical performance.
        
        Args:
            task: TaskModel to check
            template: Template to evaluate
            
        Returns:
            Similarity score (higher is better)
        """
        if not task.id or task.id not in self.task_history:
            return 0.0
        
        # Check if this template has been used for similar tasks
        similarity_score = 0.0
        
        for other_task_id in self.task_history:
            if other_task_id == task.id:
                continue
                
            # Calculate task similarity
            task_similarity = self._calculate_task_similarity(task.id, other_task_id)
            
            # Check if this template was used for the other task
            for template_id, performance in self.task_history[other_task_id]:
                if template_id == template.id:
                    # Weight the performance by task similarity
                    similarity_score += task_similarity * performance
        
        return similarity_score
    
    def _find_closest_template(self, architecture: ArchitectureModel) -> Optional[str]:
        """Find the ID of the template closest to the given architecture.
        
        Args:
            architecture: Architecture to find closest template for
            
        Returns:
            ID of the closest template, or None if no templates
        """
        if not self.templates:
            return None
        
        # Calculate similarity to each template
        max_similarity = -1
        closest_template_id = None
        
        for template, _ in self.templates:
            similarity = self._calculate_architecture_similarity(architecture, template)
            if similarity > max_similarity:
                max_similarity = similarity
                closest_template_id = template.id
        
        return closest_template_id
    
    def _calculate_architecture_similarity(self, arch1: ArchitectureModel, 
                                         arch2: ArchitectureModel) -> float:
        """Calculate similarity between two architectures.
        
        Args:
            arch1: First architecture
            arch2: Second architecture
            
        Returns:
            Similarity score between 0 and 1
        """
        # Calculate Jaccard similarity of agent roles
        roles1 = set(agent.role for agent in arch1.agents)
        roles2 = set(agent.role for agent in arch2.agents)
        
        if not roles1 or not roles2:
            return 0.0
        
        role_similarity = len(roles1.intersection(roles2)) / len(roles1.union(roles2))
        
        # Calculate similarity of agent counts
        count1 = len(arch1.agents)
        count2 = len(arch2.agents)
        count_similarity = 1.0 - abs(count1 - count2) / max(count1, count2, 1)
        
        # Calculate similarity of connection patterns
        # This is a simplified measure based on connection density
        if count1 > 1 and count2 > 1:
            max_conn1 = count1 * (count1 - 1)
            max_conn2 = count2 * (count2 - 1)
            density1 = len(arch1.connections) / max_conn1
            density2 = len(arch2.connections) / max_conn2
            conn_similarity = 1.0 - abs(density1 - density2)
        else:
            conn_similarity = 1.0
        
        # Combine similarities with weights
        return 0.5 * role_similarity + 0.3 * count_similarity + 0.2 * conn_similarity
    
    def _update_model(self) -> None:
        """Update the model based on performance history."""
        if not self.performance_history:
            return
        
        # Update template weights based on performance
        template_performances = defaultdict(list)
        
        # Collect performances by template
        for architecture, evaluation in self.performance_history:
            template_id = self._find_closest_template(architecture)
            if template_id:
                template_performances[template_id].append(evaluation.fitness)
        
        # Update template weights
        for i, (template, weight) in enumerate(self.templates):
            if template.id in template_performances:
                performances = template_performances[template.id]
                avg_performance = sum(performances) / len(performances)
                
                # Update weight using simple moving average
                new_weight = weight * (1 - self.learning_rate) + avg_performance * self.learning_rate
                self.templates[i] = (template, new_weight)
        
        # Normalize weights
        total_weight = sum(weight for _, weight in self.templates)
        if total_weight > 0:
            self.templates = [(template, weight / total_weight) 
                             for template, weight in self.templates]
        
        # Adjust exploration rate based on performance variance
        if len(self.performance_history) > 5:
            performances = [eval_result.fitness for _, eval_result in self.performance_history[-5:]]
            variance = np.var(performances)
            
            # If variance is low, reduce exploration rate
            if variance < 0.01:
                self.exploration_rate = max(0.05, self.exploration_rate * 0.9)
            else:
                # If variance is high, increase exploration rate
                self.exploration_rate = min(0.5, self.exploration_rate * 1.1)
        
        # Clear old history to prevent memory issues
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-50:]
