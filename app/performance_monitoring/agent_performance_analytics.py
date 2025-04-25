"""
Agent Performance Analytics Module

This module implements comprehensive monitoring of agent performance metrics.
It provides tools for tracking, analyzing, and visualizing agent performance.
"""

import json
import os
import datetime
import uuid
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import io
import base64

class MetricType(Enum):
    """Types of performance metrics that can be tracked."""
    COMPLETION_TIME = "completion_time"
    ACCURACY = "accuracy"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    RESOURCE_USAGE = "resource_usage"
    USER_SATISFACTION = "user_satisfaction"
    COLLABORATION = "collaboration"
    LEARNING_RATE = "learning_rate"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


class MetricUnit(Enum):
    """Units for performance metrics."""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    PERCENTAGE = "percentage"
    COUNT = "count"
    SCORE = "score"  # Arbitrary score, typically 0-100
    RATIO = "ratio"
    BYTES = "bytes"
    MEGABYTES = "megabytes"
    OPERATIONS = "operations"
    TOKENS = "tokens"


class AgentRole(Enum):
    """Roles that agents can have in a team."""
    PROJECT_MANAGER = "project_manager"
    PRODUCT_MANAGER = "product_manager"
    DEVELOPER = "developer"
    DESIGNER = "designer"
    QA_TESTER = "qa_tester"
    DATA_SCIENTIST = "data_scientist"
    DEVOPS = "devops"
    SECURITY_SPECIALIST = "security_specialist"
    GENERAL_ASSISTANT = "general_assistant"


class TaskStatus(Enum):
    """Status of a task assigned to an agent."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PerformanceMetric:
    """Represents a performance metric for an agent."""
    
    def __init__(self, metric_id: str, agent_id: str, metric_type: MetricType, 
                value: float, unit: MetricUnit, timestamp: Optional[datetime.datetime] = None,
                task_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Initialize a performance metric.
        
        Args:
            metric_id: Unique identifier for the metric
            agent_id: ID of the agent this metric is for
            metric_type: Type of metric
            value: Numeric value of the metric
            unit: Unit of measurement
            timestamp: When the metric was recorded (defaults to now)
            task_id: Optional ID of the associated task
            context: Optional additional context for the metric
        """
        self.metric_id = metric_id
        self.agent_id = agent_id
        self.metric_type = metric_type
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or datetime.datetime.now()
        self.task_id = task_id
        self.context = context or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the metric
        """
        return {
            "metric_id": self.metric_id,
            "agent_id": self.agent_id,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "unit": self.unit.value,
            "timestamp": self.timestamp.isoformat(),
            "task_id": self.task_id,
            "context": self.context
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceMetric':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            PerformanceMetric instance
        """
        return cls(
            metric_id=data["metric_id"],
            agent_id=data["agent_id"],
            metric_type=MetricType(data["metric_type"]),
            value=data["value"],
            unit=MetricUnit(data["unit"]),
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]),
            task_id=data.get("task_id"),
            context=data.get("context", {})
        )


class AgentTask:
    """Represents a task assigned to an agent."""
    
    def __init__(self, task_id: str, agent_id: str, title: str, description: str,
                priority: TaskPriority, estimated_duration: Optional[float] = None,
                created_at: Optional[datetime.datetime] = None):
        """
        Initialize an agent task.
        
        Args:
            task_id: Unique identifier for the task
            agent_id: ID of the agent assigned to this task
            title: Short title of the task
            description: Detailed description of the task
            priority: Priority level of the task
            estimated_duration: Estimated duration in minutes
            created_at: When the task was created (defaults to now)
        """
        self.task_id = task_id
        self.agent_id = agent_id
        self.title = title
        self.description = description
        self.priority = priority
        self.estimated_duration = estimated_duration
        self.created_at = created_at or datetime.datetime.now()
        self.started_at = None
        self.completed_at = None
        self.status = TaskStatus.PENDING
        self.actual_duration = None  # In minutes
        self.dependencies = []  # List of task IDs this task depends on
        self.subtasks = []  # List of subtask IDs
        self.parent_task = None  # ID of parent task if this is a subtask
        self.tags = []  # List of tags for categorization
        self.metrics = {}  # metric_type -> PerformanceMetric
        self.notes = []  # List of notes about the task
        
    def start(self) -> None:
        """Mark the task as started."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.IN_PROGRESS
            self.started_at = datetime.datetime.now()
            
    def complete(self) -> None:
        """Mark the task as completed."""
        if self.status == TaskStatus.IN_PROGRESS:
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.datetime.now()
            
            # Calculate actual duration
            if self.started_at:
                delta = self.completed_at - self.started_at
                self.actual_duration = delta.total_seconds() / 60  # Convert to minutes
                
    def fail(self) -> None:
        """Mark the task as failed."""
        if self.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            self.status = TaskStatus.FAILED
            
    def block(self) -> None:
        """Mark the task as blocked."""
        if self.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            self.status = TaskStatus.BLOCKED
            
    def cancel(self) -> None:
        """Mark the task as cancelled."""
        if self.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED):
            self.status = TaskStatus.CANCELLED
            
    def add_dependency(self, task_id: str) -> None:
        """
        Add a dependency to this task.
        
        Args:
            task_id: ID of the task this task depends on
        """
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            
    def add_subtask(self, task_id: str) -> None:
        """
        Add a subtask to this task.
        
        Args:
            task_id: ID of the subtask
        """
        if task_id not in self.subtasks:
            self.subtasks.append(task_id)
            
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to this task.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            
    def add_note(self, content: str, author: str) -> Dict[str, Any]:
        """
        Add a note to this task.
        
        Args:
            content: Note content
            author: Author of the note
            
        Returns:
            The note record
        """
        note = {
            "id": str(uuid.uuid4()),
            "content": content,
            "author": author,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.notes.append(note)
        return note
        
    def add_metric(self, metric: PerformanceMetric) -> None:
        """
        Add a performance metric to this task.
        
        Args:
            metric: The metric to add
        """
        self.metrics[metric.metric_type.value] = metric
        
    def get_completion_percentage(self) -> float:
        """
        Get the completion percentage of this task.
        
        Returns:
            Completion percentage (0-100)
        """
        if self.status == TaskStatus.COMPLETED:
            return 100.0
        elif self.status == TaskStatus.PENDING:
            return 0.0
        elif self.status == TaskStatus.IN_PROGRESS:
            # If there's a metric for completion percentage, use that
            if MetricType.COMPLETION_TIME.value in self.metrics:
                return self.metrics[MetricType.COMPLETION_TIME.value].value
                
            # Otherwise, estimate based on elapsed time vs. estimated duration
            if self.started_at and self.estimated_duration:
                elapsed = (datetime.datetime.now() - self.started_at).total_seconds() / 60
                percentage = min(95, (elapsed / self.estimated_duration) * 100)
                return percentage
                
            # Default to 50% if we can't calculate
            return 50.0
        else:
            return 0.0
            
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the task
        """
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "estimated_duration": self.estimated_duration,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status.value,
            "actual_duration": self.actual_duration,
            "dependencies": self.dependencies,
            "subtasks": self.subtasks,
            "parent_task": self.parent_task,
            "tags": self.tags,
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()},
            "notes": self.notes
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTask':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            AgentTask instance
        """
        task = cls(
            task_id=data["task_id"],
            agent_id=data["agent_id"],
            title=data["title"],
            description=data["description"],
            priority=TaskPriority(data["priority"]),
            estimated_duration=data.get("estimated_duration"),
            created_at=datetime.datetime.fromisoformat(data["created_at"])
        )
        
        # Restore timestamps
        if data.get("started_at"):
            task.started_at = datetime.datetime.fromisoformat(data["started_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.datetime.fromisoformat(data["completed_at"])
            
        # Restore other fields
        task.status = TaskStatus(data["status"])
        task.actual_duration = data.get("actual_duration")
        task.dependencies = data.get("dependencies", [])
        task.subtasks = data.get("subtasks", [])
        task.parent_task = data.get("parent_task")
        task.tags = data.get("tags", [])
        
        # Restore metrics
        for metric_type, metric_data in data.get("metrics", {}).items():
            task.metrics[metric_type] = PerformanceMetric.from_dict(metric_data)
            
        # Restore notes
        task.notes = data.get("notes", [])
        
        return task


class AgentProfile:
    """Represents an agent's profile with performance history."""
    
    def __init__(self, agent_id: str, name: str, role: AgentRole, 
                capabilities: Optional[List[str]] = None):
        """
        Initialize an agent profile.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            role: Role of the agent
            capabilities: List of agent capabilities
        """
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.created_at = datetime.datetime.now()
        self.metrics = []  # List of PerformanceMetric objects
        self.tasks = {}  # task_id -> AgentTask
        self.performance_history = {}  # metric_type -> List of (timestamp, value) tuples
        self.strengths = []  # List of identified strengths
        self.areas_for_improvement = []  # List of identified areas for improvement
        self.tags = []  # List of tags for categorization
        
    def add_metric(self, metric: PerformanceMetric) -> None:
        """
        Add a performance metric to this agent's profile.
        
        Args:
            metric: The metric to add
        """
        self.metrics.append(metric)
        
        # Update performance history
        metric_type = metric.metric_type.value
        if metric_type not in self.performance_history:
            self.performance_history[metric_type] = []
            
        self.performance_history[metric_type].append((metric.timestamp, metric.value))
        
        # Sort by timestamp
        self.performance_history[metric_type].sort(key=lambda x: x[0])
        
    def add_task(self, task: AgentTask) -> None:
        """
        Add a task to this agent's profile.
        
        Args:
            task: The task to add
        """
        self.tasks[task.task_id] = task
        
    def add_capability(self, capability: str) -> None:
        """
        Add a capability to this agent's profile.
        
        Args:
            capability: The capability to add
        """
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            
    def add_strength(self, strength: str) -> None:
        """
        Add a strength to this agent's profile.
        
        Args:
            strength: The strength to add
        """
        if strength not in self.strengths:
            self.strengths.append(strength)
            
    def add_area_for_improvement(self, area: str) -> None:
        """
        Add an area for improvement to this agent's profile.
        
        Args:
            area: The area for improvement to add
        """
        if area not in self.areas_for_improvement:
            self.areas_for_improvement.append(area)
            
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to this agent's profile.
        
        Args:
            tag: The tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)
            
    def get_average_metric(self, metric_type: MetricType, 
                          time_period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> Optional[float]:
        """
        Get the average value of a metric over a time period.
        
        Args:
            metric_type: Type of metric to average
            time_period: Optional (start, end) tuple for time range
            
        Returns:
            Average value, or None if no metrics of that type
        """
        values = []
        
        for metric in self.metrics:
            if metric.metric_type != metric_type:
                continue
                
            if time_period:
                start, end = time_period
                if not (start <= metric.timestamp <= end):
                    continue
                    
            values.append(metric.value)
            
        if not values:
            return None
            
        return sum(values) / len(values)
        
    def get_metric_trend(self, metric_type: MetricType, 
                        num_points: int = 10) -> Optional[List[Tuple[datetime.datetime, float]]]:
        """
        Get the trend of a metric over time.
        
        Args:
            metric_type: Type of metric to analyze
            num_points: Number of data points to return
            
        Returns:
            List of (timestamp, value) tuples, or None if no metrics of that type
        """
        history = self.performance_history.get(metric_type.value, [])
        
        if not history:
            return None
            
        # If we have fewer points than requested, return all
        if len(history) <= num_points:
            return history
            
        # Otherwise, sample evenly
        indices = np.linspace(0, len(history) - 1, num_points, dtype=int)
        return [history[i] for i in indices]
        
    def get_task_completion_rate(self, 
                               time_period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> float:
        """
        Get the task completion rate for this agent.
        
        Args:
            time_period: Optional (start, end) tuple for time range
            
        Returns:
            Completion rate as a percentage (0-100)
        """
        completed = 0
        total = 0
        
        for task in self.tasks.values():
            if time_period:
                start, end = time_period
                if not (start <= task.created_at <= end):
                    continue
                    
            total += 1
            if task.status == TaskStatus.COMPLETED:
                completed += 1
                
        if total == 0:
            return 0.0
            
        return (completed / total) * 100
        
    def get_average_task_duration(self, 
                                time_period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> Optional[float]:
        """
        Get the average task duration for this agent.
        
        Args:
            time_period: Optional (start, end) tuple for time range
            
        Returns:
            Average duration in minutes, or None if no completed tasks
        """
        durations = []
        
        for task in self.tasks.values():
            if task.status != TaskStatus.COMPLETED or task.actual_duration is None:
                continue
                
            if time_period:
                start, end = time_period
                if not (start <= task.created_at <= end):
                    continue
                    
            durations.append(task.actual_duration)
            
        if not durations:
            return None
            
        return sum(durations) / len(durations)
        
    def get_task_estimation_accuracy(self, 
                                   time_period: Optional[Tuple[datetime.datetime, datetime.datetime]] = None) -> Optional[float]:
        """
        Get the task estimation accuracy for this agent.
        
        Args:
            time_period: Optional (start, end) tuple for time range
            
        Returns:
            Estimation accuracy as a percentage (0-100), or None if no completed tasks with estimates
        """
        accuracies = []
        
        for task in self.tasks.values():
            if (task.status != TaskStatus.COMPLETED or 
                task.actual_duration is None or 
                task.estimated_duration is None):
                continue
                
            if time_period:
                start, end = time_period
                if not (start <= task.created_at <= end):
                    continue
                    
            # Calculate accuracy as 1 - abs(actual - estimated) / estimated
            # Clamp to 0-100%
            accuracy = max(0, min(100, 100 * (1 - abs(task.actual_duration - task.estimated_duration) / task.estimated_duration)))
            accuracies.append(accuracy)
            
        if not accuracies:
            return None
            
        return sum(accuracies) / len(accuracies)
        
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze the agent's performance across various metrics.
        
        Returns:
            Dictionary with performance analysis
        """
        # Calculate basic statistics
        task_count = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED)
        
        completion_rate = (completed_tasks / task_count) * 100 if task_count > 0 else 0
        
        # Calculate average metrics
        avg_metrics = {}
        for metric_type in MetricType:
            avg = self.get_average_metric(metric_type)
            if avg is not None:
                avg_metrics[metric_type.value] = avg
                
        # Calculate task duration statistics
        durations = [task.actual_duration for task in self.tasks.values() 
                    if task.status == TaskStatus.COMPLETED and task.actual_duration is not None]
        
        avg_duration = sum(durations) / len(durations) if durations else None
        min_duration = min(durations) if durations else None
        max_duration = max(durations) if durations else None
        
        # Calculate estimation accuracy
        estimation_accuracy = self.get_task_estimation_accuracy()
        
        # Identify strengths and areas for improvement
        strengths = []
        improvements = []
        
        # Check completion rate
        if completion_rate >= 90:
            strengths.append("High task completion rate")
        elif completion_rate <= 70:
            improvements.append("Improve task completion rate")
            
        # Check estimation accuracy
        if estimation_accuracy is not None:
            if estimation_accuracy >= 85:
                strengths.append("Accurate task estimation")
            elif estimation_accuracy <= 60:
                improvements.append("Improve task estimation accuracy")
                
        # Check specific metrics
        if MetricType.QUALITY.value in avg_metrics:
            quality = avg_metrics[MetricType.QUALITY.value]
            if quality >= 85:
                strengths.append("High quality of work")
            elif quality <= 70:
                improvements.append("Improve quality of work")
                
        if MetricType.EFFICIENCY.value in avg_metrics:
            efficiency = avg_metrics[MetricType.EFFICIENCY.value]
            if efficiency >= 85:
                strengths.append("High efficiency")
            elif efficiency <= 70:
                improvements.append("Improve efficiency")
                
        # Update profile with identified strengths and improvements
        for strength in strengths:
            if strength not in self.strengths:
                self.strengths.append(strength)
                
        for improvement in improvements:
            if improvement not in self.areas_for_improvement:
                self.areas_for_improvement.append(improvement)
                
        return {
            "task_count": task_count,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "completion_rate": completion_rate,
            "avg_metrics": avg_metrics,
            "avg_duration": avg_duration,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "estimation_accuracy": estimation_accuracy,
            "strengths": strengths,
            "areas_for_improvement": improvements
        }
        
    def generate_performance_report(self) -> str:
        """
        Generate a human-readable performance report for this agent.
        
        Returns:
            Performance report text
        """
        analysis = self.analyze_performance()
        
        report = f"# Performance Report: {self.name}\n\n"
        report += f"**Role:** {self.role.value}\n"
        report += f"**Agent ID:** {self.agent_id}\n"
        report += f"**Report Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        report += "## Task Performance\n\n"
        report += f"**Total Tasks:** {analysis['task_count']}\n"
        report += f"**Completed Tasks:** {analysis['completed_tasks']}\n"
        report += f"**Failed Tasks:** {analysis['failed_tasks']}\n"
        report += f"**Completion Rate:** {analysis['completion_rate']:.1f}%\n"
        
        if analysis['avg_duration'] is not None:
            report += f"**Average Task Duration:** {analysis['avg_duration']:.1f} minutes\n"
        if analysis['estimation_accuracy'] is not None:
            report += f"**Estimation Accuracy:** {analysis['estimation_accuracy']:.1f}%\n"
            
        report += "\n## Performance Metrics\n\n"
        
        for metric_type, value in analysis['avg_metrics'].items():
            report += f"**{metric_type}:** {value:.2f}\n"
            
        report += "\n## Strengths\n\n"
        
        for strength in self.strengths:
            report += f"- {strength}\n"
            
        report += "\n## Areas for Improvement\n\n"
        
        for area in self.areas_for_improvement:
            report += f"- {area}\n"
            
        report += "\n## Capabilities\n\n"
        
        for capability in self.capabilities:
            report += f"- {capability}\n"
            
        return report
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the agent profile
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat(),
            "metrics": [metric.to_dict() for metric in self.metrics],
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "tags": self.tags
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentProfile':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary representation
            
        Returns:
            AgentProfile instance
        """
        profile = cls(
            agent_id=data["agent_id"],
            name=data["name"],
            role=AgentRole(data["role"]),
            capabilities=data.get("capabilities", [])
        )
        
        # Restore timestamp
        profile.created_at = datetime.datetime.fromisoformat(data["created_at"])
        
        # Restore metrics
        for metric_data in data.get("metrics", []):
            metric = PerformanceMetric.from_dict(metric_data)
            profile.add_metric(metric)
            
        # Restore tasks
        for task_id, task_data in data.get("tasks", {}).items():
            task = AgentTask.from_dict(task_data)
            profile.tasks[task_id] = task
            
        # Restore other fields
        profile.strengths = data.get("strengths", [])
        profile.areas_for_improvement = data.get("areas_for_improvement", [])
        profile.tags = data.get("tags", [])
        
        return profile


class PerformanceVisualization:
    """Provides visualization capabilities for agent performance data."""
    
    @staticmethod
    def generate_metric_trend_chart(agent_profile: AgentProfile, metric_type: MetricType, 
                                  title: Optional[str] = None) -> str:
        """
        Generate a chart showing the trend of a metric over time.
        
        Args:
            agent_profile: Agent profile to visualize
            metric_type: Type of metric to visualize
            title: Optional chart title
            
        Returns:
            Base64-encoded PNG image
        """
        trend_data = agent_profile.get_metric_trend(metric_type)
        
        if not trend_data:
            return None
            
        timestamps, values = zip(*trend_data)
        
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, values, marker='o')
        
        if title:
            plt.title(title)
        else:
            plt.title(f"{metric_type.value.replace('_', ' ').title()} Trend for {agent_profile.name}")
            
        plt.xlabel("Time")
        plt.ylabel(metric_type.value.replace('_', ' ').title())
        plt.grid(True)
        
        # Format x-axis dates
        plt.gcf().autofmt_xdate()
        
        # Save to in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return f"data:image/png;base64,{img_str}"
        
    @staticmethod
    def generate_task_status_chart(agent_profile: AgentProfile, 
                                 title: Optional[str] = None) -> str:
        """
        Generate a pie chart showing task status distribution.
        
        Args:
            agent_profile: Agent profile to visualize
            title: Optional chart title
            
        Returns:
            Base64-encoded PNG image
        """
        status_counts = defaultdict(int)
        
        for task in agent_profile.tasks.values():
            status_counts[task.status.value] += 1
            
        if not status_counts:
            return None
            
        labels = list(status_counts.keys())
        sizes = list(status_counts.values())
        
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        if title:
            plt.title(title)
        else:
            plt.title(f"Task Status Distribution for {agent_profile.name}")
            
        # Save to in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return f"data:image/png;base64,{img_str}"
        
    @staticmethod
    def generate_estimation_accuracy_chart(agent_profile: AgentProfile, 
                                         title: Optional[str] = None) -> str:
        """
        Generate a chart comparing estimated vs. actual task durations.
        
        Args:
            agent_profile: Agent profile to visualize
            title: Optional chart title
            
        Returns:
            Base64-encoded PNG image
        """
        tasks_with_both = [task for task in agent_profile.tasks.values() 
                          if task.status == TaskStatus.COMPLETED 
                          and task.estimated_duration is not None 
                          and task.actual_duration is not None]
        
        if not tasks_with_both:
            return None
            
        task_names = [task.title for task in tasks_with_both]
        estimated = [task.estimated_duration for task in tasks_with_both]
        actual = [task.actual_duration for task in tasks_with_both]
        
        # Limit to most recent 10 tasks if there are more
        if len(task_names) > 10:
            task_names = task_names[-10:]
            estimated = estimated[-10:]
            actual = actual[-10:]
            
        x = np.arange(len(task_names))
        width = 0.35
        
        plt.figure(figsize=(12, 6))
        plt.bar(x - width/2, estimated, width, label='Estimated')
        plt.bar(x + width/2, actual, width, label='Actual')
        
        if title:
            plt.title(title)
        else:
            plt.title(f"Estimated vs. Actual Task Duration for {agent_profile.name}")
            
        plt.xlabel("Task")
        plt.ylabel("Duration (minutes)")
        plt.xticks(x, task_names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        # Save to in-memory buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        
        # Convert to base64
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return f"data:image/png;base64,{img_str}"
        
    @staticmethod
    def generate_performance_dashboard(agent_profile: AgentProfile) -> Dict[str, str]:
        """
        Generate a complete performance dashboard with multiple charts.
        
        Args:
            agent_profile: Agent profile to visualize
            
        Returns:
            Dictionary mapping chart names to base64-encoded PNG images
        """
        charts = {}
        
        # Task status chart
        status_chart = PerformanceVisualization.generate_task_status_chart(
            agent_profile, f"Task Status Distribution - {agent_profile.name}")
        if status_chart:
            charts["task_status"] = status_chart
            
        # Estimation accuracy chart
        estimation_chart = PerformanceVisualization.generate_estimation_accuracy_chart(
            agent_profile, f"Estimation Accuracy - {agent_profile.name}")
        if estimation_chart:
            charts["estimation_accuracy"] = estimation_chart
            
        # Metric trend charts for common metrics
        for metric_type in [MetricType.QUALITY, MetricType.EFFICIENCY, 
                           MetricType.COMPLETION_TIME, MetricType.USER_SATISFACTION]:
            trend_chart = PerformanceVisualization.generate_metric_trend_chart(
                agent_profile, metric_type, 
                f"{metric_type.value.replace('_', ' ').title()} Trend - {agent_profile.name}")
            if trend_chart:
                charts[f"{metric_type.value}_trend"] = trend_chart
                
        return charts


class AgentPerformanceManager:
    """Manages performance tracking and analysis for multiple agents."""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the agent performance manager.
        
        Args:
            storage_dir: Directory to store agent profiles
        """
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "agent_profiles")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.agent_profiles = {}  # agent_id -> AgentProfile
        
        # Load existing profiles
        self._load_profiles()
        
    def _load_profiles(self) -> None:
        """Load all agent profiles from storage."""
        if not os.path.exists(self.storage_dir):
            return
            
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                agent_id = filename[:-5]  # Remove .json extension
                profile_path = os.path.join(self.storage_dir, filename)
                
                try:
                    with open(profile_path, 'r') as f:
                        profile_data = json.load(f)
                        profile = AgentProfile.from_dict(profile_data)
                        self.agent_profiles[agent_id] = profile
                except Exception as e:
                    print(f"Error loading agent profile {agent_id}: {e}")
                    
    def _save_profile(self, profile: AgentProfile) -> None:
        """
        Save an agent profile to storage.
        
        Args:
            profile: The profile to save
        """
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
            
        profile_path = os.path.join(self.storage_dir, f"{profile.agent_id}.json")
        
        try:
            with open(profile_path, 'w') as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving agent profile {profile.agent_id}: {e}")
            
    def create_agent_profile(self, agent_id: str, name: str, role: AgentRole, 
                           capabilities: Optional[List[str]] = None) -> AgentProfile:
        """
        Create a new agent profile.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Name of the agent
            role: Role of the agent
            capabilities: List of agent capabilities
            
        Returns:
            The created profile
        """
        profile = AgentProfile(
            agent_id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities
        )
        
        self.agent_profiles[agent_id] = profile
        self._save_profile(profile)
        
        return profile
        
    def get_agent_profile(self, agent_id: str) -> Optional[AgentProfile]:
        """
        Get an agent profile by ID.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            The agent profile, or None if not found
        """
        return self.agent_profiles.get(agent_id)
        
    def update_agent_profile(self, profile: AgentProfile) -> None:
        """
        Update an agent profile in storage.
        
        Args:
            profile: The profile to update
        """
        self.agent_profiles[profile.agent_id] = profile
        self._save_profile(profile)
        
    def delete_agent_profile(self, agent_id: str) -> bool:
        """
        Delete an agent profile.
        
        Args:
            agent_id: ID of the agent profile to delete
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agent_profiles:
            return False
            
        # Remove from memory
        del self.agent_profiles[agent_id]
        
        # Remove from storage
        profile_path = os.path.join(self.storage_dir, f"{agent_id}.json")
        if os.path.exists(profile_path):
            try:
                os.remove(profile_path)
                return True
            except Exception as e:
                print(f"Error deleting agent profile {agent_id}: {e}")
                return False
        
        return True
        
    def record_metric(self, agent_id: str, metric_type: MetricType, 
                     value: float, unit: MetricUnit, 
                     task_id: Optional[str] = None, 
                     context: Optional[Dict[str, Any]] = None) -> Optional[PerformanceMetric]:
        """
        Record a performance metric for an agent.
        
        Args:
            agent_id: ID of the agent
            metric_type: Type of metric
            value: Numeric value of the metric
            unit: Unit of measurement
            task_id: Optional ID of the associated task
            context: Optional additional context for the metric
            
        Returns:
            The created metric, or None if agent not found
        """
        profile = self.get_agent_profile(agent_id)
        if not profile:
            return None
            
        metric = PerformanceMetric(
            metric_id=str(uuid.uuid4()),
            agent_id=agent_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            task_id=task_id,
            context=context
        )
        
        profile.add_metric(metric)
        
        # If this metric is associated with a task, add it to the task too
        if task_id and task_id in profile.tasks:
            profile.tasks[task_id].add_metric(metric)
            
        self.update_agent_profile(profile)
        
        return metric
        
    def create_task(self, agent_id: str, title: str, description: str,
                  priority: TaskPriority, estimated_duration: Optional[float] = None) -> Optional[AgentTask]:
        """
        Create a new task for an agent.
        
        Args:
            agent_id: ID of the agent
            title: Short title of the task
            description: Detailed description of the task
            priority: Priority level of the task
            estimated_duration: Estimated duration in minutes
            
        Returns:
            The created task, or None if agent not found
        """
        profile = self.get_agent_profile(agent_id)
        if not profile:
            return None
            
        task = AgentTask(
            task_id=str(uuid.uuid4()),
            agent_id=agent_id,
            title=title,
            description=description,
            priority=priority,
            estimated_duration=estimated_duration
        )
        
        profile.add_task(task)
        self.update_agent_profile(profile)
        
        return task
        
    def update_task_status(self, agent_id: str, task_id: str, 
                         new_status: TaskStatus) -> bool:
        """
        Update the status of a task.
        
        Args:
            agent_id: ID of the agent
            task_id: ID of the task
            new_status: New status for the task
            
        Returns:
            True if successful, False otherwise
        """
        profile = self.get_agent_profile(agent_id)
        if not profile or task_id not in profile.tasks:
            return False
            
        task = profile.tasks[task_id]
        
        # Update status based on the requested transition
        if new_status == TaskStatus.IN_PROGRESS:
            task.start()
        elif new_status == TaskStatus.COMPLETED:
            task.complete()
        elif new_status == TaskStatus.FAILED:
            task.fail()
        elif new_status == TaskStatus.BLOCKED:
            task.block()
        elif new_status == TaskStatus.CANCELLED:
            task.cancel()
        else:
            # Direct status update
            task.status = new_status
            
        self.update_agent_profile(profile)
        
        return True
        
    def get_team_performance_summary(self) -> Dict[str, Any]:
        """
        Get a summary of performance across all agents.
        
        Returns:
            Dictionary with team performance summary
        """
        if not self.agent_profiles:
            return {"agent_count": 0}
            
        # Count agents by role
        role_counts = defaultdict(int)
        for profile in self.agent_profiles.values():
            role_counts[profile.role.value] += 1
            
        # Calculate task statistics
        total_tasks = 0
        completed_tasks = 0
        failed_tasks = 0
        
        for profile in self.agent_profiles.values():
            total_tasks += len(profile.tasks)
            completed_tasks += sum(1 for task in profile.tasks.values() 
                                 if task.status == TaskStatus.COMPLETED)
            failed_tasks += sum(1 for task in profile.tasks.values() 
                              if task.status == TaskStatus.FAILED)
                              
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        # Calculate average metrics across all agents
        metric_sums = defaultdict(float)
        metric_counts = defaultdict(int)
        
        for profile in self.agent_profiles.values():
            for metric in profile.metrics:
                metric_sums[metric.metric_type.value] += metric.value
                metric_counts[metric.metric_type.value] += 1
                
        avg_metrics = {}
        for metric_type, total in metric_sums.items():
            count = metric_counts[metric_type]
            if count > 0:
                avg_metrics[metric_type] = total / count
                
        # Calculate average task duration
        durations = []
        for profile in self.agent_profiles.values():
            for task in profile.tasks.values():
                if task.status == TaskStatus.COMPLETED and task.actual_duration is not None:
                    durations.append(task.actual_duration)
                    
        avg_duration = sum(durations) / len(durations) if durations else None
        
        # Calculate average estimation accuracy
        accuracies = []
        for profile in self.agent_profiles.values():
            accuracy = profile.get_task_estimation_accuracy()
            if accuracy is not None:
                accuracies.append(accuracy)
                
        avg_estimation_accuracy = sum(accuracies) / len(accuracies) if accuracies else None
        
        return {
            "agent_count": len(self.agent_profiles),
            "role_distribution": dict(role_counts),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "completion_rate": completion_rate,
            "avg_metrics": avg_metrics,
            "avg_task_duration": avg_duration,
            "avg_estimation_accuracy": avg_estimation_accuracy
        }
        
    def generate_team_performance_report(self) -> str:
        """
        Generate a human-readable performance report for the entire team.
        
        Returns:
            Team performance report text
        """
        summary = self.get_team_performance_summary()
        
        report = "# Team Performance Report\n\n"
        report += f"**Report Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        report += f"**Total Agents:** {summary['agent_count']}\n\n"
        
        report += "## Role Distribution\n\n"
        
        for role, count in summary['role_distribution'].items():
            report += f"**{role}:** {count}\n"
            
        report += "\n## Task Performance\n\n"
        report += f"**Total Tasks:** {summary['total_tasks']}\n"
        report += f"**Completed Tasks:** {summary['completed_tasks']}\n"
        report += f"**Failed Tasks:** {summary['failed_tasks']}\n"
        report += f"**Completion Rate:** {summary['completion_rate']:.1f}%\n"
        
        if summary['avg_task_duration'] is not None:
            report += f"**Average Task Duration:** {summary['avg_task_duration']:.1f} minutes\n"
        if summary['avg_estimation_accuracy'] is not None:
            report += f"**Average Estimation Accuracy:** {summary['avg_estimation_accuracy']:.1f}%\n"
            
        report += "\n## Average Performance Metrics\n\n"
        
        for metric_type, value in summary['avg_metrics'].items():
            report += f"**{metric_type}:** {value:.2f}\n"
            
        report += "\n## Agent Performance Summary\n\n"
        
        # Add a brief summary for each agent
        for agent_id, profile in self.agent_profiles.items():
            analysis = profile.analyze_performance()
            
            report += f"### {profile.name} ({profile.role.value})\n\n"
            report += f"**Tasks:** {analysis['task_count']} total, {analysis['completed_tasks']} completed\n"
            report += f"**Completion Rate:** {analysis['completion_rate']:.1f}%\n"
            
            if analysis['estimation_accuracy'] is not None:
                report += f"**Estimation Accuracy:** {analysis['estimation_accuracy']:.1f}%\n"
                
            if analysis['strengths']:
                report += "**Strengths:** " + ", ".join(analysis['strengths']) + "\n"
                
            if analysis['areas_for_improvement']:
                report += "**Areas for Improvement:** " + ", ".join(analysis['areas_for_improvement']) + "\n"
                
            report += "\n"
            
        return report
        
    def compare_agents(self, agent_ids: List[str], 
                     metrics: Optional[List[MetricType]] = None) -> Dict[str, Any]:
        """
        Compare performance between multiple agents.
        
        Args:
            agent_ids: List of agent IDs to compare
            metrics: Optional list of metrics to compare (defaults to all)
            
        Returns:
            Dictionary with comparison results
        """
        if not metrics:
            metrics = list(MetricType)
            
        # Get profiles for all specified agents
        profiles = {}
        for agent_id in agent_ids:
            profile = self.get_agent_profile(agent_id)
            if profile:
                profiles[agent_id] = profile
                
        if not profiles:
            return {"error": "No valid agent profiles found"}
            
        # Compare metrics
        metric_comparisons = {}
        for metric_type in metrics:
            values = {}
            for agent_id, profile in profiles.items():
                avg = profile.get_average_metric(metric_type)
                if avg is not None:
                    values[agent_id] = avg
                    
            if values:
                metric_comparisons[metric_type.value] = values
                
        # Compare task performance
        task_comparisons = {}
        for agent_id, profile in profiles.items():
            task_count = len(profile.tasks)
            completed = sum(1 for task in profile.tasks.values() 
                          if task.status == TaskStatus.COMPLETED)
            completion_rate = (completed / task_count) * 100 if task_count > 0 else 0
            
            avg_duration = profile.get_average_task_duration()
            estimation_accuracy = profile.get_task_estimation_accuracy()
            
            task_comparisons[agent_id] = {
                "task_count": task_count,
                "completed_tasks": completed,
                "completion_rate": completion_rate,
                "avg_duration": avg_duration,
                "estimation_accuracy": estimation_accuracy
            }
            
        return {
            "agents": {agent_id: {"name": profile.name, "role": profile.role.value} 
                     for agent_id, profile in profiles.items()},
            "metric_comparisons": metric_comparisons,
            "task_comparisons": task_comparisons
        }
        
    def get_all_agent_profiles(self) -> List[AgentProfile]:
        """
        Get all agent profiles.
        
        Returns:
            List of all agent profiles
        """
        return list(self.agent_profiles.values())
        
    def get_agents_by_role(self, role: AgentRole) -> List[AgentProfile]:
        """
        Get all agents with a specific role.
        
        Args:
            role: Role to filter by
            
        Returns:
            List of agent profiles with the specified role
        """
        return [profile for profile in self.agent_profiles.values() 
               if profile.role == role]
