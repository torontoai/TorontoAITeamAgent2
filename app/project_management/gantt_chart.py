"""
Gantt Chart Generation Module for TORONTO AI TEAM AGENT

This module provides functionality for creating and maintaining detailed project timelines
with dependencies using Gantt charts. It supports visualization of project schedules,
critical paths, resource allocations, and timeline adjustments.

Features:
- Create Gantt charts from project tasks and dependencies
- Visualize critical paths and bottlenecks
- Support for milestones and deadlines
- Interactive timeline adjustments
- Export to various formats (PNG, PDF, HTML)
- Integration with project management tools
"""

import datetime
import json
import os
from typing import Dict, List, Optional, Tuple, Union
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from dataclasses import dataclass, field

@dataclass
class Task:
    """Represents a project task with scheduling and dependency information."""
    id: str
    name: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    progress: float = 0.0  # 0.0 to 1.0
    dependencies: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    color: str = "#3498db"  # Default blue color
    milestone: bool = False
    
    @property
    def duration(self) -> int:
        """Calculate task duration in days."""
        return (self.end_date - self.start_date).days + 1
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "progress": self.progress,
            "dependencies": self.dependencies,
            "resources": self.resources,
            "color": self.color,
            "milestone": self.milestone
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create task from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            start_date=datetime.datetime.fromisoformat(data["start_date"]),
            end_date=datetime.datetime.fromisoformat(data["end_date"]),
            progress=data.get("progress", 0.0),
            dependencies=data.get("dependencies", []),
            resources=data.get("resources", []),
            color=data.get("color", "#3498db"),
            milestone=data.get("milestone", False)
        )


class GanttChart:
    """
    Gantt chart generator for project timeline visualization and management.
    """
    
    def __init__(self, project_name: str, description: str = ""):
        """
        Initialize a new Gantt chart.
        
        Args:
            project_name: Name of the project
            description: Optional project description
        """
        self.project_name = project_name
        self.description = description
        self.tasks: Dict[str, Task] = {}
        self.last_update = datetime.datetime.now()
    
    def add_task(self, task: Task) -> None:
        """
        Add a task to the Gantt chart.
        
        Args:
            task: Task object to add
        """
        self.tasks[task.id] = task
        self.last_update = datetime.datetime.now()
    
    def update_task(self, task_id: str, **kwargs) -> None:
        """
        Update an existing task's attributes.
        
        Args:
            task_id: ID of the task to update
            **kwargs: Task attributes to update
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        task = self.tasks[task_id]
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
            else:
                raise ValueError(f"Invalid task attribute: {key}")
        
        self.last_update = datetime.datetime.now()
    
    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the Gantt chart.
        
        Args:
            task_id: ID of the task to remove
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Remove this task from all dependencies
        for task in self.tasks.values():
            if task_id in task.dependencies:
                task.dependencies.remove(task_id)
        
        del self.tasks[task_id]
        self.last_update = datetime.datetime.now()
    
    def get_task(self, task_id: str) -> Task:
        """
        Get a task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task object
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} not found")
        
        return self.tasks[task_id]
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks in the Gantt chart.
        
        Returns:
            List of all Task objects
        """
        return list(self.tasks.values())
    
    def calculate_critical_path(self) -> List[str]:
        """
        Calculate the critical path of the project.
        
        Returns:
            List of task IDs in the critical path
        """
        # Build dependency graph
        graph = {task_id: task.dependencies for task_id, task in self.tasks.items()}
        
        # Calculate earliest start times
        earliest_start = {}
        for task_id in self._topological_sort():
            task = self.tasks[task_id]
            if not task.dependencies:
                earliest_start[task_id] = 0
            else:
                earliest_start[task_id] = max(
                    earliest_start[dep] + self.tasks[dep].duration 
                    for dep in task.dependencies
                )
        
        # Calculate latest start times
        latest_start = {}
        for task_id in reversed(self._topological_sort()):
            task = self.tasks[task_id]
            successors = [t_id for t_id, t in self.tasks.items() if task_id in t.dependencies]
            
            if not successors:
                latest_start[task_id] = earliest_start[task_id]
            else:
                latest_start[task_id] = min(
                    latest_start[succ] - task.duration 
                    for succ in successors
                )
        
        # Tasks with zero slack are on the critical path
        critical_path = [
            task_id for task_id in self.tasks
            if earliest_start[task_id] == latest_start[task_id]
        ]
        
        return critical_path
    
    def _topological_sort(self) -> List[str]:
        """
        Perform topological sort of tasks based on dependencies.
        
        Returns:
            List of task IDs in topological order
        """
        # Build dependency graph
        graph = {task_id: set(task.dependencies) for task_id, task in self.tasks.items()}
        
        # Find all nodes with no incoming edges
        no_incoming = {
            task_id for task_id in self.tasks
            if not any(task_id in deps for deps in graph.values())
        }
        
        result = []
        while no_incoming:
            # Remove a node with no incoming edges
            node = no_incoming.pop()
            result.append(node)
            
            # Remove edges from this node
            if node in graph:
                for m in list(graph[node]):
                    graph[node].remove(m)
                    # If m has no other incoming edges, add it to no_incoming
                    if not any(m in deps for deps in graph.values()):
                        no_incoming.add(m)
        
        # Check for cycles
        if any(deps for deps in graph.values()):
            raise ValueError("Dependency cycle detected in tasks")
        
        return result
    
    def validate_dependencies(self) -> List[str]:
        """
        Validate task dependencies and detect cycles.
        
        Returns:
            List of error messages, empty if no errors
        """
        errors = []
        
        # Check for missing dependencies
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                if dep_id not in self.tasks:
                    errors.append(f"Task {task_id} depends on non-existent task {dep_id}")
        
        # Check for cycles
        try:
            self._topological_sort()
        except ValueError as e:
            errors.append(str(e))
        
        # Check for date inconsistencies
        for task_id, task in self.tasks.items():
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if dep_task and dep_task.end_date > task.start_date:
                    errors.append(
                        f"Task {task_id} starts before its dependency {dep_id} ends"
                    )
        
        return errors
    
    def adjust_dates_based_on_dependencies(self) -> None:
        """
        Automatically adjust task dates based on dependencies.
        """
        # Sort tasks topologically
        sorted_tasks = self._topological_sort()
        
        for task_id in sorted_tasks:
            task = self.tasks[task_id]
            
            if task.dependencies:
                # Find the latest end date among dependencies
                latest_end = max(
                    self.tasks[dep_id].end_date 
                    for dep_id in task.dependencies
                )
                
                # If task starts before latest dependency ends, adjust it
                if task.start_date <= latest_end:
                    duration = task.duration
                    new_start = latest_end + datetime.timedelta(days=1)
                    new_end = new_start + datetime.timedelta(days=duration - 1)
                    
                    task.start_date = new_start
                    task.end_date = new_end
        
        self.last_update = datetime.datetime.now()
    
    def get_project_duration(self) -> int:
        """
        Calculate the total project duration in days.
        
        Returns:
            Project duration in days
        """
        if not self.tasks:
            return 0
        
        start_date = min(task.start_date for task in self.tasks.values())
        end_date = max(task.end_date for task in self.tasks.values())
        
        return (end_date - start_date).days + 1
    
    def get_project_progress(self) -> float:
        """
        Calculate the overall project progress.
        
        Returns:
            Project progress as a percentage (0.0 to 1.0)
        """
        if not self.tasks:
            return 0.0
        
        total_duration = sum(task.duration for task in self.tasks.values())
        weighted_progress = sum(
            task.duration * task.progress for task in self.tasks.values()
        )
        
        return weighted_progress / total_duration if total_duration > 0 else 0.0
    
    def plot(self, figsize: Tuple[int, int] = (12, 8), 
             highlight_critical: bool = True,
             show_progress: bool = True) -> plt.Figure:
        """
        Generate a Gantt chart visualization.
        
        Args:
            figsize: Figure size (width, height) in inches
            highlight_critical: Whether to highlight critical path tasks
            show_progress: Whether to show progress bars
            
        Returns:
            Matplotlib figure object
        """
        if not self.tasks:
            raise ValueError("No tasks to plot")
        
        # Sort tasks by start date
        sorted_tasks = sorted(
            self.tasks.values(), 
            key=lambda x: (x.start_date, x.end_date)
        )
        
        # Prepare data
        labels = [task.name for task in sorted_tasks]
        start_dates = [task.start_date for task in sorted_tasks]
        durations = [task.duration for task in sorted_tasks]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot tasks
        y_positions = range(len(sorted_tasks))
        
        # Get critical path if requested
        critical_path = self.calculate_critical_path() if highlight_critical else []
        
        for i, task in enumerate(sorted_tasks):
            start = task.start_date
            end = task.end_date
            duration = (end - start).days + 1
            
            # Determine color based on critical path
            color = "#e74c3c" if task.id in critical_path else task.color
            
            # Plot task bar
            ax.barh(
                i, duration, left=mdates.date2num(start), 
                color=color, alpha=0.8, 
                edgecolor="black", linewidth=1
            )
            
            # Add progress bar if requested
            if show_progress and task.progress > 0:
                progress_width = duration * task.progress
                ax.barh(
                    i, progress_width, left=mdates.date2num(start),
                    color="darkgreen", alpha=0.5, height=0.3
                )
            
            # Add milestone marker if applicable
            if task.milestone:
                ax.scatter(
                    mdates.date2num(end), i,
                    marker="D", s=100, color="black", zorder=5
                )
        
        # Format axes
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels)
        ax.set_xlabel("Date")
        
        # Format x-axis as dates
        date_format = mdates.DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
        fig.autofmt_xdate()
        
        # Add grid
        ax.grid(True, axis="x", alpha=0.3)
        
        # Add title
        ax.set_title(f"{self.project_name} - Gantt Chart")
        
        # Add legend
        if highlight_critical:
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor="#e74c3c", edgecolor="black", label="Critical Path"),
                Patch(facecolor="#3498db", edgecolor="black", label="Regular Task")
            ]
            if show_progress:
                legend_elements.append(
                    Patch(facecolor="darkgreen", alpha=0.5, label="Progress")
                )
            ax.legend(handles=legend_elements, loc="upper right")
        
        plt.tight_layout()
        return fig
    
    def export_image(self, filename: str, dpi: int = 300) -> str:
        """
        Export Gantt chart as an image file.
        
        Args:
            filename: Output filename (without extension)
            dpi: Image resolution
            
        Returns:
            Path to the saved file
        """
        fig = self.plot()
        output_path = f"{filename}.png"
        fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        return output_path
    
    def export_pdf(self, filename: str) -> str:
        """
        Export Gantt chart as a PDF file.
        
        Args:
            filename: Output filename (without extension)
            
        Returns:
            Path to the saved file
        """
        fig = self.plot(figsize=(12, 10))
        output_path = f"{filename}.pdf"
        fig.savefig(output_path, format="pdf", bbox_inches="tight")
        plt.close(fig)
        return output_path
    
    def export_html(self, filename: str) -> str:
        """
        Export Gantt chart as an interactive HTML file.
        
        Args:
            filename: Output filename (without extension)
            
        Returns:
            Path to the saved file
        """
        try:
            import plotly.figure_factory as ff
            import plotly.io as pio
        except ImportError:
            raise ImportError("Plotly is required for HTML export. Install with 'pip install plotly'")
        
        # Prepare data for plotly
        df = []
        
        for task in self.tasks.values():
            df.append({
                "Task": task.name,
                "Start": task.start_date,
                "Finish": task.end_date,
                "Resource": ", ".join(task.resources) if task.resources else "Unassigned",
                "Complete": task.progress * 100
            })
        
        df = pd.DataFrame(df)
        
        # Create Gantt chart
        fig = ff.create_gantt(
            df, colors=["#3498db", "#e74c3c"], 
            index_col="Resource", show_colorbar=True,
            group_tasks=True, title=f"{self.project_name} - Gantt Chart"
        )
        
        # Add hover information
        fig.update_traces(
            mode="lines",
            hovertemplate="%{text}<br>Start: %{start}<br>End: %{end}<br>Progress: %{customdata}%",
            text=df["Task"],
            customdata=df["Complete"]
        )
        
        # Save as HTML
        output_path = f"{filename}.html"
        pio.write_html(fig, file=output_path, auto_open=False)
        
        return output_path
    
    def save(self, filename: str) -> str:
        """
        Save Gantt chart data to a JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to the saved file
        """
        data = {
            "project_name": self.project_name,
            "description": self.description,
            "last_update": self.last_update.isoformat(),
            "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        }
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    @classmethod
    def load(cls, filename: str) -> 'GanttChart':
        """
        Load Gantt chart data from a JSON file.
        
        Args:
            filename: Input filename
            
        Returns:
            GanttChart object
        """
        with open(filename, "r") as f:
            data = json.load(f)
        
        chart = cls(data["project_name"], data["description"])
        chart.last_update = datetime.datetime.fromisoformat(data["last_update"])
        
        for task_id, task_data in data["tasks"].items():
            chart.tasks[task_id] = Task.from_dict(task_data)
        
        return chart


class GanttChartManager:
    """
    Manager for creating and maintaining multiple Gantt charts.
    """
    
    def __init__(self, storage_dir: str = None):
        """
        Initialize a new Gantt chart manager.
        
        Args:
            storage_dir: Directory for storing Gantt chart data
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "gantt_charts")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.charts: Dict[str, GanttChart] = {}
    
    def create_chart(self, project_id: str, project_name: str, description: str = "") -> GanttChart:
        """
        Create a new Gantt chart.
        
        Args:
            project_id: Unique project identifier
            project_name: Name of the project
            description: Optional project description
            
        Returns:
            New GanttChart object
        """
        if project_id in self.charts:
            raise ValueError(f"Project with ID {project_id} already exists")
        
        chart = GanttChart(project_name, description)
        self.charts[project_id] = chart
        
        return chart
    
    def get_chart(self, project_id: str) -> GanttChart:
        """
        Get a Gantt chart by project ID.
        
        Args:
            project_id: Project identifier
            
        Returns:
            GanttChart object
        """
        if project_id not in self.charts:
            raise ValueError(f"Project with ID {project_id} not found")
        
        return self.charts[project_id]
    
    def list_charts(self) -> List[Tuple[str, str]]:
        """
        List all available Gantt charts.
        
        Returns:
            List of (project_id, project_name) tuples
        """
        return [(project_id, chart.project_name) for project_id, chart in self.charts.items()]
    
    def save_chart(self, project_id: str) -> str:
        """
        Save a Gantt chart to disk.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Path to the saved file
        """
        if project_id not in self.charts:
            raise ValueError(f"Project with ID {project_id} not found")
        
        chart = self.charts[project_id]
        filename = os.path.join(self.storage_dir, f"{project_id}.json")
        
        return chart.save(filename)
    
    def load_chart(self, project_id: str) -> GanttChart:
        """
        Load a Gantt chart from disk.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Loaded GanttChart object
        """
        filename = os.path.join(self.storage_dir, f"{project_id}.json")
        
        if not os.path.exists(filename):
            raise ValueError(f"No saved chart found for project ID {project_id}")
        
        chart = GanttChart.load(filename)
        self.charts[project_id] = chart
        
        return chart
    
    def delete_chart(self, project_id: str) -> None:
        """
        Delete a Gantt chart.
        
        Args:
            project_id: Project identifier
        """
        if project_id not in self.charts:
            raise ValueError(f"Project with ID {project_id} not found")
        
        # Remove from memory
        del self.charts[project_id]
        
        # Remove from disk if exists
        filename = os.path.join(self.storage_dir, f"{project_id}.json")
        if os.path.exists(filename):
            os.remove(filename)
    
    def save_all(self) -> List[str]:
        """
        Save all Gantt charts to disk.
        
        Returns:
            List of saved file paths
        """
        return [self.save_chart(project_id) for project_id in self.charts]
    
    def load_all(self) -> List[str]:
        """
        Load all Gantt charts from disk.
        
        Returns:
            List of loaded project IDs
        """
        loaded = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                project_id = os.path.splitext(filename)[0]
                self.load_chart(project_id)
                loaded.append(project_id)
        
        return loaded
