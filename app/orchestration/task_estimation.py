"""
Task Estimation Framework for TORONTO AI TEAM AGENT

This module provides a comprehensive framework for estimating task completion times,
enabling agents to accurately predict how long tasks will take and communicate
their estimated time of arrival (ETA) to project managers and stakeholders.

Features:
- Task complexity analysis
- Historical performance tracking
- Agent capability profiling
- Dependency-aware estimation
- Confidence intervals for estimates
- Automatic adjustment based on actual performance
"""

import logging
import time
import json
import os
import math
import statistics
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum
from dataclasses import dataclass
import uuid
import datetime

# Set up logging
logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels."""
    TRIVIAL = 1
    SIMPLE = 2
    MODERATE = 3
    COMPLEX = 4
    VERY_COMPLEX = 5


class TaskType(Enum):
    """Types of tasks."""
    CODING = "coding"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    DESIGN = "design"
    TESTING = "testing"
    REVIEW = "review"
    PLANNING = "planning"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class TaskStatus(Enum):
    """Task status values."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    DELAYED = "delayed"


@dataclass
class TaskEstimate:
    """Represents a task time estimate."""
    task_id: str
    agent_id: str
    estimated_duration: float  # In hours
    confidence_level: float  # 0.0 to 1.0
    lower_bound: float  # In hours
    upper_bound: float  # In hours
    estimated_start_time: Optional[float] = None  # Unix timestamp
    estimated_completion_time: Optional[float] = None  # Unix timestamp
    actual_start_time: Optional[float] = None  # Unix timestamp
    actual_completion_time: Optional[float] = None  # Unix timestamp
    created_at: float = time.time()  # Unix timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "estimated_duration": self.estimated_duration,
            "confidence_level": self.confidence_level,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "estimated_start_time": self.estimated_start_time,
            "estimated_completion_time": self.estimated_completion_time,
            "actual_start_time": self.actual_start_time,
            "actual_completion_time": self.actual_completion_time,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskEstimate':
        """Create from dictionary."""
        return cls(
            task_id=data["task_id"],
            agent_id=data["agent_id"],
            estimated_duration=data["estimated_duration"],
            confidence_level=data["confidence_level"],
            lower_bound=data["lower_bound"],
            upper_bound=data["upper_bound"],
            estimated_start_time=data.get("estimated_start_time"),
            estimated_completion_time=data.get("estimated_completion_time"),
            actual_start_time=data.get("actual_start_time"),
            actual_completion_time=data.get("actual_completion_time"),
            created_at=data.get("created_at", time.time())
        )
    
    def get_eta(self) -> Optional[str]:
        """
        Get the estimated time of arrival (ETA) as a formatted string.
        
        Returns:
            Formatted ETA string or None if not available
        """
        if self.estimated_completion_time is None:
            return None
        
        eta_datetime = datetime.datetime.fromtimestamp(self.estimated_completion_time)
        return eta_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    def get_time_remaining(self) -> Optional[float]:
        """
        Get the estimated time remaining in hours.
        
        Returns:
            Time remaining in hours or None if not available
        """
        if self.estimated_completion_time is None:
            return None
        
        time_remaining = self.estimated_completion_time - time.time()
        return max(0, time_remaining / 3600)  # Convert seconds to hours
    
    def get_progress_percentage(self) -> Optional[float]:
        """
        Get the estimated progress percentage.
        
        Returns:
            Progress percentage (0-100) or None if not available
        """
        if self.estimated_start_time is None or self.estimated_completion_time is None:
            return None
        
        total_duration = self.estimated_completion_time - self.estimated_start_time
        if total_duration <= 0:
            return 100.0
        
        elapsed_time = time.time() - self.estimated_start_time
        progress = min(100.0, (elapsed_time / total_duration) * 100.0)
        return max(0.0, progress)
    
    def update_actual_start(self) -> None:
        """Update the actual start time to now."""
        self.actual_start_time = time.time()
    
    def update_actual_completion(self) -> None:
        """Update the actual completion time to now."""
        self.actual_completion_time = time.time()
    
    def get_accuracy(self) -> Optional[float]:
        """
        Calculate the accuracy of the estimate.
        
        Returns:
            Accuracy as a percentage (0-100) or None if not available
        """
        if self.actual_completion_time is None or self.actual_start_time is None:
            return None
        
        actual_duration = (self.actual_completion_time - self.actual_start_time) / 3600  # Convert to hours
        
        if actual_duration == 0:
            return 100.0 if self.estimated_duration == 0 else 0.0
        
        error = abs(self.estimated_duration - actual_duration) / actual_duration
        accuracy = max(0.0, 100.0 * (1.0 - error))
        
        return accuracy


@dataclass
class Task:
    """Represents a task with estimation data."""
    id: str
    title: str
    description: str
    type: TaskType
    complexity: TaskComplexity
    status: TaskStatus
    assigned_agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    dependencies: List[str] = None  # List of task IDs
    estimate: Optional[TaskEstimate] = None
    created_at: float = time.time()  # Unix timestamp
    updated_at: float = time.time()  # Unix timestamp
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type.value,
            "complexity": self.complexity.value,
            "status": self.status.value,
            "assigned_agent_id": self.assigned_agent_id,
            "parent_task_id": self.parent_task_id,
            "dependencies": self.dependencies,
            "estimate": self.estimate.to_dict() if self.estimate else None,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create from dictionary."""
        estimate = TaskEstimate.from_dict(data["estimate"]) if data.get("estimate") else None
        
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            type=TaskType(data["type"]),
            complexity=TaskComplexity(data["complexity"]) if isinstance(data["complexity"], int) else TaskComplexity[data["complexity"]],
            status=TaskStatus(data["status"]),
            assigned_agent_id=data.get("assigned_agent_id"),
            parent_task_id=data.get("parent_task_id"),
            dependencies=data.get("dependencies", []),
            estimate=estimate,
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
    
    def update_status(self, status: TaskStatus) -> None:
        """
        Update the task status.
        
        Args:
            status: New status
        """
        self.status = status
        self.updated_at = time.time()
        
        # Update estimate timestamps based on status
        if self.estimate:
            if status == TaskStatus.IN_PROGRESS and self.estimate.actual_start_time is None:
                self.estimate.update_actual_start()
            elif status == TaskStatus.COMPLETED and self.estimate.actual_completion_time is None:
                self.estimate.update_actual_completion()


@dataclass
class AgentPerformanceProfile:
    """Represents an agent's performance profile for estimation."""
    agent_id: str
    task_type_performance: Dict[str, Dict[str, float]] = None  # TaskType -> {avg_duration, std_dev, count}
    complexity_performance: Dict[int, Dict[str, float]] = None  # TaskComplexity -> {avg_duration, std_dev, count}
    overall_accuracy: float = 0.0
    total_tasks_completed: int = 0
    created_at: float = time.time()  # Unix timestamp
    updated_at: float = time.time()  # Unix timestamp
    
    def __post_init__(self):
        if self.task_type_performance is None:
            self.task_type_performance = {}
        if self.complexity_performance is None:
            self.complexity_performance = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "task_type_performance": self.task_type_performance,
            "complexity_performance": {str(k): v for k, v in self.complexity_performance.items()},
            "overall_accuracy": self.overall_accuracy,
            "total_tasks_completed": self.total_tasks_completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentPerformanceProfile':
        """Create from dictionary."""
        # Convert complexity keys back to integers
        complexity_performance = {}
        for k, v in data.get("complexity_performance", {}).items():
            try:
                complexity_performance[int(k)] = v
            except ValueError:
                complexity_performance[k] = v
        
        return cls(
            agent_id=data["agent_id"],
            task_type_performance=data.get("task_type_performance", {}),
            complexity_performance=complexity_performance,
            overall_accuracy=data.get("overall_accuracy", 0.0),
            total_tasks_completed=data.get("total_tasks_completed", 0),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time())
        )
    
    def update_with_task(self, task: Task) -> None:
        """
        Update the performance profile with a completed task.
        
        Args:
            task: Completed task with actual duration
        """
        if task.status != TaskStatus.COMPLETED or not task.estimate or not task.estimate.actual_completion_time:
            return
        
        # Calculate actual duration in hours
        actual_duration = (task.estimate.actual_completion_time - task.estimate.actual_start_time) / 3600
        
        # Update task type performance
        task_type = task.type.value
        if task_type not in self.task_type_performance:
            self.task_type_performance[task_type] = {"avg_duration": 0.0, "std_dev": 0.0, "count": 0}
        
        type_perf = self.task_type_performance[task_type]
        new_count = type_perf["count"] + 1
        new_avg = ((type_perf["avg_duration"] * type_perf["count"]) + actual_duration) / new_count
        
        # Update standard deviation (simplified approach)
        if new_count > 1:
            variance = type_perf["std_dev"] ** 2
            new_variance = variance + ((actual_duration - type_perf["avg_duration"]) * (actual_duration - new_avg)) / new_count
            new_std_dev = math.sqrt(max(0, new_variance))
        else:
            new_std_dev = 0.0
        
        type_perf["avg_duration"] = new_avg
        type_perf["std_dev"] = new_std_dev
        type_perf["count"] = new_count
        
        # Update complexity performance
        complexity = task.complexity.value
        if complexity not in self.complexity_performance:
            self.complexity_performance[complexity] = {"avg_duration": 0.0, "std_dev": 0.0, "count": 0}
        
        comp_perf = self.complexity_performance[complexity]
        new_count = comp_perf["count"] + 1
        new_avg = ((comp_perf["avg_duration"] * comp_perf["count"]) + actual_duration) / new_count
        
        # Update standard deviation (simplified approach)
        if new_count > 1:
            variance = comp_perf["std_dev"] ** 2
            new_variance = variance + ((actual_duration - comp_perf["avg_duration"]) * (actual_duration - new_avg)) / new_count
            new_std_dev = math.sqrt(max(0, new_variance))
        else:
            new_std_dev = 0.0
        
        comp_perf["avg_duration"] = new_avg
        comp_perf["std_dev"] = new_std_dev
        comp_perf["count"] = new_count
        
        # Update overall accuracy
        accuracy = task.estimate.get_accuracy() or 0.0
        total_accuracy = (self.overall_accuracy * self.total_tasks_completed) + accuracy
        self.total_tasks_completed += 1
        self.overall_accuracy = total_accuracy / self.total_tasks_completed
        
        # Update timestamp
        self.updated_at = time.time()


class TaskEstimationFramework:
    """
    Framework for estimating task completion times.
    """
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the task estimation framework.
        
        Args:
            storage_dir: Directory for storing estimation data (if None, will use a temporary directory)
        """
        # Set storage directory
        if storage_dir:
            self.storage_dir = storage_dir
            os.makedirs(self.storage_dir, exist_ok=True)
        else:
            self.storage_dir = os.path.join(os.getcwd(), "task_estimation_data")
            os.makedirs(self.storage_dir, exist_ok=True)
        
        # Initialize data stores
        self.tasks: Dict[str, Task] = {}
        self.agent_profiles: Dict[str, AgentPerformanceProfile] = {}
        
        # Load existing data if available
        self._load_data()
    
    def _load_data(self) -> None:
        """Load existing data from storage."""
        # Load tasks
        tasks_file = os.path.join(self.storage_dir, "tasks.json")
        if os.path.exists(tasks_file):
            try:
                with open(tasks_file, "r") as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        task = Task.from_dict(task_data)
                        self.tasks[task.id] = task
            except Exception as e:
                logger.error(f"Error loading tasks data: {str(e)}")
        
        # Load agent profiles
        profiles_file = os.path.join(self.storage_dir, "agent_profiles.json")
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, "r") as f:
                    profiles_data = json.load(f)
                    for profile_data in profiles_data:
                        profile = AgentPerformanceProfile.from_dict(profile_data)
                        self.agent_profiles[profile.agent_id] = profile
            except Exception as e:
                logger.error(f"Error loading agent profiles data: {str(e)}")
    
    def _save_data(self) -> None:
        """Save data to storage."""
        # Save tasks
        tasks_file = os.path.join(self.storage_dir, "tasks.json")
        try:
            with open(tasks_file, "w") as f:
                tasks_data = [task.to_dict() for task in self.tasks.values()]
                json.dump(tasks_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tasks data: {str(e)}")
        
        # Save agent profiles
        profiles_file = os.path.join(self.storage_dir, "agent_profiles.json")
        try:
            with open(profiles_file, "w") as f:
                profiles_data = [profile.to_dict() for profile in self.agent_profiles.values()]
                json.dump(profiles_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving agent profiles data: {str(e)}")
    
    def create_task(self, 
                   title: str, 
                   description: str, 
                   task_type: TaskType,
                   complexity: TaskComplexity,
                   assigned_agent_id: Optional[str] = None,
                   parent_task_id: Optional[str] = None,
                   dependencies: Optional[List[str]] = None) -> Task:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            task_type: Type of task
            complexity: Task complexity
            assigned_agent_id: ID of the assigned agent (if any)
            parent_task_id: ID of the parent task (if any)
            dependencies: List of task IDs that this task depends on
            
        Returns:
            Created task
        """
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            type=task_type,
            complexity=complexity,
            status=TaskStatus.NOT_STARTED,
            assigned_agent_id=assigned_agent_id,
            parent_task_id=parent_task_id,
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        self._save_data()
        
        return task
    
    def estimate_task(self, 
                     task_id: str, 
                     agent_id: str,
                     confidence_level: float = 0.8) -> TaskEstimate:
        """
        Estimate the duration of a task.
        
        Args:
            task_id: ID of the task to estimate
            agent_id: ID of the agent performing the estimation
            confidence_level: Confidence level for the estimate (0.0 to 1.0)
            
        Returns:
            Task estimate
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        # Get agent profile or create a new one
        if agent_id not in self.agent_profiles:
            self.agent_profiles[agent_id] = AgentPerformanceProfile(agent_id=agent_id)
        
        agent_profile = self.agent_profiles[agent_id]
        
        # Calculate base duration estimate
        base_duration = self._calculate_base_duration(task, agent_profile)
        
        # Adjust for dependencies
        dependency_factor = self._calculate_dependency_factor(task)
        adjusted_duration = base_duration * dependency_factor
        
        # Calculate confidence intervals
        lower_bound, upper_bound = self._calculate_confidence_intervals(
            adjusted_duration, task, agent_profile, confidence_level
        )
        
        # Create estimate
        estimate = TaskEstimate(
            task_id=task_id,
            agent_id=agent_id,
            estimated_duration=adjusted_duration,
            confidence_level=confidence_level,
            lower_bound=lower_bound,
            upper_bound=upper_bound
        )
        
        # Update task with estimate
        task.estimate = estimate
        task.updated_at = time.time()
        
        self._save_data()
        
        return estimate
    
    def _calculate_base_duration(self, task: Task, agent_profile: AgentPerformanceProfile) -> float:
        """
        Calculate the base duration estimate for a task.
        
        Args:
            task: Task to estimate
            agent_profile: Agent performance profile
            
        Returns:
            Base duration estimate in hours
        """
        task_type = task.type.value
        complexity = task.complexity.value
        
        # Check if we have historical data for this task type
        type_duration = None
        if task_type in agent_profile.task_type_performance:
            type_perf = agent_profile.task_type_performance[task_type]
            if type_perf["count"] > 0:
                type_duration = type_perf["avg_duration"]
        
        # Check if we have historical data for this complexity
        complexity_duration = None
        if complexity in agent_profile.complexity_performance:
            comp_perf = agent_profile.complexity_performance[complexity]
            if comp_perf["count"] > 0:
                complexity_duration = comp_perf["avg_duration"]
        
        # Use available data or fallback to default estimates
        if type_duration is not None and complexity_duration is not None:
            # Weighted average of type and complexity estimates
            return (type_duration + complexity_duration) / 2
        elif type_duration is not None:
            return type_duration
        elif complexity_duration is not None:
            return complexity_duration
        else:
            # Fallback to default estimates based on complexity
            default_durations = {
                1: 0.5,    # TRIVIAL: 30 minutes
                2: 1.0,    # SIMPLE: 1 hour
                3: 4.0,    # MODERATE: 4 hours
                4: 8.0,    # COMPLEX: 8 hours
                5: 16.0    # VERY_COMPLEX: 16 hours
            }
            return default_durations.get(complexity, 4.0)
    
    def _calculate_dependency_factor(self, task: Task) -> float:
        """
        Calculate a factor to adjust duration based on dependencies.
        
        Args:
            task: Task with dependencies
            
        Returns:
            Dependency adjustment factor
        """
        if not task.dependencies:
            return 1.0
        
        # Count how many dependencies are not completed
        incomplete_deps = 0
        for dep_id in task.dependencies:
            if dep_id in self.tasks and self.tasks[dep_id].status != TaskStatus.COMPLETED:
                incomplete_deps += 1
        
        # Increase estimate if there are incomplete dependencies
        if incomplete_deps > 0:
            return 1.0 + (0.1 * incomplete_deps)  # 10% increase per incomplete dependency
        
        return 1.0
    
    def _calculate_confidence_intervals(self, 
                                       duration: float, 
                                       task: Task, 
                                       agent_profile: AgentPerformanceProfile,
                                       confidence_level: float) -> Tuple[float, float]:
        """
        Calculate confidence intervals for the duration estimate.
        
        Args:
            duration: Estimated duration
            task: Task being estimated
            agent_profile: Agent performance profile
            confidence_level: Confidence level (0.0 to 1.0)
            
        Returns:
            Tuple of (lower_bound, upper_bound) in hours
        """
        task_type = task.type.value
        complexity = task.complexity.value
        
        # Determine standard deviation to use
        std_dev = None
        
        # Try to get std_dev from historical data
        if task_type in agent_profile.task_type_performance:
            type_perf = agent_profile.task_type_performance[task_type]
            if type_perf["count"] > 1:
                std_dev = type_perf["std_dev"]
        
        if std_dev is None and complexity in agent_profile.complexity_performance:
            comp_perf = agent_profile.complexity_performance[complexity]
            if comp_perf["count"] > 1:
                std_dev = comp_perf["std_dev"]
        
        # If no historical data, use a default based on complexity
        if std_dev is None:
            # Default standard deviation as a percentage of duration
            default_std_dev_pct = {
                1: 0.2,    # TRIVIAL: 20% of duration
                2: 0.3,    # SIMPLE: 30% of duration
                3: 0.4,    # MODERATE: 40% of duration
                4: 0.5,    # COMPLEX: 50% of duration
                5: 0.6     # VERY_COMPLEX: 60% of duration
            }
            std_dev = duration * default_std_dev_pct.get(complexity, 0.4)
        
        # Calculate z-score for the given confidence level
        # This is a simplified approach - for a more accurate implementation,
        # you would use a statistical library to get the z-score
        z_scores = {
            0.5: 0.67,
            0.6: 0.84,
            0.7: 1.04,
            0.8: 1.28,
            0.9: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        
        # Find the closest confidence level
        closest_conf = min(z_scores.keys(), key=lambda x: abs(x - confidence_level))
        z_score = z_scores[closest_conf]
        
        # Calculate bounds
        margin = z_score * std_dev
        lower_bound = max(0.1, duration - margin)  # Minimum of 6 minutes
        upper_bound = duration + margin
        
        return lower_bound, upper_bound
    
    def schedule_task(self, 
                     task_id: str, 
                     start_time: Optional[float] = None) -> None:
        """
        Schedule a task with start and completion times.
        
        Args:
            task_id: ID of the task to schedule
            start_time: Start time as Unix timestamp (if None, will use current time)
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        if not task.estimate:
            raise ValueError(f"Task {task_id} has no estimate")
        
        # Set start time
        start_time = start_time or time.time()
        task.estimate.estimated_start_time = start_time
        
        # Calculate completion time
        duration_seconds = task.estimate.estimated_duration * 3600  # Convert hours to seconds
        task.estimate.estimated_completion_time = start_time + duration_seconds
        
        # Update task
        task.updated_at = time.time()
        
        self._save_data()
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> None:
        """
        Update the status of a task.
        
        Args:
            task_id: ID of the task to update
            status: New status
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.update_status(status)
        
        # If task is completed, update agent profile
        if status == TaskStatus.COMPLETED and task.estimate and task.assigned_agent_id:
            agent_id = task.assigned_agent_id
            
            # Get or create agent profile
            if agent_id not in self.agent_profiles:
                self.agent_profiles[agent_id] = AgentPerformanceProfile(agent_id=agent_id)
            
            # Update profile with completed task
            self.agent_profiles[agent_id].update_with_task(task)
        
        self._save_data()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None if not found
        """
        return self.tasks.get(task_id)
    
    def get_agent_profile(self, agent_id: str) -> Optional[AgentPerformanceProfile]:
        """
        Get an agent's performance profile.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            AgentPerformanceProfile or None if not found
        """
        return self.agent_profiles.get(agent_id)
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.
        
        Returns:
            List of all tasks
        """
        return list(self.tasks.values())
    
    def get_agent_tasks(self, agent_id: str) -> List[Task]:
        """
        Get all tasks assigned to an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of tasks assigned to the agent
        """
        return [task for task in self.tasks.values() if task.assigned_agent_id == agent_id]
    
    def get_task_eta(self, task_id: str) -> Optional[str]:
        """
        Get the estimated time of arrival (ETA) for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Formatted ETA string or None if not available
        """
        task = self.get_task(task_id)
        if not task or not task.estimate:
            return None
        
        return task.estimate.get_eta()
    
    def get_task_progress(self, task_id: str) -> Optional[float]:
        """
        Get the progress percentage for a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Progress percentage (0-100) or None if not available
        """
        task = self.get_task(task_id)
        if not task or not task.estimate:
            return None
        
        return task.estimate.get_progress_percentage()
    
    def get_agent_accuracy(self, agent_id: str) -> float:
        """
        Get an agent's estimation accuracy.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Accuracy as a percentage (0-100) or 0 if no data
        """
        profile = self.get_agent_profile(agent_id)
        if not profile:
            return 0.0
        
        return profile.overall_accuracy
    
    def get_team_workload(self, agent_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get workload information for a team of agents.
        
        Args:
            agent_ids: List of agent IDs
            
        Returns:
            Dictionary mapping agent IDs to workload information
        """
        workload = {}
        
        for agent_id in agent_ids:
            agent_tasks = self.get_agent_tasks(agent_id)
            
            # Count tasks by status
            status_counts = {status.value: 0 for status in TaskStatus}
            for task in agent_tasks:
                status_counts[task.status.value] += 1
            
            # Calculate total estimated hours
            total_estimated_hours = sum(
                task.estimate.estimated_duration for task in agent_tasks 
                if task.estimate and task.status != TaskStatus.COMPLETED
            )
            
            # Get in-progress tasks with ETAs
            in_progress_tasks = [
                {
                    "id": task.id,
                    "title": task.title,
                    "eta": task.estimate.get_eta() if task.estimate else None,
                    "progress": task.estimate.get_progress_percentage() if task.estimate else None
                }
                for task in agent_tasks if task.status == TaskStatus.IN_PROGRESS
            ]
            
            # Get agent accuracy
            accuracy = self.get_agent_accuracy(agent_id)
            
            workload[agent_id] = {
                "total_tasks": len(agent_tasks),
                "status_counts": status_counts,
                "total_estimated_hours": total_estimated_hours,
                "in_progress_tasks": in_progress_tasks,
                "estimation_accuracy": accuracy
            }
        
        return workload
    
    def get_critical_path(self, task_ids: List[str]) -> List[str]:
        """
        Calculate the critical path through a set of tasks.
        
        Args:
            task_ids: List of task IDs to consider
            
        Returns:
            List of task IDs forming the critical path
        """
        # Build dependency graph
        graph = {}
        for task_id in task_ids:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                duration = task.estimate.estimated_duration if task.estimate else 0
                graph[task_id] = {
                    "duration": duration,
                    "dependencies": [dep for dep in task.dependencies if dep in task_ids]
                }
        
        # Find tasks with no dependencies (start nodes)
        start_nodes = [
            task_id for task_id in graph 
            if not graph[task_id]["dependencies"]
        ]
        
        # Calculate earliest start and finish times
        earliest_start = {task_id: 0 for task_id in start_nodes}
        earliest_finish = {task_id: graph[task_id]["duration"] for task_id in start_nodes}
        
        # Process remaining tasks
        remaining = set(graph.keys()) - set(start_nodes)
        while remaining:
            processed = set()
            for task_id in remaining:
                deps = graph[task_id]["dependencies"]
                if all(dep in earliest_finish for dep in deps):
                    # All dependencies have been processed
                    earliest_start[task_id] = max(earliest_finish.get(dep, 0) for dep in deps)
                    earliest_finish[task_id] = earliest_start[task_id] + graph[task_id]["duration"]
                    processed.add(task_id)
            
            if not processed:
                # Circular dependency or missing tasks
                break
            
            remaining -= processed
        
        # Find the end time
        if not earliest_finish:
            return []
        
        end_time = max(earliest_finish.values())
        
        # Find tasks that finish at the end time
        end_tasks = [
            task_id for task_id, finish in earliest_finish.items() 
            if finish == end_time
        ]
        
        # Trace back from end tasks to start tasks
        critical_path = []
        current_tasks = end_tasks
        
        while current_tasks:
            # Find the task with the latest finish time
            current_task = max(current_tasks, key=lambda t: earliest_finish.get(t, 0))
            critical_path.insert(0, current_task)
            
            # Find the dependencies that are on the critical path
            deps = graph[current_task]["dependencies"]
            if not deps:
                break
            
            current_tasks = [
                dep for dep in deps 
                if earliest_finish.get(dep, 0) == earliest_start.get(current_task, 0)
            ]
        
        return critical_path
