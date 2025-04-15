"""
Architecture evaluator for Multi-agent Architecture Search (MaAS).

This module provides functionality for evaluating agent architectures based on performance metrics.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import json
import os
from datetime import datetime

from ..models import TaskModel, ArchitectureModel, EvaluationResult
from .metrics import MetricsCalculator
from .fitness import FitnessFunction

logger = logging.getLogger(__name__)

class ArchitectureEvaluator:
    """Evaluates agent architectures based on performance metrics."""
    
    def __init__(self, metrics_calculator: Optional[MetricsCalculator] = None,
                fitness_function: Optional[FitnessFunction] = None,
                results_dir: Optional[str] = None):
        """Initialize the architecture evaluator.
        
        Args:
            metrics_calculator: Optional MetricsCalculator instance
            fitness_function: Optional FitnessFunction instance
            results_dir: Optional directory to store evaluation results
        """
        self.metrics_calculator = metrics_calculator or MetricsCalculator()
        self.fitness_function = fitness_function or FitnessFunction(self.metrics_calculator)
        self.results_dir = results_dir or os.path.join(os.path.dirname(__file__), "results")
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Store evaluation history
        self.evaluation_history = []
    
    def evaluate_architecture(self, architecture: ArchitectureModel, 
                             task: TaskModel,
                             results: Optional[Dict[str, Any]] = None,
                             metrics: Optional[Dict[str, float]] = None) -> EvaluationResult:
        """Evaluate an architecture based on workflow execution results or provided metrics.
        
        Args:
            architecture: ArchitectureModel to evaluate
            task: TaskModel that was executed
            results: Optional workflow execution results
            metrics: Optional pre-calculated metrics
            
        Returns:
            EvaluationResult with fitness score and metrics
        """
        # Calculate metrics if not provided
        if metrics is None:
            if results is None:
                raise ValueError("Either results or metrics must be provided")
            
            metrics = self.metrics_calculator.calculate_metrics(results, task, architecture)
        
        # Create evaluation result
        evaluation_result = self.fitness_function.create_evaluation_result(
            architecture=architecture,
            task=task,
            metrics=metrics
        )
        
        # Set timestamp
        evaluation_result.timestamp = datetime.now().isoformat()
        
        # Store in history
        self.evaluation_history.append(evaluation_result)
        
        # Save to file
        self._save_evaluation_result(evaluation_result)
        
        logger.info(f"Evaluated architecture '{architecture.name}' with fitness {evaluation_result.fitness:.4f}")
        return evaluation_result
    
    def compare_architectures(self, evaluation_results: List[EvaluationResult]) -> Dict[str, Any]:
        """Compare multiple architecture evaluation results.
        
        Args:
            evaluation_results: List of EvaluationResult objects to compare
            
        Returns:
            Dictionary with comparison results
        """
        if not evaluation_results:
            return {"error": "No evaluation results provided"}
        
        # Sort by fitness
        sorted_results = sorted(evaluation_results, key=lambda x: x.fitness, reverse=True)
        
        # Extract key information
        comparison = {
            "best_architecture": {
                "name": sorted_results[0].architecture_name,
                "id": sorted_results[0].architecture_id,
                "fitness": sorted_results[0].fitness
            },
            "rankings": [
                {
                    "rank": i+1,
                    "name": result.architecture_name,
                    "id": result.architecture_id,
                    "fitness": result.fitness
                }
                for i, result in enumerate(sorted_results)
            ],
            "metric_comparison": {}
        }
        
        # Compare key metrics
        all_metrics = set()
        for result in evaluation_results:
            all_metrics.update(result.metrics.keys())
        
        for metric in all_metrics:
            comparison["metric_comparison"][metric] = {
                result.architecture_name: result.metrics.get(metric, None)
                for result in evaluation_results
                if metric in result.metrics
            }
        
        return comparison
    
    def get_best_architecture(self, task_id: Optional[str] = None) -> Optional[EvaluationResult]:
        """Get the best architecture based on evaluation history.
        
        Args:
            task_id: Optional task ID to filter by
            
        Returns:
            EvaluationResult for the best architecture, or None if no evaluations
        """
        if not self.evaluation_history:
            return None
        
        # Filter by task if provided
        filtered_history = self.evaluation_history
        if task_id:
            filtered_history = [result for result in filtered_history if result.task_id == task_id]
        
        if not filtered_history:
            return None
        
        # Sort by fitness and return the best
        return max(filtered_history, key=lambda x: x.fitness)
    
    def load_evaluation_history(self) -> List[EvaluationResult]:
        """Load evaluation history from saved files.
        
        Returns:
            List of EvaluationResult objects
        """
        history = []
        
        if not os.path.exists(self.results_dir):
            return history
        
        # Load all JSON files in the results directory
        for filename in os.listdir(self.results_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(self.results_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    # Create EvaluationResult from data
                    result = EvaluationResult(
                        architecture_id=data.get("architecture_id"),
                        architecture_name=data.get("architecture_name"),
                        task_id=data.get("task_id"),
                        fitness=data.get("fitness", 0.0),
                        metrics=data.get("metrics", {}),
                        timestamp=data.get("timestamp")
                    )
                    
                    history.append(result)
                except Exception as e:
                    logger.error(f"Error loading evaluation result from {file_path}: {e}")
        
        # Sort by timestamp
        history.sort(key=lambda x: x.timestamp if x.timestamp else "")
        
        # Update internal history
        self.evaluation_history = history
        
        return history
    
    def _save_evaluation_result(self, evaluation_result: EvaluationResult) -> None:
        """Save an evaluation result to a file.
        
        Args:
            evaluation_result: EvaluationResult to save
        """
        if not self.results_dir:
            return
        
        # Create a filename based on architecture and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arch_name = evaluation_result.architecture_name.replace(" ", "_")
        filename = f"{arch_name}_{timestamp}.json"
        
        file_path = os.path.join(self.results_dir, filename)
        
        # Convert to dictionary
        data = {
            "architecture_id": evaluation_result.architecture_id,
            "architecture_name": evaluation_result.architecture_name,
            "task_id": evaluation_result.task_id,
            "fitness": evaluation_result.fitness,
            "metrics": evaluation_result.metrics,
            "timestamp": evaluation_result.timestamp
        }
        
        # Save to file
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved evaluation result to {file_path}")
        except Exception as e:
            logger.error(f"Error saving evaluation result to {file_path}: {e}")
    
    def generate_evaluation_report(self, evaluation_results: Optional[List[EvaluationResult]] = None) -> Dict[str, Any]:
        """Generate a comprehensive evaluation report.
        
        Args:
            evaluation_results: Optional list of EvaluationResult objects to include in the report
            
        Returns:
            Dictionary with report data
        """
        # Use provided results or load from history
        results = evaluation_results or self.evaluation_history
        
        if not results:
            return {"error": "No evaluation results available"}
        
        # Basic statistics
        num_architectures = len({result.architecture_id for result in results})
        num_tasks = len({result.task_id for result in results if result.task_id})
        
        # Calculate average fitness
        avg_fitness = sum(result.fitness for result in results) / len(results)
        
        # Find best and worst architectures
        best_result = max(results, key=lambda x: x.fitness)
        worst_result = min(results, key=lambda x: x.fitness)
        
        # Group by task
        task_results = {}
        for result in results:
            if result.task_id:
                if result.task_id not in task_results:
                    task_results[result.task_id] = []
                task_results[result.task_id].append(result)
        
        # Find best architecture for each task
        best_by_task = {}
        for task_id, task_eval_results in task_results.items():
            best_result = max(task_eval_results, key=lambda x: x.fitness)
            best_by_task[task_id] = {
                "architecture_name": best_result.architecture_name,
                "architecture_id": best_result.architecture_id,
                "fitness": best_result.fitness
            }
        
        # Compile report
        report = {
            "summary": {
                "num_architectures": num_architectures,
                "num_tasks": num_tasks,
                "num_evaluations": len(results),
                "avg_fitness": avg_fitness
            },
            "best_architecture": {
                "name": best_result.architecture_name,
                "id": best_result.architecture_id,
                "fitness": best_result.fitness,
                "metrics": best_result.metrics
            },
            "worst_architecture": {
                "name": worst_result.architecture_name,
                "id": worst_result.architecture_id,
                "fitness": worst_result.fitness,
                "metrics": worst_result.metrics
            },
            "best_by_task": best_by_task,
            "recent_evaluations": [
                {
                    "architecture_name": result.architecture_name,
                    "task_id": result.task_id,
                    "fitness": result.fitness,
                    "timestamp": result.timestamp
                }
                for result in sorted(results, key=lambda x: x.timestamp if x.timestamp else "", reverse=True)[:10]
            ]
        }
        
        return report
