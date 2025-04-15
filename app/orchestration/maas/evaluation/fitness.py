"""
Fitness function for Multi-agent Architecture Search (MaAS).

This module provides functionality for calculating fitness scores for agent architectures.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import logging

from ..models import TaskModel, ArchitectureModel, MetricType, EvaluationResult
from .metrics import MetricsCalculator

logger = logging.getLogger(__name__)

class FitnessFunction:
    """Calculates fitness scores for agent architectures based on performance metrics."""
    
    def __init__(self, metrics_calculator: Optional[MetricsCalculator] = None):
        """Initialize the fitness function.
        
        Args:
            metrics_calculator: Optional MetricsCalculator instance for metric normalization
        """
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        
        # Define default weights for metric categories
        self.category_weights = {
            MetricType.ACCURACY: 0.4,    # Metrics related to task success and quality
            MetricType.RESOURCE: 0.3,    # Metrics related to resource usage
            MetricType.LATENCY: 0.2,     # Metrics related to time and speed
            MetricType.OTHER: 0.1        # Other metrics
        }
        
        # Define default metric weights within each category
        self.metric_weights = {
            # Accuracy metrics
            "success": 0.5,
            "quality_score": 0.3,
            "complexity_efficiency": 0.2,
            
            # Resource metrics
            "token_usage": 0.4,
            "cost": 0.4,
            "cost_effectiveness": 0.2,
            
            # Latency metrics
            "execution_time": 0.5,
            "iterations": 0.3,
            "speed": 0.2,
            
            # Other metrics
            "message_count": 0.3,
            "average_response_time": 0.3,
            "architecture_complexity": 0.4
        }
    
    def calculate_fitness(self, metrics: Dict[str, float], 
                         task: Optional[TaskModel] = None) -> float:
        """Calculate a fitness score from performance metrics.
        
        Args:
            metrics: Dictionary of performance metrics
            task: Optional TaskModel for task-specific weighting
            
        Returns:
            Fitness score between 0 and 1
        """
        # Normalize metrics
        normalized_metrics = self.metrics_calculator.normalize_metrics(metrics)
        
        # Adjust weights based on task if provided
        weights = self._adjust_weights_for_task(task)
        
        # Calculate weighted score by category
        category_scores = {}
        
        for category, category_weight in self.category_weights.items():
            # Get metrics for this category
            category_metrics = {}
            for metric_name, metric_value in normalized_metrics.items():
                if self.metrics_calculator.get_metric_type(metric_name) == category:
                    category_metrics[metric_name] = metric_value
            
            # Calculate weighted score for this category
            if category_metrics:
                category_score = 0.0
                total_weight = 0.0
                
                for metric_name, metric_value in category_metrics.items():
                    # Get weight for this metric
                    metric_weight = weights.get(metric_name, 0.1)  # Default weight
                    category_score += metric_value * metric_weight
                    total_weight += metric_weight
                
                # Normalize by total weight
                if total_weight > 0:
                    category_scores[category] = category_score / total_weight
                else:
                    category_scores[category] = 0.0
            else:
                category_scores[category] = 0.0
        
        # Calculate overall fitness score
        fitness = 0.0
        total_weight = 0.0
        
        for category, score in category_scores.items():
            category_weight = self.category_weights[category]
            fitness += score * category_weight
            total_weight += category_weight
        
        # Normalize by total weight
        if total_weight > 0:
            fitness = fitness / total_weight
        
        logger.info(f"Calculated fitness score: {fitness:.4f}")
        return fitness
    
    def create_evaluation_result(self, architecture: ArchitectureModel, 
                               task: TaskModel, 
                               metrics: Dict[str, float]) -> EvaluationResult:
        """Create an evaluation result from metrics.
        
        Args:
            architecture: ArchitectureModel that was evaluated
            task: TaskModel that was executed
            metrics: Dictionary of performance metrics
            
        Returns:
            EvaluationResult object
        """
        # Calculate fitness score
        fitness = self.calculate_fitness(metrics, task)
        
        # Create evaluation result
        result = EvaluationResult(
            architecture_id=architecture.id,
            architecture_name=architecture.name,
            task_id=task.id if task else None,
            fitness=fitness,
            metrics=metrics,
            timestamp=None  # Will be set automatically
        )
        
        return result
    
    def _adjust_weights_for_task(self, task: Optional[TaskModel] = None) -> Dict[str, float]:
        """Adjust metric weights based on task characteristics.
        
        Args:
            task: Optional TaskModel for task-specific weighting
            
        Returns:
            Dictionary of adjusted metric weights
        """
        # Start with default weights
        weights = self.metric_weights.copy()
        
        if not task:
            return weights
        
        # Adjust weights based on task domain
        if task.domain:
            domain = task.domain.lower()
            
            if "research" in domain:
                # For research tasks, prioritize accuracy and quality
                weights["quality_score"] = weights.get("quality_score", 0.3) * 1.5
                weights["success"] = weights.get("success", 0.5) * 1.2
                
            elif "coding" in domain or "development" in domain:
                # For coding tasks, prioritize success and efficiency
                weights["success"] = weights.get("success", 0.5) * 1.3
                weights["complexity_efficiency"] = weights.get("complexity_efficiency", 0.2) * 1.5
                
            elif "creative" in domain:
                # For creative tasks, prioritize quality and creativity
                weights["quality_score"] = weights.get("quality_score", 0.3) * 1.8
                
            elif "analysis" in domain or "data" in domain:
                # For analytical tasks, prioritize accuracy and efficiency
                weights["success"] = weights.get("success", 0.5) * 1.4
                weights["efficiency"] = weights.get("efficiency", 0.2) * 1.6
        
        # Adjust weights based on task complexity
        if task.complexity_score is not None:
            complexity = task.complexity_score
            
            if complexity > 0.7:  # High complexity
                # For complex tasks, prioritize success and quality over speed
                weights["success"] = weights.get("success", 0.5) * 1.3
                weights["quality_score"] = weights.get("quality_score", 0.3) * 1.2
                weights["execution_time"] = weights.get("execution_time", 0.5) * 0.8
                
            elif complexity < 0.3:  # Low complexity
                # For simple tasks, prioritize speed and efficiency
                weights["execution_time"] = weights.get("execution_time", 0.5) * 1.3
                weights["speed"] = weights.get("speed", 0.2) * 1.5
        
        # Normalize weights to ensure they sum to appropriate values
        self._normalize_weights(weights)
        
        return weights
    
    def _normalize_weights(self, weights: Dict[str, float]) -> None:
        """Normalize weights to ensure they maintain appropriate proportions.
        
        Args:
            weights: Dictionary of weights to normalize
        """
        # Group metrics by category
        category_metrics = {category: [] for category in self.category_weights}
        
        for metric_name in weights:
            category = self.metrics_calculator.get_metric_type(metric_name)
            category_metrics[category].append(metric_name)
        
        # Normalize weights within each category
        for category, metrics in category_metrics.items():
            if metrics:
                total = sum(weights[metric] for metric in metrics)
                if total > 0:
                    for metric in metrics:
                        weights[metric] = weights[metric] / total
