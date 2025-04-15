"""
Metrics calculator for Multi-agent Architecture Search (MaAS).

This module provides functionality for calculating performance metrics for agent architectures.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
import logging
from datetime import datetime

from ..models import TaskModel, ArchitectureModel, MetricType

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Calculates performance metrics for agent architectures."""
    
    def __init__(self):
        """Initialize the metrics calculator."""
        # Define metric categories and weights
        self.metric_categories = {
            MetricType.ACCURACY: 0.4,    # Metrics related to task success and quality
            MetricType.RESOURCE: 0.3,    # Metrics related to resource usage
            MetricType.LATENCY: 0.2,     # Metrics related to time and speed
            MetricType.OTHER: 0.1        # Other metrics
        }
        
        # Define default metrics for each category
        self.default_metrics = {
            MetricType.ACCURACY: ["success", "quality_score"],
            MetricType.RESOURCE: ["token_usage", "cost"],
            MetricType.LATENCY: ["execution_time", "iterations"],
            MetricType.OTHER: ["message_count"]
        }
        
        # Define metric normalization ranges (min, max, higher_is_better)
        self.metric_ranges = {
            "success": (0.0, 1.0, True),
            "quality_score": (0.0, 1.0, True),
            "token_usage": (0.0, 10000.0, False),
            "cost": (0.0, 10.0, False),
            "execution_time": (0.0, 300.0, False),
            "iterations": (1.0, 50.0, False),
            "message_count": (0.0, 100.0, False),
            "average_response_time": (0.0, 10.0, False)
        }
    
    def calculate_metrics(self, results: Dict[str, Any], 
                         task: TaskModel, 
                         architecture: ArchitectureModel) -> Dict[str, float]:
        """Calculate performance metrics from workflow execution results.
        
        Args:
            results: Results from workflow execution
            task: TaskModel that was executed
            architecture: ArchitectureModel that was used
            
        Returns:
            Dictionary of calculated metrics
        """
        metrics = {}
        
        # Extract basic metrics from results
        self._extract_basic_metrics(metrics, results)
        
        # Extract agent-specific metrics
        self._extract_agent_metrics(metrics, results, architecture)
        
        # Calculate derived metrics
        self._calculate_derived_metrics(metrics, results, task, architecture)
        
        # Log the calculated metrics
        logger.info(f"Calculated {len(metrics)} metrics for architecture '{architecture.name}'")
        
        return metrics
    
    def normalize_metrics(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Normalize metrics to a 0-1 scale for comparison.
        
        Args:
            metrics: Dictionary of raw metrics
            
        Returns:
            Dictionary of normalized metrics
        """
        normalized = {}
        
        for metric_name, value in metrics.items():
            if metric_name in self.metric_ranges:
                min_val, max_val, higher_is_better = self.metric_ranges[metric_name]
                
                # Clip value to range
                value = max(min_val, min(max_val, value))
                
                # Normalize to 0-1 scale
                if max_val > min_val:
                    normalized_value = (value - min_val) / (max_val - min_val)
                    
                    # Invert if lower is better
                    if not higher_is_better:
                        normalized_value = 1.0 - normalized_value
                else:
                    normalized_value = 0.5  # Default if range is invalid
                
                normalized[metric_name] = normalized_value
            else:
                # For unknown metrics, pass through unchanged
                normalized[metric_name] = value
                logger.warning(f"No normalization range defined for metric '{metric_name}'")
        
        return normalized
    
    def get_metric_type(self, metric_name: str) -> MetricType:
        """Determine the type of a metric based on its name.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            MetricType enum value
        """
        metric_name = metric_name.lower()
        
        # Check in default metrics
        for metric_type, metrics in self.default_metrics.items():
            if any(metric.lower() == metric_name for metric in metrics):
                return metric_type
        
        # Check by keyword
        if any(term in metric_name for term in ['accuracy', 'precision', 'recall', 'f1', 'auc', 'success', 'quality']):
            return MetricType.ACCURACY
        
        if any(term in metric_name for term in ['memory', 'cpu', 'gpu', 'resource', 'cost', 'token', 'call']):
            return MetricType.RESOURCE
        
        if any(term in metric_name for term in ['latency', 'time', 'speed', 'duration', 'delay', 'iteration']):
            return MetricType.LATENCY
        
        # Default to OTHER
        return MetricType.OTHER
    
    def _extract_basic_metrics(self, metrics: Dict[str, float], results: Dict[str, Any]) -> None:
        """Extract basic metrics from workflow execution results.
        
        Args:
            metrics: Dictionary to add metrics to
            results: Results from workflow execution
        """
        # Extract execution time
        if 'execution_time' in results:
            metrics['execution_time'] = float(results['execution_time'])
        elif 'start_time' in results and 'end_time' in results:
            # Calculate from timestamps
            start = results['start_time']
            end = results['end_time']
            
            # Convert to datetime if they're strings
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace('Z', '+00:00'))
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace('Z', '+00:00'))
                
            if isinstance(start, datetime) and isinstance(end, datetime):
                metrics['execution_time'] = (end - start).total_seconds()
        
        # Extract iterations
        if 'iterations' in results:
            metrics['iterations'] = float(results['iterations'])
        
        # Extract token usage
        if 'token_usage' in results:
            metrics['token_usage'] = float(results['token_usage'])
        
        # Extract cost
        if 'cost' in results:
            metrics['cost'] = float(results['cost'])
        
        # Extract success metrics
        if 'success' in results:
            metrics['success'] = 1.0 if results['success'] else 0.0
        
        if 'quality_score' in results:
            metrics['quality_score'] = float(results['quality_score'])
        
        # Extract message count
        if 'message_count' in results:
            metrics['message_count'] = float(results['message_count'])
        
        # Extract average response time
        if 'average_response_time' in results:
            metrics['average_response_time'] = float(results['average_response_time'])
    
    def _extract_agent_metrics(self, metrics: Dict[str, float], 
                             results: Dict[str, Any],
                             architecture: ArchitectureModel) -> None:
        """Extract agent-specific metrics from workflow execution results.
        
        Args:
            metrics: Dictionary to add metrics to
            results: Results from workflow execution
            architecture: ArchitectureModel that was used
        """
        if 'agent_metrics' in results:
            agent_metrics = results['agent_metrics']
            
            for agent_id, agent_data in agent_metrics.items():
                # Find the agent in the architecture
                agent = next((a for a in architecture.agents if a.id == agent_id), None)
                
                if agent:
                    # Add agent-specific metrics with agent role as prefix
                    role = agent.role.value.lower()
                    
                    for metric_name, metric_value in agent_data.items():
                        if isinstance(metric_value, (int, float)):
                            metrics[f"{role}_{metric_name}"] = float(metric_value)
    
    def _calculate_derived_metrics(self, metrics: Dict[str, float], 
                                 results: Dict[str, Any],
                                 task: TaskModel,
                                 architecture: ArchitectureModel) -> None:
        """Calculate derived metrics from basic metrics.
        
        Args:
            metrics: Dictionary to add metrics to
            results: Results from workflow execution
            task: TaskModel that was executed
            architecture: ArchitectureModel that was used
        """
        # Calculate efficiency (success / resources)
        if 'success' in metrics and 'token_usage' in metrics and metrics['token_usage'] > 0:
            metrics['efficiency'] = metrics['success'] / (metrics['token_usage'] / 1000.0)
        
        # Calculate speed (success / time)
        if 'success' in metrics and 'execution_time' in metrics and metrics['execution_time'] > 0:
            metrics['speed'] = metrics['success'] / metrics['execution_time']
        
        # Calculate cost-effectiveness (success / cost)
        if 'success' in metrics and 'cost' in metrics and metrics['cost'] > 0:
            metrics['cost_effectiveness'] = metrics['success'] / metrics['cost']
        
        # Calculate architecture complexity score
        complexity = self._calculate_architecture_complexity(architecture)
        metrics['architecture_complexity'] = complexity
        
        # Calculate complexity efficiency (success / complexity)
        if 'success' in metrics and complexity > 0:
            metrics['complexity_efficiency'] = metrics['success'] / complexity
    
    def _calculate_architecture_complexity(self, architecture: ArchitectureModel) -> float:
        """Calculate the complexity of an architecture.
        
        Args:
            architecture: ArchitectureModel to calculate complexity for
            
        Returns:
            Complexity score (higher means more complex)
        """
        # Base complexity from number of agents
        agent_count = len(architecture.agents)
        
        # Connection complexity
        connection_count = len(architecture.connections)
        
        # Calculate maximum possible connections
        max_connections = agent_count * (agent_count - 1) if agent_count > 1 else 1
        
        # Connection density (0-1)
        connection_density = connection_count / max_connections if max_connections > 0 else 0
        
        # Role diversity (0-1)
        unique_roles = len(set(agent.role for agent in architecture.agents))
        role_diversity = unique_roles / agent_count if agent_count > 0 else 0
        
        # Capability diversity (0-1)
        all_capabilities = set()
        for agent in architecture.agents:
            if agent.capabilities:
                all_capabilities.update(agent.capabilities)
        
        capability_diversity = len(all_capabilities) / 30.0  # Normalize by approximate max capabilities
        
        # Calculate weighted complexity score
        complexity = (
            0.3 * agent_count / 10.0 +  # Normalize by assuming max 10 agents
            0.3 * connection_density +
            0.2 * role_diversity +
            0.2 * capability_diversity
        )
        
        return min(1.0, complexity)  # Cap at 1.0
